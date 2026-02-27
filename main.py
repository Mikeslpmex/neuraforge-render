import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from neura_brain import NeuraHiveMind
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# ================= CONFIGURACIÓN =================
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Falta TELEGRAM_TOKEN en el entorno")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")   # Ej: https://tudominio.com
PORT = int(os.environ.get("PORT", 5000))

# ================= CEREBRO =================
cerebro = NeuraHiveMind()

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= APLICACIÓN DE TELEGRAM =================
application = Application.builder().token(TOKEN).build()

# ---------- Manejadores ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start: activa el cerebro y muestra personalidad."""
    prediccion = await cerebro.despertar()
    nombre, agente = cerebro.seleccionar_agente_activo(prediccion.valor)
    frase = agente.get('frase_activacion', 'Activado')
    estilo = agente.get('estilo_operativo', 'Estándar')
    mensaje = (f"{frase}\n\n"
               f"📊 **Mercado (IA):** {prediccion.valor:.2f}\n"
               f"🎯 **Estrategia:** {estilo}")
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def pagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /pagar: genera link de pago."""
    agente = cerebro.personalidades.get("COMANDANTE", {})
    emoji = agente.get('emoji', '💰')
    # Link fijo de preventa (cámbialo si quieres uno dinámico)
    link = "https://mpago.li/1wbjMgo"
    await update.message.reply_text(
        f"{emoji} **ORDEN DE PAGO GENERADA**\n"
        f"El algoritmo ha reservado este slot para ti.\n\n"
        f"👉 [Pagar ahora]({link})",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensajes de texto normales: el cerebro elige agente."""
    texto = update.message.text
    # Lógica simple de predicción (puedes mejorarla)
    if "dinero" in texto.lower() or "comprar" in texto.lower():
        valor = 0.8
    elif "problema" in texto.lower() or "error" in texto.lower():
        valor = 0.2
    else:
        valor = 0.5
    nombre, agente = cerebro.seleccionar_agente_activo(valor, texto)
    respuesta = cerebro.generar_respuesta(nombre, agente, texto)
    await update.message.reply_text(respuesta, parse_mode='Markdown')

# Registrar manejadores
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("pagar", pagar))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ================= SERVIDOR FLASK (WEBHOOK) =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Neuraforge AI Agent está vivo."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe actualizaciones de Telegram."""
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        # Procesar en el loop de asyncio de la aplicación
        asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Endpoint para configurar el webhook manualmente."""
    if not WEBHOOK_URL:
        return "WEBHOOK_URL no definida", 500
    url = f"{WEBHOOK_URL}/webhook"
    async def config():
        await application.bot.set_webhook(url)
    asyncio.run(config())
    return f"Webhook configurado en {url}", 200

# ================= PUNTO DE ENTRADA =================
if __name__ == '__main__':
    # Configurar webhook al arrancar (si tenemos URL)
    if WEBHOOK_URL:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.bot.set_webhook(f"{WEBHOOK_URL}/webhook"))
        logger.info(f"✅ Webhook configurado en {WEBHOOK_URL}/webhook")
    else:
        logger.warning("⚠️ WEBHOOK_URL no definida. No se configuró webhook.")

    # Iniciar Flask
    app.run(host='0.0.0.0', port=PORT)
