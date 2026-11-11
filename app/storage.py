import os
import time
from typing import List, Dict, Any, Optional
from app.utils import format_size

user_home = os.path.expanduser("~")

COMMON_PATHS = {
    "downloads": os.path.join(user_home, "Downloads"),
    "desktop": os.path.join(user_home, "Desktop"),
    "documents": os.path.join(user_home, "Documents"),
    "videos": os.path.join(user_home, "Videos"),
    "user_profile": user_home,
    "c_drive": "C:\\",
    "d_drive": "D:\\"
}

def scan_heavy_files(
    target_path: str,
    min_size_mb: int = 100,
    max_results: int = 100,
    excluded_dirs: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Busca archivos pesados (> min_size_mb) de forma optimizada y veloz.
    Omite carpetas de sistema y cachés internas gigantes para responder en pocos segundos.
    """
    if not os.path.exists(target_path):
        return {
            "error": "La ruta especificada no existe en el equipo",
            "files": [],
            "found_count": 0,
            "total_size_bytes": 0,
            "total_size_formatted": "0 B"
        }

    min_size_bytes = min_size_mb * 1024 * 1024
    heavy_files = []
    
    # Exclusiones automáticas para acelerar el escaneo en 10x
    norm_target = os.path.normpath(target_path).lower()
    default_excluded = {
        '$recycle.bin', 'system volume information', 'recovery',
        'windows\\winsxs', 'windows\\servicing', 'node_modules', '.git', '.cache'
    }

    # Si se escanea todo el perfil de usuario (C:\Users\X), excluir AppData para no demorar 40s
    if norm_target == user_home.lower():
        default_excluded.add('appdata')
        default_excluded.add('application data')
        default_excluded.add('local settings')

    # Si se escanea todo el disco C:\, excluir Windows y AppData por velocidad
    if norm_target in ['c:\\', 'c:']:
        default_excluded.add('windows')
        default_excluded.add('appdata')

    if excluded_dirs:
        default_excluded.update([d.lower() for d in excluded_dirs])

    start_time = time.time()
    scanned_count = 0

    try:
        for root, dirs, files in os.walk(target_path, topdown=True, followlinks=False):
            # Filtrar carpetas excluidas de raíz
            dirs[:] = [
                d for d in dirs 
                if d.lower() not in default_excluded 
                and not d.startswith('$')
                and not d.startswith('.')
            ]

            for f in files:
                scanned_count += 1
                try:
                    fpath = os.path.join(root, f)
                    stat = os.stat(fpath)
                    fsize = stat.st_size

                    if fsize >= min_size_bytes:
                        ext = os.path.splitext(f)[1].lower() or "sin extensión"
                        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                        heavy_files.append({
                            "name": f,
                            "path": fpath,
                            "folder": root,
                            "extension": ext,
                            "size_bytes": fsize,
                            "size_formatted": format_size(fsize),
                            "modified": mtime
                        })
                except (PermissionError, FileNotFoundError, OSError):
                    continue

    except (PermissionError, OSError):
        pass

    # Ordenar por tamaño de mayor a menor
    heavy_files.sort(key=lambda x: x["size_bytes"], reverse=True)
    total_found_size = sum(x["size_bytes"] for x in heavy_files)

    return {
        "target_path": target_path,
        "min_size_mb": min_size_mb,
        "scanned_files_count": scanned_count,
        "found_count": len(heavy_files),
        "total_size_bytes": total_found_size,
        "total_size_formatted": format_size(total_found_size),
        "elapsed_seconds": round(time.time() - start_time, 2),
        "files": heavy_files[:max_results]
    }

