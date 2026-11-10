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
