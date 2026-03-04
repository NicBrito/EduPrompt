"""
Interface de Linha de Comando (CLI) do EduPrompt.

Permite selecionar aluno, tópico e tipo de conteúdo,
além de gerenciar cache e comparar versões de prompts.
"""

import sys
import logging
from typing import Optional

from src.config import Config, STUDENTS_FILE
from src.models.student import Student, StudentRepository
from src.generators.conceptual import ConceptualGenerator
from src.generators.practical import PracticalGenerator
from src.generators.reflection import ReflectionGenerator
from src.generators.visual import VisualGenerator
from src.generators.base import ContentGenerator
from src.prompts.engine import PromptEngine
from src.services.ai_client import AIClient, AIClientError
from src.services.cache import CacheManager
from src.services.storage import StorageService, ContentRecord
from src.services.comparison import ComparisonAnalysis
from src.utils.helpers import setup_logging, safe_input

logger = logging.getLogger(__name__)

# Mapeamento dos tipos de conteúdo para seus geradores
CONTENT_GENERATORS = {
    "1": ("Explicação Conceitual", ConceptualGenerator),
    "2": ("Exemplos Práticos", PracticalGenerator),
    "3": ("Perguntas de Reflexão", ReflectionGenerator),
    "4": ("Resumo Visual (ASCII)", VisualGenerator),
}


class CLI:
    """Interface de linha de comando do EduPrompt."""

    def __init__(self):
        self.repo = StudentRepository(STUDENTS_FILE)
        self.storage = StorageService()
        self.cache = CacheManager()
        self.current_version = "v2"

    def run(self) -> None:
        """Loop principal da CLI."""
        setup_logging("INFO")
        self._print_header()

        # Valida configuração
        warnings = Config.validate()
        if warnings:
            print("\n⚠️  Avisos de configuração:")
            for w in warnings:
                print(f"   - {w}")
            print()

        while True:
            self._print_menu()
            choice = safe_input("\n→ Escolha uma opção: ")

            actions = {
                "1": self._generate_content,
                "2": self._generate_all_content,
                "3": self._list_students,
                "4": self._compare_versions,
                "5": self._view_history,
                "6": self._manage_cache,
                "7": self._change_prompt_version,
                "8": self._run_comparison_analysis,
                "0": self._exit,
            }

            action = actions.get(choice)
            if action:
                try:
                    action()
                except AIClientError as e:
                    print(f"\n❌ Erro na API: {e}")
                except Exception as e:
                    logger.exception("Erro inesperado")
                    print(f"\n❌ Erro inesperado: {e}")
            else:
                print("\n⚠️  Opção inválida. Tente novamente.")

    def _print_header(self) -> None:
        """Imprime o cabeçalho da aplicação."""
        print("\n" + "=" * 60)
        print("   📚 EduPrompt — Plataforma Educativa com IA")
        print("   Gerador de conteúdo personalizado por aluno")
        print("=" * 60)
        print(f"   Provedor: {Config.AI_PROVIDER} | Modelo: {Config.AI_MODEL}")
        print(f"   Versão de prompts: {self.current_version}")
        print("=" * 60)

    def _print_menu(self) -> None:
        """Imprime o menu principal."""
        print("\n┌─────────────────────────────────┐")
        print("│        MENU PRINCIPAL           │")
        print("├─────────────────────────────────┤")
        print("│  1. Gerar conteúdo específico   │")
        print("│  2. Gerar todos os conteúdos    │")
        print("│  3. Listar perfis de alunos     │")
        print("│  4. Comparar versões de prompt  │")
        print("│  5. Ver histórico de geração    │")
        print("│  6. Gerenciar cache             │")
        print("│  7. Trocar versão de prompts    │")
        print("│  8. Análise comparativa completa│")
        print("│  0. Sair                        │")
        print("└─────────────────────────────────┘")

    def _select_student(self) -> Optional[Student]:
        """Permite ao usuário selecionar um aluno."""
        students = self.repo.load_all()
        if not students:
            print("\n⚠️  Nenhum aluno cadastrado. Verifique data/students.json")
            return None

        print("\n📋 Alunos disponíveis:")
        print("-" * 50)
        for i, student in enumerate(students, 1):
            print(
                f"  {i}. {student.name} "
                f"({student.age} anos, {student.knowledge_level.value}, "
                f"{student.learning_style.value})"
            )
        print("-" * 50)

        choice = safe_input("→ Selecione o aluno (número): ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(students):
                return students[index]
            print("⚠️  Número inválido.")
        except ValueError:
            print("⚠️  Digite um número válido.")
        return None

    def _select_topic(self) -> str:
        """Solicita ao usuário um tópico."""
        topic = safe_input("\n📝 Digite o tópico a ser ensinado: ")
        if not topic:
            print("⚠️  O tópico não pode ser vazio.")
            return ""
        if len(topic) > 200:
            print("⚠️  O tópico deve ter no máximo 200 caracteres.")
            return ""
        return topic

    def _generate_content(self) -> None:
        """Gera um tipo específico de conteúdo para um aluno."""
        student = self._select_student()
        if not student:
            return

        topic = self._select_topic()
        if not topic:
            return

        print("\n📚 Tipos de conteúdo:")
        for key, (name, _) in CONTENT_GENERATORS.items():
            print(f"  {key}. {name}")

        choice = safe_input("\n→ Selecione o tipo de conteúdo: ")
        if choice not in CONTENT_GENERATORS:
            print("⚠️  Opção inválida.")
            return

        name, generator_cls = CONTENT_GENERATORS[choice]
        print(f"\n⏳ Gerando '{name}' para {student.name} sobre '{topic}'...")

        generator = generator_cls(prompt_version=self.current_version)
        record = generator.generate(student, topic)

        # Salva o resultado
        self.storage.save(record)

        # Exibe o conteúdo
        print(f"\n{'=' * 60}")
        print(f"   {name} — {topic}")
        print(f"   Aluno: {student.name} | Versão: {self.current_version}")
        print(f"{'=' * 60}\n")
        print(record.content)
        print(f"\n{'=' * 60}")
        print("✅ Conteúdo salvo com sucesso!")

    def _generate_all_content(self) -> None:
        """Gera todos os 4 tipos de conteúdo para um aluno."""
        student = self._select_student()
        if not student:
            return

        topic = self._select_topic()
        if not topic:
            return

        print(f"\n⏳ Gerando todos os conteúdos para {student.name} sobre '{topic}'...")
        print(f"   Versão de prompts: {self.current_version}")
        print()

        records = []
        generators = [
            ("Explicação Conceitual", ConceptualGenerator),
            ("Exemplos Práticos", PracticalGenerator),
            ("Perguntas de Reflexão", ReflectionGenerator),
            ("Resumo Visual", VisualGenerator),
        ]

        for i, (name, generator_cls) in enumerate(generators, 1):
            print(f"  [{i}/4] Gerando {name}...")
            generator = generator_cls(prompt_version=self.current_version)
            record = generator.generate(student, topic)
            records.append(record)

            print(f"\n{'─' * 60}")
            print(f"   📌 {name}")
            print(f"{'─' * 60}\n")
            print(record.content)
            print()

        # Salva geração completa
        filepath = self.storage.save_complete_generation(
            student_id=student.id,
            topic=topic,
            records=records,
        )

        print(f"\n{'=' * 60}")
        print(f"✅ Todos os conteúdos gerados e salvos!")
        print(f"📁 Arquivo: {filepath}")
        print(f"{'=' * 60}")

    def _list_students(self) -> None:
        """Lista todos os perfis de alunos."""
        students = self.repo.load_all()
        if not students:
            print("\n⚠️  Nenhum aluno cadastrado.")
            return

        print(f"\n📋 Perfis de Alunos ({len(students)} cadastrados)")
        print("=" * 60)

        for student in students:
            print(f"\n  👤 {student.name} (ID: {student.id})")
            print(f"     Idade: {student.age} anos")
            print(f"     Nível: {student.knowledge_level.value}")
            print(f"     Estilo: {student.learning_style.value}")
            if student.interests:
                print(f"     Interesses: {', '.join(student.interests)}")
            print(f"     Descrição: {student.describe()}")

        print("\n" + "=" * 60)

    def _compare_versions(self) -> None:
        """Compara conteúdo gerado com diferentes versões de prompts."""
        student = self._select_student()
        if not student:
            return

        topic = self._select_topic()
        if not topic:
            return

        print("\n📚 Tipos de conteúdo para comparar:")
        for key, (name, _) in CONTENT_GENERATORS.items():
            print(f"  {key}. {name}")

        choice = safe_input("\n→ Selecione o tipo: ")
        if choice not in CONTENT_GENERATORS:
            print("⚠️  Opção inválida.")
            return

        name, generator_cls = CONTENT_GENERATORS[choice]
        versions = PromptEngine.list_versions()

        print(f"\n⏳ Gerando '{name}' com {len(versions)} versões de prompt...")
        print()

        for version_info in versions:
            v = version_info["version"]
            print(f"\n{'=' * 60}")
            print(f"   Versão: {v} — {version_info['description']}")
            print(f"   Técnicas: {', '.join(version_info['techniques'])}")
            print(f"{'=' * 60}\n")

            generator = generator_cls(prompt_version=v)
            record = generator.generate(student, topic, use_cache=False)
            self.storage.save(record)

            print(record.content)
            print()

        print("✅ Comparação concluída! Resultados salvos no histórico.")

    def _view_history(self) -> None:
        """Visualiza o histórico de conteúdo gerado."""
        outputs = self.storage.list_outputs()

        if not outputs:
            print("\n⚠️  Nenhum conteúdo gerado ainda.")
            return

        print(f"\n📂 Histórico de Gerações ({len(outputs)} arquivos)")
        print("=" * 60)

        for o in outputs:
            print(
                f"  📄 {o['filename']}\n"
                f"     Aluno: {o['student_id']} | Tópico: {o['topic']}\n"
                f"     Gerado em: {o['generated_at']}"
            )
            print()

    def _manage_cache(self) -> None:
        """Gerencia o cache da aplicação."""
        stats = self.cache.stats()

        print(f"\n📊 Estatísticas do Cache")
        print(f"   Total de entradas: {stats['total_entries']}")
        print(f"   Entradas válidas: {stats['valid_entries']}")
        print(f"   Entradas expiradas: {stats['expired_entries']}")
        print(f"   Tamanho: {stats['size_kb']} KB")

        choice = safe_input("\n→ Limpar cache? (s/n): ", "n")
        if choice.lower() == "s":
            removed = self.cache.clear()
            print(f"✅ {removed} entradas removidas do cache.")

    def _change_prompt_version(self) -> None:
        """Troca a versão de prompts utilizada."""
        versions = PromptEngine.list_versions()

        print(f"\n📋 Versões de Prompt Disponíveis (atual: {self.current_version})")
        print("-" * 60)

        for v in versions:
            marker = " ← atual" if v["version"] == self.current_version else ""
            print(f"  {v['version']}: {v['description']}{marker}")
            print(f"     Técnicas: {', '.join(v['techniques'])}")
            print()

        choice = safe_input("→ Selecione a versão: ", self.current_version)
        available = [v["version"] for v in versions]

        if choice in available:
            self.current_version = choice
            print(f"✅ Versão alterada para: {self.current_version}")
        else:
            print(f"⚠️  Versão '{choice}' não disponível.")

    def _run_comparison_analysis(self) -> None:
        """Executa análise comparativa completa entre versões de prompts."""
        student = self._select_student()
        if not student:
            return

        topic = self._select_topic()
        if not topic:
            return

        print("\n📚 Tipos de conteúdo para análise comparativa:")
        types_map = {
            "1": "conceptual",
            "2": "practical",
            "3": "reflection",
            "4": "visual",
        }
        for key, ct in types_map.items():
            print(f"  {key}. {ct.capitalize()}")

        choice = safe_input("\n→ Selecione o tipo: ")
        content_type = types_map.get(choice, "conceptual")

        analyzer = ComparisonAnalysis()
        versions = [v["version"] for v in PromptEngine.list_versions()]

        print(f"\n⏳ Gerando análise comparativa com {len(versions)} versões...")
        print(f"   Versões: {', '.join(versions)}")
        print(f"   Isso pode levar alguns minutos.\n")

        report = analyzer.generate_comparison(
            student=student,
            topic=topic,
            content_type=content_type,
        )

        # Exibe o relatório formatado
        print(analyzer.format_report_text(report))

        # Salva o relatório
        filepath = analyzer.save_report(report)
        print(f"\n📁 Relatório salvo em: {filepath}")

    def _exit(self) -> None:
        """Encerra a aplicação."""
        print("\n👋 Até a próxima! Bons estudos!")
        sys.exit(0)


def main():
    """Ponto de entrada da CLI."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
