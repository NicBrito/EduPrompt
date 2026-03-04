"""
Motor de Engenharia de Prompt.

Monta prompts dinâmicos baseados no perfil do aluno, utilizando
técnicas avançadas: persona prompting, context setting,
chain-of-thought e output formatting.
"""

import logging
from typing import Optional

from src.models.student import Student
from src.prompts.templates import PromptTemplates
from src.prompts.versions import PromptVersion, PROMPT_VERSIONS

logger = logging.getLogger(__name__)


class PromptEngine:
    """
    Motor central de engenharia de prompt.

    Combina perfil do aluno, tópico e técnicas de prompt para
    gerar instruções otimizadas para a IA.
    """

    def __init__(self, version: str = "v2"):
        """
        Inicializa o motor de prompt.

        Args:
            version: Versão dos templates de prompt a usar (v1, v2).
        """
        if version not in PROMPT_VERSIONS:
            raise ValueError(
                f"Versão '{version}' não existe. "
                f"Disponíveis: {', '.join(PROMPT_VERSIONS.keys())}"
            )
        self.version = version
        self.templates = PROMPT_VERSIONS[version]
        logger.info("PromptEngine inicializado com versão: %s", version)

    def build_system_prompt(self, student: Student) -> str:
        """
        Constrói o prompt de sistema com persona e contexto do aluno.

        Técnicas utilizadas:
        - Persona Prompting: Define o papel do professor
        - Context Setting: Inclui dados específicos do aluno

        Args:
            student: Perfil do aluno.

        Returns:
            Prompt de sistema formatado.
        """
        persona = self.templates.persona
        context = self._build_student_context(student)

        system_prompt = f"{persona}\n\n{context}"
        logger.debug("System prompt construído (%d chars)", len(system_prompt))
        return system_prompt

    def build_conceptual_prompt(self, student: Student, topic: str) -> str:
        """
        Constrói prompt para explicação conceitual usando chain-of-thought.

        Técnicas:
        - Chain-of-Thought: Solicita raciocínio passo a passo
        - Output Formatting: Estrutura a resposta esperada

        Args:
            student: Perfil do aluno.
            topic: Tópico a ser explicado.

        Returns:
            Prompt formatado para explicação conceitual.
        """
        template = self.templates.conceptual
        return template.format(
            topic=topic,
            student_description=student.describe(),
            age=student.age,
            level=student.knowledge_level.value,
            style=student.learning_style.value,
        )

    def build_practical_prompt(self, student: Student, topic: str) -> str:
        """
        Constrói prompt para exemplos práticos contextualizados.

        Técnicas:
        - Context Setting: Contextualiza para idade/nível
        - Output Formatting: Especifica formato dos exemplos

        Args:
            student: Perfil do aluno.
            topic: Tópico para exemplos práticos.

        Returns:
            Prompt formatado para exemplos práticos.
        """
        template = self.templates.practical
        interests = ", ".join(student.interests) if student.interests else "diversos"
        return template.format(
            topic=topic,
            student_description=student.describe(),
            age=student.age,
            level=student.knowledge_level.value,
            style=student.learning_style.value,
            interests=interests,
        )

    def build_reflection_prompt(self, student: Student, topic: str) -> str:
        """
        Constrói prompt para perguntas de reflexão.

        Técnicas:
        - Chain-of-Thought: Justifica cada pergunta
        - Context Setting: Adapta nível de complexidade

        Args:
            student: Perfil do aluno.
            topic: Tópico para reflexão.

        Returns:
            Prompt formatado para perguntas de reflexão.
        """
        template = self.templates.reflection
        return template.format(
            topic=topic,
            student_description=student.describe(),
            age=student.age,
            level=student.knowledge_level.value,
            style=student.learning_style.value,
        )

    def build_visual_prompt(self, student: Student, topic: str) -> str:
        """
        Constrói prompt para resumo visual (diagrama/mapa mental ASCII).

        Técnicas:
        - Output Formatting: Especifica formato ASCII art
        - Context Setting: Adapta complexidade visual

        Args:
            student: Perfil do aluno.
            topic: Tópico para resumo visual.

        Returns:
            Prompt formatado para resumo visual.
        """
        template = self.templates.visual_summary
        return template.format(
            topic=topic,
            student_description=student.describe(),
            age=student.age,
            level=student.knowledge_level.value,
            style=student.learning_style.value,
        )

    def _build_student_context(self, student: Student) -> str:
        """Constrói a seção de contexto do aluno para o prompt."""
        context_parts = [
            "## Contexto do Aluno",
            f"- **Nome:** {student.name}",
            f"- **Idade:** {student.age} anos",
            f"- **Nível de Conhecimento:** {student.knowledge_level.value}",
            f"- **Estilo de Aprendizado:** {student.learning_style.value}",
        ]

        if student.interests:
            context_parts.append(
                f"- **Interesses:** {', '.join(student.interests)}"
            )

        context_parts.append(f"\n**Descrição:** {student.describe()}")

        return "\n".join(context_parts)

    @staticmethod
    def list_versions() -> list[dict]:
        """Lista todas as versões de prompt disponíveis."""
        return [
            {
                "version": v,
                "description": templates.description,
                "techniques": templates.techniques,
            }
            for v, templates in PROMPT_VERSIONS.items()
        ]
