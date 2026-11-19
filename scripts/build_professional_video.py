import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import win32com.client
import wave
import contextlib
import subprocess

WIDTH = 1920
HEIGHT = 1080
FPS = 30
TEMP_VIDEO = "scripts/temp_video_silent.mp4"
TEMP_AUDIO = "scripts/temp_audio.wav"
FINAL_VIDEO = "NosClean_Promo_LinkedIn.mp4"
FFMPEG = os.path.abspath("scripts/bin/ffmpeg.exe")

# Paleta corporativa NosClean
BG_DARK = (16, 45, 37)        # #102D25
BG_DEEP = (10, 26, 21)        # #0A1A15
PRIMARY = (8, 122, 69)        # #087A45
PRIMARY_LIGHT = (16, 185, 129)# #10B981
ACCENT = (22, 184, 78)        # #16B84E
WHITE = (255, 255, 255)
SLATE_LIGHT = (226, 232, 240)
SLATE_MUTED = (148, 163, 184)
CARD_BG = (22, 54, 45)
CARD_BORDER = (40, 95, 78)

# Fuentes Segoe UI
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"

def get_font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except Exception:
        return ImageFont.load_default()

F_HERO = get_font(68, bold=True)
F_TITLE = get_font(46, bold=True)
F_SUBTITLE = get_font(30, bold=True)
F_BODY = get_font(23, bold=False)
F_BODY_BOLD = get_font(23, bold=True)
F_BADGE = get_font(20, bold=True)
F_SUBTITLE_TXT = get_font(24, bold=False)

# Cargar recursos
LOGO_PATH = "static/logo.png"
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = "assets/branding/NosClean_icon_large.png"
logo_img = Image.open(LOGO_PATH).convert("RGBA") if os.path.exists(LOGO_PATH) else None

ROCKET_PATH = "scripts/rocket_card_clean.png"
rocket_img = Image.open(ROCKET_PATH).convert("RGBA") if os.path.exists(ROCKET_PATH) else None

WIDGET_PATH = "scripts/widget_card_clean.png"
widget_img = Image.open(WIDGET_PATH).convert("RGBA") if os.path.exists(WIDGET_PATH) else None

def create_base_canvas():
    base = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_DEEP[0] * (1 - ratio) + BG_DARK[0] * ratio)
        g = int(BG_DEEP[1] * (1 - ratio) + BG_DARK[1] * ratio)
        b = int(BG_DEEP[2] * (1 - ratio) + BG_DARK[2] * ratio)
        base[y, :] = (r, g, b)
    return Image.fromarray(base)

BASE_BG = create_base_canvas()

def draw_card(draw, x, y, w, h, bg_col=CARD_BG, border_col=CARD_BORDER, radius=18):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_col, outline=border_col, width=2)

def draw_badge(draw, text, x, y, bg_col=PRIMARY, text_col=WHITE, font=F_BADGE, padding=(18, 6)):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + padding[0] * 2
    h = bbox[3] - bbox[1] + padding[1] * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=bg_col)
    draw.text((x + padding[0], y + padding[1]), text, fill=text_col, font=font)
    return w, h

def draw_subtitles(draw, text):
    """Subtítulos nítidos en la parte inferior para consumo con o sin volumen."""
    if not text:
        return
    padding_x = 36
    padding_y = 12
    bbox = F_SUBTITLE_TXT.getbbox(text)
    txt_w = bbox[2] - bbox[0]
    txt_h = bbox[3] - bbox[1]
    box_w = min(1700, txt_w + padding_x * 2)
    box_h = txt_h + padding_y * 2
    box_x = (WIDTH - box_w) // 2
    box_y = HEIGHT - 85
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=14, fill=(10, 20, 16, 230), outline=(35, 75, 60), width=1)
    draw.text((WIDTH // 2, box_y + padding_y + txt_h // 2), text, fill=WHITE, font=F_SUBTITLE_TXT, anchor="mm")

def draw_check_icon(draw, cx, cy, radius=12, color=ACCENT):
    """Dibuja un icono vectorial de verificación nativo sin depender de fuentes."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(20, 60, 48), outline=color, width=2)
    points = [
        (cx - 5, cy),
        (cx - 1, cy + 4),
        (cx + 5, cy - 3)
    ]
    draw.line(points, fill=color, width=3)

# ==================== ESCENAS ====================

def render_scene_1(t, dur):
    """Escena 1: Presentación institucional NosClean v5.0.7"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "NosClean versión 5.0.7. Auditoría inteligente, optimización y limpieza para Windows."

    # Logo suave zoom
    if logo_img:
        lw = int(190)
        lh = int(190)
        l_scaled = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (WIDTH - lw) // 2
        ly = 200
        img.paste(l_scaled, (lx, ly), l_scaled)

    draw.text((WIDTH // 2, 435), "NOSCLEAN", fill=ACCENT, font=F_HERO, anchor="mm")
    draw_badge(draw, "VERSIÓN 5.0.7 • 100% CÓDIGO ABIERTO", (WIDTH // 2) - 180, 490, bg_col=PRIMARY, font=F_BADGE)

    draw.text((WIDTH // 2, 590), "Auditoría integral, optimización y mantenimiento para Windows", fill=WHITE, font=F_SUBTITLE, anchor="mm")
    draw.text((WIDTH // 2, 650), "100% Nativo en Python • Sin telemetría oculta • Cero publicidad", fill=SLATE_MUTED, font=F_BODY, anchor="mm")

    # Stack pills
    pills = ["Python 3.10", "FastAPI", "WebView2", "TailwindCSS", "PyInstaller Standalone"]
    total_w = sum(F_BADGE.getbbox(p)[2] + 40 for p in pills)
    bx = (WIDTH - total_w) // 2
    for p in pills:
        bw, _ = draw_badge(draw, p, bx, 730, bg_col=CARD_BG, text_col=PRIMARY_LIGHT, font=F_BADGE, padding=(18, 6))
        bx += bw + 15

    draw_subtitles(draw, sub_text)
    return img

def render_scene_2(t, dur):
    """Escena 2: El problema común con optimizadores en Windows"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "¿Cansado de optimizadores lentos, llenos de publicidad y con métricas engañosas?"

    draw_badge(draw, "EL PROBLEMA ACTUAL", 140, 70, bg_col=(180, 50, 50), text_col=WHITE)
    draw.text((140, 145), "¿Por qué la mayoría de limpiadores de PC decepcionan?", fill=WHITE, font=F_TITLE)

    pains = [
        ("Publicidad y Bloatware invasivo",
         "Instalan barras de búsqueda secundarias, navegadores no deseados y alertas falsas de virus."),
        ("Métricas infladas y engañosas",
         "Prometen borrar gigabytes que en realidad están bloqueados por el propio sistema operativo."),
        ("Procesos pesados que ralentizan tu equipo",
         "Servicios residentes en segundo plano que consumen memoria y ciclos continuos de procesador.")
    ]

    card_y = 240
    for idx, (title, desc) in enumerate(pains):
        draw_card(draw, 140, card_y, 1640, 160, bg_col=(32, 24, 24), border_col=(110, 50, 50))
        # Icono X rojo
        cx, cy = 195, card_y + 55
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(80, 25, 25), outline=(230, 80, 80), width=2)
        draw.line([(cx - 6, cy - 6), (cx + 6, cy + 6)], fill=(255, 120, 120), width=3)
        draw.line([(cx - 6, cy + 6), (cx + 6, cy - 6)], fill=(255, 120, 120), width=3)

        draw.text((235, card_y + 38), title, fill=(255, 130, 130), font=F_SUBTITLE)
        draw.text((235, card_y + 90), desc, fill=SLATE_LIGHT, font=F_BODY)
        card_y += 195

    draw_subtitles(draw, sub_text)
    return img

def render_scene_3(t, dur):
    """Escena 3: Diagnóstico en tiempo real - Dashboard 1080p Nativo"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "Obtén un diagnóstico transparente con métricas de procesador, RAM y discos en tiempo real."

    draw_badge(draw, "AUDITORÍA TRANSPARENTE", 140, 60, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 130), "Diagnóstico de hardware en tiempo real sin telemetría", fill=WHITE, font=F_TITLE)
    draw.text((140, 190), "Lectura directa de sensores de Windows: CPU, Memoria, GPU y Discos", fill=SLATE_MUTED, font=F_BODY)

    # Grid de 4 tarjetas de monitoreo en ultra alta definición (1080p nativo)
    # Card 1: CPU (140, 250, 790, 280)
    draw_card(draw, 140, 245, 790, 290, bg_col=CARD_BG, border_col=PRIMARY)
    draw.text((180, 280), "PROCESADOR (CPU)", fill=SLATE_MUTED, font=F_BADGE)
    draw.text((180, 315), "AMD Ryzen 5 4600H", fill=WHITE, font=F_SUBTITLE)
    draw.text((180, 365), "6 Núcleos Físicos • 12 Hilos lógicos • 3.00 GHz", fill=SLATE_LIGHT, font=F_BODY)
    # Barra de uso CPU animada
    cpu_pct = int(35 + 8 * np.sin(t * 2))
    draw.text((790, 280), f"{cpu_pct}%", fill=ACCENT, font=F_TITLE, anchor="rt")
    draw.rounded_rectangle([180, 420, 880, 440], radius=10, fill=(15, 35, 30))
    bar_w = int(700 * (cpu_pct / 100))
    draw.rounded_rectangle([180, 420, 180 + bar_w, 440], radius=10, fill=ACCENT)
    draw.text((180, 460), "Carga de trabajo en tiempo real vía psutil", fill=SLATE_MUTED, font=get_font(18))

    # Card 2: Memoria RAM (980, 245, 800, 290)
    draw_card(draw, 980, 245, 800, 290, bg_col=CARD_BG, border_col=PRIMARY)
    draw.text((1020, 280), "MEMORIA RAM", fill=SLATE_MUTED, font=F_BADGE)
    draw.text((1020, 315), "15.42 GB DDR4", fill=WHITE, font=F_SUBTITLE)
    draw.text((1020, 365), "9.39 GB en uso • 6.03 GB disponible para aplicaciones", fill=SLATE_LIGHT, font=F_BODY)
    draw.text((1640, 280), "60.9%", fill=PRIMARY_LIGHT, font=F_TITLE, anchor="rt")
    draw.rounded_rectangle([1020, 420, 1720, 440], radius=10, fill=(15, 35, 30))
    draw.rounded_rectangle([1020, 420, 1020 + int(700 * 0.609), 440], radius=10, fill=PRIMARY_LIGHT)
    draw.text((1020, 460), "Optimizador de Working Set con 1 solo clic", fill=SLATE_MUTED, font=get_font(18))

    # Card 3: Almacenamiento (140, 565, 790, 280)
    draw_card(draw, 140, 565, 790, 280, bg_col=CARD_BG, border_col=CARD_BORDER)
    draw.text((180, 600), "UNIDAD DE SISTEMA (C:)", fill=SLATE_MUTED, font=F_BADGE)
    draw.text((180, 635), "SSD NVMe M.2 (237.8 GB)", fill=WHITE, font=F_SUBTITLE)
    draw.text((180, 685), "189.5 GB Usado • 48.3 GB Libres", fill=SLATE_LIGHT, font=F_BODY)
    draw.rounded_rectangle([180, 735, 880, 755], radius=10, fill=(15, 35, 30))
    draw.rounded_rectangle([180, 735, 180 + int(700 * 0.79), 755], radius=10, fill=(234, 179, 8))
    draw.text((180, 775), "Detección automática de temporales y archivos pesados", fill=SLATE_MUTED, font=get_font(18))

    # Card 4: Seguridad y Privacidad (980, 565, 800, 280)
    draw_card(draw, 980, 565, 800, 280, bg_col=CARD_BG, border_col=CARD_BORDER)
    draw.text((1020, 600), "ESTADO DEL SISTEMA", fill=SLATE_MUTED, font=F_BADGE)
    draw.text((1020, 635), "NosClean en Modo Administrador Activo", fill=WHITE, font=F_SUBTITLE)
    draw.text((1020, 685), "Permisos UAC verificados • Sin telemetría • Modo Standalone", fill=SLATE_LIGHT, font=F_BODY)
    draw.rounded_rectangle([1020, 735, 1720, 755], radius=10, fill=(15, 35, 30))
    draw.rounded_rectangle([1020, 735, 1720, 755], radius=10, fill=ACCENT)
    draw.text((1020, 775), "Acceso directo a herramientas nativas de Windows", fill=SLATE_MUTED, font=get_font(18))

    draw_subtitles(draw, sub_text)
    return img

def render_scene_4(t, dur):
    """Escena 4: Optimización en 1 Clic con Cohete Centrado y Limpio"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "Con un solo clic, libera bloques de memoria inactiva y depura archivos temporales."

    draw_badge(draw, "OPTIMIZACIÓN INSTANTÁNEA", 140, 60, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 130), "Liberación de memoria RAM y caché en 1 solo clic", fill=WHITE, font=F_TITLE)
    draw.text((140, 190), "API de Windows EmptyWorkingSet y limpieza segura de archivos temporales", fill=SLATE_MUTED, font=F_BODY)

    # Panel izquierdo (beneficios)
    draw_card(draw, 140, 245, 840, 595)
    bullets = [
        ("Vaciado de memoria RAM inactiva",
         "Limpia el Working Set de programas en segundo plano sin cerrar ninguna aplicación activa."),
        ("Depuración segura de temporales",
         "Elimina cachés de Chrome, Edge y %TEMP% protegiendo archivos en uso por el sistema."),
        ("Cero congelamientos de pantalla",
         "Animación fluida con Cohete SVG y porcentaje real sincronizado."),
        ("Transparencia absoluta garantizada",
         "Reporte exacto de los megabytes liberados sin números inflados ni datos ficticios.")
    ]

    by = 285
    for title, desc in bullets:
        draw_check_icon(draw, 185, by + 12, radius=14, color=ACCENT)
        draw.text((220, by), title, fill=WHITE, font=F_SUBTITLE)
        draw.text((220, by + 45), desc, fill=SLATE_LIGHT, font=F_BODY)
        by += 135

    # Panel derecho con la tarjeta real y limpia del cohete
    if rocket_img:
        # Dibujar marco contenedor elegante centrado en la mitad derecha
        card_w, card_h = 600, 595
        card_x = 1070
        card_y = 245
        draw_card(draw, card_x, card_y, card_w, card_h, bg_col=(18, 48, 40), border_col=ACCENT, radius=22)

        # Redimensionar la tarjeta limpia del cohete proporcionalmente
        r_scale = min(540 / rocket_img.width, 530 / rocket_img.height)
        new_w = int(rocket_img.width * r_scale)
        new_h = int(rocket_img.height * r_scale)
        r_res = rocket_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        rx = card_x + (card_w - new_w) // 2
        ry = card_y + (card_h - new_h) // 2
        img.paste(r_res, (rx, ry), r_res)

    draw_subtitles(draw, sub_text)
    return img

def render_scene_5(t, dur):
    """Escena 5: Modo Widget Flotante y Modo Centinela en Segundo Plano"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "Pasa al Modo Widget flotante o déjalo en segundo plano con cero consumo de procesador."

    draw_badge(draw, "MODO WIDGET Y CENTINELA", 140, 60, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 130), "Vigilancia silenciosa con cero impacto en el rendimiento", fill=WHITE, font=F_TITLE)
    draw.text((140, 190), "Control total desde la esquina de tu pantalla o de forma 100% invisible", fill=SLATE_MUTED, font=F_BODY)

    # Panel izquierdo con el widget limpio y centrado
    card_w, card_h = 750, 595
    card_x = 140
    card_y = 245
    draw_card(draw, card_x, card_y, card_w, card_h, bg_col=(18, 48, 40), border_col=PRIMARY, radius=22)

    if widget_img:
        # Escalar widget para que se vea nítido y prominente
        w_scale = 1.35
        ww = int(widget_img.width * w_scale)
        wh = int(widget_img.height * w_scale)
        w_res = widget_img.resize((ww, wh), Image.Resampling.LANCZOS)
        wx = card_x + (card_w - ww) // 2
        wy = card_y + (card_h - wh) // 2 - 25

        # Sombra sutil debajo del widget
        draw.rounded_rectangle([wx - 6, wy - 6, wx + ww + 6, wy + wh + 6], radius=16, fill=(5, 15, 12))
        img.paste(w_res, (wx, wy), w_res)

        draw.text((card_x + card_w // 2, wy + wh + 35), "Modo Widget Flotante Siempre Visible", fill=ACCENT, font=F_BODY_BOLD, anchor="mm")

    # Panel derecho con explicaciones técnicas
    draw_card(draw, 960, 245, 820, 595)
    draw.text((1010, 290), "Vigilancia Inteligente 'De la Nada'", fill=ACCENT, font=F_SUBTITLE)

    widget_bullets = [
        ("Cierre inteligente a segundo plano",
         "Al pulsar la 'X', la ventana desaparece por completo sin dejar iconos molestos en la barra de tareas."),
        ("0% de CPU en estado de reposo",
         "El hilo centinela duerme pacíficamente y no afecta los FPS en tus juegos ni el trabajo intensivo."),
        ("Notificaciones nativas oficiales",
         "Si la memoria RAM supera el 80%, Windows te avisa automáticamente con una alerta oficial de escritorio."),
        ("Reactivación instantánea en 1 clic",
         "Vuelve a hacer doble clic en el acceso directo de NosClean y tu ventana reaparece de inmediato.")
    ]

    by = 355
    for title, desc in widget_bullets:
        draw_check_icon(draw, 1025, by + 12, radius=12, color=PRIMARY_LIGHT)
        draw.text((1055, by), title, fill=WHITE, font=F_BODY_BOLD)
        draw.text((1055, by + 36), desc, fill=SLATE_LIGHT, font=F_BODY)
        by += 115

    draw_subtitles(draw, sub_text)
    return img

def render_scene_6(t, dur):
    """Escena 6: Stack Tecnológico y Descarga Oficial"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    sub_text = "NosClean es gratuito y de código abierto. Descarga el ejecutable oficial en GitHub."

    if logo_img:
        lw = int(170)
        lh = int(170)
        l_scaled = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        img.paste(l_scaled, ((WIDTH - lw) // 2, 110), l_scaled)

    draw.text((WIDTH // 2, 320), "NOSCLEAN v5.0.7", fill=ACCENT, font=F_HERO, anchor="mm")
    draw.text((WIDTH // 2, 385), "100% Gratuito y de Código Abierto para Windows", fill=WHITE, font=F_SUBTITLE, anchor="mm")

    # Badges tecnológicos
    badges = ["Python 3.10", "FastAPI", "Microsoft WebView2", "TailwindCSS", "PyInstaller Standalone"]
    total_w = sum(F_BADGE.getbbox(b)[2] + 40 for b in badges)
    bx = (WIDTH - total_w) // 2
    for b in badges:
        bw, _ = draw_badge(draw, b, bx, 450, bg_col=CARD_BG, text_col=ACCENT, font=F_BADGE, padding=(20, 8))
        bx += bw + 15

    # Caja verde prominente de descarga
    box_w = 1180
    box_h = 180
    box_x = (WIDTH - box_w) // 2
    box_y = 560
    draw_card(draw, box_x, box_y, box_w, box_h, bg_col=PRIMARY, border_col=ACCENT, radius=22)
    draw.text((WIDTH // 2, box_y + 45), "Disponible para descargar gratis el ejecutable .exe en:", fill=WHITE, font=F_BODY, anchor="mm")
    draw.text((WIDTH // 2, box_y + 110), "github.com/yKoutl/NosClean/releases/tag/v5.0.7", fill=WHITE, font=F_TITLE, anchor="mm")

    draw.text((WIDTH // 2, 800), "Desarrollado para quienes valoran la velocidad, la privacidad y el código limpio.", fill=SLATE_LIGHT, font=F_BODY, anchor="mm")
    draw.text((WIDTH // 2, 840), "Comparte tu opinión o deja una estrella en el repositorio de GitHub.", fill=SLATE_MUTED, font=F_BODY, anchor="mm")

    draw_subtitles(draw, sub_text)
    return img

def build_video_and_mux():
    print("Iniciando generación de audio y video con locución en español...")

    # 1. Tiempos exactos sincronizados con los archivos de voz generados
    scenes = [
        (render_scene_1, 9.2),
        (render_scene_2, 9.5),
        (render_scene_3, 8.8),
        (render_scene_4, 7.8),
        (render_scene_5, 7.5),
        (render_scene_6, 9.0)
    ]
    total_dur = sum(dur for _, dur in scenes)
    total_frames = int(total_dur * FPS)
    print(f"Duración total del video: {total_dur:.1f} segundos ({total_frames} cuadros a {FPS} FPS)")

    # 2. Renderizar video silencioso en MP4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(TEMP_VIDEO, fourcc, float(FPS), (WIDTH, HEIGHT))

    for s_idx, (render_fn, dur) in enumerate(scenes):
        s_frames = int(dur * FPS)
        print(f"Renderizando Escena {s_idx + 1}/{len(scenes)} ({s_frames} cuadros)...")
        for f in range(s_frames):
            t = f / FPS
            pil_frame = render_fn(t, dur)

            # Fundido cruzado de 6 cuadros entre escenas
            if f >= s_frames - 6 and s_idx < len(scenes) - 1:
                alpha = (s_frames - f) / 6.0
                next_frame = scenes[s_idx + 1][0](0.0, scenes[s_idx + 1][1])
                pil_frame = Image.blend(next_frame, pil_frame, alpha)

            arr = np.array(pil_frame)
            cv_frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

    out.release()
    print(f"Video visual generado: {TEMP_VIDEO} ({os.path.getsize(TEMP_VIDEO)} bytes)")

    # 3. Muxing con FFmpeg: fusionar video + locución en español AAC de alta fidelidad
    audio_full = os.path.abspath("scripts/audio/voiceover_full.wav")
    print(f"Fusionando con FFmpeg: {FFMPEG}")

    cmd = [
        FFMPEG,
        "-y",
        "-i", os.path.abspath(TEMP_VIDEO),
        "-i", audio_full,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        os.path.abspath(FINAL_VIDEO)
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"Video final con audio completado exitosamente: {FINAL_VIDEO} ({os.path.getsize(FINAL_VIDEO)} bytes)")
        # Copiar también a backup
        backup_path = r"D:\PROYECTOS\NosClean\NosClean_Promo_LinkedIn.mp4"
        import shutil
        shutil.copy2(FINAL_VIDEO, backup_path)
        print(f"Copia actualizada en: {backup_path}")
    else:
        print("Error en FFmpeg:")
        print(res.stderr)

if __name__ == "__main__":
    build_video_and_mux()
