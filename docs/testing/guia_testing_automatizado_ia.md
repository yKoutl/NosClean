# Guía Maestra de Testing Automatizado para Proyectos con Inteligencia Artificial

Este documento establece el protocolo estándar obligatorio para que cualquier Inteligencia Artificial (o desarrollador) audite, diseñe y ejecute pruebas automatizadas de integridad en cualquier proyecto de software, adaptándose dinámicamente a la naturaleza específica de cada repositorio antes de empaquetar o entregar cambios.

---

## 1. Principio Fundamental

> **Regla de Oro:** Ninguna tarea, refactorización o corrección se considera terminada si no pasa por una suite de pruebas automatizadas que valide que la lógica de negocio, la estructura de archivos y los artefactos de producción permanecen íntegros.

---

## 2. Fase 1: Identificación y Diagnóstico del Proyecto por la IA

Antes de escribir una sola prueba, la IA debe inspeccionar el repositorio y clasificarlo respondiendo estas 4 preguntas:

### A. ¿Qué tipo de arquitectura tiene el proyecto?
- **SPA (Single Page Application):** Vite + React, Vue, Svelte. Enfoque: Verificación de rutas, bundles de `dist/`, reactividad de estado y componentes.
- **SSR / Fullstack:** Next.js, Remix, Astro. Enfoque: Renderizado en servidor, endpoints de API, hidratación del cliente.
- **Backend / Microservicio:** Node.js Express, NestJS, PHP Laravel/scripts nativos. Enfoque: Contratos de endpoints, códigos de estado HTTP, conexiones a base de datos.
- **PWA (Progressive Web App):** Service Worker, `manifest.webmanifest`, precaching de assets sin conexión.

### B. ¿Cuál es el núcleo crítico de negocio (Core Business)?
Cada proyecto tiene una función vital que **nunca debe romperse**:
- **ReporteDash / Dashboards de Ventas:** Fórmulas financieras (PPTO, ventas base, porcentaje de cumplimiento, variación), cruce de archivos Excel y generación de reportes PDF.
- **Agenda / CRM:** Sincronización en tiempo real con Firestore, asignación de trabajadores por zona, control de cuotas y flujos de envío SMTP.
- **Met / Producción / OTs:** Estados del ciclo de vida de órdenes de trabajo, control de supervisores y operarios, validación de formularios de campo.
- **Rendiciones / Finanzas:** Cuadre de cajas chicas, sumatorias contables con impuestos y aprobaciones jerárquicas.
- **Firma Digital:** Integridad de documentos PDF, coordenadas de estampado y firmas biométricas.

### C. ¿Qué dependencias de compilación y empaquetado existen?
- Inspeccionar `package.json`: verificar gestor de paquetes (`pnpm`, `npm`, `yarn`), scripts existentes y TypeScript (`tsconfig.json`).

---

## 3. Fase 2: Arquitectura del Suite de Pruebas Ligero (Node.js Nativo)

Para garantizar que las pruebas se ejecuten de forma instantánea (en menos de 1 segundo) sin necesidad de instalar suites pesadas de cientos de megabytes (como Jest o Mocha), se utiliza un ejecutor nativo en Node.js ECMAScript Modules (`.mjs`) ubicado en:

```
scripts/test_modular_integrity.mjs
```

### Estructura en 5 Niveles de Validación Obligatorios

```
[TEST 1: Estructura de Archivos y Carpetas]
   ├── Verifica existencia física de módulos críticos y dependencias
   └── Valida que no se hayan borrado archivos esenciales durante refactorizaciones

[TEST 2: Integridad Modular, Fachadas y Retrocompatibilidad]
   ├── Verifica que los índices exporten las funciones públicas requeridas
   └── Valida alias retrocompatibles para evitar que componentes antiguos se rompan

[TEST 3: Artefactos de Compilación de Producción]
   ├── Verifica dist/index.html y títulos institucionales
   ├── Verifica generación de chunks JS y CSS en dist/assets/
   └── Valida manifiestos PWA y Service Workers

[TEST 4: Funciones Puras, Fórmulas y Lógica Matemática]
   ├── Formateo de moneda, porcentajes y redondeos
   ├── Pruebas con valores extremos (0, negativos, NaN, decimales largos)
   └── Fórmulas de cumplimiento y sumatorias acumuladas

[TEST 5: Reglas de Negocio Condicionales y Filtros de Interfaz]
   ├── Permisos por rol (ADMIN, SUPERVISOR, OPERARIO, VENDEDOR)
   ├── Restricciones de seguridad por zona o departamento
   └── Modos excluyentes de interfaz (ej. Unidades Equipos vs Post-Venta)
```

---

## 4. Fase 3: Plantilla Base para el Script de Pruebas (`scripts/test_modular_integrity.mjs`)

Copia y adapta esta estructura según el diagnóstico obtenido en la Fase 1:

```javascript
import fs from 'fs';
import path from 'path';

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  [PASS] ${message}`);
    passed++;
  } else {
    console.error(`  [FAIL] ${message}`);
    failed++;
  }
}

console.log('====================================================');
console.log(' INICIANDO SUITE DE TESTS AUTOMATIZADOS');
console.log('====================================================\n');

// 1. Verificación de archivos esenciales
console.log('Test 1: Estructura de archivos críticos...');
const requiredFiles = [
  'src/main.tsx',
  'src/App.tsx',
  'src/index.css'
];
requiredFiles.forEach(file => {
  assert(fs.existsSync(file), `Archivo existe: ${file}`);
});

// 2. Verificación de artefactos de compilación
console.log('\nTest 2: Verificación de compilación en dist/...');
if (fs.existsSync('dist')) {
  assert(fs.existsSync('dist/index.html'), 'dist/index.html generado correctamente');
} else {
  console.log('  [WARN] dist/ no existe aún. Ejecutar build primero.');
}

// 3. Verificación de fórmulas matemáticas y funciones puras
console.log('\nTest 3: Funciones puras y fórmulas...');
const formatPct = (val) => isNaN(val) ? '0%' : `${Math.round(val * 100)}%`;
assert(formatPct(0.854) === '85%', 'formatPct(0.854) redondea a 85%');
assert(formatPct(NaN) === '0%', 'formatPct(NaN) fallback seguro a 0%');

// Resumen final
console.log('\n====================================================');
console.log(` Total pruebas: ${passed + failed} | Aprobadas: ${passed} | Fallidas: ${failed}`);
console.log('====================================================');

if (failed > 0) {
  process.exit(1);
} else {
  console.log('\n TODAS LAS PRUEBAS PASARON EXITOSAMENTE!');
}
```

---

## 5. Fase 4: Integración en el Flujo de Trabajo del Proyecto

Para que el proyecto ejecute siempre las pruebas:

1. **Configurar en `package.json`:**
   ```json
   "scripts": {
     "test": "node scripts/test_modular_integrity.mjs",
     "build": "tsc -b && vite build"
   }
   ```

2. **Protocolo Obligatorio antes de cada Commit o Entrega:**
   - Paso 1: Ejecutar `pnpm tsc -b` (o `npm run build`) para verificar tipos.
   - Paso 2: Ejecutar `pnpm test` (o `npm test`) para verificar las 5 capas de integridad.
   - Paso 3: Solo si ambos comandos terminan con código de salida 0, se aprueba la versión.

---

## 6. Checklist de Validación para la IA

Antes de responder al usuario que un cambio está listo:
- [ ] ¿Identifiqué el Core de Negocio del proyecto antes de tocar el código?
- [ ] ¿El script `scripts/test_modular_integrity.mjs` cubre los módulos modificados?
- [ ] ¿Se agregaron pruebas para cualquier fórmula matemática o regla nueva?
- [ ] ¿Ejecuté `pnpm test` y el conteo de fallos fue 0?
- [ ] ¿Verifiqué que no existan errores de TypeScript con `tsc -b`?
