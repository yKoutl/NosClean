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

def scan_directory_size(path: str) -> (int, int):
    """Calcula recursivamente el tamaño en bytes y cantidad de archivos en un directorio."""
    total_size = 0
    file_count = 0
    if not os.path.exists(path):
        return 0, 0

    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat().st_size
                        file_count += 1
                    elif entry.is_dir(follow_symlinks=False):
                        s, c = scan_directory_size(entry.path)
                        total_size += s
                        file_count += c
                except (PermissionError, FileNotFoundError, OSError):
                    continue
    except (PermissionError, FileNotFoundError, OSError):
        pass

    return total_size, file_count

def scan_junk() -> Dict[str, Any]:
    """Escanea todas las categorías y devuelve el resumen sin borrar nada."""
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

    return {
        "categories": results,
        "total_bytes": grand_total_bytes,
        "total_formatted": format_size(grand_total_bytes),
        "total_files": grand_total_files
    }

def clean_directory_contents(path: str) -> (int, int, int):
    """Limpia el contenido de un directorio sin eliminar el directorio raíz."""
    bytes_freed = 0
    files_deleted = 0
    skipped_count = 0

    if not os.path.exists(path):
        return 0, 0, 0

    try:
        entries = list(os.scandir(path))
    except (PermissionError, OSError):
        return 0, 0, 1

    for entry in entries:
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
                dir_size, dir_files = scan_directory_size(entry.path)
                try:
                    shutil.rmtree(entry.path, ignore_errors=False)
                    bytes_freed += dir_size
                    files_deleted += dir_files
                except Exception:
                    bf, fd, sc = clean_directory_contents(entry.path)
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

    return {
        "success": True,
        "freed_bytes": total_freed_bytes,
        "freed_formatted": format_size(total_freed_bytes),
        "total_files_deleted": total_files_deleted,
        "total_skipped": total_skipped,
        "details": details
    }

def quick_optimize() -> Dict[str, Any]:
    """Optimización rápida en 1 clic:
    1. Vacía la memoria de procesos inactivos (EmptyWorkingSet).
    2. Limpia temporales seguros de usuario y cachés de navegadores.
    3. Retorna estadísticas precisas antes y después."""
    import psutil
    import ctypes
    
    mem_before = psutil.virtual_memory()
    
    # 1. Optimizar RAM
    trimmed_procs = 0
    try:
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        for p in psutil.process_iter(['pid']):
            try:
                h = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, p.info['pid'])
                if h:
                    psapi.EmptyWorkingSet(h)
                    kernel32.CloseHandle(h)
                    trimmed_procs += 1
            except:
                pass
    except:
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
