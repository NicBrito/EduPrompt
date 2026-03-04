"""
Templates de prompt por tipo de conteúdo.

Cada template utiliza técnicas específicas de engenharia de prompt
documentadas em PROMPT_ENGINEERING_NOTES.md.
"""

from dataclasses import dataclass, field


@dataclass
class PromptTemplates:
    """Conjunto de templates de prompt para uma versão específica."""

    version: str
    description: str
    techniques: list[str]
    persona: str
    conceptual: str
    practical: str
    reflection: str
    visual_summary: str
