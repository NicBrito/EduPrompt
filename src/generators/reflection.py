"""
Gerador de perguntas de reflexão.

Produz perguntas que estimulam pensamento crítico,
seguindo a Taxonomia de Bloom.
"""

from src.generators.base import ContentGenerator
from src.models.student import Student


class ReflectionGenerator(ContentGenerator):
    """Gera perguntas de reflexão que estimulam pensamento crítico."""

    content_type = "perguntas_reflexao"

    def _build_prompt(self, student: Student, topic: str) -> str:
        """Constrói prompt para perguntas de reflexão."""
        return self.prompt_engine.build_reflection_prompt(student, topic)
