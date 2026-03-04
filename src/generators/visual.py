"""
Gerador de resumo visual.

Produz diagramas, mapas mentais e representações visuais
em formato ASCII art.
"""

from src.generators.base import ContentGenerator
from src.models.student import Student


class VisualGenerator(ContentGenerator):
    """Gera resumos visuais em formato ASCII (mapa mental/diagrama)."""

    content_type = "resumo_visual"

    def _build_prompt(self, student: Student, topic: str) -> str:
        """Constrói prompt para resumo visual ASCII."""
        return self.prompt_engine.build_visual_prompt(student, topic)
