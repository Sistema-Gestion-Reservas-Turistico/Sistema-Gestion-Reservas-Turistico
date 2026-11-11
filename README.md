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

Los datos se guardan en memoria y se pierden al reiniciar la aplicación. La
autorización por rol Administrador y el manejo de indisponibilidad de una base
de datos quedan pendientes: el proyecto aún no proporciona autenticación ni
una base de datos y no se simulan esas dependencias.

## Valores de categorías de parámetros

HU-01B agrega estas operaciones:

- `GET /api/v1/parametros/categorias/{clave}/valores`: lista los valores por orden.
- `POST /api/v1/parametros/categorias/{clave}/valores`: crea un valor en la categoría.
- `PUT /api/v1/parametros/categorias/{clave}/valores/{id}`: edita nombre, descripción u orden.

El cuerpo de creación incluye `codigo`, `nombre` y `descripcion`; `orden` es
opcional y, si se omite, el valor se agrega al final. Los valores nuevos se
crean activos. El código es único dentro de la categoría y no se puede cambiar.
Un código repetido responde `409`; una categoría inexistente responde `404`.
Los datos también se almacenan en memoria. La autorización y el error `503`
por base de datos siguen pendientes hasta que existan autenticación y
persistencia en base de datos.
