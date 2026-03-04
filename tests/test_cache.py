"""
Testes do sistema de cache.
"""

import tempfile
import time
from pathlib import Path

import pytest

from src.services.cache import CacheManager


class TestCacheManager:
    """Testes do CacheManager."""

    def _create_cache(self, ttl: int = 3600) -> CacheManager:
        """Cria um CacheManager temporário."""
        tmpdir = tempfile.mkdtemp()
        return CacheManager(cache_dir=Path(tmpdir), ttl=ttl)

    def test_cache_miss(self):
        """Testa que cache vazio retorna None."""
        cache = self._create_cache()
        result = cache.get("teste", "system")
        assert result is None

    def test_cache_set_and_get(self):
        """Testa armazenar e recuperar do cache."""
        cache = self._create_cache()

        cache.set("prompt_teste", "system_teste", "resposta_123")
        result = cache.get("prompt_teste", "system_teste")

        assert result == "resposta_123"

    def test_cache_with_extra_params(self):
        """Testa que parâmetros extras afetam a chave de cache."""
        cache = self._create_cache()

        cache.set("prompt", "system", "resp1", model="gpt-4o")
        cache.set("prompt", "system", "resp2", model="gpt-4o-mini")

        assert cache.get("prompt", "system", model="gpt-4o") == "resp1"
        assert cache.get("prompt", "system", model="gpt-4o-mini") == "resp2"

    def test_cache_expiration(self):
        """Testa que entradas expiradas não são retornadas."""
        cache = self._create_cache(ttl=1)

        cache.set("prompt", "system", "resposta")

        # Deve estar no cache imediatamente
        assert cache.get("prompt", "system") == "resposta"

        # Aguarda expiração
        time.sleep(1.5)

        # Deve estar expirado
        assert cache.get("prompt", "system") is None

    def test_clear_cache(self):
        """Testa limpeza do cache."""
        cache = self._create_cache()

        cache.set("p1", "s1", "r1")
        cache.set("p2", "s2", "r2")

        removed = cache.clear()

        assert removed == 2
        assert cache.get("p1", "s1") is None
        assert cache.get("p2", "s2") is None

    def test_cache_stats(self):
        """Testa estatísticas do cache."""
        cache = self._create_cache()

        cache.set("p1", "s1", "r1")
        cache.set("p2", "s2", "r2")

        stats = cache.stats()

        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 2
        assert stats["expired_entries"] == 0
        assert stats["size_kb"] > 0

    def test_different_prompts_different_keys(self):
        """Testa que prompts diferentes geram chaves diferentes."""
        cache = self._create_cache()

        cache.set("prompt_A", "system", "resposta_A")
        cache.set("prompt_B", "system", "resposta_B")

        assert cache.get("prompt_A", "system") == "resposta_A"
        assert cache.get("prompt_B", "system") == "resposta_B"
