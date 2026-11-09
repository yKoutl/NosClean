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

