"""
Modelo de perfil de aluno.

Define a estrutura de dados para representar alunos com suas
características de aprendizado.
"""

import json
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Optional


class KnowledgeLevel(str, Enum):
    """Nível de conhecimento do aluno."""
    BEGINNER = "iniciante"
    INTERMEDIATE = "intermediário"
    ADVANCED = "avançado"


class LearningStyle(str, Enum):
    """Estilo de aprendizado do aluno."""
    VISUAL = "visual"
    AUDITORY = "auditivo"
    READING_WRITING = "leitura-escrita"
    KINESTHETIC = "cinestésico"


@dataclass
class Student:
    """Representa o perfil de um aluno."""

    name: str
    age: int
    knowledge_level: KnowledgeLevel
    learning_style: LearningStyle
    interests: list[str] = field(default_factory=list)
    id: Optional[str] = None

    def __post_init__(self):
        """Valida e normaliza os dados do aluno."""
        if self.id is None:
            self.id = self.name.lower().replace(" ", "_")

        # Permitir strings e converter para enums
        if isinstance(self.knowledge_level, str):
            self.knowledge_level = KnowledgeLevel(self.knowledge_level)
        if isinstance(self.learning_style, str):
            self.learning_style = LearningStyle(self.learning_style)

        if self.age < 5 or self.age > 100:
            raise ValueError(f"Idade inválida: {self.age}. Deve estar entre 5 e 100.")

    def to_dict(self) -> dict:
        """Converte o perfil para dicionário."""
        data = asdict(self)
        data["knowledge_level"] = self.knowledge_level.value
        data["learning_style"] = self.learning_style.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Cria um Student a partir de um dicionário."""
        return cls(
            name=data["name"],
            age=data["age"],
            knowledge_level=data["knowledge_level"],
            learning_style=data["learning_style"],
            interests=data.get("interests", []),
            id=data.get("id"),
        )

    def describe(self) -> str:
        """Retorna uma descrição textual do aluno para uso em prompts."""
        style_descriptions = {
            LearningStyle.VISUAL: "aprende melhor com imagens, diagramas e representações visuais",
            LearningStyle.AUDITORY: "aprende melhor ouvindo explicações e discussões",
            LearningStyle.READING_WRITING: "aprende melhor lendo textos e escrevendo anotações",
            LearningStyle.KINESTHETIC: "aprende melhor com exemplos práticos e atividades hands-on",
        }

        level_descriptions = {
            KnowledgeLevel.BEGINNER: "está começando a aprender o assunto",
            KnowledgeLevel.INTERMEDIATE: "já tem noções básicas do assunto",
            KnowledgeLevel.ADVANCED: "tem bom domínio do assunto e busca aprofundamento",
        }

        desc = (
            f"{self.name} tem {self.age} anos, "
            f"{level_descriptions[self.knowledge_level]} e "
            f"{style_descriptions[self.learning_style]}."
        )

        if self.interests:
            desc += f" Seus interesses incluem: {', '.join(self.interests)}."

        return desc


class StudentRepository:
    """Gerencia a persistência dos perfis de alunos."""

    def __init__(self, filepath: Path):
        self.filepath = filepath

    def load_all(self) -> list[Student]:
        """Carrega todos os perfis de alunos do arquivo JSON."""
        if not self.filepath.exists():
            return []

        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Student.from_dict(s) for s in data.get("students", [])]

    def save_all(self, students: list[Student]) -> None:
        """Salva todos os perfis de alunos no arquivo JSON."""
        data = {"students": [s.to_dict() for s in students]}

        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """Busca um aluno pelo ID."""
        students = self.load_all()
        for student in students:
            if student.id == student_id:
                return student
        return None

    def add(self, student: Student) -> None:
        """Adiciona um novo perfil de aluno."""
        students = self.load_all()
        # Verifica duplicidade
        if any(s.id == student.id for s in students):
            raise ValueError(f"Aluno com ID '{student.id}' já existe.")
        students.append(student)
        self.save_all(students)
