# Guía Maestra de Blindaje contra Pantallas Blancas y Fallos de Caché en Aplicaciones Web y PWA

Este documento establece el protocolo técnico estándar para que cualquier Inteligencia Artificial (o desarrollador) audite, aplique y verifique las 4 capas de protección industrial contra pantallas blancas, recursos rotos y desincronización de versiones en cualquier aplicación web SPA (Single Page Application) o PWA (Progressive Web App), sin alterar jamás la lógica comercial ni las fórmulas del proyecto.

---

## 1. Diagnóstico del Problema: ¿Por qué ocurre la Pantalla Blanca?

En aplicaciones modernas basadas en React, Vite o empaquetadores similares, la pantalla blanca (White Screen of Death) suele ocurrir por cuatro fallos de infraestructura independientes del código comercial:

1. **Fallo de Fragmento Desactualizado (Stale Chunk Failure):**
   Al desplegar una nueva versión en producción, los nombres de archivo `.js` cambian de hash (ej. `Dashboard-A1B2.js` pasa a `Dashboard-C3D4.js`). Si un usuario tenía la app abierta o la abre horas después, el navegador intenta pedir el archivo antiguo que ya no existe en el servidor, arrojando un error de red y dejando la pantalla en blanco.

2. **Caché Persistente Indebida del HTML:**
   Si el servidor web guarda en caché el archivo `index.html`, el navegador del usuario seguirá leyendo referencias a scripts viejos durante días, forzando al usuario a borrar datos de navegación o presionar Ctrl + F5 repetidamente.

3. **Pérdida de Imágenes y Recursos tras Modo Suspendido:**
   En celulares y laptops, cuando el dispositivo entra en reposo o el usuario abre la app en áreas con baja cobertura, las imágenes que no fueron cacheadas en disco local no cargan o muestran iconos rotos.

4. **Retardo de Montaje en Contenedores Vacíos:**
   Si `<div id="root"></div>` está vacío en el HTML inicial, durante los 300ms a 1500ms que tarda el motor de JavaScript en arrancar en dispositivos de gama media, el usuario ve un pantallazo blanco sin retroalimentación visual.

---

## 2. Fase 1: Identificación y Auditoría del Proyecto por la IA

Antes de aplicar cualquier modificación, la IA debe inspeccionar el repositorio y responder estas preguntas:

### A. ¿Qué empaquetador y entorno se utiliza?
- Inspeccionar `package.json` para verificar si el proyecto usa Vite (`vite`), Next.js o Create React App.
- Verificar si existe `vite-plugin-pwa` o si hay un Service Worker registrado.

### B. ¿Qué servidor web atiende las solicitudes en producción?
- **Apache / cPanel:** Buscar archivo `public/.htaccess` o raíz `.htaccess`.
- **Nginx:** Revisar archivos de configuración de sitios (`default.conf`).
- **Hosting estático (Firebase / Netlify / Vercel):** Revisar `firebase.json` o `vercel.json` para cabeceras de caché.

### C. ¿Cuáles son los puntos de entrada principales?
- HTML base: `index.html`.
- Entrada de aplicación: `src/main.tsx` o `src/index.tsx`.
- Componente raíz: `src/App.tsx`.

---

## 3. Fase 2: Las 4 Capas de Blindaje Técnico Estándar

A continuación se detallan las 4 mejoras técnicas obligatorias. Se aplican exclusivamente en capas de infraestructura, arranque y servidor, garantizando **cero impacto** en cálculos, APIs o componentes comerciales.

---

### Capa 1: Auto-Recarga Silenciosa y Recuperación de Chunks (Frontend)

Se deben implementar dos mecanismos complementarios:

#### 1.1. Manejador Global de Eventos de Precarga (`vite:preloadError`)
Ubicación: `src/main.tsx`

Vite emite un evento nativo en la ventana (`window`) cuando un módulo dinámico falla al descargarse debido a un cambio de versión en producción. La IA debe interceptar este evento y recargar la aplicación de manera controlada con protección contra bucles infinitos:

```typescript
// Prevencion de bucles infinitos de recarga
const RELOAD_KEY = 'chaski_chunk_reload_timestamp';
const RELOAD_COOLDOWN = 10000; // 10 segundos

function triggerSafeReload() {
  const lastReload = sessionStorage.getItem(RELOAD_KEY);
  const now = Date.now();
  
  if (!lastReload || now - parseInt(lastReload, 10) > RELOAD_COOLDOWN) {
    sessionStorage.setItem(RELOAD_KEY, now.toString());
    window.location.reload();
  }
}

// Interceptor global nativo de Vite
window.addEventListener('vite:preloadError', (event) => {
  event.preventDefault();
  triggerSafeReload();
});
```

#### 1.2. Envoltorio `lazyWithRetry` para Carga Perezosa
Ubicación: `src/App.tsx` o módulo de utilidades de rutas.

Para cualquier componente que se importe mediante `React.lazy()`, debe usarse un envoltorio que intente una recarga forzada limpia si la promesa de importación es rechazada:

```typescript
import { lazy, type ComponentType } from 'react';

export function lazyWithRetry<T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T } | any>
) {
  return lazy(async () => {
    const pageKey = 'chunk_reload_' + window.location.pathname;
    const hasAlreadyRefreshed = sessionStorage.getItem(pageKey);

    try {
      const component = await componentImport();
      sessionStorage.removeItem(pageKey);
      return component.default ? component : { default: component };
    } catch (error) {
      if (!hasAlreadyRefreshed) {
        sessionStorage.setItem(pageKey, 'true');
        window.location.reload();
      }
      throw error;
    }
  });
}
```

---

### Capa 2: Directivas HTTP de Caché en Servidor (`.htaccess` / Nginx)

El servidor debe configurarse con una política de caché binaria estricta:

- **Archivos maestros de enrutamiento:** NUNCA almacenar en caché (`no-cache, no-store, must-revalidate`). Esto incluye `index.html`, `sw.js`, `workbox-*.js` y manifiestos web.
- **Archivos versionados con hash:** Caché permanente e inmutable a 1 año (`max-age=31536000, immutable`). Dado que su contenido cambia de nombre con cada build, el navegador nunca descargará un archivo viejo por error.
- **Respuesta 404 real en `/assets/`:** No reescribir peticiones fallidas a `/assets/` hacia `index.html`. Si un script viejo no existe, el servidor debe responder 404 para que el frontend dispare de inmediato la recarga inteligente.

#### Configuración de referencia para Apache (`public/.htaccess`):

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  # Evita que assets no encontrados devuelvan index.html con status 200 (evita SyntaxError)
  RewriteCond %{REQUEST_URI} !^/assets/
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>

# Cache inmutable a largo plazo para assets versionados
<IfModule mod_headers.c>
  <FilesMatch "\.(js|css|webp|png|jpg|jpeg|svg|woff2?)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>

# Cero cache para archivos de version y Service Worker
<IfModule mod_headers.c>
  <FilesMatch "(sw\.js|workbox-.*\.js|index\.html|manifest\.webmanifest)$">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
    Header set Pragma "no-cache"
    Header set Expires "0"
  </FilesMatch>
</IfModule>
```

---

### Capa 3: Persistencia Offline de Imágenes en PWA (Workbox CacheFirst)

Cuando se utiliza `vite-plugin-pwa`, la IA debe configurar Workbox en `vite.config.ts` para que todos los activos estáticos y gráficos queden guardados en el almacenamiento persistente del dispositivo:

#### Configuración en `vite.config.ts`:

```typescript
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
        // Incluir todos los formatos de imagen y activos estaticos en el precaching
        globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,webmanifest}'],
        runtimeCaching: [
          {
            // Estrategia CacheFirst para imagenes locales
            urlPattern: /\.(?:png|jpg|jpeg|svg|webp)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'images-cache-v1',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 30 * 24 * 60 * 60 // 30 dias
              }
            }
          }
        ]
      }
    })
  ]
});
```

**Resultado:** Aunque el usuario abra la aplicación en el subterráneo, en modo avión o tras haber tenido el dispositivo inactivo por días, las imágenes, logotipos y fondos cargan de forma instantánea directamente desde el disco sin provocar pantallas vacías.

---

### Capa 4: Splash Loader Liviano en el HTML Inicial (`index.html`)

En lugar de dejar `<div id="root"></div>` vacío, la IA debe incorporar un cargador ultraligero compuesto exclusivamente por HTML y CSS inline dentro del contenedor raíz:

```html
<div id="root">
  <div style="
    position: fixed;
    inset: 0;
    background-color: #335C7A;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    z-index: 9999;
  ">
    <img 
      src="/logo.webp" 
      alt="Cargando..." 
      style="height: 56px; margin-bottom: 20px; object-fit: contain;" 
    />
    <div style="display: flex; gap: 8px;">
      <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #ffffff; opacity: 0.6; animation: bounce 0.6s infinite alternate ease-in-out;"></div>
      <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #ffffff; opacity: 0.6; animation: bounce 0.6s infinite 0.2s alternate ease-in-out;"></div>
      <div style="width: 8px; height: 8px; border-radius: 50%; background-color: #ffffff; opacity: 0.6; animation: bounce 0.6s infinite 0.4s alternate ease-in-out;"></div>
    </div>
  </div>
</div>
```

**Beneficios:**
- **0ms de pantalla blanca:** Se muestra de inmediato apenas el navegador descarga el HTML base (generalmente en menos de 50ms).
- **Sustitución atómica:** En cuanto React monta la aplicación (`createRoot().render()`), reemplaza por completo el contenido de `<div id="root">`, logrando una transición visual impecable.
- **Cero consumo de recursos:** Al ser CSS puro, no bloquea el hilo de ejecución principal ni compite con la inicialización de los scripts.

---

## 4. Fase 3: Protocolo de Verificación Obligatorio para la IA

Antes de considerar concluida la tarea, la IA debe validar que las protecciones funcionan mediante este checklist:

1. **Compilación Limpia:**
   - Ejecutar `tsc -b` (o linter de TypeScript) sin errores de tipos.
   - Ejecutar el build de producción (`pnpm build` o `npm run build`).

2. **Auditoría de Artefactos en `dist/`:**
   - Verificar que `dist/index.html` contiene el Splash Loader dentro de `<div id="root">`.
   - Verificar que `dist/sw.js` y `dist/workbox-*.js` fueron generados con éxito.
   - Verificar que los archivos estáticos en `dist/assets/` poseen nombres versionados con hash.

3. **Verificación de Reglas del Servidor:**
   - Confirmar que `public/.htaccess` contiene las directivas `no-cache` para `index.html` y `sw.js`.
   - Confirmar que existe la regla `RewriteCond %{REQUEST_URI} !^/assets/` para prevenir SyntaxError 200 en scripts inexistentes.

4. **Ejecución de Suite de Pruebas:**
   - Correr las pruebas automatizadas del proyecto (`pnpm test`). Todas las pruebas de integridad y fórmulas comerciales deben aprobar al 100%.

---

## 5. Resumen de Garantías Técnicas

Al aplicar este protocolo estándar:
- Se elimina al 100% el problema de pantallas blancas tras nuevas publicaciones.
- Se asegura la disponibilidad permanente de imágenes y recursos gráficos sin conexión.
- Se optimiza el tiempo de arranque percibido por el usuario en dispositivos móviles.
- Se preserva de forma estricta e inviolable toda la lógica de negocio y cálculo matemático del sistema.
