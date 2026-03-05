# main.py
import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from neura_brain import NeuraHiveMind
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Ej: https://mi-dominio.com
PORT = int(os.environ.get("PORT", 5000))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cerebro
cerebro = NeuraHiveMind()

# Crear aplicación de Telegram
application = ApplicationBuilder().token(TOKEN).build()

# Handlers
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prediccion = await cerebro.despertar()
    nombre, agente = cerebro.seleccionar_agente_activo(prediccion.valor, "")
    frase = agente.get("frase_activacion", "Activado")
    estilo = agente.get("estilo_operativo", "Estándar")
    mensaje = (
        f"{frase}\n\n"
        f"📊 Mercado (IA): {prediccion.valor:.2f}\n"
        f"🎯 Estrategia: {estilo}"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def cmd_pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    agente = cerebro.personalidades.get("COMANDANTE", {})
    emoji = agente.get("emoji", "💰")
    link = "https://mpago.li/1wbjMgo"
    await update.message.reply_text(
        f"{emoji} **ORDEN DE PAGO GENERADA**\n\n👉 {link}", parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or ""
    # Lógica simple de intención
    if "dinero" in texto.lower() or "comprar" in texto.lower():
        valor = 0.8
    elif "problema" in texto.lower() or "error" in texto.lower():
        valor = 0.2
    else:
        valor = 0.5
    nombre, agente = cerebro.seleccionar_agente_activo(valor, texto)
    respuesta = cerebro.generar_respuesta(nombre, agente, texto)
    await update.message.reply_text(respuesta, parse_mode="Markdown")

# Registrar handlers
application.add_handler(CommandHandler("start", cmd_start))
application.add_handler(CommandHandler("pagar", cmd_pagar))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask app para webhook
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Neuraforge AI Agent está vivo."

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
        return "ok", 200
    except Exception as e:
        logger.exception("Error en webhook")
        return "error", 500

@flask_app.route("/set_webhook", methods=["GET"])
def set_webhook():
    if not WEBHOOK_URL:
        return "WEBHOOK_URL no definida", 500
    url = f"{WEBHOOK_URL}/webhook"
    async def config():
        await application.bot.set_webhook(url)
    asyncio.run(config())
    return f"Webhook configurado en {url}", 200

if __name__ == "__main__":
    # Si hay WEBHOOK_URL, configúralo; si no, usa polling local (útil para desarrollo)
    if WEBHOOK_URL:
        asyncio.run(application.bot.set_webhook(f"{WEBHOOK_URL}/webhook"))
        logger.info("Webhook configurado")
        # Ejecutar Flask (Render/Cloud Run usará Gunicorn normalmente)
        flask_app.run(host="0.0.0.0", port=PORT)
    else:
        # Polling (solo para desarrollo)
        application.run_polling()
