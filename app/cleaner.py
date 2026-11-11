import os
import shutil
import glob
from typing import Dict, List, Any
from app.utils import format_size, get_recycle_bin_info, empty_recycle_bin

def is_admin() -> bool:
    """Verifica si NosClean se está ejecutando con permisos de Administrador."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_junk_categories() -> List[Dict[str, Any]]:
    """Define las categorías de archivos temporales y basura del sistema."""
    user_local = os.environ.get('LOCALAPPDATA', '')
    user_roaming = os.environ.get('APPDATA', '')
    user_temp = os.environ.get('TEMP', '')
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    admin_mode = is_admin()

    # Detectar todas las cachés de perfiles de Chrome (Default, Profile 1, Profile 2, etc.)
    chrome_paths = []
    chrome_base = os.path.join(user_local, r"Google\Chrome\User Data")
    if os.path.exists(chrome_base):
        for profile_dir in ["Default"] + [os.path.basename(p) for p in glob.glob(os.path.join(chrome_base, "Profile *"))]:
            p_cache = os.path.join(chrome_base, profile_dir, "Cache")
            p_code = os.path.join(chrome_base, profile_dir, "Code Cache")
            p_gpu = os.path.join(chrome_base, profile_dir, "GPUCache")
            if os.path.exists(p_cache): chrome_paths.append(p_cache)
            if os.path.exists(p_code): chrome_paths.append(p_code)
            if os.path.exists(p_gpu): chrome_paths.append(p_gpu)

    # Detectar perfiles de Edge
    edge_paths = []
    edge_base = os.path.join(user_local, r"Microsoft\Edge\User Data")
    if os.path.exists(edge_base):
        for profile_dir in ["Default"] + [os.path.basename(p) for p in glob.glob(os.path.join(edge_base, "Profile *"))]:
            p_cache = os.path.join(edge_base, profile_dir, "Cache")
            p_code = os.path.join(edge_base, profile_dir, "Code Cache")
            if os.path.exists(p_cache): edge_paths.append(p_cache)
            if os.path.exists(p_code): edge_paths.append(p_code)

    categories = [
        {
            "id": "chrome_cache",
            "name": "Caché de Google Chrome (Todos los perfiles)",
            "description": "Imágenes, scripts y archivos web acumulados en tus perfiles de Chrome.",
            "paths": chrome_paths,
            "safe": True
        },
        {
            "id": "recycle_bin",
            "name": "Papelera de Reciclaje",
            "description": "Archivos eliminados que aún ocupan espacio en el disco.",
            "is_recycle_bin": True,
            "paths": [],
            "safe": True
        },
        {
            "id": "user_temp",
            "name": "Temporales del Usuario",
            "description": "Archivos generados por aplicaciones en la sesión actual (%TEMP%).",
            "paths": [user_temp] if user_temp else [],
            "safe": True
        },
        {
            "id": "system_temp",
            "name": "Temporales de Windows",
            "description": "Archivos temporales del sistema operativo (C:\\Windows\\Temp)." + (" (Requiere ejecutar como Administrador para borrado total)" if not admin_mode else ""),
            "paths": [os.path.join(system_root, "Temp")],
            "safe": True,
            "requires_admin": not admin_mode
        },
        {
            "id": "crash_dumps",
            "name": "Reportes de Errores y Crashes",
            "description": "Dumps de memoria generados cuando un programa falla.",
            "paths": [os.path.join(user_local, "CrashDumps")],
            "safe": True
        },
        {
            "id": "edge_cache",
            "name": "Caché de Microsoft Edge",
            "description": "Archivos temporales y caché del navegador Edge.",
            "paths": edge_paths,
            "safe": True
        },
        {
            "id": "pip_cache",
            "name": "Caché de Python Pip",
            "description": "Descargas previas de paquetes instalados por pip.",
            "paths": [os.path.join(user_local, "pip", "cache")],
            "safe": True
        },
        {
            "id": "npm_cache",
            "name": "Caché de Node.js / NPM",
            "description": "Archivos temporales generados al instalar paquetes con npm.",
            "paths": [os.path.join(user_roaming, "npm-cache")],
            "safe": True
        },
        {
            "id": "win_update_cache",
            "name": "Descargas de Windows Update",
            "description": "Instaladores residuales de actualizaciones ya descargadas." + (" (Requiere ejecutar como Administrador para eliminar)" if not admin_mode else ""),
            "paths": [os.path.join(system_root, r"SoftwareDistribution\Download")],
            "safe": True,
            "requires_admin": not admin_mode
        },
        {
            "id": "recent_history",
            "name": "Historial de Archivos Recientes",
            "description": "Accesos directos a archivos abiertos recientemente.",
            "paths": [os.path.join(user_roaming, r"Microsoft\Windows\Recent")],
            "safe": True
        }
    ]
    return categories

def _is_protected_temp_entry(entry_name: str, entry_path: str) -> bool:
    """
    Protege las carpetas activas de PyInstaller (_MEIxxxxxx) y de WebView2/pywebview
    para evitar que NosClean escanee o intente borrar sus propios binarios en ejecución.
    """
    import sys
    name_low = entry_name.lower()
    if name_low.startswith("_mei") or "pywebview" in name_low or "ebwebview" in name_low or "nosclean" in name_low:
        return True
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        try:
            norm_entry = os.path.normcase(os.path.abspath(entry_path))
            norm_mei = os.path.normcase(os.path.abspath(meipass))
            if norm_entry == norm_mei or norm_entry.startswith(norm_mei + os.sep):
                return True
        except Exception:
            pass
    return False

def scan_directory_size(path: str, max_seconds: float = 1.2, max_files: int = 15000) -> (int, int):
    """
    Calcula de forma iterativa y ultrarrápida el tamaño en bytes y cantidad de archivos.
    Incluye un presupuesto máximo de tiempo (max_seconds) y límite de archivos para que,
    al ejecutarse como Administrador sobre carpetas masivas como Windows Update o Temp,
    nunca congele el hilo principal ni ralentice la interfaz.
    """
    import time
    total_size = 0
    file_count = 0
    if not os.path.exists(path):
        return 0, 0

    deadline = time.perf_counter() + max_seconds
    stack = [path]
    is_root = True

    while stack:
        if time.perf_counter() > deadline or file_count >= max_files:
            break
        current_dir = stack.pop()
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    if is_root and _is_protected_temp_entry(entry.name, entry.path):
                        continue
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total_size += entry.stat().st_size
                            file_count += 1
                            if file_count >= max_files:
                                break
                        elif entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        except (PermissionError, FileNotFoundError, OSError):
            pass
        is_root = False

    return total_size, file_count

_JUNK_SCAN_CACHE = {"timestamp": 0.0, "data": None}

def invalidate_junk_cache():
    _JUNK_SCAN_CACHE["timestamp"] = 0.0
    _JUNK_SCAN_CACHE["data"] = None

def scan_junk(force_refresh: bool = False) -> Dict[str, Any]:
    """Escanea todas las categorías y devuelve el resumen sin borrar nada."""
    import time
    now = time.time()
    if not force_refresh and _JUNK_SCAN_CACHE["data"] is not None and (now - _JUNK_SCAN_CACHE["timestamp"] < 4.0):
        return _JUNK_SCAN_CACHE["data"]

    categories = get_junk_categories()
    results = []
    grand_total_bytes = 0
    grand_total_files = 0

    for cat in categories:
        if cat.get("is_recycle_bin"):
            rb = get_recycle_bin_info()
            cat_bytes = rb["size_bytes"]
            cat_files = rb["items_count"]
        else:
            cat_bytes = 0
            cat_files = 0
            for p in cat.get("paths", []):
                if os.path.exists(p):
                    s, f = scan_directory_size(p)
                    cat_bytes += s
                    cat_files += f

        grand_total_bytes += cat_bytes
        grand_total_files += cat_files

        results.append({
            "id": cat["id"],
            "name": cat["name"],
            "description": cat["description"],
            "safe": cat.get("safe", True),
            "requires_admin": cat.get("requires_admin", False),
            "size_bytes": cat_bytes,
            "size_formatted": format_size(cat_bytes),
            "file_count": cat_files,
            "exists": cat_bytes > 0 or cat_files > 0
        })

    res_data = {
        "is_admin": is_admin(),
        "categories": results,
        "total_bytes": grand_total_bytes,
        "total_formatted": format_size(grand_total_bytes),
        "total_files": grand_total_files
    }
    _JUNK_SCAN_CACHE["timestamp"] = time.time()
    _JUNK_SCAN_CACHE["data"] = res_data
    return res_data

def clean_directory_contents(path: str, _depth: int = 0) -> (int, int, int):
    """Limpia el contenido de un directorio sin eliminar el directorio raíz ni carpetas protegidas de NosClean."""
    bytes_freed = 0
    files_deleted = 0
    skipped_count = 0

    if not os.path.exists(path) or _depth > 6:
        return 0, 0, 0

    try:
        entries = list(os.scandir(path))
    except (PermissionError, OSError):
        return 0, 0, 1

    for entry in entries:
        if _depth == 0 and _is_protected_temp_entry(entry.name, entry.path):
            continue
        try:
            if entry.is_file(follow_symlinks=False):
                try:
                    size = entry.stat().st_size
                    os.remove(entry.path)
                    bytes_freed += size
                    files_deleted += 1
                except (PermissionError, OSError):
                    skipped_count += 1
            elif entry.is_dir(follow_symlinks=False):
                dir_size, dir_files = scan_directory_size(entry.path, max_seconds=0.4, max_files=3000)
                try:
                    shutil.rmtree(entry.path, ignore_errors=False)
                    bytes_freed += dir_size
                    files_deleted += dir_files
                except Exception:
                    bf, fd, sc = clean_directory_contents(entry.path, _depth + 1)
                    bytes_freed += bf
                    files_deleted += fd
                    skipped_count += (sc + 1)
        except Exception:
            skipped_count += 1

    return bytes_freed, files_deleted, skipped_count

def clean_selected_categories(selected_ids: List[str]) -> Dict[str, Any]:
    """Ejecuta la limpieza para las categorías seleccionadas."""
    categories = get_junk_categories()
    cat_dict = {c["id"]: c for c in categories}

    total_freed_bytes = 0
    total_files_deleted = 0
    total_skipped = 0
    details = []

    for cat_id in selected_ids:
        cat = cat_dict.get(cat_id)
        if not cat:
            continue

        if cat.get("is_recycle_bin"):
            rb_before = get_recycle_bin_info()
            success, msg = empty_recycle_bin()
            if success:
                total_freed_bytes += rb_before["size_bytes"]
                total_files_deleted += rb_before["items_count"]
                details.append({
                    "id": cat_id,
                    "name": cat["name"],
                    "freed_formatted": rb_before["size_formatted"],
                    "files_deleted": rb_before["items_count"],
                    "skipped": 0,
                    "status": "Vaciada exitosamente"
                })
            else:
                details.append({
                    "id": cat_id,
                    "name": cat["name"],
                    "freed_formatted": "0 B",
                    "files_deleted": 0,
                    "skipped": 0,
                    "status": msg
                })
        else:
            cat_freed = 0
            cat_deleted = 0
            cat_skipped = 0
            for p in cat.get("paths", []):
                if os.path.exists(p):
                    bf, fd, sc = clean_directory_contents(p)
                    cat_freed += bf
                    cat_deleted += fd
                    cat_skipped += sc

            total_freed_bytes += cat_freed
            total_files_deleted += cat_deleted
            total_skipped += cat_skipped
            details.append({
                "id": cat_id,
                "name": cat["name"],
                "freed_formatted": format_size(cat_freed),
                "files_deleted": cat_deleted,
                "skipped": cat_skipped,
                "status": f"Limpieza completada ({cat_skipped} omitidos en uso)" if cat_skipped > 0 else "Limpieza completa"
            })

    invalidate_junk_cache()
    return {
        "success": True,
        "freed_bytes": total_freed_bytes,
        "freed_formatted": format_size(total_freed_bytes),
        "total_files_deleted": total_files_deleted,
        "total_skipped": total_skipped,
        "details": details
    }

# Procesos críticos del sistema y del propio motor gráfico de NosClean que jamás deben paginarse a disco
PROTECTED_SYSTEM_PROCS = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "dwm.exe", "explorer.exe",
    "fontdrvhost.exe", "wmiprvse.exe", "searchindexer.exe", "searchhost.exe",
    "startmenuexperiencehost.exe", "shellexperiencehost.exe", "sihost.exe",
    "taskhostw.exe", "ctfmon.exe", "audiodg.exe", "spoolsv.exe",
    "msmpeng.exe", "securityhealthservice.exe", "nosclean.exe",
    "msedgewebview2.exe", "python.exe", "pythonw.exe"
}

def quick_optimize() -> Dict[str, Any]:
    """Optimización rápida en 1 clic:
    1. Vacía la memoria de procesos inactivos de usuario (excluyendo servicios críticos de Windows y NosClean).
    2. Limpia temporales seguros de usuario y cachés de navegadores.
    3. Retorna estadísticas precisas antes y después."""
    import psutil
    import ctypes
    
    mem_before = psutil.virtual_memory()
    current_pid = os.getpid()
    
    # 1. Optimizar RAM de forma segura (sin paginar procesos críticos de Windows ni WebView2 cuando es Admin)
    trimmed_procs = 0
    try:
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        for p in psutil.process_iter(['pid', 'name']):
            try:
                pid = p.info['pid']
                pname = (p.info['name'] or '').lower()
                if pid <= 4 or pid == current_pid or pname in PROTECTED_SYSTEM_PROCS:
                    continue
                h = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
                if h:
                    psapi.EmptyWorkingSet(h)
                    kernel32.CloseHandle(h)
                    trimmed_procs += 1
            except Exception:
                pass
    except Exception:
        pass
        
    mem_after = psutil.virtual_memory()
    ram_freed_bytes = max(0, mem_before.used - mem_after.used)
    
    # 2. Limpieza rápida de temporales de usuario y cachés
    quick_categories = ["user_temp", "chrome_cache", "edge_cache"]
    clean_res = clean_selected_categories(quick_categories)
    
    return {
        "success": True,
        "ram_freed_bytes": ram_freed_bytes,
        "ram_freed_formatted": format_size(ram_freed_bytes),
        "disk_freed_bytes": clean_res.get("freed_bytes", 0),
        "disk_freed_formatted": clean_res.get("freed_formatted", "0 B"),
        "files_deleted": clean_res.get("total_files_deleted", 0),
        "processes_optimized": trimmed_procs,
        "new_ram_percent": mem_after.percent,
        "new_ram_used_gb": round(mem_after.used / (1024**3), 2),
        "new_ram_total_gb": round(mem_after.total / (1024**3), 2),
        "new_ram_avail_gb": round(mem_after.available / (1024**3), 2),
    }
