from mem0 import AsyncMemoryClient
from cachetools import TTLCache
import asyncio
from typing import Any

class CachedMemoryClient:
    def __init__(self):
        self.client = AsyncMemoryClient()
        # Cache for search results: 5 minutes TTL, max 100 items
        self.search_cache = TTLCache(maxsize=100, ttl=300)
        # Cache for get_all results: 5 minutes TTL, max 100 items
        self.get_all_cache = TTLCache(maxsize=100, ttl=300)
        # Cache for single memory retrieval: 5 minutes TTL, max 100 items
        self.get_cache = TTLCache(maxsize=100, ttl=300)

    async def add(self, messages: list[dict[str, Any]], user_id: str, **kwargs) -> dict[str, Any]:
        """
        Add a memory. Cache invalidation is handled by webhook.
        """
        return await self.client.add(messages, user_id=user_id, **kwargs)

    async def search(self, query: str, filters: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """
        Search memories with caching.
        """
        user_id = filters.get("user_id") if filters else None
        if not user_id:
             return await self.client.search(query, filters=filters, **kwargs)

        cache_key = (query, frozenset(filters.items()) if filters else None, frozenset(kwargs.items()))
        
        if cache_key in self.search_cache:
            # Refresh TTL
            result = self.search_cache[cache_key]
            self.search_cache[cache_key] = result
            return result

        result = await self.client.search(query, filters=filters, **kwargs)
        self.search_cache[cache_key] = result
        return result

    async def get_all(self, filters: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """
        Get all memories with caching.
        """
        user_id = filters.get("user_id") if filters else None
        if not user_id:
            return await self.client.get_all(filters=filters, **kwargs)

        cache_key = (frozenset(filters.items()) if filters else None, frozenset(kwargs.items()))
        
        if cache_key in self.get_all_cache:
            # Refresh TTL
            result = self.get_all_cache[cache_key]
            self.get_all_cache[cache_key] = result
            return result

        result = await self.client.get_all(filters=filters, **kwargs)
        self.get_all_cache[cache_key] = result
        return result

    async def get(self, memory_id: str, **kwargs) -> dict[str, Any]:
        """
        Get a specific memory with caching.
        """
        cache_key = (memory_id, frozenset(kwargs.items()))
        
        if cache_key in self.get_cache:
            # Refresh TTL
            result = self.get_cache[cache_key]
            self.get_cache[cache_key] = result
            return result

        result = await self.client.get(memory_id, **kwargs)
        self.get_cache[cache_key] = result
        return result

    async def delete(self, memory_id: str, **kwargs) -> dict[str, Any]:
        """
        Delete a memory. Cache invalidation is handled by webhook.
        """
        return await self.client.delete(memory_id, **kwargs)

    def _invalidate_cache(self, user_id: str):
        """
        Invalidate all caches related to a specific user.
        """
        # Clear search cache for this user
        keys_to_remove = []
        for key in self.search_cache.keys():
            # key is (query, frozenset(filters.items()), ...)
            # filters is the second element
            filters_items = key[1]
            if filters_items:
                filters_dict = dict(filters_items)
                if filters_dict.get("user_id") == user_id:
                    keys_to_remove.append(key)
        
        for k in keys_to_remove:
            del self.search_cache[k]

        # Clear get_all cache for this user
        keys_to_remove = []
        for key in self.get_all_cache.keys():
            # key is (frozenset(filters.items()), ...)
            filters_items = key[0]
            if filters_items:
                filters_dict = dict(filters_items)
                if filters_dict.get("user_id") == user_id:
                    keys_to_remove.append(key)
        
        for k in keys_to_remove:
            del self.get_all_cache[k]

        # Clear get_cache for this user
        keys_to_remove = []
        for key, value in self.get_cache.items():
            # value is the memory dict, should contain user_id
            if isinstance(value, dict) and value.get("user_id") == user_id:
                keys_to_remove.append(key)
        
        for k in keys_to_remove:
            del self.get_cache[k]

    def reset_cache(self, user_id: str | None = None):
        """
        Reset the cache. If user_id is provided, clear only for that user.
        Otherwise, clear all caches.
        """
        if user_id:
            self._invalidate_cache(user_id)
        else:
            self.search_cache.clear()
            self.get_all_cache.clear()
            self.get_cache.clear()

    async def warmup(self, user_id: str):
        """
        Warmup the cache for a specific user by running common queries.
        """
        filters = {"user_id": user_id}
        
        await asyncio.gather(
            self.search("user_preferences", filters=filters),
            self.get_all(filters=filters, page=1, page_size=100)
        )

mem0 = CachedMemoryClient()
