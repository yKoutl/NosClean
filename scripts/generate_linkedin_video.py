import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30
OUTPUT_FILE = "NosClean_Promo_LinkedIn.mp4"

# Paleta de colores oficial NosClean
BG_DARK = (16, 45, 37)       # #102D25
BG_DEEP = (10, 29, 23)       # #0A1D17
PRIMARY = (8, 122, 69)       # #087A45
ACCENT = (22, 184, 78)       # #16B84E
WHITE = (255, 255, 255)
SLATE_LIGHT = (226, 232, 240)
SLATE_MUTED = (148, 163, 184)
CARD_BG = (20, 54, 45)
CARD_BORDER = (35, 85, 70)

# Cargar fuentes del sistema
FONT_BOLD_PATH = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG_PATH = r"C:\Windows\Fonts\segoeui.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

FONT_HERO = get_font(72, bold=True)
FONT_TITLE = get_font(52, bold=True)
FONT_SUBTITLE = get_font(34, bold=True)
FONT_BODY = get_font(26, bold=False)
FONT_BADGE = get_font(22, bold=True)
FONT_SMALL = get_font(20, bold=False)

# Rutas de recursos visuales
LOGO_PATH = "static/logo.png"
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = "assets/branding/NosClean_icon_large.png"

UI_MAIN_PATH = r"C:/Users/RAUL/.gemini/antigravity/brain/18bec041-707c-4000-86be-1e15a9d49b23/.user_uploaded/media_1794577761220_0dbd9e5d.png"
UI_WIDGET_PATH = r"C:/Users/RAUL/.gemini/antigravity/brain/18bec041-707c-4000-86be-1e15a9d49b23/.user_uploaded/media_1794518905962_587780e3.png"
UI_ROCKET_PATH = r"C:/Users/RAUL/.gemini/antigravity/brain/18bec041-707c-4000-86be-1e15a9d49b23/.user_uploaded/media_1794519917941_47d26f2b.png"

logo_img = Image.open(LOGO_PATH).convert("RGBA") if os.path.exists(LOGO_PATH) else None
ui_main_img = Image.open(UI_MAIN_PATH).convert("RGBA") if os.path.exists(UI_MAIN_PATH) else None
ui_widget_img = Image.open(UI_WIDGET_PATH).convert("RGBA") if os.path.exists(UI_WIDGET_PATH) else None
ui_rocket_img = Image.open(UI_ROCKET_PATH).convert("RGBA") if os.path.exists(UI_ROCKET_PATH) else None

def create_base_canvas():
    """Genera fondo degradado corporativo de NosClean."""
    base = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_DEEP[0] * (1 - ratio) + BG_DARK[0] * ratio)
        g = int(BG_DEEP[1] * (1 - ratio) + BG_DARK[1] * ratio)
        b = int(BG_DEEP[2] * (1 - ratio) + BG_DARK[2] * ratio)
        base[y, :] = (r, g, b)
    return Image.fromarray(base)

BASE_BG = create_base_canvas()

def draw_badge(draw, text, x, y, bg_col=PRIMARY, text_col=WHITE, font=FONT_BADGE, padding=(16, 6)):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + padding[0] * 2
    h = bbox[3] - bbox[1] + padding[1] * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=bg_col)
    draw.text((x + padding[0], y + padding[1]), text, fill=text_col, font=font)
    return w, h

def draw_card(draw, x, y, w, h, bg_col=CARD_BG, border_col=CARD_BORDER, radius=20):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg_col, outline=border_col, width=2)

def pil_to_cv(pil_img):
    arr = np.array(pil_img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def render_scene_1(t, dur=4.5):
    """Escena 1: Presentación / Intro Corporativo"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)
    progress = min(1.0, t / 1.5)
    scale = 0.8 + 0.2 * progress

    # Logo centrado
    if logo_img:
        lw, lh = int(180 * scale), int(180 * scale)
        l_scaled = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (WIDTH - lw) // 2
        ly = int(240 - 20 * (1 - progress))
        img.paste(l_scaled, (lx, ly), l_scaled)

    # Título NosClean
    draw.text((WIDTH // 2, 470), "NOSCLEAN", fill=ACCENT, font=FONT_HERO, anchor="mm")
    
    # Badge de versión
    draw_badge(draw, "VERSIÓN 5.0.7", (WIDTH // 2) - 90, 525, bg_col=PRIMARY, font=FONT_BADGE)

    # Subtítulo y propuesta
    draw.text((WIDTH // 2, 630), "Auditoría inteligente, optimización y limpieza para Windows", fill=WHITE, font=FONT_SUBTITLE, anchor="mm")
    draw.text((WIDTH // 2, 690), "100% Nativo • Sin telemetría • Standalone ejecutable", fill=SLATE_MUTED, font=FONT_BODY, anchor="mm")

    # Barra decorativa de progreso
    bar_w = int(600 * min(1.0, t / dur))
    draw.rounded_rectangle([(WIDTH - 600) // 2, 760, (WIDTH - 600) // 2 + bar_w, 766], radius=3, fill=ACCENT)

    return img

def render_scene_2(t, dur=5.0):
    """Escena 2: El problema en Windows"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "EL PROBLEMA ACTUAL", 140, 100, bg_col=(180, 50, 50), text_col=WHITE)
    draw.text((140, 180), "¿Por qué la mayoría de limpiadores de PC decepcionan?", fill=WHITE, font=FONT_TITLE)

    pains = [
        ("Publicidad y Bloatware invasivo", "Te instalan navegadores secundarios, barras de búsqueda y programas no deseados."),
        ("Métricas infladas y engañosas", "Prometen borrar gigabytes que en realidad están bloqueados por el propio Windows."),
        ("Procesos pesados que ralentizan tu equipo", "Consumen memoria continua en segundo plano empeorando el rendimiento.")
    ]

    card_y = 280
    for idx, (title, desc) in enumerate(pains):
        appear_t = 0.5 + idx * 0.7
        if t >= appear_t:
            draw_card(draw, 140, card_y, 1640, 150, bg_col=(30, 25, 25), border_col=(100, 50, 50))
            draw.text((180, card_y + 35), f"• {title}", fill=(255, 120, 120), font=FONT_SUBTITLE)
            draw.text((210, card_y + 85), desc, fill=SLATE_LIGHT, font=FONT_BODY)
        card_y += 180

    return img

def render_scene_3(t, dur=6.5):
    """Escena 3: La solución NosClean (Auditoría en tiempo real)"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "SOLUCIÓN INTEGRAL", 140, 70, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 140), "Diagnóstico transparente y hardware en tiempo real", fill=WHITE, font=FONT_TITLE)
    draw.text((140, 205), "Sin telemetría oculta • Métricas de procesador, RAM, GPU y discos en un solo panel", fill=SLATE_MUTED, font=FONT_BODY)

    # Marco con la captura real de NosClean con suave paneo
    if ui_main_img:
        target_w, target_h = 1640, 740
        # Zoom sutil
        zoom_factor = 1.0 + (t / dur) * 0.05
        cw = int(ui_main_img.width / zoom_factor)
        ch = int(ui_main_img.height / zoom_factor)
        crop_box = (0, 0, min(ui_main_img.width, cw), min(ui_main_img.height, ch))
        cropped = ui_main_img.crop(crop_box).resize((target_w, target_h), Image.Resampling.LANCZOS)

        draw_card(draw, 140, 260, target_w, target_h, border_col=ACCENT, radius=24)
        img.paste(cropped, (140, 260))

    return img

def render_scene_4(t, dur=6.0):
    """Escena 4: Optimización instantánea con Cohete"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "OPTIMIZACIÓN INSTANTÁNEA", 140, 70, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 140), "Liberación de memoria RAM y caché en 1 solo clic", fill=WHITE, font=FONT_TITLE)

    # Panel izquierdo explicativo
    draw_card(draw, 140, 240, 760, 720)
    features = [
        ("Vaciado de bloques de RAM inactiva", "Recupera cientos de MB de memoria retenida por programas antiguos."),
        ("Depuración segura de temporales", "Elimina cachés de Chrome, Edge y %TEMP% protegiendo archivos en uso."),
        ("Cero congelamientos de pantalla", "Animación fluida con Cohete SVG y porcentaje real de progreso."),
        ("Transparencia absoluta", "Reporte exacto de MB liberados sin números inflados.")
    ]
    fy = 280
    for f_title, f_desc in features:
        draw.text((170, fy), f"✔ {f_title}", fill=ACCENT, font=FONT_SUBTITLE)
        draw.text((170, fy + 45), f_desc, fill=SLATE_LIGHT, font=FONT_BODY)
        fy += 140

    # Panel derecho con modal real de optimización
    if ui_rocket_img:
        rw, rh = 760, 720
        r_resized = ui_rocket_img.resize((rw, rh), Image.Resampling.LANCZOS)
        draw_card(draw, 960, 240, rw, rh, border_col=ACCENT, radius=24)
        img.paste(r_resized, (960, 240))

    return img

def render_scene_5(t, dur=5.5):
    """Escena 5: Modo Widget y Centinela en Segundo Plano"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    draw_badge(draw, "CERO MOLESTIAS EN PANTALLA", 140, 70, bg_col=PRIMARY, text_col=WHITE)
    draw.text((140, 140), "Modo Widget Flotante y Centinela Invisible (0% CPU)", fill=WHITE, font=FONT_TITLE)

    # Panel izquierdo con imagen del widget
    if ui_widget_img:
        ww, wh = 800, 520
        w_resized = ui_widget_img.resize((ww, wh), Image.Resampling.LANCZOS)
        draw_card(draw, 140, 280, ww, wh, border_col=ACCENT, radius=24)
        img.paste(w_resized, (140, 280))

    # Panel derecho explicativo
    draw_card(draw, 980, 280, 800, 520)
    draw.text((1020, 330), "Vigilancia de Memoria 'De la Nada'", fill=ACCENT, font=FONT_SUBTITLE)
    draw.text((1020, 390), "• Al pulsar la 'X', la ventana se oculta completamente.", fill=WHITE, font=FONT_BODY)
    draw.text((1020, 440), "• Cero iconos molestos estorbando en la barra de tareas.", fill=WHITE, font=FONT_BODY)
    draw.text((1020, 490), "• Consume 0% de CPU mientras duerme en segundo plano.", fill=WHITE, font=FONT_BODY)
    draw.text((1020, 540), "• Si la RAM supera el 80%, Windows te avisa automáticamente", fill=SLATE_LIGHT, font=FONT_BODY)
    draw.text((1040, 580), "con una notificación nativa oficial en tu escritorio.", fill=SLATE_LIGHT, font=FONT_BODY)
    draw.text((1020, 640), "• Haz doble clic en el acceso directo y reaparece al instante.", fill=ACCENT, font=FONT_BODY)

    return img

def render_scene_6(t, dur=4.5):
    """Escena 6: Stack Tecnológico y Call to Action"""
    img = BASE_BG.copy()
    draw = ImageDraw.Draw(img)

    if logo_img:
        l_scaled = logo_img.resize((140, 140), Image.Resampling.LANCZOS)
        img.paste(l_scaled, (WIDTH // 2 - 70, 140), l_scaled)

    draw.text((WIDTH // 2, 330), "NOSCLEAN v5.0.7", fill=ACCENT, font=FONT_HERO, anchor="mm")
    draw.text((WIDTH // 2, 410), "100% Gratuito y de Código Abierto para Windows", fill=WHITE, font=FONT_SUBTITLE, anchor="mm")

    # Badges del stack tecnológico
    badges = ["Python 3.10", "FastAPI", "WebView2", "TailwindCSS", "PyInstaller Standalone"]
    total_w = sum(get_font(24, bold=True).getbbox(b)[2] + 40 for b in badges)
    bx = (WIDTH - total_w) // 2
    for b in badges:
        bw, _ = draw_badge(draw, b, bx, 480, bg_col=CARD_BG, text_col=ACCENT, font=get_font(24, bold=True), padding=(20, 8))
        bx += bw + 15

    # Caja de descarga GitHub
    draw_card(draw, (WIDTH - 1100) // 2, 600, 1100, 180, bg_col=PRIMARY, border_col=ACCENT, radius=24)
    draw.text((WIDTH // 2, 650), "Disponible para descargar el ejecutable .exe en:", fill=WHITE, font=FONT_BODY, anchor="mm")
    draw.text((WIDTH // 2, 710), "github.com/yKoutl/NosClean/releases/tag/v5.0.7", fill=WHITE, font=FONT_SUBTITLE, anchor="mm")

    draw.text((WIDTH // 2, 860), "Optimiza tu PC sin complicaciones. Comparte o deja tu estrella en GitHub.", fill=SLATE_MUTED, font=FONT_BODY, anchor="mm")

    return img

def main():
    print("Iniciando renderizado del video promocional para LinkedIn...")
    scenes = [
        (render_scene_1, 4.5),
        (render_scene_2, 5.0),
        (render_scene_3, 6.5),
        (render_scene_4, 6.0),
        (render_scene_5, 5.5),
        (render_scene_6, 4.5)
    ]
    total_duration = sum(dur for _, dur in scenes)
    total_frames = int(total_duration * FPS)
    print(f"Duración total: {total_duration:.1f} segundos ({total_frames} cuadros a {FPS} FPS, 1920x1080 Full HD)")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, float(FPS), (WIDTH, HEIGHT))

    frame_count = 0
    for s_idx, (render_fn, dur) in enumerate(scenes):
        s_frames = int(dur * FPS)
        print(f"Renderizando Escena {s_idx + 1}/{len(scenes)} ({s_frames} cuadros)...")
        for f in range(s_frames):
            t = f / FPS
            pil_frame = render_fn(t, dur)

            # Efecto sutil de fundido cruzado (fade out) en los últimos 8 cuadros de cada escena
            if f >= s_frames - 8 and s_idx < len(scenes) - 1:
                alpha = (s_frames - f) / 8.0
                next_frame = scenes[s_idx + 1][0](0.0, scenes[s_idx + 1][1])
                pil_frame = Image.blend(next_frame, pil_frame, alpha)

            cv_frame = pil_to_cv(pil_frame)
            out.write(cv_frame)
            frame_count += 1

    out.release()
    print(f"Video completado exitosamente: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")

if __name__ == "__main__":
    main()
