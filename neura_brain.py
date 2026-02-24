# neura_brain.py
import logging
import json
import random
from datetime import datetime
import asyncio
from prediction_engine import SistemaIAPredictiva, TipoPrediccion

class NeuraHiveMind:
    def __init__(self, config_path="agents_manifest.json"):
        self.logger = logging.getLogger("NeuraHive")
        
        # 1. Cargar Personalidades
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.personalidades = json.load(f)
        except Exception as e:
            self.logger.warning(f"No se pudo cargar {config_path}, usando defaults: {e}")
            self.personalidades = {
                "COMANDANTE": {"arquetipo": "Dominante", "tono": "firme", "emoji": "🔥", "frase_activacion": "🔥 COMANDANTE", "estilo_operativo": "Control"},
                "SABINO": {"arquetipo": "Sabio", "tono": "sereno", "emoji": "🧠", "frase_activacion": "🧠 SABINO", "estilo_operativo": "Análisis"},
                "CHINO": {"arquetipo": "Disruptivo", "tono": "irreverente", "emoji": "🌱", "frase_activacion": "🌱 CHINO", "estilo_operativo": "Innovación"},
                "NEUTRO": {"arquetipo": "Neutro", "tono": "objetivo", "emoji": "⚪", "frase_activacion": "⚪ NEUTRO", "estilo_operativo": "Equilibrio"}
            }

        # 2. Inicializar sistema de predicción
        self.ia_predictiva = SistemaIAPredictiva()
        self.estado_mercado = "NEUTRO"

    async def despertar(self):
        """Ciclo de vida del agente: Entrena y Predice"""
        self.logger.info("🧠 Entrenando redes neuronales...")
        try:
            resultado = await self.ia_predictiva.entrenar_modelo_ventas()
            self.logger.info(f"Entrenamiento completado: {resultado}")
        except Exception as e:
            self.logger.error(f"Error en entrenamiento: {e}")
        
        try:
            prediccion = await self.ia_predictiva.predecir_tendencia_mercado("digital")
            self.logger.info(f"🔮 Predicción de Mercado: {prediccion.valor} (Confianza: {prediccion.confianza})")
            return prediccion
        except Exception as e:
            self.logger.error(f"Error en predicción: {e}")
            # Devolver una predicción por defecto
            from prediction_engine import Prediccion, TipoPrediccion
            return Prediccion(TipoPrediccion.TENDENCIA_MERCADO, 0.5, 0.5, datetime.now(), "Error", [])

    def seleccionar_agente_activo(self, prediccion_valor, mensaje_usuario=""):
        """
        Elige qué personalidad toma el control basado en la IA Predictiva
        y el contenido del mensaje.
        """
        mensaje_lower = mensaje_usuario.lower()
        
        if prediccion_valor > 0.7:
            return "COMANDANTE", self.personalidades["COMANDANTE"]
        elif prediccion_valor < 0.3 or "miedo" in mensaje_lower or "peligro" in mensaje_lower:
            return "SABINO", self.personalidades["SABINO"]
        elif "idea" in mensaje_lower or "nuevo" in mensaje_lower or "creativo" in mensaje_lower:
            return "CHINO", self.personalidades["CHINO"]
        else:
            return "NEUTRO", self.personalidades["NEUTRO"]

    def generar_respuesta(self, agente_key, agente_data, mensaje_usuario):
        """
        Genera una respuesta simulada basada en el agente.
        En producción, aquí se conectaría con un LLM.
        """
        prefix = f"{agente_data.get('emoji', '')} **[{agente_key}]**: "
        
        if "precio" in mensaje_usuario or "comprar" in mensaje_usuario:
            return prefix + "Detecto intención de compra. Según mis modelos predictivos, es el momento exacto. Aquí tienes el enlace prioritario: /pagar"
        elif "ayuda" in mensaje_usuario:
            return prefix + "Estoy aquí para guiarte. ¿Qué necesitas?"
        else:
            return prefix + f"He analizado tu mensaje. Mi red neuronal sugiere: '{agente_data.get('estilo_operativo', 'proceder')}'."
