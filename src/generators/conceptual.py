"""
Gerador de explicações conceituais.

Utiliza a técnica de Chain-of-Thought para produzir
explicações claras e progressivas.
"""

from src.generators.base import ContentGenerator
from src.models.student import Student


class ConceptualGenerator(ContentGenerator):
    """Gera explicações conceituais usando chain-of-thought."""

    content_type = "explicacao_conceitual"

    def _build_prompt(self, student: Student, topic: str) -> str:
        """Constrói prompt para explicação conceitual."""
        return self.prompt_engine.build_conceptual_prompt(student, topic)
