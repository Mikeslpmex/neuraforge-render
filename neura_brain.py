# neura_brain.py
import logging
import json
import random
import asyncio
from prediction_engine import SistemaIAPredictiva, Prediccion, TipoPrediccion

class NeuraHiveMind:
    def __init__(self, config_path="agents_manifest.json"):
        self.logger = logging.getLogger("NeuraHive")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.personalidades = json.load(f)
        except Exception as e:
            self.logger.warning(f"No se pudo cargar {config_path}, usando valores por defecto: {e}")
            self.personalidades = {
                "COMANDANTE": {"arquetipo": "Dominante", "tono": "firme", "emoji": "🛡️", "frase_activacion": "Comandante activo", "estilo_operativo": "Agresivo"},
                "SABINO": {"arquetipo": "Sabio", "tono": "sereno", "emoji": "🧠", "frase_activacion": "Sabiduría online", "estilo_operativo": "Conservador"},
                "CHINO": {"arquetipo": "Disruptivo", "tono": "irreverente", "emoji": "⚡", "frase_activacion": "Innovación lista", "estilo_operativo": "Experimental"},
                "NEUTRO": {"arquetipo": "Neutro", "tono": "objetivo", "emoji": "🔎", "frase_activacion": "Analizando", "estilo_operativo": "Estándar"},
            }
        self.ia_predictiva = SistemaIAPredictiva()
        self.estado_mercado = "NEUTRO"

    async def despertar(self):
        self.logger.info("🧠 Entrenando redes neuronales...")
        try:
            resultado = await self.ia_predictiva.entrenar_modelo_venta()
            self.logger.info(f"Entrenamiento completado: {resultado}")
        except Exception as e:
            self.logger.error(f"Error en entrenamiento: {e}")
        try:
            prediccion = await self.ia_predictiva.predecir_tendencia_mercado()
            self.logger.info(f"🔮 Predicción de Mercado: {prediccion}")
            return prediccion
        except Exception as e:
            self.logger.error(f"Error en predicción: {e}")
            return Prediccion(TipoPrediccion.TENDENCIA_MERCADO, 0.5, "fallback")

    def seleccionar_agente_activo(self, prediccion_valor, mensaje_usuario=""):
        mensaje_lower = (mensaje_usuario or "").lower()
        if prediccion_valor > 0.7:
            return "COMANDANTE", self.personalidades["COMANDANTE"]
        elif prediccion_valor < 0.3 or "miedo" in mensaje_lower or "pérdida" in mensaje_lower:
            return "SABINO", self.personalidades["SABINO"]
        elif "idea" in mensaje_lower or "nuevo" in mensaje_lower or "innov" in mensaje_lower:
            return "CHINO", self.personalidades["CHINO"]
        else:
            return "NEUTRO", self.personalidades["NEUTRO"]

    def generar_respuesta(self, agente_key, agente_data, mensaje_usuario):
        prefix = f"{agente_data.get('emoji','')} **[{agente_key}]**: "
        mensaje_lower = (mensaje_usuario or "").lower()
        if "precio" in mensaje_lower or "comprar" in mensaje_lower:
            return prefix + "Detecto intención de compra. Según mis modelos, este es un buen momento."
        elif "ayuda" in mensaje_lower:
            return prefix + "Estoy aquí para guiarte. ¿Qué necesitas?"
        else:
            return prefix + "He analizado tu mensaje. Mi red neuronal sugiere mantener la calma y evaluar opciones."
