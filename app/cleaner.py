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

_TASK_PROGRESS = {"percent": 0, "step": "", "active": False}

def set_task_progress(percent: int, step: str = "", active: bool = True):
    """Actualiza el porcentaje real de la operación en curso."""
    _TASK_PROGRESS["percent"] = max(0, min(100, int(percent)))
    if step:
        _TASK_PROGRESS["step"] = step
    _TASK_PROGRESS["active"] = active

def get_task_progress() -> Dict[str, Any]:
    """Devuelve el progreso real de la tarea actual."""
    return dict(_TASK_PROGRESS)

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
    total_cats = max(1, len(categories))
    set_task_progress(5, "Iniciando análisis de categorías...", True)

    for idx, cat in enumerate(categories):
        pct = int(5 + ((idx + 1) / total_cats) * 92)
        set_task_progress(pct, f"Analizando {cat['name']}...", True)

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
    set_task_progress(100, "Análisis completado", False)
    return res_data

def clean_directory_contents(
    path: str,
    _depth: int = 0,
    progress_start: float = None,
    progress_end: float = None,
    step_label: str = ""
) -> (int, int, int):
    """Limpia el contenido de un directorio en una sola pasada rápida (O(N)), retirando atributos Read-Only si es necesario."""
    import time
    import stat
    bytes_freed = 0
    files_deleted = 0
    skipped_count = 0

    if not os.path.exists(path):
        return 0, 0, 0

    try:
        top_entries = list(os.scandir(path))
    except (PermissionError, OSError):
        return 0, 0, 1

    total_top = max(1, len(top_entries))
    deadline = time.monotonic() + 3.0

    for idx, entry in enumerate(top_entries):
        if progress_start is not None and progress_end is not None:
            cur_pct = progress_start + ((idx + 1) / total_top) * (progress_end - progress_start)
            set_task_progress(int(cur_pct), step_label, True)

        if _is_protected_temp_entry(entry.name, entry.path):
            continue

        if time.monotonic() > deadline:
            break

        try:
            if entry.is_file(follow_symlinks=False):
                try:
                    size = entry.stat().st_size
                    try:
                        os.remove(entry.path)
                    except PermissionError:
                        os.chmod(entry.path, stat.S_IWRITE)
                        os.remove(entry.path)
                    bytes_freed += size
                    files_deleted += 1
                except (PermissionError, OSError):
                    skipped_count += 1
            elif entry.is_dir(follow_symlinks=False):
                for root_dir, dirs, files in os.walk(entry.path, topdown=False):
                    if time.monotonic() > deadline:
                        break
                    for fname in files:
                        fpath = os.path.join(root_dir, fname)
                        try:
                            fsize = os.path.getsize(fpath)
                            try:
                                os.remove(fpath)
                            except PermissionError:
                                os.chmod(fpath, stat.S_IWRITE)
                                os.remove(fpath)
                            bytes_freed += fsize
                            files_deleted += 1
                        except (PermissionError, OSError):
                            skipped_count += 1
                    for dname in dirs:
                        dpath = os.path.join(root_dir, dname)
                        try:
                            try:
                                os.rmdir(dpath)
                            except PermissionError:
                                os.chmod(dpath, stat.S_IWRITE)
                                os.rmdir(dpath)
                        except (PermissionError, OSError):
                            pass
                try:
                    try:
                        os.rmdir(entry.path)
                    except PermissionError:
                        os.chmod(entry.path, stat.S_IWRITE)
                        os.rmdir(entry.path)
                except (PermissionError, OSError):
                    pass
        except Exception:
            skipped_count += 1

    return bytes_freed, files_deleted, skipped_count

def clean_selected_categories(
    selected_ids: List[str],
    progress_min: int = 5,
    progress_max: int = 98
) -> Dict[str, Any]:
    """Ejecuta la limpieza para las categorías seleccionadas reportando progreso real."""
    categories = get_junk_categories()
    cat_dict = {c["id"]: c for c in categories}

    total_freed_bytes = 0
    total_files_deleted = 0
    total_skipped = 0
    details = []

    valid_ids = [cid for cid in selected_ids if cid in cat_dict]
    total_cats = max(1, len(valid_ids))
    span_per_cat = (progress_max - progress_min) / total_cats

    for idx, cat_id in enumerate(valid_ids):
        cat = cat_dict[cat_id]
        c_start = progress_min + idx * span_per_cat
        c_end = c_start + span_per_cat
        step_msg = f"Limpiando {cat['name']}..."
        set_task_progress(int(c_start), step_msg, True)

        if cat.get("is_recycle_bin"):
            rb_before = get_recycle_bin_info()
            success, msg = empty_recycle_bin()
            set_task_progress(int(c_end), step_msg, True)
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
            paths = [p for p in cat.get("paths", []) if os.path.exists(p)]
            p_count = max(1, len(paths))
            p_span = (c_end - c_start) / p_count
            for p_idx, p in enumerate(paths):
                p_start = c_start + p_idx * p_span
                p_end = p_start + p_span
                bf, fd, sc = clean_directory_contents(p, 0, p_start, p_end, step_msg)
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
    if progress_min <= 5:
        set_task_progress(100, "¡Limpieza completada!", False)
    return {
        "success": True,
        "freed_bytes": total_freed_bytes,
        "freed_formatted": format_size(total_freed_bytes),
        "total_files_deleted": total_files_deleted,
        "total_skipped": total_skipped,
        "details": details
    }

# Procesos críticos del kernel que no deben paginarse
PROTECTED_SYSTEM_PROCS = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "dwm.exe", "fontdrvhost.exe",
    "audiodg.exe", "nosclean.exe"
}

def quick_optimize() -> Dict[str, Any]:
    """Optimización rápida en 1 clic:
    1. Primero limpia temporales seguros de usuario y cachés de navegadores (para que el I/O de disco ocurra antes de liberar RAM).
    2. Luego vacía el Working Set de procesos en memoria RAM (excluyendo kernel y el propio NosClean).
    3. Invalida la caché de monitoreo y retorna estadísticas exactas antes y después."""
    import psutil
    import ctypes
    import gc
    from app.auditor import invalidate_overview_cache
    
    set_task_progress(5, "Iniciando depuración de archivos temporales...", True)
    mem_before = psutil.virtual_memory()
    current_pid = os.getpid()

    # Identificar árbol de procesos propio de NosClean (incluyendo su WebView2 hijo) para no tocar su ventana
    nosclean_pids = {current_pid}
    try:
        curr_proc = psutil.Process(current_pid)
        for child in curr_proc.children(recursive=True):
            nosclean_pids.add(child.pid)
    except Exception:
        pass

    # 1. Limpieza rápida de temporales y cachés PRIMERO (5% a 52%)
    quick_categories = ["user_temp", "chrome_cache", "edge_cache", "windows_temp", "crash_dumps"]
    clean_res = clean_selected_categories(quick_categories, progress_min=5, progress_max=52)
    
    # 2. Optimizar RAM al final para que quede en su punto más bajo al terminar (52% a 98%)
    trimmed_procs = 0
    try:
        gc.collect()
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        procs = list(psutil.process_iter(['pid', 'name']))
        total_procs = max(1, len(procs))
        for idx, p in enumerate(procs):
            if idx % 8 == 0:
                pct = int(52 + ((idx + 1) / total_procs) * 46)
                set_task_progress(pct, f"Liberando memoria RAM inactiva ({trimmed_procs} procesos optimizados)...", True)
            try:
                pid = p.info['pid']
                pname = (p.info['name'] or '').lower()
                if pid <= 4 or pid in nosclean_pids or pname in PROTECTED_SYSTEM_PROCS:
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
    invalidate_overview_cache()
    set_task_progress(100, "¡Optimización completada!", False)
    
    return {
        "success": True,
        "ram_freed_bytes": ram_freed_bytes,
        "ram_freed_formatted": format_size(ram_freed_bytes),
        "disk_freed_bytes": clean_res.get("freed_bytes", 0),
        "disk_freed_formatted": clean_res.get("freed_formatted", "0 B"),
        "files_deleted": clean_res.get("total_files_deleted", 0),
        "processes_optimized": trimmed_procs,
        "before_ram_used_gb": round(mem_before.used / (1024**3), 2),
        "before_ram_used_formatted": format_size(mem_before.used),
        "new_ram_percent": mem_after.percent,
        "new_ram_used_gb": round(mem_after.used / (1024**3), 2),
        "new_ram_used_formatted": format_size(mem_after.used),
        "new_ram_free_formatted": format_size(mem_after.available),
        "new_ram_total_gb": round(mem_after.total / (1024**3), 2),
        "new_ram_avail_gb": round(mem_after.available / (1024**3), 2),
    }
