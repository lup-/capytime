from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()

STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR_RESOLVED = STATIC_DIR.resolve()


@router.get("/api/pages")
async def list_pages():
    pages = []
    for f in STATIC_DIR.rglob("*.json"):
        rel = f.relative_to(STATIC_DIR)
        path = str(rel.with_suffix(""))
        html_file = f.with_suffix(".html")
        if html_file.exists():
            with open(f, encoding="utf-8") as meta_f:
                meta = json.load(meta_f)
            pages.append({"path": path, "title": meta.get("title", path)})
    return pages


@router.get("/api/pages/{path:path}")
async def get_page(path: str):
    html_file = (STATIC_DIR / f"{path}.html").resolve()
    meta_file = (STATIC_DIR / f"{path}.json").resolve()
    if not str(html_file).startswith(str(STATIC_DIR_RESOLVED)) or not html_file.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    if not str(meta_file).startswith(str(STATIC_DIR_RESOLVED)) or not meta_file.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    content = html_file.read_text(encoding="utf-8")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    return {"path": path, "content": content, "title": meta.get("title", path)}
