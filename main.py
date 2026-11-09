import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.auditor import get_system_overview, get_top_processes
from app.cleaner import scan_junk, clean_selected_categories, quick_optimize
from app.storage import scan_heavy_files, analyze_folder_breakdown, COMMON_PATHS
from app.software import get_installed_programs, get_startup_applications
from app.organizer import scan_target_folder, organize_files
from app.advisor import generate_pc_advice
from app.utils import open_in_explorer, recycle_path, open_windows_app

app = FastAPI(
    title="NosClean",
    description="Panel integral para auditar, limpiar y organizar tu PC en Windows.",
    version="5.0.3"
)

# Servir archivos estáticos (compatible con empaquetado PyInstaller y ejecución normal)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico")
def get_favicon():
    fav_file = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav_file):
        return FileResponse(fav_file, media_type="image/x-icon")
    return Response(status_code=404)

@app.get("/manifest.json")
def get_manifest():
    manifest_file = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return Response(status_code=404)

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "El dashboard frontend está cargando."}

# ================== ASESOR Y CONSEJOS ==================
@app.get("/api/advisor/recommendations")
def api_advisor_recommendations():
    return generate_pc_advice()

# ================== RUTAS DE SISTEMA ==================
@app.get("/api/system/overview")
def api_system_overview():
    return get_system_overview()

@app.get("/api/system/processes")
def api_system_processes(limit: int = 15):
    return get_top_processes(limit=limit)

# ================== RUTAS DE LIMPIEZA ==================
@app.post("/api/system/optimize")
def api_system_optimize():
    return quick_optimize()

@app.post("/api/system/shutdown")
def api_system_shutdown():
    import threading, time
    def delayed_kill():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=delayed_kill).start()
    return {"success": True, "message": "Servidor cerrado. Consumo actual: 0 MB."}

@app.get("/api/junk/scan")
def api_junk_scan():
    return scan_junk()

class CleanRequest(BaseModel):
    categories: List[str]

@app.post("/api/junk/clean")
def api_junk_clean(req: CleanRequest):
    return clean_selected_categories(req.categories)

# ================== RUTAS DE ALMACENAMIENTO ==================
@app.get("/api/storage/common-paths")
def api_storage_common_paths():
    return COMMON_PATHS

@app.get("/api/storage/heavy-files")
def api_storage_heavy_files(
    path: str = Query(..., description="Ruta a escanear"),
    min_size_mb: int = Query(100, description="Tamaño mínimo en MB"),
    max_results: int = Query(100, description="Máximo número de resultados")
):
    return scan_heavy_files(path, min_size_mb, max_results)

@app.get("/api/storage/folder-breakdown")
def api_storage_folder_breakdown(
    path: str = Query(..., description="Ruta de la carpeta base")
):
    return analyze_folder_breakdown(path)

# ================== RUTAS DE SOFTWARE ==================
@app.get("/api/software/installed")
def api_software_installed():
    return get_installed_programs()

@app.get("/api/software/startup")
def api_software_startup():
    return get_startup_applications()

# ================== RUTAS DE ORGANIZADOR ==================
@app.get("/api/organizer/scan")
def api_organizer_scan(path: str = Query(...)):
    return scan_target_folder(path)

class OrganizeRequest(BaseModel):
    path: str
    simulate: bool = False

@app.post("/api/organizer/organize")
def api_organizer_execute(req: OrganizeRequest):
    return organize_files(req.path, req.simulate)

# ================== ACCIONES DE WINDOWS ==================
class PathActionRequest(BaseModel):
    path: str

@app.post("/api/actions/open-explorer")
def api_action_open_explorer(req: PathActionRequest):
    success, msg = open_in_explorer(req.path)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@app.post("/api/actions/recycle")
def api_action_recycle(req: PathActionRequest):
    success, msg = recycle_path(req.path)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

class ToolActionRequest(BaseModel):
    tool: str

@app.post("/api/actions/open-tool")
def api_action_open_tool(req: ToolActionRequest):
    success, msg = open_windows_app(req.tool)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

def launch_browser():
    import time, subprocess
    time.sleep(0.7)
    url = "http://127.0.0.1:8000"
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in edge_paths:
        if os.path.exists(p):
            subprocess.Popen([p, f"--app={url}", "--window-size=1280,820"])
            return
    for p in chrome_paths:
        if os.path.exists(p):
            subprocess.Popen([p, f"--app={url}", "--window-size=1280,820"])
            return
    import webbrowser
    webbrowser.open(url)

if __name__ == "__main__":
    import socket, threading, ctypes

    # Registrar AppUserModelID para que Windows asigne el icono oficial de NosClean en la barra de tareas
    try:
        myappid = 'NosClean.OptimizationSuite.v5.0.3'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    def is_port_busy(port=8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    if is_port_busy(8000):
        launch_browser()
    else:
        # En modo ejecutable (.exe), arrancar como ventana de escritorio nativa WebView2
        if getattr(sys, 'frozen', False):
            server_thread = threading.Thread(
                target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning"),
                daemon=True
            )
            server_thread.start()

            try:
                import webview
                ico_path = os.path.join(BASE_DIR, "NosClean.ico")
                window = webview.create_window(
                    title='NosClean',
                    url='http://127.0.0.1:8000',
                    width=1280,
                    height=820,
                    min_size=(960, 640)
                )
                webview.start()
                os._exit(0)
            except Exception:
                launch_browser()
                server_thread.join()
        else:
            uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
