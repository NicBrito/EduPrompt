"""
Testes do motor de engenharia de prompt.
"""

import pytest

from src.models.student import Student, KnowledgeLevel, LearningStyle
from src.prompts.engine import PromptEngine
from src.prompts.versions import PROMPT_VERSIONS


class TestPromptEngine:
    """Testes do PromptEngine."""

    @pytest.fixture
    def student_beginner(self):
        """Aluno iniciante para testes."""
        return Student(
            name="Ana",
            age=12,
            knowledge_level=KnowledgeLevel.BEGINNER,
            learning_style=LearningStyle.VISUAL,
            interests=["desenho", "animais"],
        )

    @pytest.fixture
    def student_advanced(self):
        """Aluno avançado para testes."""
        return Student(
            name="Maria",
            age=25,
            knowledge_level=KnowledgeLevel.ADVANCED,
            learning_style=LearningStyle.KINESTHETIC,
            interests=["ciência de dados"],
        )

    def test_init_valid_version(self):
        """Testa inicialização com versão válida."""
        engine = PromptEngine(version="v1")
        assert engine.version == "v1"

        engine = PromptEngine(version="v2")
        assert engine.version == "v2"

    def test_init_invalid_version(self):
        """Testa que versão inválida gera erro."""
        with pytest.raises(ValueError, match="não existe"):
            PromptEngine(version="v99")

    def test_system_prompt_contains_persona(self, student_beginner):
        """Testa que o system prompt contém a persona."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_system_prompt(student_beginner)

        assert "professor" in prompt.lower()
        assert student_beginner.name in prompt

    def test_system_prompt_contains_student_context(self, student_beginner):
        """Testa que o system prompt contém o contexto do aluno."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_system_prompt(student_beginner)

        assert str(student_beginner.age) in prompt
        assert student_beginner.knowledge_level.value in prompt
        assert student_beginner.learning_style.value in prompt

    def test_conceptual_prompt_has_chain_of_thought(self, student_beginner):
        """Testa que o prompt conceitual usa chain-of-thought."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_conceptual_prompt(student_beginner, "Fotossíntese")

        assert "passo" in prompt.lower()
        assert "Fotossíntese" in prompt

    def test_practical_prompt_includes_interests(self, student_beginner):
        """Testa que o prompt prático inclui interesses do aluno."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_practical_prompt(student_beginner, "Matemática")

        assert "desenho" in prompt
        assert "Matemática" in prompt

    def test_reflection_prompt_has_levels(self, student_advanced):
        """Testa que o prompt de reflexão inclui níveis de pensamento."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_reflection_prompt(student_advanced, "Machine Learning")

        assert "Compreensão" in prompt
        assert "Análise" in prompt
        assert "Machine Learning" in prompt

    def test_visual_prompt_mentions_ascii(self, student_beginner):
        """Testa que o prompt visual menciona ASCII."""
        engine = PromptEngine(version="v2")
        prompt = engine.build_visual_prompt(student_beginner, "Ciclo da Água")

        assert "ASCII" in prompt or "ascii" in prompt
        assert "Ciclo da Água" in prompt

    def test_different_versions_produce_different_prompts(self, student_beginner):
        """Testa que versões diferentes geram prompts diferentes."""
        engine_v1 = PromptEngine(version="v1")
        engine_v2 = PromptEngine(version="v2")

        prompt_v1 = engine_v1.build_conceptual_prompt(student_beginner, "Gravidade")
        prompt_v2 = engine_v2.build_conceptual_prompt(student_beginner, "Gravidade")

        # v2 deve ser mais elaborado
        assert len(prompt_v2) > len(prompt_v1)

    def test_different_students_produce_different_prompts(
        self, student_beginner, student_advanced
    ):
        """Testa que alunos diferentes geram prompts diferentes."""
        engine = PromptEngine(version="v2")
        topic = "Inteligência Artificial"

        prompt_beginner = engine.build_conceptual_prompt(student_beginner, topic)
        prompt_advanced = engine.build_conceptual_prompt(student_advanced, topic)

        assert "12" in prompt_beginner
        assert "25" in prompt_advanced
        assert "iniciante" in prompt_beginner
        assert "avançado" in prompt_advanced

    def test_list_versions(self):
        """Testa listagem de versões disponíveis."""
        versions = PromptEngine.list_versions()

        assert len(versions) >= 2
        assert all("version" in v for v in versions)
        assert all("description" in v for v in versions)
        assert all("techniques" in v for v in versions)
