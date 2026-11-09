# 🔤 Guía de Codificación de Caracteres y Carácter de Reemplazo (U+FFFD)

Este documento detalla qué es el símbolo ``, por qué aparece en aplicaciones web y cómo se gestiona la codificación de caracteres en **ReporteDash** para evitar textos corruptos en la interfaz.

---

## 1. ¿Qué es exactamente el símbolo ``?

El símbolo del rombo negro con signo de interrogación `` se conoce formalmente como el **Carácter de Reemplazo de Unicode (Unicode Replacement Character - `U+FFFD`)**.

* **No es un emoji ni un icono:** Es una señal de emergencia que introduce el motor de texto del navegador web o del sistema operativo.
* **Significado:** *"Aquí había un carácter que no pude interpretar porque la secuencia de bytes no coincide con la codificación esperada."*

---

## 2. ¿Por qué ocurre esto en palabras en español?

En el idioma español usamos caracteres especiales que no existen en el inglés básico (ASCII):
* Signos de apertura: `¡`, `¿`
* Vocales con tilde: `á`, `é`, `í`, `ó`, `ú`, `Á`, `É`, `Í`, `Ó`, `Ú`
* Letras especiales: `ñ`, `Ñ`, `ü`

### El choque de codificaciones:
1. **UTF-8 (Estándar Web Moderno):** Usa entre 2 y 4 bytes para representar caracteres especiales (por ejemplo, `¡` en UTF-8 se guarda con los bytes `0xC2 0xA1`).
2. **Windows-1252 / ANSI / ISO-8859-1 (Codificaciones antiguas de Windows):** Guardan la `¡` en un solo byte (`0xA1`).

### El error en `ModalUpload.tsx`:
En el archivo `ModalUpload.tsx` (línea 49), se guardó en algún momento el texto:
```tsx
// Incorrecto (bytes corruptos):
<span className="...">Data Actualizada!</span>
```
Al intentar interpretarlo bajo UTF-8 estricto, el navegador no reconoció el byte solitario y pintó el rombo ``. Su contenido previsto era:
```tsx
// Correcto (UTF-8 estándar):
<span className="...">¡Data Actualizada!</span>
```

---

## 3. ¿Cómo se diagnosticó y resolvió en el proyecto?

1. **Búsqueda profunda por código hexadecimal:**
   Se ejecutó un script en Node.js que escaneó cada archivo `.ts`, `.tsx`, `.md` y `.json` del repositorio buscando la secuencia `\uFFFD`.
2. **Archivos detectados y reparados:**
   * **`src/components/modals/ModalUpload.tsx`**: Se corrigió `Data Actualizada!` a `¡Data Actualizada!` y se acentuó `Información`.
   * **`README.md`**: Tenía una cabecera histórica creada con codificación UTF-16 LE con BOM; se reescribió en UTF-8 plano sin BOM.
3. **Validación:**
   Se volvió a correr el verificador automatizado y el conteo de caracteres `\uFFFD` en todo el proyecto es exactamente **0**.

---

## 4. Buenas Prácticas para Evitar que Vuelva a Suceder

Para asegurar que todo el equipo mantenga la codificación uniforme:

1. **Configuración del Editor (VS Code / Antigravity):**
   * En la barra inferior derecha del editor, verificar siempre que la codificación diga **UTF-8** (nunca `Windows 1252`, `Western` o `UTF-16`).
   * Configuración recomendada en `.vscode/settings.json`:
     ```json
     {
       "files.encoding": "utf8",
       "files.autoGuessEncoding": false
     }
     ```
2. **Copiar y Pegar desde Documentos Externos:**
   * Al copiar textos desde correos antiguos, documentos Word o archivos `.bat` de Windows, pegarlos como texto plano para evitar arrastrar bytes no compatibles con UTF-8.
3. **Declaración en `index.html`:**
   * El proyecto ya cuenta en la primera línea de su `<head>` con:
     ```html
     <meta charset="UTF-8" />
     ```
     Esto obliga a los navegadores modernos a procesar todos los módulos bajo el estándar UTF-8.
