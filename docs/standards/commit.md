Guía General para Escribir Commits
Principios
Un commit debe:
- en español
- Explicar qué cambió.
- Ser corto y claro.
- Representar una sola intención.
- Poder entenderse meses después.
Formato recomendado
[VERBO] + [OBJETO]
Verbos recomendados
- Nuevas funcionalidades: Agrega, Implementa, Integra, Crea
- Corrección de errores: Corrige, Soluciona, Ajusta
- Mejoras: Mejora, Optimiza, Refactoriza
- Cambios de estructura: Actualiza, Reorganiza, Renombra
- Eliminaciones: Elimina, Remueve, Depura
Ejemplos Correctos:
Agrega exportacion a Excel
Corrige validacion de stock
Implementa seguimiento de pedidos
Regla práctica: Si alguien lee únicamente el historial de Git, debe entender el proyecto.
### Commits de Agenda
Verifica envio formal de agenda en base de datos para reporte de planificacion
Estandariza columnas de unidad y zona en reporte semanal de planificacion
Separa columnas de unidad y zona con agrupacion compacta en reporte semanal de gestion
Desglosa gestion realizada por unidad y zona en correo semanal para supervisores
Discrimina cotizaciones por unidad de negocio en tabla de conciliacion y auditoria
Agrega separador en Sidebar, colores dinámicos en formulario de gestión y resaltado de día actual en DatePicker
Actualiza texto de correo de recordatorio diario con día de la semana dinámico y saludo personalizado
Mejora sombreado interactivo de semana seleccionada en calendario respetando estados de hover
Corrige filtro de ejecutivos y zonas respetando el tipo de venta en el calendario
Agrega estilos y colores a tarjetas de eventos de categoría Operativo (Ferias, Despachos, Otros)
Corrige marcado de ruta activa en Sidebar leyendo zona desde los parámetros de URL
Mantiene persistencia de zona en la URL al alternar vistas en el calendario (Día, Semana, Mes)
Ajusta título dinámico en tarjetas de eventos para exhibir la categoría si no requiere cliente
Corrige altura de las tarjetas de evento para ajustarse proporcionalmente a su duración visual
Oculta opción de exportar a Excel en el calendario para usuarios ejecutivos
Corrige bug visual de hover en componente Select cuando se encuentra deshabilitado
Implementa renderizado dinámico de DatePicker según la vista activa (Día, Semana, Mes) en la agenda
Reemplaza selectores estáticos por DatePicker y WeekPicker en el Dashboard de Gerencia
Agrega estilos CSS globales para maximizar tamaño y diseño de la ventana de selección de Mes/Año
Reemplaza emojis por íconos SVG profesionales de Lucide en el ranking de Top Vendedores y Clientes
Corrige bug de filtros en la agenda para resetear dependencias al cambiar de Unidad o Zona
Implementa estado de carga (loading) interactivo en la agenda durante la actualización de datos
Añade overlay de desenfoque en el Dashboard General para transiciones fluidas sin saltos de altura
Ejecuta limpieza de base de datos Firebase para estandarizar nombres de usuarios sin etiquetas de roles
Agrega estilos CSS de scrollbar global y efectos de hover mejorados para los componentes Select
Añade toggle de roles (Ejecutivos/Técnicos) en el Dashboard de Gerencia para optimizar espacio
Corrige bug en el sistema de rutas del calendario para mantener contexto de unidad al alternar vistas
Añade selectores de rango de fechas libres en el Dashboard General y remueve gráfico de embudo
Depura importaciones sin uso y reestructura componentes para asegurar compilación limpia en TypeScript
Refactoriza diseño de KPIs en Dashboard con barras de progreso y colores temáticos por métrica
Implementa gráfico de embudo basado en clip-path CSS puro para prevenir colapso con valores nulos
Optimiza ranking de clientes y vendedores filtrando guiones y usuarios sin nombre
Actualiza diseño de etiquetas de unidad en tabla de metas utilizando bordes y colores sutiles
Ajusta tipografía de la Nota de Gestión en generación de reportes PDF
Implementa pantalla de carga interactiva en modales de gestión y reemplaza emojis por íconos SVG
Corrige agrupacion de vendedores por DNI y UID e implementa nuevo diseño de ranking
Corrige filtro de eventos en Dashboard para matchear DNI, UID y zona normalizada
Agrega enlace de Dashboard General en menu lateral para ejecutivos
Implementa modulo de mantenimiento y cierre mensual de agenda con respaldo excel e inmutabilidad
Unifica boton de envio de agenda y viaticos con modal consolidado, corrige seleccion multiple en Sidebar y estandariza nomenclatura PDF
Implementa catalogo global de destinatarios de notificacion con seleccion por checks, autenticacion SMTP individual blindada en servidor, reactiva ezeballos y actualiza a v1.0.56
Integra Manual Operativo PDF oficial con capturas en alta resolucion, reestructura descarga en perfil con marco responsivo, depura archivos temporales y actualiza a v1.0.58
Optimiza formato de reporte PDF con leyenda de cotizaciones y tarjeta ejecutiva de viáticos por día, estandariza tarjetas de métricas en correo Outlook y actualiza a v1.0.59
Estandariza modales y estados de carga con GlobalLoader y ConfirmModal, reemplaza diálogos nativos y botones inline, depura archivos huérfanos de viáticos y actualiza a v1.0.60
Modulariza componentes de viaticos y usuarios, simplifica filtros de vendedor, habilita navegacion a agenda con viaticos y actualiza a v1.0.61
Corrige inconsistencias de frontend segun Guia IA, implementa cierre de sesion suave, sincroniza perfil en vivo sin desconexion y empaqueta v1.0.61
Implementa blindaje PWA anti-pantalla blanca con recarga dinámica, soluciona persistencia y distribución de metas, estandariza diseño corporativo y empaqueta v1.0.67
Corrige flujo de CI en GitHub Actions reemplazando npm ci por pnpm y pnpm-lock.yaml
Implementa cálculo de porcentaje real en metas sin tope de 100%, agrega frases motivacionales dinámicas y empaqueta v1.0.68
Corrige renderizado de tarjetas KPI en plantilla de correo PHP de cPanel y empaqueta v1.0.69
Corrige solapamiento de textos de viáticos y nota de gestión en reporte PDF y empaqueta v1.0.70
Deshabilita guardar cambios sin edicion en formulario de gestion, aisla cruce por ejecutivo y empaqueta v1.0.71
Implementa exportacion de Matriz Semanal PDF consolidada para administracion y supervision, optimiza componentes Select y empaqueta v1.0.72
Implementa tablero semaforo de cumplimiento semanal para gerencia y supervision, incorpora sistema de alerta preventiva para ejecutivos y empaqueta v1.0.73
Estandariza tablero de cumplimiento y alertas al sistema de diseno Chaski UI con CSS Modules, Table y Modal canonicos
Remueve pestana de cumplimiento en panel de administracion y centraliza acceso exclusivamente en el sidebar
Simplifica etiquetas de alternancia de modo en tablero de cumplimiento a Corte Viernes y Semana Única
Optimiza velocidad de modal de envío e integra indicadores de semana actual y planificación en cabecera de agenda
Implementa check de confirmación de gestión cumplida e indicador de visto celeste en tarjetas de agenda
Mejora visibilidad del visto celeste en tarjeta de evento y estandariza tarjeta de cotización con color diferencial
Mejora visibilidad del botón de viáticos en cabecera de días con ícono de billete y resalte amarillo
Actualiza botón de viáticos a signo de dólar sin texto con estilo verde limón tipo amarillo
Reduce tamaño de botón de viáticos y círculo de fecha en cabecera para evitar solapamiento
Corrige duplicidad de moneda mostrando solo el monto registrado sin el signo de dólar
Restaura flujo original simple de envío de agenda semanal conservando mejoras visuales y funcionales
Implementa bloqueo visual con patrón de rayadas y toast para horarios ocupados en otras agendas
Agrega navegación directa 'Ir a la agenda' en notificación y bloque de horario ocupado
Ajusta diseño de horario ocupado con estilo difuminado y texto discreto Ocupado
Optimiza visibilidad de franjas y texto con rango horario en bloqueo de agenda
Filtra opciones de hora de fin para mostrar solo horarios posteriores al inicio en formulario de gestión
Agrega métrica de Actividades Confirmadas en cabecera y deshabilita horas ocupadas en selector de inicio
Mantiene solo la hora en opciones deshabilitadas con color diferencial en selectores de tiempo
Optimiza tamaño compacto de selectores de hora, corrige desbordamiento y remueve límite de 50 opciones
Permite seleccionar la hora de inicio de una gestión posterior como hora de fin contigua
Calcula automáticamente la hora de fin a 1 hora de diferencia por defecto según disponibilidad
Remueve tarjeta de métrica de Actividades Confirmadas conservando el indicador de check en tarjetas
Muestra tarjeta de actividades confirmadas con ícono de doble check y cantidad numérica sin texto extenso
Implementa cabecera plegable tipo acordeón para maximizar el espacio del calendario
Filtra el embudo de ventas para contabilizar únicamente las actividades realizadas
Calcula contactos realizados en meta de cobertura contabilizando únicamente actividades confirmadas
Filtra rankings de vendedores y clientes para contabilizar únicamente actividades realizadas
Optimiza diseño responsivo de cabecera de agenda en móviles con contracción compacta y botones adaptativos
Separa resumen en dos renglones en móvil para evitar recortes y ajusta espacios laterales en modal de gestión
Optimiza diseño responsivo integral de modales, reactividad de viáticos en móvil y flujo de clientes
Agrega seccion de cambio de contrasena en Mi Perfil con validaciones y reautenticacion
Actualiza documentacion de versiones en guia cPanel y empaquetador v1.0.74
Restablece cuentas de ejecutivos para primer ingreso e implementa empaquetado v1.0.75
Actualiza data embudo comercial a 20/10/2026 y documenta registro historico
Sincroniza y estandariza asignaciones de zonas canonicas, boton de actualizacion y reactividad en tiempo real en Administracion
Implementa contador de cotizaciones en cabecera de agenda y reemplaza borde de tarjetas por distintivo C superior
Actualiza tipo de contacto Correo a Correo / Mensajes en formularios leyendas y reportes
Corrige visibilidad de actividades en agenda unificando comparacion canonica de zonas y migra eventos a ICA / ARE
Actualiza color de actividad Reunion a Naranja Fuego y optimiza prominencia del distintivo C de cotizaciones
Convierte logo de Agro Retail a WebP e implementa selector corporativo de empresa en formulario de gestion
Mejora contraste y resaltado visual con distintivo de seleccion activa en selector de empresa
Simplifica etiqueta de selector de empresa removiendo subtitulo dinamico
Reubica indicador de cotizacion como texto C junto al tipo de actividad abajo eliminando distintivo circular superior
Ajusta indicador circular de cotizacion con diseno minimalista C fina sin sombra ni borde grueso en esquina superior
Ubica distintivo circular de cotizacion al costado del texto de actividad y remueve brillo y sombras en KPIs superiores
Optimiza diseno responsivo de embudo de ventas con clip-path suave y tipografia fluida para dispositivos moviles
Estandariza tipo de contacto a Llamada / WhatsApp y restablece opcion Correo en formularios y reportes
Refuerza adaptabilidad responsiva con tipografia fluida y truncado eliptico en botones y tarjetas
Implementa filtro por empresa (Chaski MAP / Agro Retail AGR) en dashboards, actualiza embudo comercial al 21/10/2026 y empaqueta v1.0.76
Reubica filtro de empresa superior como selector segmentado TODAS / MAP / AGR y restaura posiciones originales 1 al 5
Sincroniza empresa en mapeo de gestiones para embudo comercial, simplifica etiqueta a Llamada en tarjetas y leyendas, y reubica indicador C junto a doble check
Actualiza embudo comercial completo con 563 registros (MAP y AGR) hasta semana 43 y sincroniza en Firestore
Actualiza color de actividad Reunion a Rojo Vino, restablece cuentas de prueba a estado inicial y empaqueta version 1.0.79
Corrige filtro de cotizaciones con agenda, leyenda e iconos de realizada y cotizada en PDF
Implementa boton e indicador PWA en Perfil y condiciona exportacion de Agenda PDF a filtro de vendedor
Elimina trampa de doble validacion de claves en login, agrega reautenticacion y centra modales con portal al body
Habilita permiso de actualizacion propia en reglas Firestore, implementa lectura directa desde servidor y depura cuentas de prueba
Oculta ojo nativo del navegador en inputs, agrega boton de cancelar en modal de login y remueve auto-aprovisionamiento fantasma
Corrige doble ojo en modal de cambio forzoso y agrega boton de cancelacion con cierre de sesion
Blindaje de flujo de autenticacion, reautenticacion en perfil y proteccion con exists en reglas firestore
Restaura tarjeta de instalacion PWA y remueve boton redundante en perfil
Actualiza documentacion en guia cPanel, version 1.0.85 y empaquetador oficial
Soluciona cambio de estado y desactivacion de usuarios soportando DNI y UID
Elimina cierre de sesion forzoso en ForceChangePasswordModal permitiendo ingreso directo
Implementa eliminacion definitiva de usuarios con confirmacion de contrasena del administrador
Integra distintivo de empresa tuerquita de Chaski y manzana de Agro Retail en tarjetas de eventos y vistas de calendario
Ajusta color y proporcion de logos de empresa, rediseña modal de eliminacion y optimiza cuadricula del reporte PDF
Restaura espaciado holgado en reporte PDF y agrega linea separadora inferior sutil en recuadros de eventos
Implementa modal dinamico de confirmacion de estado de usuario con bloqueo de concurrencia y empaqueta version 1.0.90
Integra embudos comerciales individuales y global en Matriz Semanal PDF con gestiones confirmadas, montos USD y panel de conclusiones
Adapta distribucion vertical de cantidad y monto en embudos para prevenir desbordes de cifras extensas
Implementa automatizacion de reportes semanales por correo con GitHub Actions y modal de detalle de gestiones en dashboard
Corrige interface BuildWeeklyMatrixOptions con propiedad opcional includeFunnels para build de CalendarPage
Restaura diseno visual original de tarjetas en anexo de Viaticos y Rutas del reporte semanal
Corrige identificacion de asesor continuado en matriz semanal, margen de salto de linea y omision de anexo con cero viaticos
Implementa distribucion dinamica de asesores con ruta y adapta escala en asesores sin viaticos
Remueve seccion redundante de asesores sin viaticos en anexo y dedica espacio a asesores con ruta
Lee asignaciones operativas oficiales de usuarios para unidad y zona en reporte semanal
Sincroniza diseno y logica de matriz semanal PDF web con reporte oficial de correos
Implementa plantillas oficiales de correos de recordatorio de planificacion para jueves y viernes
Implementa motor automatizado de recordatorios semanales y persistencia de envio formal de agendas
Actualiza documentacion en guia cPanel, version 1.0.91 y empaqueta paquete oficial tar.gz
Actualiza datos consolidados de embudo comercial al 28 de octubre en Firestore
Implementa modal de control semanal de cumplimiento y boton de ayuda en cabecera de agenda
Ajusta boton de control semanal a solo icono y corrige lectura de actividades y estado de envio en modal
Optimiza carga de KPIs en modal de cumplimiento semanal y muestra marcas de tiempo reales
Abre ciclo de version 1.0.92 en desarrollo e implementa guia oficial de gestion y empaquetado de versiones
Implementa diseno responsivo para moviles y tablets en modal de control semanal de cumplimiento
Unifica zonas Lima y Ancash en territorio canonico LIMA / ANCASH en base de datos y aplicacion
Implementa sistema de auto-actualizacion transparente para cPanel con purga de cache y modal oficial Chaski
Cierra ciclo de version 1.0.92, actualiza guia de despliegue cPanel y empaqueta paquete oficial tar.gz
Ajusta reglas de Firestore para persistencia de estado de agendas y adelanta horario de recordatorios a 5:00 AM
Normaliza zonas en selector de Dashboard unificando Ancash en LIMA / ANCASH
Estandariza comparacion de zonas en metricas de dashboard y tabla de clientes
Implementa precalentamiento a las 11:45 AM en reporte semanal con envio exacto al mediodia
Optimiza diseno flexible en tarjetas de viaticos con ancho panoramico para 1 y 2 asesores
Cierra ciclo de version 1.0.93, actualiza guia de despliegue cPanel y empaqueta paquete oficial tar.gz
Abre ciclo de version 1.0.94 en desarrollo
Actualiza horario de precalentamiento a las 12:30 PM y despacho a la 1:00 PM en reportes y recordatorios
Reemplaza __dirname por import.meta.dirname en vite.config.ts para estandar ESM nativo
Deduplica y normaliza zonas de asesores en modal de control semanal de cumplimiento
Estandariza deduplicacion y normalizacion de zonas en CalendarPage y CentralizedSendModal
Desactiva visualmente indicadores y pestañas de metas en Dashboard preservando logica interna
Alinea simetricamente tarjetas de KPIs en Dashboard con alturas y filas estandarizadas
Asegura resolucion de unidad asignada del ejecutivo en CalendarPage e inyecta gestiones a Postventa
Remueve filas secundarias del pie de tarjetas de KPIs en Dashboard
Cierra ciclo de version 1.0.94, actualiza guia de despliegue cPanel y empaqueta paquete oficial tar.gz
Abre ciclo de version 1.0.95 en desarrollo
Implementa precalentamiento a las 7:00 AM y soporte dry-run en reportes semanales
Agrega dependencia explicita @google-cloud/firestore y regla de hoisting en pnpm para GitHub Actions
Remueve workflow en desuso de despliegue a Firebase Hosting
Remueve recordatorios automáticos de los jueves conservando únicamente aviso de cierre de viernes
Restablece recordatorio preventivo de jueves 5:00 AM y elimina envio redundante de 11:30 AM
Implementa precalentamiento a las 6:30 AM y envio exacto a las 7:00 AM en recordatorios de jueves y viernes
Optimiza visualizacion de porcentajes en embudos eliminando textos redundantes y omitiendo ceros
Mantiene visible seccion de instalacion de aplicacion con estado activo y guia de instalacion en perfil
Sincroniza formato limpio de porcentajes en embudos de matriz semanal PDF web
Implementa bloqueo historico en agenda con vistas ejecutivas de consulta para gestiones y viaticos
Aplica bloqueo historico automatico en agenda a todos los asesores comerciales
Abre ciclo de version 1.0.98 en desarrollo
Permite configurar hora inicial de scroll en agenda desde el perfil del asesor
Optimiza selector de hora de inicio en perfil con diseno compacto y sin textos redundantes
Corrige referencia de scroll inicial conectando al contenedor de cuadricula
Restaura visibilidad de lineas divisorias horarias en modo noche
Abre ciclo de version 1.0.99 en desarrollo
Habilita disparador repository_dispatch para Google Cloud Scheduler en flujos de automatizacion
Soporta tipo de reporte opcional en payload de repository_dispatch para reportes corporativos
Excluye usuarios con estado inactivo de recordatorios, reportes y selectores de agenda
Incluye rol tecnico en flujos de recordatorios, reportes corporativos y matriz de agenda
Alinea calculo de productividad exclusivamente con datos oficiales de cotprod
Filtra estrictamente visitas presenciales en detalle de viaticos del reporte semanal
Corrige salto de pagina y cabeceras huerfanas en PDF de agenda
Empaqueta version 1.0.99 para produccion
Abre ciclo de version 1.0.100 en desarrollo
Implementa flujo dinamico de cierre semanal y gestion realizada
