# Guía Maestra para Detección y Eliminación de Incoherencias en Proyectos Frontend con IA

Este documento sirve como manual e instrucción directa para que cualquier Inteligencia Artificial (o desarrollador) audite un proyecto, detecte elementos improvisados, incongruencias visuales, código huérfano y estandarice la arquitectura bajo el sistema de diseño corporativo.

---

## 🎯 Objetivo de esta Auditoría

Asegurar que **ninguna pantalla, modal o flujo** use soluciones aisladas, alertas nativas del sistema operativo, spinners CSS rústicos o etiquetas HTML crudas habiendo componentes oficiales diseñados para tal fin.

---

## 🔍 Checklist de Detección (Los 6 Pecados Capitales del Frontend)

### 1. Cuadros de Diálogo Nativos del Navegador (`alert`, `confirm`, `prompt`)
* **Incoherencia:** Usar `window.confirm(...)`, `alert(...)` o `prompt(...)`. Estos cuadros bloquean el hilo principal de JavaScript, son grises y rompen por completo la experiencia de usuario corporativa.
* **Solución Estandarizada:**
  * Para confirmaciones destructivas o de seguridad: Usar `ConfirmModal` (`variant="error"` o `variant="primary"`).
  * Para avisos informativos o de éxito/error: Usar el sistema de notificaciones `toast.success(...)`, `toast.error(...)` o `toast(...)`.

### 2. Estados de Carga Improvisados vs. `GlobalLoader`
* **Incoherencia:** Crear spinners CSS inline con `border-radius: 50%` y `@keyframes spin` artesanales, o usar íconos de carga simples (`Loader2 animate-spin`) en áreas principales.
* **Solución Estandarizada:**
  * Pantalla o modal en proceso: Utilizar el componente oficial `GlobalLoader` con la propiedad `isOverlay` (activando el desenfoque `backdrop-filter: blur(6px)` y la tuerca/isotipo animado de la marca).
  * Contenedor base `Modal`: Pasar las props `isLoading={loading}` y `loadingText="..."` para que el contenedor gestione el bloqueo de interacción y el loader automáticamente.

### 3. Etiquetas HTML Nativas sin Diseño Corporativo (`<button>`, `<select>`, `<input>`)
* **Incoherencia:** Colocar etiquetas `<button>` directas con CSS inline (`padding: 10px`, `borderRadius: 8px`), o `<select>` estándar de HTML.
* **Solución Estandarizada:**
  * Botones: Usar siempre `Button` (`variant="primary"`, `variant="secondary"`, `variant="error"`). Este componente ya incluye microanimaciones hover, elevación de sombras (`boxShadow`), estados `disabled` y el spinner `isLoading` integrado.
  * Selectores: Usar el componente corporativo `Select` que implementa dropdown estilizado, scrollbar temática y compatibilidad con tema oscuro/claro.

### 4. Presencia de Emojis en Interfaces Corporativas
* **Incoherencia:** Utilizar emojis de texto (como 😅, ℹ️, ⚠️, 🚀) en títulos, diálogos, notificaciones o botones. Los emojis renderizan de forma diferente en Windows, macOS, Android e iOS, y lucen poco profesionales.
* **Solución Estandarizada:**
  * Utilizar exclusivamente íconos SVG de la librería oficial instalada (por ejemplo, **Lucide React**: `Info`, `AlertCircle`, `CheckCircle2`, `Send`, etc.).

### 5. Incoherencias de Animación y Keyframes Huérfanos
* **Incoherencia:** Invocar clases o estilos como `animation: 'fadeIn 0.2s ease-out'` sin tener la regla `@keyframes fadeIn` declarada en el módulo CSS del componente, o inyectar etiquetas `<style>` directas en el árbol JSX en cada render.
* **Solución Estandarizada:**
  * Centralizar las animaciones en archivos CSS Modules (`.module.css`) o en `globals.css`.

### 6. Archivos y Componentes Huérfanos (Código Muerto)
* **Incoherencia:** Componentes de versiones anteriores que quedaron abandonados tras una refactorización (ej. formularios duplicados, estilos antiguos sin imports).
* **Solución Estandarizada:**
  * Escanear el proyecto verificando si cada archivo en `src/components/` tiene al menos una importación activa. Si no se usa en ninguna ruta ni componente padre, debe ser eliminado de forma limpia.

---

## 🛠️ Prompts de Auditoría para pasarle a la IA

Si abres un nuevo proyecto o inicias una sesión con una IA, copia y pega estos prompts en orden:

### Paso 1: Auditoría de Diálogos Nativos y Emojis
> *"Busca en todo el proyecto si existen llamadas a `window.confirm`, `window.alert`, `alert(`, `confirm(` o `prompt(`. Además, realiza un escaneo de caracteres Unicode de emojis `[\uD83C-\uDBFF\uDC00-\uDFFF]` en los archivos `.tsx` y `.ts`. Reemplaza los diálogos nativos por nuestro componente `ConfirmModal` o notificaciones `toast`, y sustituye cualquier emoji por íconos SVG de Lucide."*

### Paso 2: Auditoría de Spinners y Estados de Carga
> *"Inspecciona todas las modales y contenedores principales de la aplicación. Busca si hay spinners CSS inline (`animation: spin`, bordes circulares improvisados) o componentes de loader genéricos. Reemplázalos por el componente corporativo `GlobalLoader` con `isOverlay` y verifica que los botones usen la prop `isLoading` del componente `Button`."*

### Paso 3: Detección de Código Muerto
> *"Revisa la carpeta `src/components/` y enumera qué componentes no están siendo importados por ninguna página, ruta ni otro componente. Si confirmas que son archivos huérfanos o reemplazados por una versión más moderna, elimínalos."*

### Paso 4: Verificación de Tipos y Empaquetado
> *"Ejecuta `npx tsc --noEmit` para garantizar cero errores de TypeScript y asegúrate de que el empaquetado de producción (`npm run build` o `npm run pack`) compile limpiamente sin advertencias de sintaxis."*

---

## 📋 Resumen de la Filosofía de Diseño Chaski

| Elemento | ❌ Lo que NO se debe hacer | ✅ Lo que SIEMPRE se debe usar |
| :--- | :--- | :--- |
| **Confirmación de Borrado/Acción** | `window.confirm('¿Desea borrar?')` | `<ConfirmModal isOpen={...} onConfirm={...} />` |
| **Notificación / Alerta** | `window.alert('Listo')` | `toast.success('...')` / `toast.error('...')` |
| **Carga en Modales** | Spinner de borde gris inline | `<GlobalLoader isOverlay text="..." />` |
| **Botones de Envío / Guardado** | `<button style={{ padding: 10 }}>` | `<Button variant="primary" isLoading={loading}>` |
| **Selectores de Zona / Catálogo** | `<select><option>...</option></select>` | `<Select options={...} value={...} />` |
| **Iconografía** | Emojis (`😅`, `ℹ️`, `📅`) | Íconos SVG Lucide (`<Calendar />`, `<Info />`) |
