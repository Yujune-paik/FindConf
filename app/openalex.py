import hashlib

import httpx
from cachetools import TTLCache

from app.config import OPENALEX_API_KEY, OPENALEX_BASE_URL, CONTACT_EMAIL

_cache: TTLCache = TTLCache(maxsize=100, ttl=3600)

MAX_WORDS = 25


def _truncate(text: str, max_words: int = MAX_WORDS) -> str:
    words = text.split()
    if len(words) > max_words:
        words = words[:max_words]
    return " ".join(words)


def _cache_key(abstract: str) -> str:
    return hashlib.sha256(abstract.encode()).hexdigest()


async def search_similar_works(abstract: str) -> list[dict]:
    """Search OpenAlex for works semantically similar to the given abstract."""
    abstract = abstract.strip()
    if not abstract:
        return []

    key = _cache_key(abstract)
    if key in _cache:
        return _cache[key]

    query_text = _truncate(abstract)

    headers = {}
    if CONTACT_EMAIL:
        headers["User-Agent"] = f"FindConf/1.0 (mailto:{CONTACT_EMAIL})"

    base_params: dict = {
        "search": query_text,
        "per_page": 50,
        "select": "id,title,publication_year,cited_by_count,primary_location,doi",
    }
    if OPENALEX_API_KEY:
        base_params["api_key"] = OPENALEX_API_KEY

    all_results: list[dict] = []
    max_pages = 4  # 50 x 4 = 最大200件

    async with httpx.AsyncClient(timeout=30.0) as client:
        for page in range(1, max_pages + 1):
            params = {**base_params, "page": page}
            resp = await client.get(
                f"{OPENALEX_BASE_URL}/works",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            all_results.extend(results)

            # 次ページがなければ終了
            meta = data.get("meta", {})
            total_count = meta.get("count", 0)
            if len(all_results) >= total_count or not results:
                break

    # Only cache non-empty results to avoid caching failures
    if all_results:
        _cache[key] = all_results
    return all_results
