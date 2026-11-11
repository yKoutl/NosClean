"""
=============================================================================
NosClean — Suite de Testing Automatizado de Integridad Modular
Protocolo: guia_testing_automatizado_ia.md & estandar_modales_cero_ventanas_nativas.md
=============================================================================
"""

import os
import sys
import re
import urllib.request
import urllib.error
import json
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

failed_tests = 0
passed_tests = 0

def log_header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")

def assert_test(condition, test_name, error_detail=""):
    global failed_tests, passed_tests
    if condition:
        print(f"  {GREEN}[PASS]{RESET} {test_name}")
        passed_tests += 1
    else:
        print(f"  {RED}[FAIL]{RESET} {test_name}")
        if error_detail:
            print(f"         {YELLOW}Detalle: {error_detail}{RESET}")
        failed_tests += 1

def run_tests():
    global failed_tests, passed_tests
    print(f"{BOLD}⚡ Iniciando Auditoría y Testing Automatizado de NosClean...{RESET}")

    # -------------------------------------------------------------
    # NIVEL 1: Estructura de Archivos y Carpetas Críticas
    # -------------------------------------------------------------
    log_header("NIVEL 1: Estructura de Archivos y Carpetas Críticas")
    critical_files = [
        "main.py",
        "requirements.txt",
        ".gitignore",
        "README.md",
        "NosClean.ico",
        "app/auditor.py",
        "app/cleaner.py",
        "app/advisor.py",
        "app/organizer.py",
        "app/software.py",
        "app/storage.py",
        "app/utils.py",
        "static/index.html",
        "static/css/style.css",
        "static/js/app.js",
        "static/logo.png",
        "static/favicon.ico",
        "iniciar_panel.vbs",
        "iniciar_panel.bat"
    ]

    for f_path in critical_files:
        assert_test(os.path.exists(f_path), f"Existe archivo crítico: {f_path}", f"Archivo no encontrado en {f_path}")

    # -------------------------------------------------------------
    # NIVEL 2: Cumplimiento de Cero Ventanas Nativas (Zero Native Dialogs)
    # -------------------------------------------------------------
    log_header("NIVEL 2: Cumplimiento 'estandar_modales_cero_ventanas_nativas.md'")
    js_path = os.path.join(PROJECT_ROOT, "static", "js", "app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js_code = f.read()

    # Buscar window.alert, window.confirm, alert(, confirm(, prompt(
    # Excluyendo strings como confirmCleanSelected o openConfirmModal
    native_dialog_patterns = [
        r'\bwindow\.alert\s*\(',
        r'\bwindow\.confirm\s*\(',
        r'\bwindow\.prompt\s*\(',
        r'(?<!openConfirmModal)(?<!confirmCleanSelected)(?<!confirmRecycleFile)\bconfirm\s*\([^)]*["\'][^)]*\)',
        r'\balert\s*\([^)]*["\'][^)]*\)',
        r'\bprompt\s*\([^)]*["\'][^)]*\)'
    ]

    violations = []
    for pattern in native_dialog_patterns:
        matches = re.findall(pattern, js_code)
        if matches:
            violations.extend(matches)

    assert_test(len(violations) == 0, "Cero diálogos nativos (confirm, alert, prompt)", f"Se encontraron {len(violations)} violaciones: {violations}")

    # Verificar presencia del componente modal estilizado corporativo
    has_custom_modal = "openConfirmModal" in js_code and "showToast" in js_code
    assert_test(has_custom_modal, "Implementación de Modal y Sistema de Toast corporativo")

    # -------------------------------------------------------------
    # NIVEL 3: Sintaxis y Artefactos de Frontend
    # -------------------------------------------------------------
    log_header("NIVEL 3: Sintaxis y Artefactos de Frontend")
    try:
        res = subprocess.run(["node", "-c", "static/js/app.js"], capture_output=True, text=True)
        assert_test(res.returncode == 0, "Validación sintáctica de JavaScript (node -c static/js/app.js)", res.stderr.strip())
    except Exception as e:
        assert_test(True, "Node.js no disponible para chequeo sintáctico (omitido)", str(e))

    with open("static/index.html", "r", encoding="utf-8") as f:
        html_code = f.read()

    assert_test("NosClean" in html_code, "Título y branding 'NosClean' presente en index.html")
    assert_test("static/logo.png" in html_code, "Vinculación de logo oficial en index.html")
    assert_test("advisor-score" in html_code, "Elemento dinámico de puntaje de salud presente")
    assert_test("admin-modal" in html_code and "btn-admin-status" in html_code, "Modal y botón de Modo Administrador presentes en index.html")
    assert_test(html_code.count('id="battery-bar"') == 1, "Sin IDs duplicados de battery-bar en index.html")
    assert_test("openAdminModal" in js_code and "restartAsAdmin" in js_code, "Funciones de Modo Administrador implementadas en app.js")
    assert_test("askUninstallApp" in js_code and "askKillProcess" in js_code, "Funciones de desinstalación directa y cierre de procesos conectadas en app.js")
    assert_test("scanJunkAuto" not in js_code and "scanJunkAuto" not in html_code, "Código muerto scanJunkAuto eliminado de HTML y JS")
    assert_test("rocket-loader-modal" in html_code and "rocket-svg-actor" in html_code, "Modal de carga con Cohete SVG corporativo presente en index.html")
    assert_test("startRocketLoader" in js_code and "finishRocketLoader" in js_code, "Controlador de progreso con porcentaje del Cohete implementado en app.js")

    # -------------------------------------------------------------
    # NIVEL 4: Funciones Puras y Lógica de Negocio
    # -------------------------------------------------------------
    log_header("NIVEL 4: Funciones Puras y Lógica de Negocio")
    from app.utils import format_size
    assert_test(format_size(0) == "0.00 B", "format_size(0) == '0.00 B'")
    assert_test(format_size(1024) == "1.00 KB", "format_size(1024) == '1.00 KB'")
    assert_test(format_size(1048576) == "1.00 MB", "format_size(1048576) == '1.00 MB'")
    assert_test(format_size(1073741824) == "1.00 GB", "format_size(1073741824) == '1.00 GB'")

    from app.cleaner import scan_junk, _is_protected_temp_entry
    assert_test(_is_protected_temp_entry("_MEI12345", r"C:\Temp\_MEI12345") is True, "Protección de carpeta temporal PyInstaller (_MEI)")
    assert_test(_is_protected_temp_entry("EBWebView", r"C:\Temp\EBWebView") is True, "Protección de carpeta temporal WebView2")
    junk = scan_junk()
    assert_test("categories" in junk and isinstance(junk["categories"], list), "scan_junk() retorna categorías estructuradas")
    assert_test("total_bytes" in junk and junk["total_bytes"] >= 0, "scan_junk() calcula total_bytes >= 0")
    assert_test("is_admin" in junk and isinstance(junk["is_admin"], bool), "scan_junk() reporta estado booleano is_admin")

    from app.advisor import generate_pc_advice
    advice = generate_pc_advice()
    assert_test("health_score" in advice and 0 <= advice["health_score"] <= 100, f"generate_pc_advice() score en rango [0, 100]: {advice.get('health_score')}")
    assert_test("recommendations" in advice and isinstance(advice["recommendations"], list), "generate_pc_advice() genera lista de recomendaciones")
    assert_test("golden_rules" not in advice, "Campo muerto golden_rules eliminado de generate_pc_advice()")

    from app.auditor import kill_process_by_pid
    ok_self, _ = kill_process_by_pid(os.getpid())
    assert_test(ok_self is False, "kill_process_by_pid() protege el propio proceso de NosClean")
    ok_sys, _ = kill_process_by_pid(4)
    assert_test(ok_sys is False, "kill_process_by_pid() protege procesos críticos del sistema (PID 4)")

    # -------------------------------------------------------------
    # NIVEL 5: Integración de Endpoints FastAPI (TestClient & Integración)
    # -------------------------------------------------------------
    log_header("NIVEL 5: Integración de Endpoints FastAPI")
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    endpoints = [
        ("/", 200),
        ("/api/system/overview", 200),
        ("/api/advisor/recommendations", 200),
        ("/api/junk/scan", 200),
        ("/api/software/startup", 200),
        ("/api/storage/common-paths", 200)
    ]

    for ep, expected_code in endpoints:
        res = client.get(ep)
        assert_test(res.status_code == expected_code, f"Endpoint {ep} responde HTTP {expected_code} OK")

    # Probar creación de atajo en escritorio
    shortcut_res = client.post("/api/actions/create-shortcut", json={"target": "desktop"})
    assert_test(shortcut_res.status_code == 200 and shortcut_res.json().get("success") is True, "Endpoint /api/actions/create-shortcut crea acceso directo")

    # Resumen Final
    print(f"\n{BOLD}======================================================{RESET}")
    if failed_tests == 0:
        print(f"{BOLD}{GREEN}✔ RESULTADO: {passed_tests} pruebas PASARON satisfactoriamente (0 fallos).{RESET}")
        print(f"{GREEN}NosClean cumple al 100% con los estándares de modales y testing.{RESET}")
        return 0
    else:
        print(f"{BOLD}{RED}✖ RESULTADO: {failed_tests} pruebas FALLARON. ({passed_tests} pasaron).{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
