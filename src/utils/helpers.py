"""
Funções utilitárias do projeto.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Configura o sistema de logging da aplicação."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Reduz verbosidade de bibliotecas externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def print_json(data: dict, indent: int = 2) -> None:
    """Imprime dados JSON formatados no terminal."""
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def safe_input(prompt: str, default: Optional[str] = None) -> str:
    """
    Solicita input do usuário com tratamento de KeyboardInterrupt.

    Args:
        prompt: Texto a ser exibido.
        default: Valor padrão se o usuário pressionar Enter.

    Returns:
        Texto digitado pelo usuário.
    """
    try:
        if default:
            prompt = f"{prompt} [{default}]: "
        result = input(prompt).strip()
        return result if result else (default or "")
    except (KeyboardInterrupt, EOFError):
        print("\n")
        sys.exit(0)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Trunca texto longo para exibição."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
