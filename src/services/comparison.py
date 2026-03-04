"""
Serviço de análise comparativa entre versões de prompts.

Gera conteúdo com todas as versões disponíveis para um mesmo aluno/tópico,
produzindo um relatório estruturado com métricas e observações.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import OUTPUTS_DIR
from src.models.student import Student
from src.generators.conceptual import ConceptualGenerator
from src.generators.practical import PracticalGenerator
from src.generators.reflection import ReflectionGenerator
from src.generators.visual import VisualGenerator
from src.prompts.engine import PromptEngine
from src.services.storage import StorageService, ContentRecord

logger = logging.getLogger(__name__)

GENERATOR_MAP = {
    "conceptual": ("Explicação Conceitual", ConceptualGenerator),
    "practical": ("Exemplos Práticos", PracticalGenerator),
    "reflection": ("Perguntas de Reflexão", ReflectionGenerator),
    "visual": ("Resumo Visual (ASCII)", VisualGenerator),
}


class ComparisonAnalysis:
    """
    Realiza análise comparativa entre versões de prompts.

    Gera o mesmo conteúdo com diferentes versões de prompts,
    calcula métricas e produz relatório detalhado.
    """

    def __init__(self):
        self.storage = StorageService()
        self.versions = PromptEngine.list_versions()

    def _compute_metrics(self, content: str) -> dict:
        """
        Calcula métricas quantitativas do conteúdo gerado.

        Args:
            content: Texto do conteúdo gerado.

        Returns:
            Dicionário com métricas.
        """
        lines = content.strip().split("\n")
        words = content.split()
        chars = len(content)

        # Conta elementos estruturais
        headings = sum(1 for line in lines if line.strip().startswith("#"))
        bullet_points = sum(
            1 for line in lines
            if line.strip().startswith(("- ", "* ", "• "))
        )
        numbered_items = sum(
            1 for line in lines
            if len(line.strip()) > 1 and line.strip()[0].isdigit()
            and line.strip()[1] in ".)"
        )
        emoji_count = sum(
            1 for ch in content if ord(ch) > 0x1F000
        )
        questions = content.count("?")
        examples_markers = sum(
            1 for marker in ["exemplo", "por exemplo", "como:", "imagine"]
            if marker in content.lower()
        )

        return {
            "total_chars": chars,
            "total_words": len(words),
            "total_lines": len(lines),
            "avg_words_per_line": round(len(words) / max(len(lines), 1), 1),
            "headings": headings,
            "bullet_points": bullet_points,
            "numbered_items": numbered_items,
            "emoji_count": emoji_count,
            "questions": questions,
            "example_markers": examples_markers,
        }

    def generate_comparison(
        self,
        student: Student,
        topic: str,
        content_type: str = "conceptual",
        versions: Optional[list[str]] = None,
    ) -> dict:
        """
        Gera conteúdo com múltiplas versões e compara.

        Args:
            student: Perfil do aluno.
            topic: Tópico educacional.
            content_type: Tipo de conteúdo a gerar.
            versions: Lista de versões a comparar (None = todas).

        Returns:
            Relatório de comparação com métricas.
        """
        if content_type not in GENERATOR_MAP:
            raise ValueError(
                f"Tipo inválido: {content_type}. "
                f"Use: {', '.join(GENERATOR_MAP.keys())}"
            )

        available_versions = [v["version"] for v in self.versions]
        target_versions = versions or available_versions

        invalid = [v for v in target_versions if v not in available_versions]
        if invalid:
            raise ValueError(f"Versões não encontradas: {invalid}")

        name, generator_cls = GENERATOR_MAP[content_type]
        results = {}

        for version in target_versions:
            logger.info("Gerando %s com %s...", content_type, version)
            generator = generator_cls(prompt_version=version)
            record = generator.generate(student, topic, use_cache=False)
            self.storage.save(record)

            metrics = self._compute_metrics(record.content)

            # Find version info
            version_info = next(
                v for v in self.versions if v["version"] == version
            )

            results[version] = {
                "version": version,
                "description": version_info["description"],
                "techniques": version_info["techniques"],
                "content": record.content,
                "prompt_used": record.prompt_used,
                "system_prompt_used": record.system_prompt_used,
                "metrics": metrics,
                "timestamp": record.timestamp,
            }

        # Build comparison report
        report = {
            "comparison_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "student": {
                "id": student.id,
                "name": student.name,
                "age": student.age,
                "knowledge_level": student.knowledge_level.value,
                "learning_style": student.learning_style.value,
            },
            "topic": topic,
            "content_type": content_type,
            "content_type_name": name,
            "versions_compared": target_versions,
            "results": results,
            "comparative_analysis": self._build_analysis(results),
            "generated_at": datetime.now().isoformat(),
        }

        return report

    def _build_analysis(self, results: dict) -> dict:
        """
        Constrói análise comparativa a partir dos resultados.

        Args:
            results: Resultados por versão.

        Returns:
            Análise comparativa com observações.
        """
        if len(results) < 2:
            return {"note": "Análise requer pelo menos 2 versões."}

        versions = list(results.keys())
        metrics_comparison = {}

        # Compare each metric across versions
        metric_keys = list(next(iter(results.values()))["metrics"].keys())
        for metric in metric_keys:
            values = {
                v: results[v]["metrics"][metric]
                for v in versions
            }
            sorted_versions = sorted(values, key=lambda x: values[x], reverse=True)
            metrics_comparison[metric] = {
                "values": values,
                "highest": sorted_versions[0],
                "lowest": sorted_versions[-1],
                "variation_pct": round(
                    (
                        (max(values.values()) - min(values.values()))
                        / max(max(values.values()), 1)
                    ) * 100,
                    1,
                ),
            }

        # Techniques evolution
        techniques_evolution = {
            v: {
                "count": len(results[v]["techniques"]),
                "techniques": results[v]["techniques"],
            }
            for v in versions
        }

        # Observations
        observations = []
        for v in versions[1:]:
            prev = versions[versions.index(v) - 1]
            word_diff = (
                results[v]["metrics"]["total_words"]
                - results[prev]["metrics"]["total_words"]
            )
            if word_diff > 0:
                observations.append(
                    f"{v} gerou {word_diff} palavras a mais que {prev}, "
                    f"indicando maior detalhamento."
                )
            elif word_diff < 0:
                observations.append(
                    f"{v} gerou {abs(word_diff)} palavras a menos que {prev}, "
                    f"indicando maior concisão."
                )

            struct_diff = (
                results[v]["metrics"]["headings"]
                + results[v]["metrics"]["bullet_points"]
            ) - (
                results[prev]["metrics"]["headings"]
                + results[prev]["metrics"]["bullet_points"]
            )
            if struct_diff > 0:
                observations.append(
                    f"{v} apresenta mais elementos estruturais ({struct_diff} a mais), "
                    f"melhorando a organização visual."
                )

        return {
            "metrics_comparison": metrics_comparison,
            "techniques_evolution": techniques_evolution,
            "observations": observations,
        }

    def save_report(self, report: dict, output_dir: Optional[Path] = None) -> str:
        """
        Salva o relatório de comparação em arquivo JSON.

        Args:
            report: Relatório de comparação.
            output_dir: Diretório de saída.

        Returns:
            Caminho do arquivo salvo.
        """
        directory = output_dir or OUTPUTS_DIR
        directory.mkdir(parents=True, exist_ok=True)

        filename = (
            f"comparison_{report['student']['id']}_"
            f"{report['topic'].lower().replace(' ', '_')[:30]}_"
            f"{report['comparison_id']}.json"
        )
        filepath = directory / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info("Relatório de comparação salvo: %s", filepath)
        return str(filepath)

    def format_report_text(self, report: dict) -> str:
        """
        Formata o relatório de comparação como texto legível.

        Args:
            report: Relatório de comparação.

        Returns:
            Texto formatado do relatório.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("  RELATÓRIO DE ANÁLISE COMPARATIVA DE PROMPTS")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"  Aluno: {report['student']['name']}")
        lines.append(f"  Idade: {report['student']['age']} anos")
        lines.append(f"  Nível: {report['student']['knowledge_level']}")
        lines.append(f"  Estilo: {report['student']['learning_style']}")
        lines.append(f"  Tópico: {report['topic']}")
        lines.append(f"  Tipo: {report['content_type_name']}")
        lines.append(f"  Versões: {', '.join(report['versions_compared'])}")
        lines.append(f"  Data: {report['generated_at']}")
        lines.append("")

        # Content per version
        for version, data in report["results"].items():
            lines.append("-" * 70)
            lines.append(f"  📌 VERSÃO: {version} — {data['description']}")
            lines.append(f"  Técnicas: {', '.join(data['techniques'])}")
            lines.append("-" * 70)
            lines.append("")
            lines.append(data["content"])
            lines.append("")

            # Metrics
            m = data["metrics"]
            lines.append(f"  📊 Métricas: {m['total_words']} palavras | "
                         f"{m['total_lines']} linhas | "
                         f"{m['headings']} títulos | "
                         f"{m['bullet_points']} tópicos | "
                         f"{m['questions']} perguntas")
            lines.append("")

        # Comparative analysis
        analysis = report.get("comparative_analysis", {})
        if analysis.get("observations"):
            lines.append("=" * 70)
            lines.append("  📈 ANÁLISE COMPARATIVA")
            lines.append("=" * 70)
            lines.append("")
            for obs in analysis["observations"]:
                lines.append(f"  • {obs}")
            lines.append("")

        # Techniques evolution
        if analysis.get("techniques_evolution"):
            lines.append("  📋 Evolução das Técnicas:")
            for v, info in analysis["techniques_evolution"].items():
                lines.append(
                    f"    {v}: {info['count']} técnicas — "
                    f"{', '.join(info['techniques'])}"
                )
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)
