# Estándar de Modales y Prohibición de Ventanas Nativas (Zero Native Dialogs)

Este documento establece la normativa técnica y de experiencia de usuario sobre la **eliminación total y prohibición estricta de ventanas o diálogos nativos del navegador** en todo el frontend de Chaski Agenda.

---

## 🚫 Regla de Oro: Cero Ventanas Nativas

Bajo ninguna circunstancia se permite el uso de diálogos nativos del navegador en código de producción:

```typescript
// ❌ ESTRICTAMENTE PROHIBIDO (Rompe la PWA, tema oscuro y bloquea JS)
window.alert("Datos guardados con éxito");
window.confirm("¿Está seguro de eliminar este registro?");
window.prompt("Ingrese su nueva contraseña:");
window.open("https://...");
<dialog open>...</dialog>
```

### ¿Por qué están prohibidos los diálogos nativos?
1. **Bloqueo del Event Loop:** `alert()`, `confirm()` y `prompt()` son síncronos y congelan por completo el hilo principal de renderizado de React, animaciones y conexiones WebSocket/Firebase en tiempo real.
2. **Incompatibilidad Estética y de Temas:** Muestran cajas grises por defecto del sistema operativo que no respetan el tema oscuro (`[data-theme="dark"]`), tipografías (`Inter`) ni los tokens CSS corporativos.
3. **Pésima Experiencia en PWA y Móviles:** En dispositivos móviles y bajo modo PWA instalada, estos cuadros se desbordan o desorientan al usuario, perdiendo la sensación de aplicación nativa.

---

## 🏛️ Catálogo de Alternativas Corporativas Estandarizadas

Cualquier interacción de alerta, confirmación o ingreso de datos debe usar exclusivamente el catálogo de componentes en `src/components/modal/`:

| Necesidad | Componente Oficial | Archivo | Características |
|---|---|---|---|
| **Confirmación de acción simple** | `<ConfirmModal />` | [`ConfirmModal.tsx`](file:///d:/ChaskiProduc/Agenda/src/components/modal/ConfirmModal.tsx) | Variantes `primary` y `error`, botón con `isLoading`, `backdrop blur`, cierre con `ESC`. |
| **Acción destructiva crítica** | `<DeleteUserModal />` | [`DeleteUserModal.tsx`](file:///d:/ChaskiProduc/Agenda/src/components/modal/DeleteUserModal.tsx) | Píldora de usuario, validación de contraseña de administrador, input con toggle de visibilidad. |
| **Mensajes de éxito o aviso** | `toast.success()` / `toast.error()` | `react-hot-toast` | Notificación flotante suave, auto-dismiss en 3-4s, adaptada al modo oscuro/claro. |
| **Formularios densos / Edición** | `<SlideOver />` | [`SlideOver.tsx`](file:///d:/ChaskiProduc/Agenda/src/components/modal/SlideOver.tsx) | Panel lateral deslizante que no pierde el contexto de la cuadrícula o agenda. |
| **Ventanas emergentes complejas** | `<Modal />` | [`Modal.tsx`](file:///d:/ChaskiProduc/Agenda/src/components/modal/Modal.tsx) | Contenedor base accesible con soporte para loader global superpuesto. |

---

## 💻 Patrones de Uso y Ejemplos

### 1. Reemplazo de `window.confirm` por `ConfirmModal`

#### ❌ Código Antiguo (Prohibido):
```typescript
const handleDelete = async () => {
  if (window.confirm("¿Seguro que deseas eliminar esta gestión?")) {
    await deleteEvent(id);
  }
};
```

#### ✅ Código Estandarizado (Correcto):
```tsx
import React, { useState } from 'react';
import { ConfirmModal } from '../components/modal/ConfirmModal';
import toast from 'react-hot-toast';

export const EventItem = ({ eventId, onDelete }) => {
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(eventId);
      toast.success("Gestión eliminada correctamente");
      setIsConfirmOpen(false);
    } catch (error) {
      toast.error("Ocurrió un error al eliminar la gestión");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <button onClick={() => setIsConfirmOpen(true)}>Eliminar</button>

      <ConfirmModal
        isOpen={isConfirmOpen}
        title="¿Eliminar esta gestión?"
        message="Esta acción no se puede deshacer y retirará el evento del calendario."
        confirmText="Sí, eliminar"
        cancelText="Cancelar"
        variant="error"
        isLoading={isDeleting}
        onConfirm={handleConfirmDelete}
        onCancel={() => setIsConfirmOpen(false)}
      />
    </>
  );
};
```

---

### 2. Reemplazo de `window.alert` por Toasts Corporativos

#### ❌ Código Antiguo (Prohibido):
```typescript
window.alert("La agenda semanal ha sido enviada a gerencia.");
```

#### ✅ Código Estandarizado (Correcto):
```typescript
import toast from 'react-hot-toast';

// Para éxito:
toast.success("Agenda enviada exitosamente con copia a supervisión");

// Para error:
toast.error("No se pudo conectar con el servidor de correo");
```

---

## 🛡️ Blindaje y Verificación Automatizada en CI/CD

Para asegurar que ningún desarrollador ni agente IA reintroduzca ventanas nativas en el futuro, el proyecto cuenta con una prueba automatizada en [`scripts/test_modular_integrity.mjs`](file:///d:/ChaskiProduc/Agenda/scripts/test_modular_integrity.mjs):

```javascript
// Test 6: Auditoría de Incoherencias Frontend
const allTsx = getAllSourceFiles('src', ['.ts', '.tsx']);
let foundDialogs = 0;

allTsx.forEach(f => {
  if (f.includes('usePWAInstall.ts')) return; // Excepción para la API PWA del navegador
  const content = fs.readFileSync(f, 'utf8');
  const lines = content.split('\n');
  lines.forEach((line) => {
    if (line.trim().startsWith('//') || line.trim().startsWith('*')) return;
    if (/\b(window\.)?(alert|confirm|prompt)\s*\(/.test(line)) {
      foundDialogs++;
    }
  });
});

assert(foundDialogs === 0, 'Cero diálogos nativos del navegador (window.alert/confirm/prompt)');
```

### Cómo ejecutar la verificación:
```bash
pnpm test
```
Si se detecta cualquier diálogo nativo, la suite de pruebas fallará inmediatamente impidiendo empaquetar o desplegar la versión.
