import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from httpx import HTTPStatusError
from pydantic import BaseModel

from app.openalex import search_similar_works
from app.ranking import rank_venues, rank_venues_xlab
from app.xlab import XLAB_KEYWORDS


def _find_project_root() -> Path:
    """プロジェクトルートを探す。Vercel/ローカル両対応。"""
    for candidate in [
        Path(__file__).resolve().parent.parent,
        Path(os.getcwd()),
        Path(os.environ.get("LAMBDA_TASK_ROOT", "/var/task")),
    ]:
        if (candidate / "templates").is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent


BASE_DIR = _find_project_root()

# HTMLとCSSをファイルから読み込んでキャッシュ
_html_cache: dict[str, str] = {}
_css_cache: str | None = None


def _load_html(name: str) -> str:
    if name not in _html_cache:
        path = BASE_DIR / "templates" / name
        _html_cache[name] = path.read_text(encoding="utf-8")
    return _html_cache[name]


def _load_css() -> str:
    global _css_cache
    if _css_cache is None:
        css_path = BASE_DIR / "static" / "style.css"
        _css_cache = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    return _css_cache


app = FastAPI(title="FindConf")

# 静的ファイル配信（ローカル用）
_static_dir = BASE_DIR / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


class RecommendRequest(BaseModel):
    abstract: str


# --- 静的アセット ---


@app.get("/css/style.css")
async def serve_css():
    return Response(content=_load_css(), media_type="text/css")


# --- メインページ ---


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=_load_html("index.html"))


@app.post("/api/recommend")
async def recommend(body: RecommendRequest):
    abstract = body.abstract.strip()
    if not abstract:
        return JSONResponse(
            status_code=400,
            content={"error": "abstractを入力してください。"},
        )

    try:
        works = await search_similar_works(abstract)
    except HTTPStatusError as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"OpenAlex APIエラー: {e.response.status_code}"},
        )

    venues = rank_venues(works)
    return {
        "total_works": len(works),
        "venues": venues,
    }


# === xlab 専用ルート ===


@app.get("/xlab", response_class=HTMLResponse)
async def xlab_page():
    return HTMLResponse(content=_load_html("xlab.html"))


@app.post("/api/xlab/recommend")
async def xlab_recommend(body: RecommendRequest):
    abstract = body.abstract.strip()
    if not abstract:
        return JSONResponse(
            status_code=400,
            content={"error": "abstractを入力してください。"},
        )

    try:
        works = await search_similar_works(abstract)

        abstract_words = abstract.split()[:10]
        abstract_prefix = " ".join(abstract_words)
        seen_ids = {w.get("id") for w in works}

        for kw in XLAB_KEYWORDS[:2]:
            query = f"{abstract_prefix} {kw}"
            extra_works = await search_similar_works(query)
            for w in extra_works:
                if w.get("id") not in seen_ids:
                    works.append(w)
                    seen_ids.add(w.get("id"))

    except HTTPStatusError as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"OpenAlex APIエラー: {e.response.status_code}"},
        )

    venues = rank_venues_xlab(works)
    return {
        "total_works": len(works),
        "venues": venues,
    }
