# ⚡ NosClean
> *Auditoría de hardware, optimización del sistema y limpieza inteligente para Windows.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Modern_API-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**NosClean** es una suite completa y moderna diseñada para auditar el hardware de tu PC en tiempo real, limpiar archivos temporales/basura de forma segura, controlar las aplicaciones de inicio y mantener organizadas tus carpetas críticas.

---

## 🌟 Características Principales

### 1. 🖥️ Auditoría de Hardware y Telemetría en Vivo
- **Procesador (CPU)**: Modelo exacto, núcleos físicos, hilos lógicos, frecuencia y porcentaje de carga en tiempo real.
- **Memoria RAM**: Monitoreo de memoria total, en uso y libre, con desglose de módulos SODIMM/DDR y alertas de saturación.
- **Gráficos (GPU)**: Detección de tarjeta gráfica, memoria VRAM y versión de drivers instalados.
- **Almacenamiento**: Estado de cada partición (`C:`, `D:`, `G:`), lectura de espacio libre vs. total y porcentaje ocupado.
- **Batería y Energía**: Capacidad de diseño, capacidad actual, desgaste porcentual y conteo de ciclos de carga.

### 2. 🧠 Asesor Inteligente & Puntuación de Salud (PC Health Score)
- Algoritmo de diagnóstico que califica el estado general de tu PC (0 a 100 puntos).
- Recomendaciones contextuales clasificadas por prioridad (Crítico, Rendimiento, Espacio, Organización).
- Detección proactiva de cuellos de botella térmicos, saturación de disco `C:` y programas de inicio pesados.

### 3. 🧹 Limpieza Profunda de Basura y Caché
- Limpieza segura sin tocar tus archivos de trabajo:
  - Temporales de usuario (`%TEMP%`).
  - Temporales del sistema (`C:\Windows\Temp`).
  - Reportes de errores de Windows y crash dumps.
  - Caché de navegadores web (Chrome, Edge, Brave, etc.).
  - Caché de gestores de desarrollo (Pip, NPM, Node.js).
  - Descargas residuales y registros de Windows Update.
  - Papelera de reciclaje (conteo de elementos y tamaño total).
- Omite automáticamente archivos protegidos o en uso sin bloquear el sistema.

### 4. ⚡ Optimización del Arranque (Startup Manager)
- Identifica aplicaciones secundarias que ralentizan el encendido de Windows (Discord, Rave, Notion, Figma, Roblox, pre-arranque de navegadores).
- Permite desactivarlas del arranque automático para encendidos en cuestión de segundos, sin desinstalarlas.

### 5. 📦 Buscador de Archivos Gigantes
- Encuentra rápidamente archivos pesados que consumen tu almacenamiento:
  - Filtros ajustables: >50 MB, >100 MB, >500 MB, >1 GB o >2 GB.
  - Exploración en perfil de usuario, Descargas, Videos, o discos enteros.
  - Opciones de acción inmediata: abrir ubicación en el Explorador o enviar a la Papelera de Reciclaje.

### 6. 📁 Organizador Inteligente de Descargas y Archivos
- Escanea carpetas desordenadas y clasifica automáticamente en categorías:
  - 📦 **Instaladores** (`.exe`, `.msi`, `.iso`)
  - 🗜️ **Comprimidos** (`.zip`, `.rar`, `.7z`)
  - 📄 **Documentos** (`.pdf`, `.docx`, `.xlsx`, `.pptx`)
  - 🖼️ **Imágenes** (`.png`, `.jpg`, `.svg`)
  - 🎬 **Videos** (`.mp4`, `.mkv`)
  - 🎵 **Música y Audio** (`.mp3`, `.wav`)
  - 💻 **Código y Scripts** (`.py`, `.js`, `.json`, `.sql`)
- Detección de archivos antiguos (>30 o >90 días) con modo **Vista Previa** antes de mover cualquier elemento.

### 7. ☁️ Soporte de Respaldos
- Scripts automáticos de respaldo con exclusión inteligente (`node_modules`, `.git`, `.pnpm-store`) listos para sincronizar carpetas críticas de proyectos hacia Google Drive o discos externos.

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Monitoreo de Sistema**: [psutil](https://github.com/giampaolo/psutil), WMI / CimInstance, WinReg
- **Frontend**: HTML5, Tailwind CSS, JavaScript Vanilla, Lucide Icons
- **Automatización**: PowerShell & Windows Shell Scripts (`.bat`, `.vbs`)

---

## 🚀 Instalación y Puesta en Marcha

### Requisitos Previos
* Windows 10 o Windows 11 (64-bit)
* Python 3.10 o superior

### Método Rápido (Doble Clic):
Haz doble clic en cualquiera de estos accesos en la raíz del proyecto:
* `iniciar_panel.vbs` *(inicia el servidor en segundo plano sin ventana negra).*
* `run.bat` o `iniciar_panel.bat`

El panel abrirá automáticamente tu navegador en:
```
http://127.0.0.1:8000
```

### Ejecución Manual por Consola:
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/NosClean.git
cd NosClean

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el servidor
python main.py
```

---

## 📄 Licencia

Distribuido bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para más información.
