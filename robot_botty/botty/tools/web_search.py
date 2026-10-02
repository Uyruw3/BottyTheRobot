"""
Web search tool — busca informacion en internet.
Soporta DuckDuckGo, Google (con API key), y Wikipedia.
"""

import re
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    title: str = ""
    url: str = ""
    snippet: str = ""
    source: str = ""


class WebSearch:
    def __init__(self):
        self._ddgs = None
        self._google_api_key = None
        self._google_cx = None

    def _init_duckduckgo(self):
        if self._ddgs is not None:
            return
        try:
            from duckduckgo_search import DDGS
            self._ddgs = DDGS()
        except ImportError:
            print("  [WebSearch] duckduckgo_search no instalado")
            self._ddgs = False

    def _init_google(self):
        if self._google_api_key and self._google_cx:
            return
        try:
            from botty.config import Config
            self._google_api_key = getattr(Config, "GOOGLE_API_KEY", "")
            self._google_cx = getattr(Config, "GOOGLE_CX", "")
        except Exception:
            pass

    def search(self, query: str, max_results: int = 5, source: str = "auto") -> list[SearchResult]:
        if source == "auto":
            source = "duckduckgo"
        if source == "duckduckgo":
            return self._search_duckduckgo(query, max_results)
        elif source == "google":
            return self._search_google(query, max_results)
        elif source == "wikipedia":
            return self._search_wikipedia(query, max_results)
        return []

    def _search_duckduckgo(self, query: str, max_results: int) -> list[SearchResult]:
        self._init_duckduckgo()
        if not self._ddgs:
            return []
        results = []
        try:
            raw = list(self._ddgs.text(query, max_results=max_results))
            for r in raw:
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                    source="duckduckgo",
                ))
        except Exception as e:
            print(f"  [WebSearch] DuckDuckGo error: {e}")
        return results

    def _search_google(self, query: str, max_results: int) -> list[SearchResult]:
        self._init_google()
        if not self._google_api_key or not self._google_cx:
            return []
        try:
            import requests
            url = "https://www.googleapis.com/customsearch/v1"
            params = {"key": self._google_api_key, "cx": self._google_cx, "q": query, "num": min(max_results, 10)}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            results = []
            for item in data.get("items", [])[:max_results]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google",
                ))
            return results
        except Exception as e:
            print(f"  [WebSearch] Google error: {e}")
            return []

    def _search_wikipedia(self, query: str, max_results: int) -> list[SearchResult]:
        try:
            import requests
            url = "https://es.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "srprop": "snippet",
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            results = []
            for item in data.get("query", {}).get("search", []):
                snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=f"https://es.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                    snippet=snippet,
                    source="wikipedia",
                ))
            return results
        except Exception as e:
            print(f"  [WebSearch] Wikipedia error: {e}")
            return []

    def search_and_format(self, query: str, max_results: int = 5, source: str = "auto") -> str:
        results = self.search(query, max_results, source)
        if not results:
            return "No encontre resultados para tu busqueda."
        lines = [f"Resultados de busqueda para: {query}", ""]
        for i, r in enumerate(results, 1):
            snippet = re.sub(r"\s+", " ", r.snippet).strip()
            if len(snippet) > 250:
                snippet = snippet[:250] + "..."
            lines.append(f"{i}. {r.title}")
            lines.append(f"   {snippet}")
            lines.append(f"   Fuente: {r.source}")
            lines.append("")
        return "\n".join(lines)

    def search_simple(self, query: str) -> str:
        """Retorna solo el primer resultado como texto simple."""
        results = self.search(query, max_results=1)
        if not results:
            return ""
        r = results[0]
        snippet = re.sub(r"\s+", " ", r.snippet).strip()
        return f"Segun {r.source}: {snippet}"
