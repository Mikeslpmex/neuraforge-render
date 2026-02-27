# main.py
import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from neura_brain import NeuraHiveMind
import dotenv
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("ruta/al/archivo-de-credenciales.json")
firebase_admin.initialize_app(cred)

def send_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
    )
    response = messaging.send(message)
    return response

dotenv.load_dotenv()

# Configuración
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Falta TELEGRAM_TOKEN en entorno")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")   # Ej: https://tusitio.onrender.com
PORT = int(os.environ.get("PORT", 5000))

# Cerebro
cerebro = NeuraHiveMind()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Aplicación de Telegram
application = Application.builder().token(TOKEN).build()

# --- Manejadores ---
async def start(update: Update, context):
    prediccion = await cerebro.despertar()
    nombre, agente = cerebro.seleccionar_agente_activo(prediccion.valor)
    mensaje = f"{agente.get('frase_activacion', 'Activado')}\n\n"
    mensaje += f"📊 **Mercado (IA):** {prediccion.valor:.2f}\n"
    mensaje += f"🎯 **Estrategia:** {agente.get('estilo_operativo', '')}"
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def pagar(update: Update, context):
    agente = cerebro.personalidades.get("COMANDANTE", {})
    link = "https://mpago.li/1wbjMgo"  # Cambia por tu link real
    await update.message.reply_text(
        f"{agente.get('emoji', '💰')} **ORDEN DE PAGO GENERADA**\n"
        f"👉 [Pagar ahora]({link})",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context):
    texto = update.message.text
    # Simulación de predicción (puedes sustituir por una llamada real)
    if "dinero" in texto.lower() or "comprar" in texto.lower():
        valor = 0.8
    elif "problema" in texto.lower():
        valor = 0.2
    else:
        valor = 0.5
    nombre, agente = cerebro.seleccionar_agente_activo(valor, texto)
    respuesta = cerebro.generar_respuesta(nombre, agente, texto)
    await update.message.reply_text(respuesta, parse_mode='Markdown')

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("pagar", pagar))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Servidor Flask ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Neuraforge AI Agent está vivo."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        asyncio.run_coroutine_threadsafe(application.process_update(update), asyncio.get_event_loop())
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    if not WEBHOOK_URL:
        return "WEBHOOK_URL no definida", 500
    url = f"{WEBHOOK_URL}/webhook"
    async def config():
        await application.bot.set_webhook(url)
    asyncio.run(config())
    return f"Webhook configurado en {url}", 200

if __name__ == '__main__':
    # Configurar webhook al arrancar si tenemos URL
    if WEBHOOK_URL:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook"))
        logger.info(f"Webhook OK en {WEBHOOK_URL}/webhook")
    else:
        logger.warning("WEBHOOK_URL no definida, no se configuró webhook.")
    # Iniciar Flask
    app.run(host='0.0.0.0', port=PORT)
