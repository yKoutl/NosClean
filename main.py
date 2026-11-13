import os
import sys

# Blindaje para PyInstaller modo ventana (--noconsole) donde sys.stdout y sys.stderr son None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import json
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

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

# ================== CONFIGURACIÓN PERSISTENTE ==================
_main_window = None

DEFAULT_CONFIG = {
    "welcome_dismissed": False,
    "admin_prompt_dismissed": False,
    "mini_mode": False,
    "notify_high_ram": True,
    "high_ram_threshold": 80,
    "notify_optimization": True,
    "always_on_top_mini": True
}

def _get_config_path() -> str:
    folder = os.path.join(os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")), "NosClean")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "nosclean_config.json")

def load_app_config():
    p = _get_config_path()
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg.update(data)
        except Exception:
            pass
    return cfg

def save_app_config(cfg):
    p = _get_config_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

@app.get("/api/system/config")
def api_get_config():
    return load_app_config()

class ConfigUpdateRequest(BaseModel):
    welcome_dismissed: Optional[bool] = None
    admin_prompt_dismissed: Optional[bool] = None
    mini_mode: Optional[bool] = None
    notify_high_ram: Optional[bool] = None
    high_ram_threshold: Optional[int] = None
    notify_optimization: Optional[bool] = None
    always_on_top_mini: Optional[bool] = None

@app.post("/api/system/config")
def api_update_config(req: ConfigUpdateRequest):
    cfg = load_app_config()
    if req.welcome_dismissed is not None:
        cfg["welcome_dismissed"] = req.welcome_dismissed
    if req.admin_prompt_dismissed is not None:
        cfg["admin_prompt_dismissed"] = req.admin_prompt_dismissed
    if req.mini_mode is not None:
        cfg["mini_mode"] = req.mini_mode
    if req.notify_high_ram is not None:
        cfg["notify_high_ram"] = req.notify_high_ram
    if req.high_ram_threshold is not None:
        cfg["high_ram_threshold"] = req.high_ram_threshold
    if req.notify_optimization is not None:
        cfg["notify_optimization"] = req.notify_optimization
    if req.always_on_top_mini is not None:
        cfg["always_on_top_mini"] = req.always_on_top_mini
    save_app_config(cfg)
    return {"success": True, "config": cfg}

def get_nosclean_hwnd():
    """Obtiene el HWND real de la ventana de NosClean con múltiples métodos a prueba de fallos."""
    try:
        import ctypes, os
        from ctypes import wintypes
        u32 = ctypes.windll.user32

        # 1. Directo desde la instancia de BrowserView de pywebview (WinForms)
        try:
            import webview.platforms.winforms as wf
            global _main_window
            if _main_window and hasattr(_main_window, 'uid'):
                form = wf.BrowserView.instances.get(_main_window.uid)
                if form and hasattr(form, 'Handle'):
                    h = int(form.Handle)
                    if h and u32.IsWindow(h):
                        return h
        except Exception:
            pass

        # 2. Enumerar ventanas pertenecientes al PID actual
        current_pid = os.getpid()
        found_hwnds = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def enum_cb(h, _):
            lp_pid = wintypes.DWORD()
            u32.GetWindowThreadProcessId(h, ctypes.byref(lp_pid))
            if lp_pid.value == current_pid and u32.IsWindowVisible(h):
                if u32.GetWindowTextLengthW(h) > 0:
                    found_hwnds.append(h)
            return True
        u32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if found_hwnds:
            return found_hwnds[0]

        # 3. Fallback por títulos conocidos
        for cand in ['NosClean (Administrador)', 'NosClean', 'NosClean ', 'NosClean (Administrador) ']:
            h = u32.FindWindowW(None, cand)
            if h:
                return h
    except Exception:
        pass
    return None

def set_mini_window_style(is_mini: bool):
    """Aplica restricciones Win32 y posiciona con precisión en la esquina inferior derecha sobre la barra de tareas."""
    try:
        import ctypes
        from ctypes import wintypes
        u32 = ctypes.windll.user32
        hwnd = get_nosclean_hwnd()
        if not hwnd:
            return

        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 0x00010000
        WS_THICKFRAME = 0x00040000
        SWP_FRAMECHANGED = 0x0020
        SWP_SHOWWINDOW = 0x0040

        style = u32.GetWindowLongW(hwnd, GWL_STYLE)
        hMenu = u32.GetSystemMenu(hwnd, False)

        rect = wintypes.RECT()
        u32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA (área libre de barra de tareas)

        if is_mini:
            # 1. Quitar botón de maximizar y borde manual
            style = style & ~WS_MAXIMIZEBOX & ~WS_THICKFRAME
            u32.SetWindowLongW(hwnd, GWL_STYLE, style)

            # 2. Bloquear arrastre de título (SC_MOVE) para que quede fija
            if hMenu:
                u32.DeleteMenu(hMenu, 0xF010, 0x0000)  # SC_MOVE
                u32.DeleteMenu(hMenu, 0xF030, 0x0000)  # SC_MAXIMIZE
                u32.DeleteMenu(hMenu, 0xF000, 0x0000)  # SC_SIZE
                u32.DrawMenuBar(hwnd)

            # 3. Detectar escala DPI real de Windows para evitar ventanas enanas en pantallas 1080p/4K
            scale = 1.0
            try:
                if hasattr(u32, "GetDpiForWindow"):
                    dpi = u32.GetDpiForWindow(hwnd)
                    if dpi and dpi > 0:
                        scale = dpi / 96.0
                elif hasattr(u32, "GetDpiForSystem"):
                    dpi = u32.GetDpiForSystem()
                    if dpi and dpi > 0:
                        scale = dpi / 96.0
            except Exception:
                scale = 1.0
            scale = max(1.0, scale)

            # Dimensiones holgadas para el widget: 500x300 lógicos escalados
            mini_w = int(500 * scale)
            mini_h = int(300 * scale)
            margin = int(24 * scale)

            pos_x = max(0, rect.right - mini_w - margin)
            pos_y = max(0, rect.bottom - mini_h - margin)

            u32.SetWindowPos(hwnd, 0, pos_x, pos_y, mini_w, mini_h, SWP_FRAMECHANGED | SWP_SHOWWINDOW)
            u32.ShowWindow(hwnd, 5)  # SW_SHOW (Visibilidad garantizada)
        else:
            # Restaurar maximizar, redimensionar y mover
            style = style | WS_MAXIMIZEBOX | WS_THICKFRAME
            u32.SetWindowLongW(hwnd, GWL_STYLE, style)

            u32.GetSystemMenu(hwnd, True)
            u32.DrawMenuBar(hwnd)

            # Restaurar a Pantalla Completa / Maximizado
            u32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    except Exception:
        pass

class WindowModeRequest(BaseModel):
    mode: str  # "mini" or "normal"
    always_on_top: Optional[bool] = None

@app.post("/api/system/window-mode")
def api_set_window_mode(req: WindowModeRequest):
    global _main_window
    cfg = load_app_config()
    target_mode = req.mode.lower()
    is_mini = (target_mode == "mini")
    always_on_top = req.always_on_top if req.always_on_top is not None else cfg.get("always_on_top_mini", True)

    if _main_window:
        try:
            if is_mini:
                _main_window.restore()  # Des-maximiza de forma limpia antes de encoger
                _main_window.on_top = bool(always_on_top)
                set_mini_window_style(True)
            else:
                set_mini_window_style(False)
                _main_window.on_top = False
                _main_window.maximize()
        except Exception:
            pass

    cfg["mini_mode"] = is_mini
    if req.always_on_top is not None:
        cfg["always_on_top_mini"] = bool(req.always_on_top)
    save_app_config(cfg)
    return {"success": True, "mode": target_mode, "config": cfg}

    cfg["mini_mode"] = is_mini
    if req.always_on_top is not None:
        cfg["always_on_top_mini"] = bool(req.always_on_top)
    save_app_config(cfg)
    return {"success": True, "mode": target_mode, "config": cfg}

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

def launch_browser(port: int = 8000):
    import time, subprocess
    time.sleep(0.7)
    url = f"http://127.0.0.1:{port}"
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

    def get_available_port():
        for candidate in [8000, 8008, 8088, 8888, 0]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', candidate))
                    return s.getsockname()[1]
                except OSError:
                    continue
        return 8000

    # Limpieza automática de instancias previas huérfanas para evitar puertos y cachés bloqueadas
    current_pid = os.getpid()
    if "--elevated-restart" not in sys.argv:
        try:
            import psutil
            for p in psutil.process_iter(['pid', 'name']):
                if p.info['pid'] != current_pid and 'nosclean' in (p.info['name'] or '').lower():
                    try:
                        p.kill()
                    except Exception:
                        pass
        except Exception:
            pass

    app_port = get_available_port()

    ico_path = os.path.join(BASE_DIR, "NosClean.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(STATIC_DIR, "favicon.ico")

    # Iniciar servidor backend FastAPI en segundo plano en el puerto disponible
    def run_server():
        try:
            config = uvicorn.Config(
                app=app,
                host="127.0.0.1",
                port=app_port,
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
            if s.connect_ex(('127.0.0.1', app_port)) == 0:
                break

    # Lanzar la aplicación en ventana de escritorio nativa WebView2 (icono verde propio, cero Edge)
    try:
        cache_name = "WebView2Cache_Admin" if is_admin() else "WebView2Cache"
        wv_storage = os.path.join(
            os.environ.get("LOCALAPPDATA", os.environ.get("TEMP", ".")),
            "NosClean",
            cache_name
        )
        os.makedirs(wv_storage, exist_ok=True)

        import webview
        from ctypes import wintypes
        u32 = ctypes.windll.user32

        cfg = load_app_config()
        start_in_mini = bool(cfg.get("mini_mode", False))

        scale = 1.0
        try:
            dpi = u32.GetDpiForSystem()
            if dpi and dpi > 0:
                scale = dpi / 96.0
        except Exception:
            scale = 1.0
        scale = max(1.0, scale)

        rect = wintypes.RECT()
        u32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)

        mini_w = int(500 * scale)
        mini_h = int(300 * scale)
        margin = int(24 * scale)
        mini_x = max(0, rect.right - mini_w - margin)
        mini_y = max(0, rect.bottom - mini_h - margin)

        init_w = mini_w if start_in_mini else 1280
        init_h = mini_h if start_in_mini else 820
        init_x = mini_x if start_in_mini else None
        init_y = mini_y if start_in_mini else None
        init_maximized = not start_in_mini
        init_on_top = bool(cfg.get("always_on_top_mini", True)) if start_in_mini else False

        window_title = 'NosClean (Administrador)' if is_admin() else 'NosClean'
        _main_window = webview.create_window(
            title=window_title,
            url=f'http://127.0.0.1:{app_port}',
            x=init_x,
            y=init_y,
            width=init_w,
            height=init_h,
            min_size=(320, 140),
            maximized=init_maximized,
            on_top=init_on_top
        )

        def on_gui_ready():
            if start_in_mini:
                time.sleep(0.18)
                set_mini_window_style(True)

        webview.start(
            on_gui_ready,
            icon=ico_path if os.path.exists(ico_path) else None,
            private_mode=False,
            storage_path=wv_storage
        )
        os._exit(0)
    except BaseException as e:
        import traceback
        log_path = os.path.join(os.environ.get("TEMP", "."), "nosclean_error.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"Webview Error: {e}\n{traceback.format_exc()}\n")
        except Exception:
            pass
        # Fallback ultra-resiliente: si WebView2 o DLLs fallan en otra PC, abrir en navegador y mantener servidor vivo
        launch_browser(app_port)
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            os._exit(0)
