"""
Testes do serviço de análise comparativa.

Testa métricas, formatação de relatório e validações
sem chamar a API real.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.models.student import Student, KnowledgeLevel, LearningStyle
from src.services.comparison import ComparisonAnalysis


class TestComparisonMetrics:
    """Testes das métricas de conteúdo."""

    def setup_method(self):
        """Inicializa o analisador."""
        self.analyzer = ComparisonAnalysis()

    def test_compute_metrics_word_count(self):
        """Testa a contagem de palavras."""
        metrics = self.analyzer._compute_metrics("Uma frase com cinco palavras")
        assert metrics["total_words"] == 5

    def test_compute_metrics_line_count(self):
        """Testa a contagem de linhas."""
        metrics = self.analyzer._compute_metrics("Linha 1\nLinha 2\nLinha 3")
        assert metrics["total_lines"] == 3

    def test_compute_metrics_headings(self):
        """Testa a contagem de títulos markdown."""
        content = "# Título\n\nTexto\n\n## Subtítulo\n\nMais texto"
        metrics = self.analyzer._compute_metrics(content)
        assert metrics["headings"] == 2

    def test_compute_metrics_bullet_points(self):
        """Testa a contagem de marcadores."""
        content = "Lista:\n- Item 1\n- Item 2\n* Item 3\n• Item 4"
        metrics = self.analyzer._compute_metrics(content)
        assert metrics["bullet_points"] == 4

    def test_compute_metrics_questions(self):
        """Testa a contagem de perguntas."""
        content = "O que é? Como funciona? Por quê?"
        metrics = self.analyzer._compute_metrics(content)
        assert metrics["questions"] == 3

    def test_compute_metrics_empty_content(self):
        """Testa métricas com conteúdo vazio."""
        metrics = self.analyzer._compute_metrics("")
        assert metrics["total_words"] == 0
        assert metrics["total_chars"] == 0


class TestComparisonAnalysis:
    """Testes da análise comparativa."""

    @pytest.fixture
    def student(self):
        """Aluno de exemplo."""
        return Student(
            name="Teste",
            age=12,
            knowledge_level=KnowledgeLevel.BEGINNER,
            learning_style=LearningStyle.VISUAL,
            interests=["ciência"],
        )

    def test_invalid_content_type_raises(self, student):
        """Testa que tipo de conteúdo inválido lança ValueError."""
        analyzer = ComparisonAnalysis()
        with pytest.raises(ValueError, match="Tipo inválido"):
            analyzer.generate_comparison(
                student=student,
                topic="Fotossíntese",
                content_type="tipo_invalido",
            )

    def test_invalid_version_raises(self, student):
        """Testa que versão inexistente lança ValueError."""
        analyzer = ComparisonAnalysis()
        with pytest.raises(ValueError, match="Versões não encontradas"):
            analyzer.generate_comparison(
                student=student,
                topic="Fotossíntese",
                content_type="conceptual",
                versions=["v99"],
            )

    def test_build_analysis_requires_two_versions(self):
        """Testa que análise requer pelo menos 2 versões."""
        analyzer = ComparisonAnalysis()
        result = analyzer._build_analysis({"v1": {"metrics": {}}})
        assert "note" in result

    def test_format_report_text(self):
        """Testa a formatação do relatório como texto."""
        analyzer = ComparisonAnalysis()
        report = {
            "student": {
                "name": "Teste",
                "age": 12,
                "knowledge_level": "iniciante",
                "learning_style": "visual",
            },
            "topic": "Fotossíntese",
            "content_type_name": "Explicação Conceitual",
            "versions_compared": ["v1", "v2"],
            "generated_at": "2025-01-01T00:00:00",
            "results": {
                "v1": {
                    "description": "Baseline",
                    "techniques": ["role-playing"],
                    "content": "Conteúdo v1",
                    "metrics": {
                        "total_words": 10,
                        "total_lines": 3,
                        "headings": 1,
                        "bullet_points": 0,
                        "questions": 0,
                    },
                },
                "v2": {
                    "description": "Otimizada",
                    "techniques": ["role-playing", "chain-of-thought"],
                    "content": "Conteúdo v2 mais elaborado",
                    "metrics": {
                        "total_words": 15,
                        "total_lines": 5,
                        "headings": 2,
                        "bullet_points": 3,
                        "questions": 1,
                    },
                },
            },
            "comparative_analysis": {
                "observations": ["v2 gerou 5 palavras a mais que v1"],
                "techniques_evolution": {
                    "v1": {"count": 1, "techniques": ["role-playing"]},
                    "v2": {"count": 2, "techniques": ["role-playing", "chain-of-thought"]},
                },
            },
        }

        text = analyzer.format_report_text(report)
        assert "RELATÓRIO" in text
        assert "Fotossíntese" in text
        assert "v1" in text
        assert "v2" in text
        assert "ANÁLISE COMPARATIVA" in text
