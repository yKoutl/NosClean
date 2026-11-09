# Manual de Uso, Términos de Servicio y Marco Legal de NosClean

**Versión:** 2.0  
**Fecha de actualización:** Noviembre 2026  
**Entorno:** Windows 10 / Windows 11 (64-bit)  
**Titular:** NosClean Software  

---

## 1. Manual de Instrucciones y Guía de Uso

NosClean es una suite de mantenimiento, optimización y organización inteligente de Windows, diseñada con arquitectura 100% local, cero ventanas nativas y mínimo consumo de recursos.

### 1.1 Optimización Rápida en 1 Clic
- **Ubicación:** Botón verde superior «Optimizar PC» en la barra de navegación.
- **Función:** Ejecuta de forma segura la purga de memoria RAM inactiva (`EmptyWorkingSet` de procesos de usuario en segundo plano) y vacía los registros de caché residual del sistema.
- **Resultado:** Liberación inmediata de entre 500 MB y 2 GB de memoria RAM sin cerrar tus programas activos.

### 1.2 Consejos y Asesor de Salud del PC
- **Función:** Diagnóstico integral del estado de salud del equipo con puntaje de 0 a 100.
- **Indicadores:** Evalúa espacio libre en unidad C:, programas pesados que ralentizan el arranque y volumen acumulado de archivos temporales.
- **Recomendaciones:** Proporciona sugerencias accionables con accesos directos con un solo clic.

### 1.3 Resumen de Hardware
- **Métricas:** Monitoreo en tiempo real del uso de CPU, cantidad de núcleos/hilos, memoria RAM (usada vs disponible), tarjeta gráfica (GPU/VRAM) y nivel de batería.
- **Unidades de Almacenamiento:** Muestra la capacidad total, porcentaje ocupado y espacio libre en cada disco (C:, D:, etc.), con acceso rápido al Explorador de Windows.

### 1.4 Limpiador de Archivos Basura y Temporales
- **Categorías auditadas:**
  - Caché de navegadores web (Google Chrome, Microsoft Edge).
  - Temporales del usuario (`%TEMP%`).
  - Temporales del sistema (`C:\Windows\Temp`).
  - Papelera de Reciclaje.
- **Procedimiento de uso:**
  1. Haz clic en **Analizar de Nuevo**.
  2. Selecciona o desmarca las categorías deseadas mediante las casillas de verificación.
  3. Haz clic en **Limpiar Seleccionados**. Aparecerá un modal corporativo de confirmación detallando los bytes a liberar.

### 1.5 Buscador de Archivos Pesados (Gigantes)
- **Función:** Localiza archivos que consumen espacio excesivo en tu disco o en tu carpeta de usuario.
- **Filtros disponibles:** Mayores a 50 MB, 100 MB, 250 MB o 500 MB.
- **Seguridad:** Permite abrir la carpeta contenedora en el Explorador o enviar a la Papelera de Reciclaje tras confirmación en modal.

### 1.6 Gestor de Programas Instalados
- **Función:** Lectura del Registro de Windows para listar todas las aplicaciones instaladas, su desarrollador, fecha de instalación y tamaño estimado.
- **Herramientas:** Barra de búsqueda en tiempo real, ordenación por tamaño o nombre, y acceso directo al desinstalador oficial de Windows.

### 1.7 Organizador Automático de Archivos
- **Objetivo:** Ordenar carpetas saturadas como Descargas o Escritorio.
- **Categorización inteligente:**
  - `Imágenes`: .jpg, .png, .webp, .svg, .gif, .ico.
  - `Documentos`: .pdf, .docx, .xlsx, .pptx, .txt.
  - `Instaladores`: .exe, .msi, .iso.
  - `Comprimidos`: .zip, .rar, .7z, .tar, .gz.
  - `Videos`: .mp4, .mkv, .avi, .mov.
  - `Audio`: .mp3, .wav, .flac.
  - `Código`: .py, .js, .html, .css, .json, .cpp.
- **Modo seguro:** Ofrece el botón **Vista Previa** para simular la organización antes de realizar cualquier movimiento de archivos físico.

### 1.8 Inicio de Windows y Procesos
- **Optimización de arranque:** Lista los programas configurados para iniciar automáticamente con Windows, permitiendo desactivar aquellos innecesarios.
- **Gestor de procesos:** Identifica procesos que consumen excesiva CPU o memoria y permite su finalización segura con confirmación.

---

## 2. Marco Legal, Derechos de Autor y Licencia

### 2.1 Propiedad Intelectual y Derechos Reservados
El software **NosClean**, incluyendo su código fuente, interfaz visual, estructura lógica, estilos gráficos, logotipos, íconos y documentación técnica, está protegido por las leyes de propiedad intelectual y derechos de autor internacionales.

**Copyright © 2026 NosClean Software. Todos los derechos reservados.**

### 2.2 Licencia de Uso
Se otorga al usuario una licencia no exclusiva, intransferible y revocable para utilizar NosClean con fines personales, profesionales y corporativos para el mantenimiento y diagnóstico de sus propios equipos informáticos.

**Queda estrictamente prohibido:**
- Realizar ingeniería inversa, descompilación o desensamblado con el propósito de crear herramientas maliciosas.
- Distribuir versiones alteradas del software que supriman las protecciones de seguridad o los avisos de autoría.
- Cobrar tarifas o suscripciones por la distribución de copias del software sin autorización expresa.

---

## 3. Política de Privacidad y Tratamiento de Datos (100% Local)

NosClean está construido bajo el principio fundamental de **Privacidad por Diseño (Privacy by Design)**:

1. **Cero Telemetría y Cero Rastreo:** NosClean no contiene identificadores de usuario, rastreadores publicitarios, analíticas de comportamiento ni balizas de telemetría.
2. **Servidor Local Exclusivo (`127.0.0.1`):** Todas las operaciones de red se ejecutan exclusivamente en la interfaz de bucle invertido local (*loopback interface*) de tu propia computadora.
3. **Cero Envío a la Nube:** Ningún archivo personal, nombre de usuario, historial de navegación, contenido de documentos ni ruta de disco es subido jamás a internet ni a servidores de terceros.
4. **Almacenamiento Temporal y Caché:** Las operaciones se procesan en la memoria volátil del equipo y no se almacenan historiales de archivos analizados fuera de la sesión activa.

---

## 4. Cláusula de Seguridad y Exención de Responsabilidad (*Disclaimer*)

### 4.1 Principio de Protección del Sistema Operativo
NosClean incluye protecciones internas de software para evitar daños accidentales al sistema operativo:
- **Protección de núcleo:** Las carpetas del sistema (`C:\Windows`, `System32`, `Program Files`, boot managers) están estrictamente excluidas de los procesos de purga automatizada.
- **Confirmación previa:** Ningún archivo es eliminado o movido sin que el usuario haya iniciado el proceso y confirmado la acción en el modal correspondiente.

### 4.2 Límite de Responsabilidad (*As-Is*)
El software se distribuye «tal cual» (*as-is*), sin garantías expresas o implícitas respecto a idoneidad para un propósito particular. Aunque NosClean se somete a rigurosas pruebas automatizadas de integridad de 38 niveles, el usuario final es el único responsable de verificar los archivos que decide eliminar o mover, especialmente al vaciar la Papelera de Reciclaje o eliminar archivos pesados personales.

En ningún caso los desarrolladores de NosClean serán responsables por pérdida incidental de datos o interrupciones derivadas del uso incorrecto de las herramientas de desinstalación de Windows o de la eliminación manual de archivos por parte del usuario.
