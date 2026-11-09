# Componentes UI y Reutilización (Modales y SlideOvers)

## ¿Son reutilizables en otros proyectos?
**Absolutamente SÍ.** 
Todo el sistema gráfico fue programado siguiendo el principio de "Componentes Tontos" (Dumb Components). 
Al utilizar **CSS Modules** (`.module.css`), los componentes no tienen dependencias de librerías gigantescas como Tailwind, Bootstrap o Material-UI. 

Si mañana inicias un nuevo proyecto en React, puedes literalmente copiar la carpeta `src/components/modal` o `src/components/buttons`, pegarla en tu nuevo proyecto, y funcionarán de inmediato manteniendo su diseño intacto. Son piezas de Lego universales.

---

## 1. Modales de Información (`Modal.tsx`)
Son los recuadros clásicos que aparecen en el centro de la pantalla. Se usan para **alertas críticas, confirmaciones de borrado o mensajes de error cortos**.

**Características Técnicas:**
* **Backdrop Flotante:** Tienen un div transparente gris por detrás (`backdrop`) que oscurece la pantalla principal y bloquea los clics para que el usuario no pueda hacer nada más hasta responder.
* **Cierre Automático:** Si el usuario hace clic fuera del recuadro blanco (en lo oscuro), el modal se cierra solo.
* **Estructura Flexible (`children`):** No están fijos a un solo texto. Puedes inyectarles cualquier cosa adentro (un formulario de cambio de clave, una tabla pequeña, o simplemente un botón de "Aceptar").

**Ejemplo de uso en código:**
```tsx
<Modal isOpen={mostrar} onClose={() => setMostrar(false)} title="¡Advertencia!">
   <p>¿Estás seguro que deseas borrar este registro?</p>
   <Button onClick={borrar}>Sí, borrar</Button>
</Modal>
```

---

## 2. Modales Laterales (`SlideOver.tsx`)
Son los paneles grandes que se deslizan suavemente desde la derecha de la pantalla. Se diseñaron para **formularios complejos, edición de datos o lectura de historiales largos** (Ej: Editar Operario, Ver Auditoría).

**¿Por qué usar SlideOvers en lugar de Modales clásicos?**
* **Experiencia de Usuario (UX):** Los modales centrales no son buenos para llenar formularios largos porque tapan todo. El `SlideOver` se abre a un lado, permitiendo al operario seguir viendo la tabla original de fondo por si necesita consultar un dato antes de editar.
* **Diseño Responsivo:** En computadoras ocupan el 30% derecho de la pantalla, pero si lo abres en un celular, inteligentemente toman el 100% del ancho de la pantalla, convirtiéndose en una "nueva vista" deslizable.

**Características Técnicas:**
* **Animación CSS fluida:** Usan `transform: translateX(100%)` a `translateX(0)` junto con `transition: transform 0.3s ease-in-out` para dar el efecto de deslizarse hacia adentro y hacia afuera de forma corporativa.
* **Scroll Interno:** Si el formulario es inmenso, solo el interior del SlideOver hará scroll, manteniendo el botón de "Cerrar (X)" siempre visible en la parte superior.

---

## Conclusión Arquitectónica
Al no amarrar la base de datos (Firebase) directamente dentro de la carpeta `components/`, te aseguras de que el diseño gráfico de tu empresa (`Chaski UI`) sea un "paquete" totalmente independiente que puede ser clonado y reutilizado en futuras aplicaciones web que la empresa necesite crear.
