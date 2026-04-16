from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import HTTPStatusError
from pydantic import BaseModel

from app.openalex import search_similar_works
from app.ranking import rank_venues, rank_venues_xlab
from app.xlab import XLAB_KEYWORDS

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="FindConf")

# 静的ファイル配信（Vercel環境でもローカルでも動くように）
_static_dir = BASE_DIR / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class RecommendRequest(BaseModel):
    abstract: str


@app.get("/css/style.css")
async def serve_css():
    """Vercel環境でも確実にCSSを配信するためのフォールバック。"""
    css_path = BASE_DIR / "static" / "style.css"
    if css_path.exists():
        from fastapi.responses import Response
        return Response(content=css_path.read_text(), media_type="text/css")
    return Response(content="", media_type="text/css")


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
        # abstractの先頭数語 + xlabキーワードで検索し、マージ
        abstract_words = abstract.split()[:10]
        abstract_prefix = " ".join(abstract_words)
        seen_ids = {w.get("id") for w in works}

        # 最も関連性の高いxlabキーワード2つで追加検索
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
