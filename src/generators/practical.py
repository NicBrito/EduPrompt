"""
Gerador de exemplos práticos.

Produz exemplos contextualizados para a idade, nível e
interesses do aluno.
"""

from src.generators.base import ContentGenerator
from src.models.student import Student


class PracticalGenerator(ContentGenerator):
    """Gera exemplos práticos contextualizados."""

    content_type = "exemplos_praticos"

    def _build_prompt(self, student: Student, topic: str) -> str:
        """Constrói prompt para exemplos práticos."""
        return self.prompt_engine.build_practical_prompt(student, topic)
