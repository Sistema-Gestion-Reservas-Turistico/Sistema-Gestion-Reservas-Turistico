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
100 caracteres.

## Sobre de respuesta de la API (TECH-01)

Todas las respuestas JSON usan `success`, `message`, `timestamp`, `errorCode` y
`data`. El timestamp se genera en UTC con formato ISO 8601. En las respuestas
exitosas, `errorCode` es `null`; en los errores se incluye un código identificador
y `data` siempre es `null`. Los campos internos de `data` y los cuerpos de
solicitud conservan sus nombres actuales, como `categorias`, `clave`, `codigo`,
`nombre`, `orden` y `activo`.

Ejemplo de respuesta exitosa:

```json
{
  "success": true,
  "message": "Payment parameters retrieved successfully",
  "timestamp": "2026-11-23T22:24:00Z",
  "errorCode": null,
  "data": {
    "categorias": [
      {
        "clave": "METODO_PAGO",
        "nombre": "Tarjeta de crédito",
        "valores": [
          {
            "id": 11,
            "codigo": "TARJETA_CREDITO",
            "nombre": "Tarjeta de crédito",
            "orden": 1,
            "activo": true,
            "es_sistema": false
          }
        ]
      }
    ]
  }
}
```

Ejemplo de respuesta de error:

```json
{
  "success": false,
  "message": "At least one payment method must remain active",
  "timestamp": "2026-11-23T22:24:00Z",
  "errorCode": "LAST_ACTIVE_PAYMENT_METHOD",
  "data": null
}
```

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

## Parámetros de alojamiento y alimentación (HU-04)

`GET /api/v1/parametros/alojamiento-alimentacion` agrupa
`TIPO_HABITACION`, `TIPO_ALIMENTACION` y `RESTRICCION_ALIMENTARIA`; la consulta
administrativa incluye valores activos e inactivos. Al iniciar FastAPI se
cargan de forma idempotente los valores iniciales SENCILLA, FAMILIAR, DESAYUNO
y VEGETARIANA, todos activos y no protegidos como valores de sistema. Estos
valores pueden inactivarse sin restricción de último valor activo, y las
consultas de uso pueden filtrar activos con `?activo=true` en el listado
existente por categoría. Los registros inactivos se conservan para mantener
referencias históricas. Las escrituras reutilizan HU-01B/HU-01C; no se agregan
rutas nuevas de escritura.

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
consultas responden `503` con el mensaje `Parameters could not be retrieved`.

## Registro de usuarios (HU-06)

`POST /api/v1/usuarios/registro` es una ruta pública que crea cuentas con rol
`Cliente` y estado `PENDIENTE_ACTIVACION`. El correo se normaliza a minúsculas
y tanto el correo como la combinación de tipo y número de documento son únicos.
La contraseña exige ocho caracteres como mínimo, mayúscula, minúscula y número;
se almacena con PBKDF2-HMAC-SHA256 y salt aleatorio. El registro requiere aceptar
el tratamiento de datos y guarda la fecha de aceptación. El teléfono es opcional
y los campos adicionales del cuerpo, incluido `rol`, se ignoran.

Al iniciar la aplicación se carga idempotentemente la categoría
`TIPO_DOCUMENTO` y los valores activos `CC`, `CE` y `PASAPORTE`, compartidos
con la consulta pública de parámetros de HU-05. Las validaciones responden
`400`, las duplicidades `409` y los fallos de persistencia `503`. Los datos de
usuarios se mantienen en memoria y se pierden al reiniciar la aplicación.

## Bloqueo de cuenta por intentos fallidos (HU-07)

`POST /api/v1/auth/login` verifica las credenciales de una cuenta activa y
mantiene el estado de intentos y la auditoría en repositorios separados por
correo normalizado, incluso si no existe un usuario para ese correo. Los
valores predeterminados son `MAX_INTENTOS_FALLIDOS_LOGIN=5` y
`MINUTOS_BLOQUEO_LOGIN=15`; se pueden configurar como variables de entorno.
Una vez alcanzado el máximo, responde `423` durante el periodo de bloqueo,
independientemente de que la contraseña posterior sea correcta. Las
credenciales incorrectas responden `401` con los intentos restantes y los
errores de persistencia `503`.

El correo `cliente.activo@correo.com` con contraseña `Viaje2026` se carga como
cuenta de prueba activa al iniciar la aplicación. El adaptador de notificaciones
en memoria permite inspeccionar avisos de bloqueo y simular fallos de envío;
el bloqueo se conserva aunque el envío del aviso falle.

## Activación de cuentas por correo (HU-08)

Al registrar una cuenta, `POST /api/v1/usuarios/registro` genera un token
aleatorio de un solo uso y envía el enlace
`{FRONTEND_URL}/activar-cuenta?token={token}`. Solo se almacena el hash SHA-256
del token. La vigencia predeterminada es de 24 horas
(`HORAS_VIGENCIA_TOKEN_ACTIVACION`); un fallo de correo no cancela el registro.

`POST /api/v1/usuarios/activacion` consume el token y activa la cuenta con
estado `ACTIVA`. Los enlaces vencidos responden `410`, los ya consumidos `409`
y los inválidos o reemplazados `400`. `POST /api/v1/usuarios/activacion/reenviar`
genera un token nuevo para cuentas
pendientes, invalida enlaces anteriores y responde igual para correos
desconocidos o cuentas ya activas. Se permiten hasta tres solicitudes por
correo por hora (`MAX_REENVIOS_ACTIVACION_POR_HORA`).

## Coordenadas de destinos (HU-12)

`PUT /api/v1/geo/destinos/{id_destino}/coordenadas` registra o reemplaza la
latitud y longitud de un destino. Requiere `Authorization: Bearer <JWT>` con
rol `Administrador`. Las coordenadas deben estar dentro de los rangos
geográficos y del municipio asociado; errores de rango responden `400`, destino
inexistente `404`, ubicación en otro municipio `409` y fallos de persistencia
`503`.

El seed idempotente carga el municipio 63690 (Salento) y el destino 15
(`Reserva Natural Demo`). El punto `4.6372, -75.5712` está dentro de los límites
de prueba configurados. Define `JWT_SECRET_KEY` con un valor aleatorio de al
menos 32 caracteres y `MINUTOS_EXPIRACION_JWT` para ajustar la vigencia del JWT.
