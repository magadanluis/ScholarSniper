# Bot de Telegram para Descargar Artículos Científicos

Este bot acepta un DOI o título de un artículo y busca versiones en PDF en fuentes open access como Unpaywall, CORE y OpenAlex.

## Despliegue en Railway

1. Sube este repositorio a Railway.
2. Añade las siguientes variables de entorno:
   - `TOKEN_TELEGRAM`: tu token de Telegram
   - `EMAIL_UNPAYWALL`: tu email registrado en Unpaywall
3. Railway detectará el `Procfile` y lanzará el bot como un worker automáticamente.

## Logging

Los logs del bot están habilitados y pueden verse en la consola de Railway.

## Requisitos

- Python 3.10+
- `python-telegram-bot`
- `requests`

¡Listo!
