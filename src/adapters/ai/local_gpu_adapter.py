"""
Path: src/adapters/ai/local_gpu_adapter.py
"""

import numpy as np
from typing import List, Optional, AsyncIterator
from sentence_transformers import SentenceTransformer, util

from src.core.domain.ports import AIEnginePort
from src.core.domain.entities import Message, ToolDefinition, ToolCall, CompletionChunk
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

from src.core.domain.ports import AIEnginePort
from src.core.domain.entities import Message, ToolDefinition, ToolCall, CompletionChunk, Intent
from src.adapters.settings.config import settings
from src.adapters.settings.logger import logger

class LocalGPUAdapter(AIEnginePort):
    def __init__(self):
        self.model_name = settings.local_gpu_model_name
        logger.info(f"Cargando modelo de IA local: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        logger.info("Modelo cargado correctamente.")

    async def classify_intent(
        self, 
        prompt: str, 
        tools: List[ToolDefinition]
    ) -> Optional[Intent]:
        """
        Clasifica el prompt usando Embeddings con contexto enriquecido.
        """
        if not tools:
            return None

        # Enriquecemos la descripción con contexto de uso y parámetros
        tool_descriptions = []
        for t in tools:
            params = ", ".join(t.input_schema.get("properties", {}).keys())
            
            # Boost semántico basado en patrones de nombres
            usage_context = ""
            if t.name.startswith("list"):
                usage_context = "IDEAL PARA: Contar cuántos elementos hay en total, listados generales y preguntas de 'cuántos'."
            elif "report" in t.name or "total" in t.name:
                usage_context = "PARA: Estadísticas avanzadas y reportes detallados."
            elif t.name.endswith("_product") or t.name.endswith("_order"):
                usage_context = "SOLO PARA: Detalles de UN solo elemento específico usando su ID."
            
            context = f"Herramienta: {t.name}. {usage_context} Descripción: {t.description}. Parámetros: {params}"
            tool_descriptions.append(context)
        
        # Generamos embeddings
        prompt_embedding = self.model.encode(prompt, convert_to_tensor=True)
        tool_embeddings = self.model.encode(tool_descriptions, convert_to_tensor=True)
        
        # Similitud de coseno
        cosine_scores = util.cos_sim(prompt_embedding, tool_embeddings)[0]
        
        # Mejor match
        best_idx = np.argmax(cosine_scores.cpu().numpy())
        best_score = cosine_scores[best_idx].item()
        best_tool = tools[best_idx]
        
        logger.info(f"Clasificación local: {best_tool.name} ({best_score:.2f})")
        
        return Intent(
            tool_name=best_tool.name,
            confidence=best_score,
            reason=f"Similitud semántica de {best_score:.2f} con la descripción de {best_tool.name}"
        )

    async def stream_completion(
        self, 
        messages: List[Message], 
        tools: List[ToolDefinition]
    ) -> AsyncIterator[CompletionChunk]:
        yield CompletionChunk(text="El motor local actualmente solo soporta clasificación directa.", is_final=True)

    async def extract_arguments(
        self,
        prompt: str,
        tool: ToolDefinition
    ) -> dict:
        """
        Extracción simplificada. 
        TODO: Implementar NER o un modelo pequeño de extracción para local-gpu.
        Por ahora, intenta buscar números que podrían ser IDs.
        """
        import re
        args = {}
        
        # Ejemplo: Si la herramienta tiene un campo 'id' o 'clienteId'
        properties = tool.input_schema.get("properties", {})
        for prop_name in properties:
            if "id" in prop_name.lower():
                # Buscamos un número en el prompt
                match = re.search(r'\b(\d+)\b', prompt)
                if match:
                    args[prop_name] = int(match.group(1))
        
        return args
