"""
Serviço de persistência de conteúdo gerado.

Salva e carrega conteúdo educacional gerado em arquivos JSON
com timestamp, permitindo histórico e comparação.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import OUTPUTS_DIR

logger = logging.getLogger(__name__)


class ContentRecord:
    """Representa um registro de conteúdo gerado."""

    def __init__(
        self,
        student_id: str,
        topic: str,
        content_type: str,
        content: str,
        prompt_version: str,
        prompt_used: str,
        system_prompt_used: str,
        provider: str,
        model: str,
        timestamp: Optional[str] = None,
    ):
        self.student_id = student_id
        self.topic = topic
        self.content_type = content_type
        self.content = content
        self.prompt_version = prompt_version
        self.prompt_used = prompt_used
        self.system_prompt_used = system_prompt_used
        self.provider = provider
        self.model = model
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Converte o registro para dicionário."""
        return {
            "student_id": self.student_id,
            "topic": self.topic,
            "content_type": self.content_type,
            "content": self.content,
            "prompt_version": self.prompt_version,
            "prompt_used": self.prompt_used,
            "system_prompt_used": self.system_prompt_used,
            "provider": self.provider,
            "model": self.model,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentRecord":
        """Cria um ContentRecord a partir de um dicionário."""
        return cls(**data)


class StorageService:
    """
    Gerencia a persistência e recuperação de conteúdo gerado.

    Organiza os arquivos JSON por aluno e data, permitindo
    consultas históricas e comparações entre versões de prompts.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or OUTPUTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_student_file(self, student_id: str) -> Path:
        """Retorna o caminho do arquivo de histórico do aluno."""
        return self.output_dir / f"{student_id}_history.json"

    def save(self, record: ContentRecord) -> str:
        """
        Salva um registro de conteúdo gerado.

        Args:
            record: O registro de conteúdo a ser salvo.

        Returns:
            O caminho do arquivo salvo.
        """
        filepath = self._get_student_file(record.student_id)

        # Carrega histórico existente ou cria novo
        history = self._load_history(filepath)
        history["records"].append(record.to_dict())
        history["last_updated"] = datetime.now().isoformat()
        history["total_records"] = len(history["records"])

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        logger.info(
            "Conteúdo salvo: %s/%s/%s",
            record.student_id,
            record.topic,
            record.content_type,
        )
        return str(filepath)

    def save_complete_generation(
        self,
        student_id: str,
        topic: str,
        records: list[ContentRecord],
    ) -> str:
        """
        Salva uma geração completa (4 tipos de conteúdo) em um arquivo único.

        Args:
            student_id: ID do aluno.
            topic: Tópico ensinado.
            records: Lista de registros de conteúdo gerados.

        Returns:
            Caminho do arquivo salvo.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.lower().replace(" ", "_")[:30]
        filename = f"{student_id}_{safe_topic}_{timestamp}.json"
        filepath = self.output_dir / filename

        output = {
            "student_id": student_id,
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "contents": {r.content_type: r.to_dict() for r in records},
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        # Também adiciona ao histórico do aluno
        for record in records:
            self.save(record)

        logger.info("Geração completa salva: %s", filepath)
        return str(filepath)

    def _load_history(self, filepath: Path) -> dict:
        """Carrega o histórico de um arquivo JSON ou cria estrutura vazia."""
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, KeyError):
                logger.warning("Histórico corrompido, criando novo: %s", filepath)

        return {
            "records": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_records": 0,
        }

    def get_history(
        self,
        student_id: str,
        content_type: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> list[ContentRecord]:
        """
        Recupera o histórico de conteúdo gerado para um aluno.

        Args:
            student_id: ID do aluno.
            content_type: Filtro por tipo de conteúdo (opcional).
            topic: Filtro por tópico (opcional).

        Returns:
            Lista de registros de conteúdo.
        """
        filepath = self._get_student_file(student_id)
        history = self._load_history(filepath)

        records = [ContentRecord.from_dict(r) for r in history["records"]]

        if content_type:
            records = [r for r in records if r.content_type == content_type]
        if topic:
            records = [r for r in records if r.topic.lower() == topic.lower()]

        return records

    def compare_versions(
        self,
        student_id: str,
        topic: str,
        content_type: str,
    ) -> list[dict]:
        """
        Compara diferentes versões de prompts para o mesmo conteúdo.

        Args:
            student_id: ID do aluno.
            topic: Tópico ensinado.
            content_type: Tipo de conteúdo a comparar.

        Returns:
            Lista de registros agrupados por versão de prompt.
        """
        records = self.get_history(student_id, content_type, topic)

        versions = {}
        for record in records:
            version = record.prompt_version
            if version not in versions:
                versions[version] = []
            versions[version].append(record.to_dict())

        return [
            {"version": v, "records": r, "count": len(r)}
            for v, r in versions.items()
        ]

    def list_outputs(self) -> list[dict]:
        """Lista todos os arquivos de output com informações básicas."""
        outputs = []
        for filepath in sorted(self.output_dir.glob("*.json")):
            if filepath.name.endswith("_history.json"):
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                outputs.append({
                    "filename": filepath.name,
                    "student_id": data.get("student_id", "?"),
                    "topic": data.get("topic", "?"),
                    "generated_at": data.get("generated_at", "?"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return outputs
