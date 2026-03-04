"""
Gerador base de conteúdo educacional.

Define a interface e lógica compartilhada por todos os geradores
de conteúdo, incluindo integração com cache e armazenamento.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.config import Config
from src.models.student import Student
from src.prompts.engine import PromptEngine
from src.services.ai_client import AIClient, AIClientError
from src.services.cache import CacheManager
from src.services.storage import ContentRecord

logger = logging.getLogger(__name__)


class ContentGenerator(ABC):
    """
    Classe base abstrata para geradores de conteúdo.

    Cada gerador implementa um tipo específico de conteúdo
    (conceitual, prático, reflexão, visual) e utiliza o
    PromptEngine para construir prompts otimizados.
    """

    # Subclasses devem definir este atributo
    content_type: str = ""

    def __init__(
        self,
        ai_client: Optional[AIClient] = None,
        prompt_engine: Optional[PromptEngine] = None,
        cache: Optional[CacheManager] = None,
        prompt_version: str = "v2",
    ):
        self.ai_client = ai_client or AIClient()
        self.prompt_engine = prompt_engine or PromptEngine(version=prompt_version)
        self.cache = cache or CacheManager()
        self.prompt_version = prompt_version

    @abstractmethod
    def _build_prompt(self, student: Student, topic: str) -> str:
        """
        Constrói o prompt específico para este tipo de conteúdo.

        Args:
            student: Perfil do aluno.
            topic: Tópico a ser ensinado.

        Returns:
            Prompt formatado.
        """
        pass

    def generate(
        self,
        student: Student,
        topic: str,
        use_cache: bool = True,
        temperature: float = 0.7,
    ) -> ContentRecord:
        """
        Gera conteúdo educacional para o aluno e tópico especificados.

        Args:
            student: Perfil do aluno.
            topic: Tópico a ser ensinado.
            use_cache: Se True, verifica cache antes de chamar API.
            temperature: Criatividade da resposta (0.0-1.0).

        Returns:
            ContentRecord com o conteúdo gerado e metadados.

        Raises:
            AIClientError: Se houver erro na chamada à API.
        """
        # Constrói prompts
        system_prompt = self.prompt_engine.build_system_prompt(student)
        user_prompt = self._build_prompt(student, topic)

        # Parâmetros para cache
        cache_params = {
            "provider": Config.AI_PROVIDER,
            "model": Config.AI_MODEL,
            "version": self.prompt_version,
            "content_type": self.content_type,
            "student_id": student.id,
            "temperature": temperature,
        }

        # Verifica cache
        content = None
        if use_cache:
            content = self.cache.get(user_prompt, system_prompt, **cache_params)
            if content:
                logger.info(
                    "Conteúdo '%s' recuperado do cache para %s/%s",
                    self.content_type,
                    student.id,
                    topic,
                )

        # Chama API se não encontrou no cache
        if content is None:
            logger.info(
                "Gerando '%s' para %s/%s via API...",
                self.content_type,
                student.id,
                topic,
            )
            content = self.ai_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )

            # Salva no cache
            self.cache.set(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response=content,
                metadata={
                    "student_id": student.id,
                    "topic": topic,
                    "content_type": self.content_type,
                },
                **cache_params,
            )

        # Cria registro de conteúdo
        record = ContentRecord(
            student_id=student.id,
            topic=topic,
            content_type=self.content_type,
            content=content,
            prompt_version=self.prompt_version,
            prompt_used=user_prompt,
            system_prompt_used=system_prompt,
            provider=Config.AI_PROVIDER,
            model=Config.AI_MODEL,
        )

        return record
