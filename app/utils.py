import os
import subprocess
import ctypes
from ctypes import wintypes
from typing import Optional

def format_size(bytes_num: int) -> str:
    """Convierte bytes a formato legible (KB, MB, GB, TB)."""
    if bytes_num is None or bytes_num < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"

def open_in_explorer(target_path: str):
    """Abre el explorador de Windows seleccionando el archivo o carpeta."""
    norm_path = os.path.normpath(target_path)
    if not os.path.exists(norm_path):
        return False, "La ruta no existe"
    try:
        if os.path.isfile(norm_path):
            subprocess.Popen(f'explorer.exe /select,"{norm_path}"')
        else:
            subprocess.Popen(f'explorer.exe "{norm_path}"')
        return True, "Abierto en el explorador"
    except Exception as e:
        return False, str(e)

def recycle_path(path: str):
    """Envía un archivo o carpeta a la Papelera de Reciclaje."""
    norm_path = os.path.normpath(path)
    if not os.path.exists(norm_path):
        return False, "El archivo o carpeta no existe"
    try:
        import send2trash
        send2trash.send2trash(norm_path)
        return True, "Enviado a la papelera con éxito"
    except Exception as e:
        err_msg = str(e)
        if "0x80270021" in err_msg or "Acceso denegado" in err_msg or "WinError 5" in err_msg:
            return False, "Windows bloqueó el borrado: Este archivo está en 'Program Files' y requiere Permisos de Administrador."
        return False, f"Error al enviar a la papelera: {err_msg}"

def get_recycle_bin_info():
    """Obtiene el tamaño total y número de elementos en la papelera de reciclaje."""
    try:
        class SHQUERYRBINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.DWORD),
                ('i64Size', ctypes.c_int64),
                ('i64NumItems', ctypes.c_int64)
            ]
        rbinfo = SHQUERYRBINFO()
        rbinfo.cbSize = ctypes.sizeof(SHQUERYRBINFO)
        res = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rbinfo))
        if res == 0:
            return {
                "size_bytes": rbinfo.i64Size,
                "size_formatted": format_size(rbinfo.i64Size),
                "items_count": rbinfo.i64NumItems
            }
    except Exception:
        pass
    return {"size_bytes": 0, "size_formatted": "0 B", "items_count": 0}

def empty_recycle_bin():
    """Vacía la papelera de reciclaje de Windows de manera silenciosa."""
    try:
        SHERB_NOCONFIRMATION = 0x00000001
        SHERB_NOPROGRESSUI = 0x00000002
        SHERB_NOSOUND = 0x00000004
        flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
        return res == 0, "Papelera vaciada correctamente" if res == 0 else "Error al vaciar papelera"
    except Exception as e:
        return False, str(e)

def open_windows_app(action_type: str):
    """Abre herramientas de configuración de Windows."""
    try:
        if action_type == "appsfeatures":
            subprocess.Popen("start ms-settings:appsfeatures", shell=True)
        elif action_type == "storagesense":
            subprocess.Popen("start ms-settings:storagesense", shell=True)
        elif action_type == "taskmgr":
            subprocess.Popen("taskmgr")
        elif action_type == "startup":
            subprocess.Popen("start ms-settings:startupapps", shell=True)
        elif action_type == "cleanmgr":
            subprocess.Popen("cleanmgr")
        return True, "Herramienta iniciada"
    except Exception as e:
        return False, str(e)

def create_windows_shortcut(target_type: str = "desktop"):
    """
    Crea el acceso directo oficial de NosClean con su icono oficial (NosClean.ico).
    target_type: 'desktop' para el Escritorio, 'taskbar' para preparar y anclar a la Barra de Tareas.
    """
    import sys
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # 1. Determinar directorio base del proyecto o ejecutable
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        exe_path = os.path.join(base_dir, "NosClean.exe")
        if not os.path.exists(exe_path):
            dist_exe = os.path.join(base_dir, "dist", "NosClean.exe")
            if os.path.exists(dist_exe):
                exe_path = dist_exe
            else:
                exe_path = os.path.join(base_dir, "iniciar_panel.bat")
                
        ico_path = os.path.join(base_dir, "NosClean.ico")
        if not os.path.exists(ico_path):
            ico_path = os.path.join(base_dir, "static", "favicon.ico")

        # 2. Rutas dinámicas de carpetas del sistema Windows
        try:
            desktop_dir = shell.SpecialFolders("Desktop")
        except Exception:
            desktop_dir = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Default"), "Desktop")

        try:
            programs_dir = shell.SpecialFolders("Programs")
        except Exception:
            programs_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")

        taskbar_dir = os.path.expandvars(r"%AppData%\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar")

        # 3. Crear siempre el acceso en el Escritorio
        desktop_lnk = os.path.join(desktop_dir, "NosClean.lnk")
        s_desk = shell.CreateShortCut(desktop_lnk)
        s_desk.TargetPath = exe_path
        s_desk.WorkingDirectory = base_dir
        s_desk.Description = "NosClean - Suite de Auditoría, Optimización y Limpieza para Windows"
        if os.path.exists(ico_path):
            s_desk.IconLocation = f"{ico_path},0"
        s_desk.save()

        # 4. Crear en el Menú Inicio (Programas)
        if os.path.exists(programs_dir):
            try:
                prog_lnk = os.path.join(programs_dir, "NosClean.lnk")
                s_prog = shell.CreateShortCut(prog_lnk)
                s_prog.TargetPath = exe_path
                s_prog.WorkingDirectory = base_dir
                s_prog.Description = "NosClean - Suite de Auditoría, Optimización y Limpieza para Windows"
                if os.path.exists(ico_path):
                    s_prog.IconLocation = f"{ico_path},0"
                s_prog.save()
            except Exception:
                pass

        # 5. Actualizar siempre los accesos en la carpeta de la Barra de Tareas (para no dejar rutas antiguas)
        if os.path.exists(taskbar_dir):
            try:
                for tb_name in ["NosClean.lnk", "NosClean (2).lnk"]:
                    tb_lnk = os.path.join(taskbar_dir, tb_name)
                    if os.path.exists(tb_lnk) or tb_name == "NosClean.lnk":
                        s_tb = shell.CreateShortCut(tb_lnk)
                        s_tb.TargetPath = exe_path
                        s_tb.WorkingDirectory = base_dir
                        s_tb.Description = "NosClean - Suite de Auditoría, Optimización y Limpieza para Windows"
                        if os.path.exists(ico_path):
                            s_tb.IconLocation = f"{ico_path},0"
                        s_tb.save()
            except Exception:
                pass

        # 6. Manejar solicitud explícita de Barra de Tareas
        if target_type == "taskbar":
            # Abrir el Explorador de Windows con el ejecutable seleccionado
            target_to_select = exe_path if os.path.exists(exe_path) else desktop_lnk
            try:
                subprocess.Popen(f'explorer.exe /select,"{target_to_select}"')
            except Exception:
                pass

            return True, "Acceso preparado para la Barra de Tareas.", {
                "type": "taskbar",
                "exe_path": exe_path,
                "shortcut_path": desktop_lnk
            }

        return True, "Acceso directo creado con éxito en tu Escritorio con el icono oficial.", {
            "type": "desktop",
            "shortcut_path": desktop_lnk
        }
    except Exception as e:
        return False, f"Error al generar acceso directo: {str(e)}", {}

def is_admin() -> bool:
    """Verifica si NosClean se está ejecutando con permisos de Administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def restart_as_admin():
    """
    Solicita elevación UAC de Windows (runas) para reiniciar NosClean como Administrador.
    Retorna (success, message, data).
    """
    import sys
    if is_admin():
        return True, "NosClean ya se está ejecutando con permisos de Administrador.", {"already_admin": True}

    try:
        if getattr(sys, 'frozen', False):
            target_exe = sys.executable
            base_dir = os.path.dirname(target_exe)
            params = "--elevated-restart"
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            exe_candidate = os.path.join(base_dir, "NosClean.exe")
            main_script = os.path.join(base_dir, "main.py")
            # Si se está ejecutando desde Python, relanzar con pythonw/python main.py para usar el código actual
            py_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(py_dir, "pythonw.exe")
            if os.path.exists(pythonw):
                target_exe = pythonw
            elif os.path.exists(sys.executable):
                target_exe = sys.executable
            elif os.path.exists(exe_candidate):
                target_exe = exe_candidate
            else:
                target_exe = sys.executable

            if target_exe.lower().endswith("nosclean.exe"):
                params = "--elevated-restart"
            else:
                params = f'"{main_script}" --elevated-restart'

        res = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            target_exe,
            params,
            base_dir,
            1
        )
        # En Windows API, ShellExecuteW retorna un valor > 32 si tuvo éxito
        if res > 32:
            return True, "Abriendo NosClean con permisos de Administrador...", {"restarting": True}
        else:
            return False, "No se otorgaron los permisos en la ventana de Windows. Puedes intentarlo de nuevo, seguir los pasos manuales o continuar sin Administrador.", {"cancelled": True, "code": res}
    except Exception as e:
        return False, f"No se pudo iniciar como Administrador: {str(e)}", {"error": str(e)}



