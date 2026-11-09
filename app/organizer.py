import os
import shutil
import time
from typing import Dict, List, Any
from app.utils import format_size

CATEGORY_RULES = {
    "Instaladores": [".exe", ".msi", ".iso", ".dmg", ".pkg", ".apk"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Documentos": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".csv", ".rtf"],
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".tiff"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Música y Audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"],
    "Código y Scripts": [".py", ".js", ".ts", ".html", ".css", ".json", ".sql", ".cpp", ".c", ".java", ".sh", ".bat", ".ps1"]
}

def classify_extension(ext: str) -> str:
    """Clasifica una extensión en una categoría semántica."""
    ext = ext.lower()
    for cat_name, extensions in CATEGORY_RULES.items():
        if ext in extensions:
            return cat_name
    return "Otros"

def scan_target_folder(folder_path: str) -> Dict[str, Any]:
    """
    Escanea una carpeta (ej: Descargas o Escritorio) para analizar
    la distribución de archivos sueltos y su antigüedad.
    """
    if not os.path.exists(folder_path):
        return {"error": "La carpeta no existe", "files": [], "summary": {}}

    now = time.time()
    day_seconds = 86400
    
    files_list = []
    category_summary = {}
    for cat in CATEGORY_RULES:
        category_summary[cat] = {"count": 0, "size_bytes": 0, "size_formatted": "0 B"}
    category_summary["Otros"] = {"count": 0, "size_bytes": 0, "size_formatted": "0 B"}

    age_summary = {
        "recent_7d": 0,
        "older_30d": 0,
        "older_90d": 0
    }

    try:
        with os.scandir(folder_path) as it:
            for entry in it:
                # Solo procesar archivos sueltos en la raíz para organizar
                if entry.is_file(follow_symlinks=False):
                    try:
                        stat = entry.stat()
                        size = stat.st_size
                        mtime = stat.st_mtime
                        ext = os.path.splitext(entry.name)[1].lower()
                        category = classify_extension(ext)
                        
                        age_days = int((now - mtime) / day_seconds)
                        if age_days < 7:
                            age_summary["recent_7d"] += 1
                        if age_days >= 30:
                            age_summary["older_30d"] += 1
                        if age_days >= 90:
                            age_summary["older_90d"] += 1

                        category_summary[category]["count"] += 1
                        category_summary[category]["size_bytes"] += size

                        files_list.append({
                            "name": entry.name,
                            "path": entry.path,
                            "extension": ext,
                            "category": category,
                            "size_bytes": size,
                            "size_formatted": format_size(size),
                            "age_days": age_days,
                            "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                        })
                    except (PermissionError, OSError):
                        continue
    except (PermissionError, OSError) as e:
        return {"error": str(e), "files": [], "summary": {}}

    for cat in category_summary:
        category_summary[cat]["size_formatted"] = format_size(category_summary[cat]["size_bytes"])

    total_size = sum(f["size_bytes"] for f in files_list)
    # Ordenar por tamaño
    files_list.sort(key=lambda x: x["size_bytes"], reverse=True)

    return {
        "folder_path": folder_path,
        "total_files": len(files_list),
        "total_size_bytes": total_size,
        "total_size_formatted": format_size(total_size),
        "category_summary": category_summary,
        "age_summary": age_summary,
        "files": files_list
    }

def organize_files(folder_path: str, simulate: bool = False) -> Dict[str, Any]:
    """
    Mueve los archivos sueltos en `folder_path` a subcarpetas ordenadas
    por categoría (ej: 'Descargas/Instaladores', 'Descargas/Documentos').
    """
    scan_res = scan_target_folder(folder_path)
    if "error" in scan_res:
        return scan_res

    moved_files = []
    skipped_files = []

    for file_info in scan_res.get("files", []):
        cat = file_info["category"]
        if cat == "Otros":
            continue

        dest_dir = os.path.join(folder_path, cat)
        dest_path = os.path.join(dest_dir, file_info["name"])

        # Evitar sobreescribir si ya existe un archivo con ese nombre
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(file_info["name"])
            dest_path = os.path.join(dest_dir, f"{base}_{int(time.time())}{ext}")

        if not simulate:
            try:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(file_info["path"], dest_path)
                moved_files.append({
                    "original": file_info["name"],
                    "from": file_info["path"],
                    "to": dest_path,
                    "category": cat
                })
            except Exception as e:
                skipped_files.append({
                    "name": file_info["name"],
                    "error": str(e)
                })
        else:
            moved_files.append({
                "original": file_info["name"],
                "from": file_info["path"],
                "to": dest_path,
                "category": cat
            })

    return {
        "success": True,
        "simulated": simulate,
        "total_moved": len(moved_files),
        "total_skipped": len(skipped_files),
        "moved_items": moved_files,
        "skipped_items": skipped_files
    }

