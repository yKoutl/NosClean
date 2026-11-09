# Configuración y Exclusión de Cuentas de Soporte (Ángel Cruz)

## 1. Contexto y Propósito
El usuario **Ángel Cruz** (`acruz@chaski.com.pe` / DNI: `71218311` / UID: `rFfZngdZn2NrYMEx2zpGxxSIO9E2`) es una cuenta utilizada para soporte técnico, automatización y pruebas de desarrollo.

Para evitar que los eventos de prueba ingresados por esta cuenta distorsionen las metas comerciales reales del equipo (por ejemplo, en la Semana 43 donde existían 10 eventos de prueba de Ángel Cruz pero ningún comercial había registrado gestiones), el sistema cuenta con una **exclusión centralizada y configurable**.

---

## 2. Archivo de Configuración
La configuración se encuentra en:
📁 [`src/config/dashboardConfig.ts`](file:///d:/ChaskiProduc/Agenda/src/config/dashboardConfig.ts)

```typescript
export const DASHBOARD_CONFIG = {
  /**
   * EXCLUIR_SOPORTE_EN_DASHBOARD:
   * - true (Por defecto / Producción): Excluye a Ángel Cruz de la vista general "Todos los Ejecutivos".
   * - false (Modo pruebas): Incluye a Ángel Cruz en todas las sumas globales.
   */
  EXCLUIR_SOPORTE_EN_DASHBOARD: true,
};
```

---

## 3. Comportamiento Inteligente

1. **Con `EXCLUIR_SOPORTE_EN_DASHBOARD: true` (Modo Recomendado):**
   - **En vista global ("Todos los Ejecutivos"):** El Dashboard filtra los eventos comerciales reales. En la tarjeta de cobertura y en el modal saldrá exactamente la actividad de los ejecutivos oficiales (0 en Semana 43).
   - **En selección directa ("3. EJECUTIVO" -> Ángel Cruz):** Si el usuario o administrador selecciona específicamente a **Angel C** en el selector de ejecutivos, el Dashboard **sí muestra sus eventos** para permitir probar todas las funcionalidades y el modal con sus datos en cualquier momento.

2. **Con `EXCLUIR_SOPORTE_EN_DASHBOARD: false` (Modo Pruebas Global):**
   - Las 10 gestiones de Ángel Cruz se sumarán en la tarjeta global de cobertura y en la modal incluso al seleccionar "Todos los Ejecutivos".

---

## 4. Archivos Involucrados
- [`src/config/dashboardConfig.ts`](file:///d:/ChaskiProduc/Agenda/src/config/dashboardConfig.ts): Interruptor principal de configuración.
- [`src/pages/DashboardPage.tsx`](file:///d:/ChaskiProduc/Agenda/src/pages/DashboardPage.tsx): Filtro de eventos para tarjetas y métricas de cobertura.
- [`src/components/modal/GestionesDetailModal.tsx`](file:///d:/ChaskiProduc/Agenda/src/components/modal/GestionesDetailModal.tsx): Visualización de acordeón y desglose por asesor y territorio.
