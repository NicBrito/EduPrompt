"""
Interface Web Flask do EduPrompt.

Fornece uma interface web simples para interagir com o sistema
de geração de conteúdo educacional.
"""

import json
import logging
from flask import Flask, render_template, request, jsonify

from src.config import Config, STUDENTS_FILE, TEMPLATES_DIR
from src.models.student import StudentRepository
from src.generators.conceptual import ConceptualGenerator
from src.generators.practical import PracticalGenerator
from src.generators.reflection import ReflectionGenerator
from src.generators.visual import VisualGenerator
from src.prompts.engine import PromptEngine
from src.services.ai_client import AIClientError
from src.services.cache import CacheManager
from src.services.storage import StorageService
from src.services.comparison import ComparisonAnalysis

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(TEMPLATES_DIR / "static"),
)

# Serviços compartilhados
repo = StudentRepository(STUDENTS_FILE)
storage = StorageService()
cache = CacheManager()

# Mapeamento de geradores
GENERATORS = {
    "explicacao_conceitual": ConceptualGenerator,
    "exemplos_praticos": PracticalGenerator,
    "perguntas_reflexao": ReflectionGenerator,
    "resumo_visual": VisualGenerator,
}

CONTENT_LABELS = {
    "explicacao_conceitual": "Explicação Conceitual",
    "exemplos_praticos": "Exemplos Práticos",
    "perguntas_reflexao": "Perguntas de Reflexão",
    "resumo_visual": "Resumo Visual (ASCII)",
}


@app.route("/")
def index():
    """Página principal."""
    students = repo.load_all()
    versions = PromptEngine.list_versions()

    return render_template(
        "index.html",
        students=[s.to_dict() for s in students],
        content_types=CONTENT_LABELS,
        versions=versions,
        provider=Config.AI_PROVIDER,
        model=Config.AI_MODEL,
    )


@app.route("/api/generate", methods=["POST"])
def generate():
    """Endpoint para gerar conteúdo via API."""
    try:
        data = request.get_json()

        student_id = data.get("student_id")
        topic = data.get("topic", "").strip()
        content_type = data.get("content_type")
        prompt_version = data.get("prompt_version", "v2")

        # Validações
        if not student_id:
            return jsonify({"error": "Selecione um aluno."}), 400
        if not topic:
            return jsonify({"error": "Informe um tópico."}), 400
        if len(topic) > 200:
            return jsonify({"error": "Tópico muito longo (máx. 200 caracteres)."}), 400
        if content_type not in GENERATORS:
            return jsonify({"error": "Tipo de conteúdo inválido."}), 400

        # Busca aluno
        student = repo.get_by_id(student_id)
        if not student:
            return jsonify({"error": f"Aluno '{student_id}' não encontrado."}), 404

        # Gera conteúdo
        generator_cls = GENERATORS[content_type]
        generator = generator_cls(prompt_version=prompt_version)
        record = generator.generate(student, topic)

        # Salva
        storage.save(record)

        return jsonify({
            "success": True,
            "content": record.content,
            "content_type": CONTENT_LABELS.get(content_type, content_type),
            "student_name": student.name,
            "topic": topic,
            "prompt_version": prompt_version,
            "timestamp": record.timestamp,
        })

    except AIClientError as e:
        return jsonify({"error": f"Erro na API de IA: {str(e)}"}), 502
    except Exception as e:
        logger.exception("Erro ao gerar conteúdo")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@app.route("/api/generate-all", methods=["POST"])
def generate_all():
    """Endpoint para gerar todos os 4 tipos de conteúdo."""
    try:
        data = request.get_json()

        student_id = data.get("student_id")
        topic = data.get("topic", "").strip()
        prompt_version = data.get("prompt_version", "v2")

        if not student_id:
            return jsonify({"error": "Selecione um aluno."}), 400
        if not topic:
            return jsonify({"error": "Informe um tópico."}), 400

        student = repo.get_by_id(student_id)
        if not student:
            return jsonify({"error": f"Aluno '{student_id}' não encontrado."}), 404

        results = {}
        records = []

        for content_type, generator_cls in GENERATORS.items():
            generator = generator_cls(prompt_version=prompt_version)
            record = generator.generate(student, topic)
            records.append(record)
            results[content_type] = {
                "label": CONTENT_LABELS[content_type],
                "content": record.content,
            }

        # Salva geração completa
        filepath = storage.save_complete_generation(
            student_id=student.id,
            topic=topic,
            records=records,
        )

        return jsonify({
            "success": True,
            "results": results,
            "student_name": student.name,
            "topic": topic,
            "prompt_version": prompt_version,
            "filepath": filepath,
        })

    except AIClientError as e:
        return jsonify({"error": f"Erro na API de IA: {str(e)}"}), 502
    except Exception as e:
        logger.exception("Erro ao gerar conteúdo")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@app.route("/api/students")
def list_students():
    """Lista todos os perfis de alunos."""
    students = repo.load_all()
    return jsonify([s.to_dict() for s in students])


@app.route("/api/history")
def list_history():
    """Lista o histórico de gerações."""
    outputs = storage.list_outputs()
    return jsonify(outputs)


@app.route("/api/cache/stats")
def cache_stats():
    """Retorna estatísticas do cache."""
    stats = cache.stats()
    return jsonify(stats)


@app.route("/api/cache/clear", methods=["POST"])
def clear_cache():
    """Limpa o cache."""
    removed = cache.clear()
    return jsonify({"removed": removed})


@app.route("/api/compare", methods=["POST"])
def compare_versions():
    """
    Endpoint para análise comparativa entre versões de prompts.

    Gera o mesmo conteúdo com todas as versões disponíveis e retorna
    relatório com métricas e observações comparativas.
    """
    try:
        data = request.get_json()

        student_id = data.get("student_id")
        topic = data.get("topic", "").strip()
        content_type = data.get("content_type", "explicacao_conceitual")
        prompt_version = data.get("prompt_version")

        if not student_id:
            return jsonify({"error": "Selecione um aluno."}), 400
        if not topic:
            return jsonify({"error": "Informe um tópico."}), 400
        if len(topic) > 200:
            return jsonify({"error": "Tópico muito longo (máx. 200 caracteres)."}), 400

        student = repo.get_by_id(student_id)
        if not student:
            return jsonify({"error": f"Aluno '{student_id}' não encontrado."}), 404

        # Map Flask content types to comparison module types
        type_mapping = {
            "explicacao_conceitual": "conceptual",
            "exemplos_praticos": "practical",
            "perguntas_reflexao": "reflection",
            "resumo_visual": "visual",
        }
        comp_type = type_mapping.get(content_type, "conceptual")

        analyzer = ComparisonAnalysis()
        report = analyzer.generate_comparison(
            student=student,
            topic=topic,
            content_type=comp_type,
        )

        # Save report
        filepath = analyzer.save_report(report)

        return jsonify({
            "success": True,
            "report": report,
            "filepath": filepath,
        })

    except AIClientError as e:
        return jsonify({"error": f"Erro na API de IA: {str(e)}"}), 502
    except Exception as e:
        logger.exception("Erro na análise comparativa")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


def run_web():
    """Inicia o servidor Flask."""
    print(f"\n🌐 Servidor web iniciando em http://localhost:{Config.FLASK_PORT}")
    print(f"   Provedor: {Config.AI_PROVIDER} | Modelo: {Config.AI_MODEL}")
    print(f"   Pressione Ctrl+C para parar\n")

    app.run(
        host="0.0.0.0",
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )


if __name__ == "__main__":
    run_web()
