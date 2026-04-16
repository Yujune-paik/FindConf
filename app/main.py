import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import HTTPStatusError
from pydantic import BaseModel

from app.openalex import search_similar_works
from app.ranking import rank_venues, rank_venues_xlab
from app.xlab import XLAB_KEYWORDS


def _find_project_root() -> Path:
    """プロジェクトルートを探す。Vercel/ローカル両対応。"""
    # 方法1: __file__ から辿る（ローカル）
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "templates").is_dir():
        return candidate

    # 方法2: カレントディレクトリ（Vercel）
    candidate = Path(os.getcwd())
    if (candidate / "templates").is_dir():
        return candidate

    # 方法3: LAMBDA_TASK_ROOT（Vercel serverless）
    task_root = os.environ.get("LAMBDA_TASK_ROOT", "")
    if task_root:
        candidate = Path(task_root)
        if (candidate / "templates").is_dir():
            return candidate

    # フォールバック
    return Path(__file__).resolve().parent.parent


BASE_DIR = _find_project_root()

app = FastAPI(title="FindConf")

# 静的ファイル配信
_static_dir = BASE_DIR / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- CSSを読み込んでキャッシュ ---
_css_cache: str | None = None


def _load_css() -> str:
    global _css_cache
    if _css_cache is None:
        css_path = BASE_DIR / "static" / "style.css"
        _css_cache = css_path.read_text() if css_path.exists() else ""
    return _css_cache


class RecommendRequest(BaseModel):
    abstract: str


@app.get("/css/style.css")
async def serve_css():
    return Response(content=_load_css(), media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
async def xlab_page(request: Request):
    return templates.TemplateResponse("xlab.html", {"request": request})


@app.post("/api/xlab/recommend")
async def xlab_recommend(body: RecommendRequest):
    abstract = body.abstract.strip()
    if not abstract:
        return JSONResponse(
            status_code=400,
            content={"error": "abstractを入力してください。"},
        )

    try:
        # メイン検索: ユーザーのabstract
        works = await search_similar_works(abstract)

        # 補助検索: xlabキーワードで追加の関連論文を取得
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


# --- Vercelデバッグ用 (問題解決後削除可) ---


@app.get("/api/health")
async def health():
    import traceback
    template_files = []
    try:
        template_dir = BASE_DIR / "templates"
        if template_dir.is_dir():
            template_files = [f.name for f in template_dir.iterdir()]
    except Exception:
        pass

    # テンプレートレンダリングテスト
    render_error = None
    try:
        from starlette.testclient import TestClient
    except Exception:
        pass

    try:
        templates.get_template("index.html")
    except Exception as e:
        render_error = f"{type(e).__name__}: {e}"

    return {
        "status": "ok",
        "base_dir": str(BASE_DIR),
        "templates_exist": (BASE_DIR / "templates").is_dir(),
        "static_exist": (BASE_DIR / "static").is_dir(),
        "template_files": template_files,
        "render_error": render_error,
        "cwd": os.getcwd(),
    }


@app.get("/api/debug-render")
async def debug_render(request: Request):
    """テンプレートレンダリングのデバッグ。"""
    import traceback
    try:
        html = templates.TemplateResponse("index.html", {"request": request})
        return {"status": "ok", "type": str(type(html))}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
