"""
Sistema de cache para evitar chamadas desnecessárias à API.

Implementa cache baseado em arquivo com TTL configurável.
A chave de cache é gerada a partir do hash do prompt + parâmetros.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional

from src.config import Config, CACHE_DIR

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerencia cache de respostas da API em arquivos JSON.

    Cada entrada de cache contém:
    - response: A resposta da API
    - timestamp: Quando foi criada
    - ttl: Tempo de vida em segundos
    - metadata: Informações adicionais (provedor, modelo, etc.)
    """

    def __init__(self, cache_dir: Optional[Path] = None, ttl: Optional[int] = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self.ttl = ttl or Config.CACHE_TTL
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """
        Gera uma chave de cache única baseada nos parâmetros.

        Combina prompt, system_prompt e parâmetros adicionais em um hash SHA256.
        """
        key_data = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            **kwargs,
        }
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Retorna o caminho do arquivo de cache para uma chave."""
        return self.cache_dir / f"{key}.json"

    def get(self, prompt: str, system_prompt: str = "", **kwargs) -> Optional[str]:
        """
        Busca uma resposta no cache.

        Args:
            prompt: O prompt usado na chamada.
            system_prompt: O prompt de sistema usado.
            **kwargs: Parâmetros adicionais (modelo, temperatura, etc.)

        Returns:
            A resposta cacheada ou None se não encontrada/expirada.
        """
        key = self._generate_key(prompt, system_prompt, **kwargs)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            logger.debug("Cache miss: %s", key[:12])
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                entry = json.load(f)

            # Verifica se expirou
            elapsed = time.time() - entry["timestamp"]
            if elapsed > entry.get("ttl", self.ttl):
                logger.debug("Cache expirado: %s (%.0fs)", key[:12], elapsed)
                cache_path.unlink(missing_ok=True)
                return None

            logger.info("Cache hit: %s", key[:12])
            return entry["response"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Cache corrompido (%s): %s", key[:12], e)
            cache_path.unlink(missing_ok=True)
            return None

    def set(
        self,
        prompt: str,
        system_prompt: str,
        response: str,
        metadata: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Armazena uma resposta no cache.

        Args:
            prompt: O prompt usado na chamada.
            system_prompt: O prompt de sistema usado.
            response: A resposta da API para cachear.
            metadata: Informações adicionais para armazenar.
            **kwargs: Parâmetros adicionais usados na chamada.
        """
        key = self._generate_key(prompt, system_prompt, **kwargs)
        cache_path = self._get_cache_path(key)

        entry = {
            "response": response,
            "timestamp": time.time(),
            "ttl": self.ttl,
            "metadata": metadata or {},
            "params": {
                "prompt_preview": prompt[:100],
                "system_prompt_preview": system_prompt[:100] if system_prompt else "",
                **kwargs,
            },
        }

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)

        logger.debug("Cache armazenado: %s", key[:12])

    def clear(self) -> int:
        """
        Limpa todo o cache.

        Returns:
            Número de entradas removidas.
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1

        logger.info("Cache limpo: %d entradas removidas", count)
        return count

    def clear_expired(self) -> int:
        """
        Remove apenas entradas expiradas do cache.

        Returns:
            Número de entradas expiradas removidas.
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)

                elapsed = time.time() - entry["timestamp"]
                if elapsed > entry.get("ttl", self.ttl):
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()
                count += 1

        logger.info("Cache: %d entradas expiradas removidas", count)
        return count

    def stats(self) -> dict:
        """Retorna estatísticas do cache."""
        total = 0
        valid = 0
        expired = 0
        size_bytes = 0

        for cache_file in self.cache_dir.glob("*.json"):
            total += 1
            size_bytes += cache_file.stat().st_size

            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)

                elapsed = time.time() - entry["timestamp"]
                if elapsed > entry.get("ttl", self.ttl):
                    expired += 1
                else:
                    valid += 1
            except (json.JSONDecodeError, KeyError):
                expired += 1

        return {
            "total_entries": total,
            "valid_entries": valid,
            "expired_entries": expired,
            "size_kb": round(size_bytes / 1024, 2),
        }
