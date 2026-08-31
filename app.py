import re
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import wikipediaapi

app = FastAPI(title="PySearch API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files serve karne ke liye
app.mount("/static", StaticFiles(directory="static"), name="static")

# Custom User-Agent Wikipedia API standards ke liye
wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="PySearchApp/1.0 (contact: pysearch@render.app)"
)

@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

@app.get("/api/search")
def search_engine(q: str = Query(..., min_length=1)):
    page = wiki.page(q)

    if not page.exists():
        return {
            "status": "error",
            "message": f"'{q}' ke liye koi direct information nahi mili. Kripya dusra keyword try karein."
        }

    # 1. TL;DR Layer (First 2-3 sentences)
    full_summary = page.summary
    sentences = re.split(r'(?<=[.!?])\s+', full_summary)
    tldr = " ".join(sentences[:2]) if len(sentences) >= 2 else full_summary

    # 2. Key Facts / Highlights
    facts = []
    for s in sentences[2:7]:
        clean_s = s.strip()
        if len(clean_s) > 25:
            facts.append(clean_s)

    # 3. Knowledge Graph / Related Nodes (Linked pages)
    related_links = list(page.links.keys())[:8]
    clean_related = [link for link in related_links if not link.startswith("Template:") and len(link) < 25]

    return {
        "status": "success",
        "title": page.title,
        "tldr": tldr,
        "key_facts": facts if facts else ["Standard encyclopedia entry."],
        "related_nodes": clean_related[:6],
        "source_url": page.fullurl
    }
