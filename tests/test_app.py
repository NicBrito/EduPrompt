"""
Testes dos endpoints da interface web Flask.

Utiliza o test client do Flask para validar rotas,
status codes, validações e respostas JSON.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.app import app
from src.models.student import Student, KnowledgeLevel, LearningStyle


@pytest.fixture
def client():
    """Cria um test client Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_student():
    """Aluno de exemplo para testes."""
    return Student(
        name="Ana Silva",
        age=12,
        knowledge_level=KnowledgeLevel.BEGINNER,
        learning_style=LearningStyle.VISUAL,
        interests=["natureza"],
    )


class TestIndexRoute:
    """Testes da página principal."""

    def test_index_returns_200(self, client):
        """Testa que a página principal retorna status 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_html(self, client):
        """Testa que a resposta contém conteúdo HTML."""
        response = client.get("/")
        assert b"EduPrompt" in response.data


class TestStudentsAPI:
    """Testes do endpoint de alunos."""

    def test_list_students_returns_json(self, client):
        """Testa que a listagem de alunos retorna JSON."""
        response = client.get("/api/students")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_list_students_has_profiles(self, client):
        """Testa que existem perfis cadastrados."""
        response = client.get("/api/students")
        data = response.get_json()
        assert len(data) > 0
        assert "name" in data[0]
        assert "age" in data[0]


class TestGenerateAPI:
    """Testes do endpoint de geração de conteúdo."""

    def test_generate_requires_student_id(self, client):
        """Testa que student_id é obrigatório."""
        response = client.post(
            "/api/generate",
            json={"topic": "Fotossíntese", "content_type": "explicacao_conceitual"},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_generate_requires_topic(self, client):
        """Testa que topic é obrigatório."""
        response = client.post(
            "/api/generate",
            json={"student_id": "ana_silva", "content_type": "explicacao_conceitual"},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_generate_rejects_empty_topic(self, client):
        """Testa que topic vazio é rejeitado."""
        response = client.post(
            "/api/generate",
            json={
                "student_id": "ana_silva",
                "topic": "   ",
                "content_type": "explicacao_conceitual",
            },
        )
        assert response.status_code == 400

    def test_generate_rejects_long_topic(self, client):
        """Testa que tópico muito longo é rejeitado (máx. 200 caracteres)."""
        response = client.post(
            "/api/generate",
            json={
                "student_id": "ana_silva",
                "topic": "x" * 201,
                "content_type": "explicacao_conceitual",
            },
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "200" in data["error"]

    def test_generate_rejects_invalid_content_type(self, client):
        """Testa que tipos de conteúdo inválidos são rejeitados."""
        response = client.post(
            "/api/generate",
            json={
                "student_id": "ana_silva",
                "topic": "Fotossíntese",
                "content_type": "tipo_invalido",
            },
        )
        assert response.status_code == 400

    def test_generate_rejects_unknown_student(self, client):
        """Testa que aluno inexistente retorna 404."""
        response = client.post(
            "/api/generate",
            json={
                "student_id": "aluno_inexistente",
                "topic": "Fotossíntese",
                "content_type": "explicacao_conceitual",
            },
        )
        assert response.status_code == 404

    @patch("src.app.storage")
    @patch("src.app.GENERATORS")
    def test_generate_success(self, mock_generators, mock_storage, client):
        """Testa geração bem-sucedida com mock da API."""
        mock_record = MagicMock()
        mock_record.content = "Conteúdo gerado"
        mock_record.timestamp = "2025-01-01T00:00:00"

        mock_gen_cls = MagicMock()
        mock_instance = MagicMock()
        mock_instance.generate.return_value = mock_record
        mock_gen_cls.return_value = mock_instance

        mock_generators.__contains__ = lambda self, key: key == "explicacao_conceitual"
        mock_generators.__getitem__ = lambda self, key: mock_gen_cls
        mock_storage.save.return_value = "/fake/path"

        response = client.post(
            "/api/generate",
            json={
                "student_id": "ana_silva",
                "topic": "Fotossíntese",
                "content_type": "explicacao_conceitual",
                "prompt_version": "v2",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["content"] == "Conteúdo gerado"
        assert data["student_name"] == "Ana Silva"


class TestGenerateAllAPI:
    """Testes do endpoint de geração completa."""

    def test_generate_all_requires_student_id(self, client):
        """Testa que student_id é obrigatório."""
        response = client.post(
            "/api/generate-all",
            json={"topic": "Fotossíntese"},
        )
        assert response.status_code == 400

    def test_generate_all_requires_topic(self, client):
        """Testa que topic é obrigatório."""
        response = client.post(
            "/api/generate-all",
            json={"student_id": "ana_silva"},
        )
        assert response.status_code == 400


class TestCacheAPI:
    """Testes dos endpoints de cache."""

    def test_cache_stats_returns_json(self, client):
        """Testa que estatísticas do cache retornam JSON."""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert "total_entries" in data
        assert "valid_entries" in data

    def test_cache_clear_returns_count(self, client):
        """Testa que limpar cache retorna contagem."""
        response = client.post("/api/cache/clear")
        assert response.status_code == 200
        data = response.get_json()
        assert "removed" in data


class TestHistoryAPI:
    """Testes do endpoint de histórico."""

    def test_history_returns_list(self, client):
        """Testa que o histórico retorna uma lista."""
        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestCompareAPI:
    """Testes do endpoint de análise comparativa."""

    def test_compare_requires_student_id(self, client):
        """Testa que student_id é obrigatório."""
        response = client.post(
            "/api/compare",
            json={"topic": "Fotossíntese"},
        )
        assert response.status_code == 400

    def test_compare_requires_topic(self, client):
        """Testa que topic é obrigatório."""
        response = client.post(
            "/api/compare",
            json={"student_id": "ana_silva"},
        )
        assert response.status_code == 400

    def test_compare_rejects_long_topic(self, client):
        """Testa que tópico muito longo é rejeitado."""
        response = client.post(
            "/api/compare",
            json={
                "student_id": "ana_silva",
                "topic": "x" * 201,
            },
        )
        assert response.status_code == 400

    def test_compare_rejects_unknown_student(self, client):
        """Testa que aluno inexistente retorna 404."""
        response = client.post(
            "/api/compare",
            json={
                "student_id": "aluno_inexistente",
                "topic": "Fotossíntese",
            },
        )
        assert response.status_code == 404
