import win32com.client
import wave
import contextlib
import os

AUDIO_DIR = "scripts/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

voice_texts = {
    "scene1": "NosClean versión 5.0.7. Auditoría inteligente, optimización y limpieza profesional para Windows.",
    "scene2": "¿Cansado de optimizadores lentos, llenos de publicidad y con métricas engañosas? NosClean fue creado para darte una solución real.",
    "scene3": "Obtén un diagnóstico transparente con métricas de procesador, memoria RAM, tarjeta gráfica y unidades de almacenamiento.",
    "scene4": "Con un solo clic, libera bloques de memoria inactiva y depura archivos temporales sin tocar tus documentos personales.",
    "scene5": "Pasa al Modo Widget flotante en tu escritorio o déjalo en segundo plano con cero por ciento de consumo de procesador.",
    "scene6": "NosClean es totalmente gratuito y de código abierto. Descarga el ejecutable oficial en GitHub y optimiza tu PC hoy mismo."
}

def generate_voiceover():
    v = win32com.client.Dispatch("Sapi.SpVoice")
    # Seleccionar voz española Helena
    for x in v.GetVoices():
        if "helena" in x.GetDescription().lower():
            v.Voice = x
            break

    v.Rate = 0  # Velocidad natural
    durations = {}

    for key, text in voice_texts.items():
        wav_path = os.path.join(AUDIO_DIR, f"{key}.wav")
        fs = win32com.client.Dispatch("Sapi.SpFileStream")
        fs.Open(wav_path, 3)  # SSFMCreateForWrite
        v.AudioOutputStream = fs
        v.Speak(text)
        fs.Close()

        with contextlib.closing(wave.open(wav_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            durations[key] = duration
            print(f"{key}: {duration:.2f}s ({wav_path})")

    # Crear audio completo combinado
    full_wav_path = os.path.join(AUDIO_DIR, "voiceover_full.wav")
    data = []
    params = None
    for key in sorted(voice_texts.keys()):
        wav_path = os.path.join(AUDIO_DIR, f"{key}.wav")
        with contextlib.closing(wave.open(wav_path, 'r')) as f:
            if params is None:
                params = f.getparams()
            data.append(f.readframes(f.getnframes()))
            # Agregar 0.8s de silencio entre escenas
            silence_frames = int(f.getframerate() * 0.8)
            silence = b'\x00' * (silence_frames * f.getnchannels() * f.getsampwidth())
            data.append(silence)

    with contextlib.closing(wave.open(full_wav_path, 'wb')) as f:
        f.setparams(params)
        for d in data:
            f.writeframes(d)

    with contextlib.closing(wave.open(full_wav_path, 'r')) as f:
        total_dur = f.getnframes() / float(f.getframerate())
        print(f"Total audio duration: {total_dur:.2f}s")

    return durations, total_dur

if __name__ == "__main__":
    generate_voiceover()
