# Sistema-Gestion-Reservas-Turistico

Sistema Padre Gestion Reservas Turistico

Proyecto académico para la gestión de reservas y servicios turísticos.

## Categorías de parámetros

Se implementan las operaciones de consulta, creación y edición en las rutas
definidas por HU-01a:

- `GET /api/v1/parametros/categorias`: lista todas las categorías.
- `POST /api/v1/parametros/categorias`: crea una categoría.
- `PUT /api/v1/parametros/categorias/{id}`: edita el nombre y/o la descripción.

El cuerpo de creación es:

```json
{
  "clave": "TIPO_DOCUMENTO",
  "nombre": "Tipo de documento",
  "descripcion": "Documentos de identidad aceptados"
}
```

La clave admite únicamente mayúsculas, números y guion bajo, tiene un máximo
de 50 caracteres, es única sin distinguir mayúsculas y no puede modificarse
después de crear la categoría. El nombre es obligatorio y tiene un máximo de
100 caracteres. Las respuestas usan `mensaje`, `data` y `success`.

Los datos se guardan en memoria y se pierden al reiniciar la aplicación. Las
operaciones de escritura requieren el rol Administrador: se lee primero
`request.state.rol` y, mientras se integra la autenticación, se acepta
`X-Rol` (su valor predeterminado es `Administrador`). Un rol distinto responde
`403`. Este fallback no autentica el header y es solo transitorio; en producción
el middleware de autenticación debe establecer el rol confiable en `request.state`.

## Valores de categorías de parámetros

HU-01B agrega estas operaciones:

- `GET /api/v1/parametros/categorias/{clave}/valores`: lista los valores por orden.
- `POST /api/v1/parametros/categorias/{clave}/valores`: crea un valor en la categoría.
- `PUT /api/v1/parametros/categorias/{clave}/valores/{id}`: edita nombre, descripción u orden.

El cuerpo de creación incluye `codigo`, `nombre` y `descripcion`; `orden` es
opcional y, si se omite, el valor se agrega al final. Los valores nuevos se
crean activos. El código es único dentro de la categoría y no se puede cambiar.
Un código repetido responde `409`; una categoría inexistente responde `404`.
Los datos también se almacenan en memoria. El repositorio de base de datos aún
no está integrado.

## Activar e inactivar valores

HU-01C expone `PATCH /api/v1/parametros/categorias/{clave}/valores/{id}/estado`
con un cuerpo `{"activo": false}` o `{"activo": true}`. El cambio conserva el
registro y puede repetirse sin error. El listado administrativo acepta el
filtro opcional `?activo=true` o `?activo=false`; sin filtro incluye todos los
valores.

## Parámetros de transporte

HU-02 expone `GET /api/v1/parametros/transporte`, que agrupa los valores de
`TIPO_VEHICULO` y `ESTADO_VEHICULO` en `data.tipo_vehiculo` y
`data.estado_vehiculo`. Cada valor incluye `es_sistema`. Al iniciar FastAPI se
cargan estas categorías y sus valores iniciales si aún no existen: automóvil,
camioneta, minibús y autobús; disponible, en mantenimiento y fuera de servicio.
La carga es idempotente y los valores iniciales del sistema no se pueden
inactivar: HU-01C responde `409` si se solicita ese cambio.

## Parámetros de pagos (HU-03)

`GET /api/v1/parametros/pagos` devuelve las categorías `METODO_PAGO` y
`ESTADO_TRANSACCION`, con todos sus valores activos e inactivos. Al iniciar
FastAPI se cargan ambas categorías de manera idempotente, incluyendo
`TARJETA_CREDITO` y los estados `PENDIENTE`, `APROBADA` y `RECHAZADA`.

Los valores de sistema no se pueden inactivar y solo permiten editar nombre y
descripción. En `METODO_PAGO` siempre debe quedar al menos un valor activo. Las
escrituras reutilizan los endpoints de HU-01B/HU-01C; no se agregan rutas de
escritura para pagos. La consulta responde `503` si la persistencia reporta una
indisponibilidad.

## Consulta pÃºblica de parÃ¡metros (HU-05)

Los mÃ³dulos pueden consultar valores vigentes sin sesiÃ³n ni rol:

- `GET /api/v1/parametros/consulta/{categoria}` devuelve `data.categoria` y
  `data.valores`, filtrados a valores activos y ordenados por `orden`.
- `GET /api/v1/parametros/consulta/{categoria}/{codigo}` devuelve un valor
  activo por categorÃ­a y cÃ³digo.

La bÃºsqueda no distingue mayÃºsculas y minÃºsculas. Un valor inexistente o
inactivo responde `404`; una categorÃ­a existente sin valores activos responde
`200` con una lista vacÃ­a. Los cambios realizados mediante HU-01B/HU-01C se
reflejan inmediatamente porque ambas consultas usan los mismos repositorios.
Cuando el adaptador de persistencia reporte un error de base de datos, las
consultas responden `503` con el mensaje `No fue posible consultar los
parÃ¡metros`.
