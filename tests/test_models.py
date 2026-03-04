"""
Testes do modelo Student e StudentRepository.
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.models.student import (
    Student,
    StudentRepository,
    KnowledgeLevel,
    LearningStyle,
)


class TestStudent:
    """Testes da classe Student."""

    def test_create_student(self):
        """Testa criação de aluno com dados válidos."""
        student = Student(
            name="João",
            age=15,
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            learning_style=LearningStyle.VISUAL,
            interests=["matemática", "jogos"],
        )

        assert student.name == "João"
        assert student.age == 15
        assert student.knowledge_level == KnowledgeLevel.INTERMEDIATE
        assert student.learning_style == LearningStyle.VISUAL
        assert student.id == "joão"

    def test_create_student_from_string_enums(self):
        """Testa criação com strings ao invés de enums."""
        student = Student(
            name="Maria",
            age=20,
            knowledge_level="avançado",
            learning_style="cinestésico",
        )

        assert student.knowledge_level == KnowledgeLevel.ADVANCED
        assert student.learning_style == LearningStyle.KINESTHETIC

    def test_invalid_age_raises_error(self):
        """Testa que idade inválida gera erro."""
        with pytest.raises(ValueError, match="Idade inválida"):
            Student(
                name="Teste",
                age=3,
                knowledge_level=KnowledgeLevel.BEGINNER,
                learning_style=LearningStyle.VISUAL,
            )

    def test_to_dict(self):
        """Testa conversão para dicionário."""
        student = Student(
            name="Ana",
            age=12,
            knowledge_level=KnowledgeLevel.BEGINNER,
            learning_style=LearningStyle.VISUAL,
            interests=["desenho"],
        )

        data = student.to_dict()

        assert data["name"] == "Ana"
        assert data["age"] == 12
        assert data["knowledge_level"] == "iniciante"
        assert data["learning_style"] == "visual"
        assert data["interests"] == ["desenho"]

    def test_from_dict(self):
        """Testa criação a partir de dicionário."""
        data = {
            "name": "Carlos",
            "age": 17,
            "knowledge_level": "intermediário",
            "learning_style": "leitura-escrita",
            "interests": ["programação"],
            "id": "carlos_123",
        }

        student = Student.from_dict(data)

        assert student.name == "Carlos"
        assert student.id == "carlos_123"
        assert student.knowledge_level == KnowledgeLevel.INTERMEDIATE

    def test_describe(self):
        """Testa descrição textual do aluno."""
        student = Student(
            name="Pedro",
            age=9,
            knowledge_level=KnowledgeLevel.BEGINNER,
            learning_style=LearningStyle.AUDITORY,
            interests=["dinossauros"],
        )

        desc = student.describe()

        assert "Pedro" in desc
        assert "9 anos" in desc
        assert "dinossauros" in desc

    def test_roundtrip_dict(self):
        """Testa que to_dict → from_dict preserva os dados."""
        original = Student(
            name="Lúcia",
            age=20,
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            learning_style=LearningStyle.VISUAL,
            interests=["design", "tecnologia"],
        )

        reconstructed = Student.from_dict(original.to_dict())

        assert reconstructed.name == original.name
        assert reconstructed.age == original.age
        assert reconstructed.knowledge_level == original.knowledge_level
        assert reconstructed.learning_style == original.learning_style
        assert reconstructed.interests == original.interests


class TestStudentRepository:
    """Testes do repositório de alunos."""

    def _create_temp_repo(self):
        """Cria um repositório temporário para testes."""
        tmpdir = tempfile.mkdtemp()
        filepath = Path(tmpdir) / "students.json"
        return StudentRepository(filepath)

    def test_load_empty(self):
        """Testa carregamento quando não há arquivo."""
        repo = self._create_temp_repo()
        students = repo.load_all()
        assert students == []

    def test_save_and_load(self):
        """Testa salvar e carregar alunos."""
        repo = self._create_temp_repo()

        students = [
            Student("Alice", 14, KnowledgeLevel.BEGINNER, LearningStyle.VISUAL),
            Student("Bob", 18, KnowledgeLevel.ADVANCED, LearningStyle.READING_WRITING),
        ]

        repo.save_all(students)
        loaded = repo.load_all()

        assert len(loaded) == 2
        assert loaded[0].name == "Alice"
        assert loaded[1].name == "Bob"

    def test_get_by_id(self):
        """Testa busca por ID."""
        repo = self._create_temp_repo()

        students = [
            Student("Alice", 14, KnowledgeLevel.BEGINNER, LearningStyle.VISUAL, id="alice_1"),
        ]
        repo.save_all(students)

        found = repo.get_by_id("alice_1")
        assert found is not None
        assert found.name == "Alice"

        not_found = repo.get_by_id("inexistente")
        assert not_found is None

    def test_add_student(self):
        """Testa adição de novo aluno."""
        repo = self._create_temp_repo()

        student = Student("Carlos", 17, KnowledgeLevel.INTERMEDIATE, LearningStyle.AUDITORY)
        repo.add(student)

        loaded = repo.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "Carlos"

    def test_add_duplicate_raises_error(self):
        """Testa que adicionar duplicata gera erro."""
        repo = self._create_temp_repo()

        student = Student("Carlos", 17, KnowledgeLevel.INTERMEDIATE, LearningStyle.AUDITORY)
        repo.add(student)

        with pytest.raises(ValueError, match="já existe"):
            repo.add(student)
