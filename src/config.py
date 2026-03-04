"""
Configuração central da aplicação.

Carrega variáveis de ambiente e define constantes globais do projeto.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Caminhos do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SAMPLES_DIR = ROOT_DIR / "samples"
STUDENTS_FILE = DATA_DIR / "students.json"
TEMPLATES_DIR = ROOT_DIR / "templates"

# Diretórios graváveis: usa /tmp na Vercel (filesystem somente leitura)
_writable_base = Path("/tmp/eduprompt") if os.getenv("VERCEL") else DATA_DIR
OUTPUTS_DIR = _writable_base / "outputs"
CACHE_DIR = _writable_base / "cache"

# Garante que diretórios graváveis existam em runtime
for directory in [OUTPUTS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Carrega variáveis do .env
load_dotenv(ROOT_DIR / ".env")


class Config:
    """Configuração da aplicação carregada do .env."""

    # Provedor de IA
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai").lower()

    # Chaves de API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Modelos padrão por provedor
    DEFAULT_MODELS = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini-flash-latest",
        "anthropic": "claude-3-haiku-20240307",
    }

    AI_MODEL: str = os.getenv("AI_MODEL", "") or DEFAULT_MODELS.get(
        os.getenv("AI_PROVIDER", "openai").lower(), "gpt-4o-mini"
    )

    # Flask
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5001"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Cache
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))

    @classmethod
    def get_api_key(cls) -> str:
        """Retorna a chave de API do provedor configurado."""
        keys = {
            "openai": cls.OPENAI_API_KEY,
            "gemini": cls.GEMINI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
        }
        key = keys.get(cls.AI_PROVIDER, "")
        if not key:
            raise ValueError(
                f"Chave de API não configurada para o provedor '{cls.AI_PROVIDER}'. "
                f"Configure a variável de ambiente correspondente no arquivo .env"
            )
        return key

    @classmethod
    def validate(cls) -> list[str]:
        """Valida a configuração e retorna lista de avisos."""
        warnings = []

        if cls.AI_PROVIDER not in ("openai", "gemini", "anthropic"):
            warnings.append(
                f"Provedor '{cls.AI_PROVIDER}' não reconhecido. "
                "Use 'openai', 'gemini' ou 'anthropic'."
            )

        try:
            cls.get_api_key()
        except ValueError as e:
            warnings.append(str(e))

        return warnings
