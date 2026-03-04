"""
Testes dos geradores de conteúdo.

Testa a construção de prompts (sem chamar a API real).
"""

from unittest.mock import MagicMock, patch

import pytest

from src.models.student import Student, KnowledgeLevel, LearningStyle
from src.generators.conceptual import ConceptualGenerator
from src.generators.practical import PracticalGenerator
from src.generators.reflection import ReflectionGenerator
from src.generators.visual import VisualGenerator
from src.services.storage import ContentRecord


class TestGenerators:
    """Testes dos geradores de conteúdo."""

    @pytest.fixture
    def student(self):
        """Aluno para testes."""
        return Student(
            name="Teste",
            age=15,
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            learning_style=LearningStyle.VISUAL,
            interests=["tecnologia"],
        )

    @pytest.fixture
    def mock_ai_client(self):
        """Mock do AIClient para evitar chamadas reais à API."""
        mock = MagicMock()
        mock.generate.return_value = "Conteúdo gerado mock"
        return mock

    @pytest.fixture
    def mock_cache(self):
        """Mock do CacheManager."""
        mock = MagicMock()
        mock.get.return_value = None  # Cache miss por padrão
        return mock

    def test_conceptual_generator_type(self):
        """Testa que o gerador conceitual tem o tipo correto."""
        assert ConceptualGenerator.content_type == "explicacao_conceitual"

    def test_practical_generator_type(self):
        """Testa que o gerador prático tem o tipo correto."""
        assert PracticalGenerator.content_type == "exemplos_praticos"

    def test_reflection_generator_type(self):
        """Testa que o gerador de reflexão tem o tipo correto."""
        assert ReflectionGenerator.content_type == "perguntas_reflexao"

    def test_visual_generator_type(self):
        """Testa que o gerador visual tem o tipo correto."""
        assert VisualGenerator.content_type == "resumo_visual"

    def test_generate_returns_content_record(
        self, student, mock_ai_client, mock_cache
    ):
        """Testa que generate() retorna um ContentRecord."""
        generator = ConceptualGenerator(
            ai_client=mock_ai_client,
            cache=mock_cache,
            prompt_version="v2",
        )

        record = generator.generate(student, "Fotossíntese")

        assert isinstance(record, ContentRecord)
        assert record.student_id == student.id
        assert record.topic == "Fotossíntese"
        assert record.content_type == "explicacao_conceitual"
        assert record.content == "Conteúdo gerado mock"

    def test_generate_uses_cache_when_available(
        self, student, mock_ai_client, mock_cache
    ):
        """Testa que o cache é usado quando disponível."""
        mock_cache.get.return_value = "Conteúdo cacheado"

        generator = ConceptualGenerator(
            ai_client=mock_ai_client,
            cache=mock_cache,
            prompt_version="v2",
        )

        record = generator.generate(student, "Fotossíntese")

        assert record.content == "Conteúdo cacheado"
        mock_ai_client.generate.assert_not_called()

    def test_generate_calls_api_on_cache_miss(
        self, student, mock_ai_client, mock_cache
    ):
        """Testa que a API é chamada quando não há cache."""
        mock_cache.get.return_value = None

        generator = PracticalGenerator(
            ai_client=mock_ai_client,
            cache=mock_cache,
            prompt_version="v2",
        )

        record = generator.generate(student, "Gravidade")

        mock_ai_client.generate.assert_called_once()
        assert record.content == "Conteúdo gerado mock"

    def test_generate_saves_to_cache_after_api_call(
        self, student, mock_ai_client, mock_cache
    ):
        """Testa que o resultado é salvo no cache após chamada à API."""
        mock_cache.get.return_value = None

        generator = ReflectionGenerator(
            ai_client=mock_ai_client,
            cache=mock_cache,
            prompt_version="v2",
        )

        generator.generate(student, "Evolução")

        mock_cache.set.assert_called_once()

    def test_generate_skips_cache_when_disabled(
        self, student, mock_ai_client, mock_cache
    ):
        """Testa que o cache pode ser desabilitado."""
        generator = VisualGenerator(
            ai_client=mock_ai_client,
            cache=mock_cache,
            prompt_version="v2",
        )

        generator.generate(student, "Células", use_cache=False)

        mock_cache.get.assert_not_called()
        mock_ai_client.generate.assert_called_once()
