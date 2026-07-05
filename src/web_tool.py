import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


TRUSTED_DOMAINS = (
    "nei.nih.gov",
    "medlineplus.gov",
    "aao.org",
    "nhs.uk",
    "mayoclinic.org",
    "cdc.gov",
    "who.int",
    "aoa.org",
    "ncbi.nlm.nih.gov",
)

WEB_TRIGGER_TERMS = (
    "latest",
    "recent",
    "new",
    "updated",
    "current",
    "guideline",
    "guidelines",
    "news",
    "research",
    "study",
    "studies",
    "website",
    "source",
    "sources",
    "evidence",
    "article",
    "recommendation",
    "recommendations",
)

EYE_HEALTH_TERMS = (
    "eye",
    "eyes",
    "vision",
    "retina",
    "retinal",
    "ophthalmology",
    "ophthalmologist",
    "optometry",
    "optometrist",
    "cataract",
    "glaucoma",
    "diabetic retinopathy",
    "macular",
    "conjunctivitis",
    "dry eye",
    "floaters",
    "uveitis",
)


def is_web_evidence_configured() -> bool:
    enabled = os.environ.get(
        "TRUSTED_WEB_EVIDENCE_ENABLED",
        os.environ.get("WEB_EVIDENCE_ENABLED", "true"),
    )
    if enabled.lower() in ("0", "false", "no", "off"):
        return False
    return bool(_api_key("tavily") or _api_key("brave"))


def should_use_web_tool(query: str) -> bool:
    text = (query or "").lower()
    if not text.strip() or not is_web_evidence_configured():
        return False

    has_eye_topic = any(term in text for term in EYE_HEALTH_TERMS)
    has_web_need = any(term in text for term in WEB_TRIGGER_TERMS)

    return has_eye_topic and has_web_need


def search_trusted_web(query: str, max_results: int = 3) -> list:
    if not should_use_web_tool(query):
        return []

    configured_max = os.environ.get("TRUSTED_WEB_EVIDENCE_MAX_RESULTS")
    if configured_max and configured_max.isdigit():
        max_results = min(max(1, int(configured_max)), 5)

    provider = os.environ.get(
        "TRUSTED_WEB_EVIDENCE_PROVIDER",
        os.environ.get("WEB_SEARCH_PROVIDER", ""),
    ).lower().strip()
    if provider == "brave" or (_api_key("brave") and not _api_key("tavily")):
        return _search_brave(query, max_results=max_results)
    return _search_tavily(query, max_results=max_results)


def format_web_evidence_for_prompt(results: list) -> str:
    if not results:
        return ""

    lines = [
        "Trusted Web Evidence",
        "Use these current external source snippets only when they directly support the answer.",
        "Cite these sources inline using [W1], [W2], etc. Do not invent claims beyond the snippets.",
    ]
    for idx, item in enumerate(results, 1):
        lines.extend([
            "",
            f"[W{idx}] {item.get('title') or 'Trusted source'}",
            f"URL: {item.get('url')}",
            f"Snippet: {item.get('snippet')}",
        ])
    return "\n".join(lines)


def format_web_evidence_for_response(results: list) -> str:
    if not results:
        return ""

    lines = [
        "\n\n---",
        "Trusted Web Evidence",
        "The assistant quietly checked trusted medical websites for this answer:",
    ]
    for idx, item in enumerate(results, 1):
        lines.extend([
            "",
            f"[W{idx}] {item.get('title') or 'Trusted source'}",
            str(item.get("url") or ""),
            str(item.get("snippet") or ""),
        ])
    return "\n".join(lines)


def _search_tavily(query: str, max_results: int) -> list:
    api_key = _api_key("tavily")
    if not api_key:
        return []

    payload = {
        "api_key": api_key,
        "query": _trusted_query(_minimize_query(query)),
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
        "include_domains": list(_trusted_domains()),
    }
    data = _post_json("https://api.tavily.com/search", payload)
    return _normalize_tavily_results(data, max_results=max_results)


def _search_brave(query: str, max_results: int) -> list:
    api_key = _api_key("brave")
    if not api_key:
        return []

    params = urllib.parse.urlencode({
        "q": _trusted_query(_minimize_query(query)),
        "count": max_results,
        "safesearch": "strict",
    })
    request = urllib.request.Request(
        f"https://api.search.brave.com/res/v1/web/search?{params}",
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        },
        method="GET",
    )
    data = _read_json(request)
    return _normalize_brave_results(data, max_results=max_results)


def _trusted_query(query: str) -> str:
    trusted_filter = " OR ".join(f"site:{domain}" for domain in _trusted_domains())
    return f"({query}) ({trusted_filter})"


def _post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return _read_json(request)


def _read_json(request: urllib.request.Request) -> dict:
    timeout = float(os.environ.get(
        "TRUSTED_WEB_EVIDENCE_TIMEOUT_SECONDS",
        os.environ.get("WEB_EVIDENCE_TIMEOUT_SECONDS", "6"),
    ))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[WebEvidence] Search failed: {exc}")
        return {}


def _normalize_tavily_results(data: dict, max_results: int) -> list:
    raw_results = data.get("results") if isinstance(data, dict) else []
    normalized = []
    for item in raw_results or []:
        normalized.append(_normalize_result(
            title=item.get("title"),
            url=item.get("url"),
            snippet=item.get("content"),
        ))
    return _filter_allowed(normalized, max_results=max_results)


def _normalize_brave_results(data: dict, max_results: int) -> list:
    raw_results = (((data or {}).get("web") or {}).get("results") or [])
    normalized = []
    for item in raw_results:
        normalized.append(_normalize_result(
            title=item.get("title"),
            url=item.get("url"),
            snippet=item.get("description"),
        ))
    return _filter_allowed(normalized, max_results=max_results)


def _normalize_result(title: str, url: str, snippet: str) -> dict:
    return {
        "title": _clean_text(title, 120),
        "url": str(url or "").strip(),
        "snippet": _clean_text(snippet, 520),
    }


def _filter_allowed(results: list, max_results: int) -> list:
    allowed = []
    seen = set()
    for item in results:
        url = item.get("url") or ""
        if not _is_allowed_url(url) or url in seen:
            continue
        seen.add(url)
        allowed.append(item)
        if len(allowed) >= max_results:
            break
    return allowed


def _is_allowed_url(url: str) -> bool:
    try:
        host = urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return False
    host = host.lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in _trusted_domains())


def _clean_text(value: str, max_chars: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) > max_chars:
        return text[:max_chars].rstrip() + "..."
    return text


def _api_key(provider: str) -> str:
    if provider == "brave":
        return os.environ.get("BRAVE_SEARCH_API_KEY", "").strip()
    return os.environ.get(
        "TAVILY_API_KEY",
        os.environ.get("TRUSTED_WEB_EVIDENCE_API_KEY", ""),
    ).strip()


def _trusted_domains() -> tuple:
    configured = os.environ.get("TRUSTED_WEB_EVIDENCE_ALLOWED_DOMAINS", "").strip()
    if not configured:
        return TRUSTED_DOMAINS
    domains = tuple(
        domain.strip().lower()
        for domain in configured.split(",")
        if domain.strip()
    )
    return domains or TRUSTED_DOMAINS


def _minimize_query(query: str) -> str:
    text = re.sub(r"\b[\w.\-+]+@[\w.\-]+\.\w+\b", " ", query or "")
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", " ", text)
    text = re.sub(r"\b\d{1,3}\s+(?:years?|yrs?)\s+old\b", " ", text, flags=re.IGNORECASE)
    return _clean_text(text, 240)
