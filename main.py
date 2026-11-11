import os
import sys

# Blindaje para PyInstaller modo ventana (--noconsole) donde sys.stdout y sys.stderr son None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List

from app.auditor import get_system_overview, get_top_processes, kill_process_by_pid
from app.cleaner import scan_junk, clean_selected_categories, quick_optimize, get_task_progress
from app.storage import scan_heavy_files, COMMON_PATHS
from app.software import get_installed_programs, get_startup_applications, launch_uninstaller
from app.organizer import scan_target_folder, organize_files
from app.advisor import generate_pc_advice
from app.utils import open_in_explorer, recycle_path, open_windows_app, create_windows_shortcut, restart_as_admin, is_admin

app = FastAPI(
    title="NosClean",
    description="Panel integral para auditar, limpiar y organizar tu PC en Windows.",
    version="5.0.7"
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
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "El dashboard frontend está cargando."}

# ================== ASESOR Y CONSEJOS ==================
@app.get("/api/advisor/recommendations")
def api_advisor_recommendations():
    return generate_pc_advice()

# ================== RUTAS DE SISTEMA ==================
@app.get("/api/system/overview")
def api_system_overview(force: bool = False):
    return get_system_overview(force_refresh=force)

@app.get("/api/system/processes")
def api_system_processes(limit: int = 15):
    return get_top_processes(limit=limit)

class KillProcessRequest(BaseModel):
    pid: int

@app.post("/api/system/kill-process")
def api_system_kill_process(req: KillProcessRequest):
    success, msg = kill_process_by_pid(req.pid)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

# ================== RUTAS DE LIMPIEZA ==================
@app.get("/api/system/progress")
def api_system_progress():
    return get_task_progress()

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
def api_junk_scan(force: bool = False):
    return scan_junk(force_refresh=force)

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

# ================== RUTAS DE SOFTWARE ==================
@app.get("/api/software/installed")
def api_software_installed():
    return get_installed_programs()

class UninstallAppRequest(BaseModel):
    uninstall_command: str = ""
    name: str = ""

@app.post("/api/software/uninstall")
def api_software_uninstall(req: UninstallAppRequest):
    success, msg = launch_uninstaller(req.uninstall_command, req.name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

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

class ShortcutRequest(BaseModel):
    target: str = "desktop"  # "desktop" o "taskbar"

@app.post("/api/actions/create-shortcut")
def api_action_create_shortcut(req: ShortcutRequest):
    success, msg, data = create_windows_shortcut(req.target)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "data": data}

@app.post("/api/actions/restart-admin")
def api_action_restart_admin():
    success, msg, data = restart_as_admin()
    if not success:
        return JSONResponse(status_code=200, content={"success": False, "message": msg, "data": data})
    if data.get("restarting"):
        import threading, time
        def delayed_exit():
            time.sleep(0.25)
            os._exit(0)
        threading.Thread(target=delayed_exit, daemon=True).start()
    return {"success": True, "message": msg, "data": data}

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
    import multiprocessing
    multiprocessing.freeze_support()

    import socket, threading, ctypes, time

    # Registrar AppUserModelID oficial para que Windows agrupe el proceso bajo NosClean y muestre NosClean.ico
    try:
        myappid = 'NosClean.OptimizationSuite.v5.0.7'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    def is_port_in_use(port=8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True

    # Si viene de un reinicio elevado (--elevated-restart), esperar a que la instancia anterior libere el puerto 8000
    if "--elevated-restart" in sys.argv:
        for _ in range(45):
            if not is_port_in_use(8000):
                break
            time.sleep(0.1)

    ico_path = os.path.join(BASE_DIR, "NosClean.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(STATIC_DIR, "favicon.ico")

    # Iniciar servidor backend FastAPI en segundo plano si no está corriendo
    server_running = is_port_in_use(8000)
    if not server_running:
        def run_server():
            try:
                config = uvicorn.Config(
                    app=app,
                    host="127.0.0.1",
                    port=8000,
                    loop="asyncio",
                    http="h11",
                    lifespan="off",
                    log_config=None,  # Evita el fallo de DefaultFormatter en ejecutables sin consola
                    log_level="critical"
                )
                server = uvicorn.Server(config)
                server.run()
            except Exception as e:
                log_path = os.path.join(os.environ.get("TEMP", "."), "nosclean_error.log")
                try:
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"Server error: {e}\n")
                except Exception:
                    pass

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        # Esperar hasta que uvicorn esté listo para responder (aprox 150 ms)
        for _ in range(60):
            time.sleep(0.05)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.05)
                if s.connect_ex(('127.0.0.1', 8000)) == 0:
                    break

    # Lanzar la aplicación en ventana de escritorio nativa WebView2 (icono verde propio, cero Edge)
    try:
        # Evitar degradación de GPU / Sandbox cuando se ejecuta con permisos de Administrador
        os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
            "--disable-features=RendererCodeIntegrity,ElasticOverscroll --disable-gpu-sandbox"
        )
        wv_storage = os.path.join(
            os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")),
            "NosClean",
            "WebView2Cache"
        )
        os.makedirs(wv_storage, exist_ok=True)

        import webview
        window_title = 'NosClean (Administrador)' if is_admin() else 'NosClean'
        window = webview.create_window(
            title=window_title,
            url='http://127.0.0.1:8000',
            width=1280,
            height=820,
            min_size=(960, 640)
        )
        webview.start(
            icon=ico_path if os.path.exists(ico_path) else None,
            private_mode=False,
            storage_path=wv_storage
        )
        os._exit(0)
    except BaseException:
        # Fallback ultra-resiliente: si WebView2 o DLLs fallan en otra PC, abrir en navegador y mantener servidor vivo
        launch_browser()
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            os._exit(0)
