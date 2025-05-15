import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# CONFIGURACIÓN desde variables de entorno
TOKEN = os.getenv('TOKEN_TELEGRAM')
EMAIL_UNPAYWALL = os.getenv('EMAIL_UNPAYWALL')

# LOGGING
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FUNCIONES DE BÚSQUEDA

def get_pdf_unpaywall(doi):
    try:
        url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL_UNPAYWALL}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if data.get('is_oa') and data.get('best_oa_location'):
            return data['best_oa_location'].get('url_for_pdf')
    except Exception as e:
        logger.error(f"Error en Unpaywall: {e}")
    return None

def search_core(title):
    try:
        r = requests.get(f"https://core.ac.uk:443/api-v2/articles/search/{title}?metadata=true&page=1&pageSize=1&fulltext=true")
        r.raise_for_status()
        results = r.json()
        return results['data'][0].get('downloadUrl') if results['data'] else None
    except Exception as e:
        logger.error(f"Error en CORE: {e}")
    return None

def search_openalex(title):
    try:
        r = requests.get(f"https://api.openalex.org/works?search={title}&per-page=1")
        r.raise_for_status()
        query = r.json()
        for result in query.get('results', []):
            pdf = result.get('open_access', {}).get('oa_url')
            if pdf:
                return pdf
    except Exception as e:
        logger.error(f"Error en OpenAlex: {e}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hola! Envíame un DOI o el título de un artículo y trataré de conseguir el PDF.')
    logger.info("Comando /start ejecutado por %s", update.effective_user.username)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    query = update.message.text.strip()
    logger.info(f"Mensaje recibido de {user}: {query}")
    await update.message.reply_text("Buscando el artículo...")

    pdf_url = None
    if query.startswith("10."):
        pdf_url = get_pdf_unpaywall(query)
    else:
        pdf_url = search_openalex(query) or search_core(query)

    if pdf_url:
        await update.message.reply_text(f"PDF encontrado: {pdf_url}")
        logger.info(f"PDF enviado a {user}: {pdf_url}")
    else:
        msg = "No encontré el PDF en fuentes legales. Puedes intentar con Sci-Hub (bajo tu responsabilidad)."
        await update.message.reply_text(msg)
        logger.warning(f"No se encontró PDF para {user}: {query}")

def main():
    if not TOKEN or not EMAIL_UNPAYWALL:
        logger.error("Faltan variables de entorno TOKEN o EMAIL_UNPAYWALL")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot iniciado correctamente.")
    app.run_polling()

if __name__ == '__main__':
    main()
