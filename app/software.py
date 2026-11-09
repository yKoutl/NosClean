import os
import winreg
import glob
from typing import List, Dict, Any
from app.utils import format_size

def get_installed_programs() -> List[Dict[str, Any]]:
    """
    Obtiene la lista completa de programas instalados en Windows
    desde el Registro (64-bit, 32-bit y Usuario Actual).
    """
    programs_map = {}
    
    registry_locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall", "Sistema (64-bit)"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall", "Sistema (32-bit)"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall", "Usuario")
    ]

    for hkey, subkey, scope in registry_locations:
        try:
            with winreg.OpenKey(hkey, subkey) as root_key:
                num_subkeys = winreg.QueryInfoKey(root_key)[0]
                for i in range(num_subkeys):
                    try:
                        app_guid = winreg.EnumKey(root_key, i)
                        with winreg.OpenKey(root_key, app_guid) as app_key:
                            # Obtener DisplayName
                            try:
                                name, _ = winreg.QueryValueEx(app_key, "DisplayName")
                                if not name or not name.strip():
                                    continue
                            except OSError:
                                continue

                            # Filtrar actualizaciones de Windows o componentes de sistema ocultos
                            try:
                                is_system, _ = winreg.QueryValueEx(app_key, "SystemComponent")
                                if is_system == 1:
                                    continue
                            except OSError:
                                pass

                            try:
                                parent_key, _ = winreg.QueryValueEx(app_key, "ParentKeyName")
                                if parent_key:
                                    continue
                            except OSError:
                                pass

                            # Versión
                            version = "N/D"
                            try:
                                v, _ = winreg.QueryValueEx(app_key, "DisplayVersion")
                                if v:
                                    version = str(v).strip()
                            except OSError:
                                pass

                            # Publicador
                            publisher = "Desconocido"
                            try:
                                p, _ = winreg.QueryValueEx(app_key, "Publisher")
                                if p:
                                    publisher = str(p).strip()
                            except OSError:
                                pass

                            # Fecha de instalación
                            install_date = "N/D"
                            try:
                                d, _ = winreg.QueryValueEx(app_key, "InstallDate")
                                if d:
                                    sd = str(d).strip()
                                    if len(sd) == 8:
                                        install_date = f"{sd[0:4]}-{sd[4:6]}-{sd[6:8]}"
                                    else:
                                        install_date = sd
                            except OSError:
                                pass

                            # Tamaño estimado
                            size_bytes = 0
                            try:
                                kb, _ = winreg.QueryValueEx(app_key, "EstimatedSize")
                                if kb and isinstance(kb, int):
                                    size_bytes = kb * 1024
                            except OSError:
                                pass

                            # Comando de desinstalación
                            uninstall_cmd = ""
                            try:
                                u, _ = winreg.QueryValueEx(app_key, "UninstallString")
                                if u:
                                    uninstall_cmd = str(u).strip()
                            except OSError:
                                pass

                            # Ubicación de instalación
                            install_loc = ""
                            try:
                                loc, _ = winreg.QueryValueEx(app_key, "InstallLocation")
                                if loc:
                                    install_loc = str(loc).strip()
                            except OSError:
                                pass

                            # Si tenía una ruta de instalación definida pero la carpeta ya fue eliminada, omitir
                            if install_loc and len(install_loc) > 3 and not os.path.exists(install_loc):
                                continue

                            item_key = f"{name.strip().lower()}--{version}"
                            if item_key not in programs_map or size_bytes > programs_map[item_key]["size_bytes"]:
                                programs_map[item_key] = {
                                    "name": name.strip(),
                                    "version": version,
                                    "publisher": publisher,
                                    "install_date": install_date,
                                    "size_bytes": size_bytes,
                                    "size_formatted": format_size(size_bytes) if size_bytes > 0 else "N/D",
                                    "uninstall_command": uninstall_cmd,
                                    "install_location": install_loc,
                                    "scope": scope
                                }

                    except OSError:
                        continue
        except OSError:
            continue

    programs_list = list(programs_map.values())
    programs_list.sort(key=lambda x: x["name"].lower())
    return programs_list

def get_startup_applications() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de aplicaciones configuradas para iniciar con Windows.
    """
    startup_items = []
    
    registry_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Usuario Actual"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "Sistema"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "Sistema (32-bit)")
    ]

    for root, subkey, origin in registry_keys:
        try:
            with winreg.OpenKey(root, subkey) as k:
                num_values = winreg.QueryInfoKey(k)[1]
                for i in range(num_values):
                    try:
                        name, val, _ = winreg.EnumValue(k, i)
                        startup_items.append({
                            "name": name,
                            "command": val,
                            "location": origin,
                            "type": "Registro"
                        })
                    except OSError:
                        continue
        except OSError:
            pass

    # Carpetas de inicio
    startup_folders = [
        (os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"), "Carpeta Inicio (Usuario)"),
        (os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup"), "Carpeta Inicio (Global)")
    ]

    for s_path, origin in startup_folders:
        if os.path.exists(s_path):
            try:
                for f in os.listdir(s_path):
                    if f.lower() != 'desktop.ini':
                        full_p = os.path.join(s_path, f)
                        startup_items.append({
                            "name": os.path.splitext(f)[0],
                            "command": full_p,
                            "location": origin,
                            "type": "Acceso Directo"
                        })
            except Exception:
                pass

    return startup_items

