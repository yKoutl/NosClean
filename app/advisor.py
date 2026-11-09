import os
import psutil
from typing import Dict, List, Any
from app.auditor import get_system_overview
from app.cleaner import scan_junk
from app.software import get_installed_programs, get_startup_applications
from app.organizer import scan_target_folder
from app.utils import format_size

# Lista de programas de inicio que típicamente retrasan el arranque y son seguros de desactivar
OPTIONAL_STARTUP_APPS = [
    "discord", "spotify", "steam", "epicgameslauncher", "notion", 
    "rave", "roblox", "telegram", "whatsapp", "skype", "origin", 
    "battle.net", "adobe acrobat synchronizer", "figma agent", "utorrent", "bittorrent"
]

def generate_pc_advice() -> Dict[str, Any]:
    """
    Analiza el estado actual del equipo y genera un diagnóstico inteligente
    con consejos personalizados, puntuación de salud y prioridades de limpieza.
    """
    system = get_system_overview()
    junk = scan_junk()
    startup = get_startup_applications()
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    downloads_info = scan_target_folder(downloads_path)
    
    recommendations = []
    score = 100
    
    # 1. EVALUAR DISCO C:
    c_drive = next((d for d in system.get("drives", []) if d["mountpoint"].upper().startswith("C")), None)
    if c_drive:
        pct = c_drive["percent_used"]
        free_gb = c_drive["free_bytes"] / (1024**3)
        if pct >= 85:
            score -= 25
            recommendations.append({
                "id": "disk_c_critical",
                "priority": "alta",
                "badge": "Crítico",
                "color": "rose",
                "title": f"Disco C: está al {pct}% de capacidad (solo {free_gb:.1f} GB libres)",
                "description": "Windows necesita al menos 15-20% de espacio libre en C: para memoria virtual, actualizaciones y evitar congelamientos.",
                "action_type": "navigate",
                "action_target": "heavy",
                "action_label": "Buscar Archivos Gigantes en C:"
            })
        elif pct >= 65:
            score -= 10
            recommendations.append({
                "id": "disk_c_warning",
                "priority": "media",
                "badge": "Atención",
                "color": "amber",
                "title": f"Disco C: tiene {c_drive['used_formatted']} ocupados ({pct}%)",
                "description": "Aún tienes espacio suficiente, pero es buen momento para hacer limpieza preventiva antes de que se llene más.",
                "action_type": "navigate",
                "action_target": "cleaner",
                "action_label": "Revisar Limpiador de Basura"
            })

    # 2. EVALUAR ARCHIVOS BASURA Y TEMPORALES
    junk_mb = junk["total_bytes"] / (1024**2)
    if junk_mb >= 500:
        score -= 15
        recommendations.append({
            "id": "junk_accumulated",
            "priority": "alta" if junk_mb > 2000 else "media",
            "badge": "Recomendado",
            "color": "rose" if junk_mb > 2000 else "amber",
            "title": f"Tienes {junk['total_formatted']} de archivos temporales y basura",
            "description": f"Se encontraron {junk['total_files']} archivos temporales, cachés de navegadores y descargas viejas que se pueden borrar con total seguridad.",
            "action_type": "navigate",
            "action_target": "cleaner",
            "action_label": "Limpiar Basura Ahora"
        })

    # 3. EVALUAR PROGRAMAS DE INICIO (BOOT TIME)
    heavy_startups = []
    for item in startup:
        name_lower = item["name"].lower()
        if any(opt in name_lower for opt in OPTIONAL_STARTUP_APPS):
            heavy_startups.append(item["name"])

    if len(heavy_startups) >= 3:
        score -= 15
        names_preview = ", ".join(heavy_startups[:4])
        recommendations.append({
            "id": "startup_slowdown",
            "priority": "alta",
            "badge": "Rendimiento",
            "color": "emerald",
            "title": f"Desactiva programas secundarios del inicio de Windows ({len(heavy_startups)} detectados)",
            "description": f"Aplicaciones como {names_preview} inician solas al prender la PC. No necesitas desinstalarlas: solo desactívalas del arranque para que tu PC encienda en segundos.",
            "action_type": "windows_tool",
            "action_target": "startup",
            "action_label": "Abrir Ajustes de Inicio"
        })
    elif len(startup) > 8:
        score -= 8
        recommendations.append({
            "id": "startup_general",
            "priority": "media",
            "badge": "Rendimiento",
            "color": "emerald",
            "title": f"Tienes {len(startup)} programas en arranque automático",
            "description": "Revisa la lista de inicio y deja únicamente tu antivirus y utilidades indispensables.",
            "action_type": "navigate",
            "action_target": "startup",
            "action_label": "Ver Programas de Inicio"
        })

    # 4. EVALUAR CARPETA DESCARGAS
    if downloads_info.get("total_files", 0) > 10:
        score -= 8
        cat_installers = downloads_info.get("category_summary", {}).get("Instaladores", {})
        inst_count = cat_installers.get("count", 0)
        inst_size = cat_installers.get("size_formatted", "0 B")
        
        desc = f"Tienes {downloads_info['total_files']} archivos sueltos en Descargas."
        if inst_count > 0:
            desc += f" Incluye {inst_count} instaladores (.exe/.msi) que ocupan {inst_size} y que normalmente ya no necesitas tras instalar el programa."

        recommendations.append({
            "id": "downloads_clutter",
            "priority": "media",
            "badge": "Organización",
            "color": "amber",
            "title": "Organiza y depura tu carpeta de Descargas",
            "description": desc,
            "action_type": "navigate",
            "action_target": "organizer",
            "action_label": "Organizar Descargas"
        })

    # 5. CONSEJO DE MEMORIA RAM
    ram_pct = system.get("ram", {}).get("percent_used", 0)
    if ram_pct >= 80:
        score -= 10
        recommendations.append({
            "id": "ram_high",
            "priority": "alta",
            "badge": "Memoria",
            "color": "rose",
            "title": f"Uso elevado de Memoria RAM ({ram_pct}%)",
            "description": "Tu PC está usando la mayor parte de sus 16 GB de RAM. Cierra pestañas pesadas del navegador o aplicaciones en segundo plano que no estés utilizando.",
            "action_type": "windows_tool",
            "action_target": "taskmgr",
            "action_label": "Ver en Administrador de Tareas"
        })

    # 6. REGLAS DE ORO: QUÉ NUNCA BORRAR Y QUÉ SÍ BORRAR
    golden_rules = {
        "safe_to_delete": [
            "Archivos de la carpeta %TEMP% y C:\\Windows\\Temp (el sistema recrea lo necesario).",
            "Instaladores (.exe, .msi) guardados en Descargas de programas que ya instalaste.",
            "Caché web de navegadores (Chrome, Edge, Firefox) y de herramientas (pip, npm).",
            "Archivos de la Papelera de Reciclaje.",
            "Reportes de fallos (Crash Dumps) y logs de error antiguos."
        ],
        "safe_to_organize": [
            "Mover fotos, videos, documentos e instaladores a subcarpetas clasificadas.",
            "Desactivar programas del inicio de Windows (no se borran, solo arrancan cuando tú los abres)."
        ],
        "never_delete": [
            "Cualquier archivo dentro de C:\\Windows o C:\\Windows\\System32.",
            "Carpetas de 'Program Files' o 'Archivos de Programa' a mano (usa siempre el desinstalador).",
            "Archivos ocultos con nombres que comiencen con '$' o archivos .sys de sistema.",
            "Carpetas de AppData sin saber a qué aplicación corresponden."
        ]
    }

    # Ajuste de puntuación entre 30 y 100
    score = max(30, min(100, score))

    health_status = "Excelente"
    if score < 60:
        health_status = "Requiere Atención"
    elif score < 80:
        health_status = "Bueno con Oportunidades de Mejora"

    return {
        "health_score": score,
        "health_status": health_status,
        "recommendations": recommendations,
        "golden_rules": golden_rules
    }
