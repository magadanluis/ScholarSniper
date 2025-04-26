import os
from bs4 import BeautifulSoup
import requests
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Envíame el título o DOI de un artículo científico y te buscaré una versión Open Access.")

def es_doi(cadena):
    return cadena.startswith("10.") and "/" in cadena

def buscar_doi_por_titulo(titulo):
    url = f"https://api.crossref.org/works?query={titulo}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get('message', {}).get('items', [])
        if items:
            return items[0]['DOI']
    return None

def obtener_pdf_desde_unpaywall(doi):
    url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        oa_location = data.get('best_oa_location')
        if oa_location and oa_location.get('url_for_pdf'):
            return oa_location['url_for_pdf']
    return None

def obtener_pdf_scihub(doi):
    url = f"https://sci-hub.se/{doi}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            src = iframe["src"]
            if src.startswith("//"):
                src = "https:" + src
            return src
    else:
        return "vacio"
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    consulta = update.message.text.strip()
    doi = consulta if es_doi(consulta) else buscar_doi_por_titulo(consulta)

    if not doi:
        await update.message.reply_text("No pude encontrar un DOI para tu consulta. Intenta ser más específico.")
        return

    pdf_url = obtener_pdf_desde_unpaywall(doi)

    if pdf_url:
        await update.message.reply_text(f"Aquí tienes el PDF Open Access:\n{pdf_url}")
    else:
        await update.message.reply_text("No hay una versión gratuita disponible para este artículo, probemos con SciHub")
        pdf_url = obtener_pdf_scihub(doi)
        if pdf_url:
            await update.message.reply_text(f"Aquí tienes el PDF Open Access:\n{pdf_url}")
        else:
            await update.message.reply_text("No hay una versión en scihub de este articulo")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()
