"""
Cliente unificado para APIs de IA.

Suporta OpenAI, Google Gemini e Anthropic Claude.
Abstrai as diferenças entre provedores em uma interface única.
"""

import json
import logging
import re
import time
from typing import Optional

import requests

from src.config import Config

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Erro ao comunicar com a API de IA."""
    pass


class AIClient:
    """
    Cliente unificado para chamadas a APIs de IA.

    Suporta OpenAI (GPT-4o/GPT-4o mini), Google Gemini e Anthropic Claude.
    """

    # Endpoints das APIs
    ENDPOINTS = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "anthropic": "https://api.anthropic.com/v1/messages",
    }

    # Timeout padrão em segundos
    DEFAULT_TIMEOUT = 60

    # Retry para erros de rate limit (429)
    MAX_RETRIES = 3

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider or Config.AI_PROVIDER
        self.api_key = api_key or Config.get_api_key()
        self.model = model or Config.AI_MODEL
        self._validate_provider()

    def _validate_provider(self) -> None:
        """Valida se o provedor é suportado."""
        if self.provider not in self.ENDPOINTS:
            raise AIClientError(
                f"Provedor '{self.provider}' não suportado. "
                f"Use: {', '.join(self.ENDPOINTS.keys())}"
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Gera conteúdo usando a API de IA configurada.

        Args:
            prompt: O prompt do usuário.
            system_prompt: Instrução de sistema (personalidade/contexto).
            temperature: Controle de criatividade (0.0 a 1.0).
            max_tokens: Limite máximo de tokens na resposta.

        Returns:
            Texto gerado pela IA.

        Raises:
            AIClientError: Se houver erro na chamada da API.
        """
        handlers = {
            "openai": self._call_openai,
            "gemini": self._call_gemini,
            "anthropic": self._call_anthropic,
        }

        handler = handlers[self.provider]
        logger.info(
            "Chamando %s (modelo: %s, temperatura: %.1f)",
            self.provider,
            self.model,
            temperature,
        )

        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return handler(prompt, system_prompt, temperature, max_tokens)
            except AIClientError as e:
                # Retry automático em rate limit (429)
                wait = self._parse_retry_after(str(e))
                if wait and attempt < self.MAX_RETRIES:
                    logger.warning(
                        "Rate limit atingido. Aguardando %.1fs antes de tentar novamente "
                        "(tentativa %d/%d)...",
                        wait, attempt, self.MAX_RETRIES,
                    )
                    print(
                        f"\n⏳ Rate limit atingido. Aguardando {wait:.0f}s... "
                        f"(tentativa {attempt}/{self.MAX_RETRIES})"
                    )
                    time.sleep(wait)
                    last_error = e
                    continue
                raise
            except requests.exceptions.Timeout:
                raise AIClientError(
                    f"Timeout ao chamar a API {self.provider}. "
                    "Tente novamente em alguns instantes."
                )
            except requests.exceptions.ConnectionError:
                raise AIClientError(
                    f"Erro de conexão com a API {self.provider}. "
                    "Verifique sua conexão com a internet."
                )
        raise last_error  # type: ignore

    @staticmethod
    def _parse_retry_after(error_msg: str) -> Optional[float]:
        """Extrai o tempo de espera sugerido da mensagem de erro 429."""
        match = re.search(r"retry in ([\d.]+)s", error_msg, re.IGNORECASE)
        if match:
            return float(match.group(1))
        if "429" in error_msg:
            return 30.0  # fallback conservador
        return None

    def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chama a API da OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.ENDPOINTS["openai"],
            headers=headers,
            json=payload,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:
            error_msg = self._extract_error(response)
            raise AIClientError(f"Erro na API OpenAI ({response.status_code}): {error_msg}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chama a API do Google Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = self.ENDPOINTS["gemini"].format(model=self.model)
        url += f"?key={self.api_key}"

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:
            error_msg = self._extract_error(response)
            raise AIClientError(f"Erro na API Gemini ({response.status_code}): {error_msg}")

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Chama a API da Anthropic Claude."""
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        response = requests.post(
            self.ENDPOINTS["anthropic"],
            headers=headers,
            json=payload,
            timeout=self.DEFAULT_TIMEOUT,
        )

        if response.status_code != 200:
            error_msg = self._extract_error(response)
            raise AIClientError(
                f"Erro na API Anthropic ({response.status_code}): {error_msg}"
            )

        data = response.json()
        return data["content"][0]["text"]

    @staticmethod
    def _extract_error(response: requests.Response) -> str:
        """Extrai mensagem de erro da resposta da API."""
        try:
            data = response.json()
            if "error" in data:
                if isinstance(data["error"], dict):
                    return data["error"].get("message", str(data["error"]))
                return str(data["error"])
            return json.dumps(data, ensure_ascii=False)
        except (json.JSONDecodeError, KeyError):
            return response.text[:200]
