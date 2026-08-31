import re
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="PySearch Knowledge Engine")

# CORS middleware for open accessibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wikipedia API headers
HEADERS = {
    "User-Agent": "PySearchBot/1.0 (https://render.com; pysearch@example.com)"
}

@app.get("/api/search")
def search_engine(q: str = Query(..., min_length=1)):
    clean_query = q.strip()
    
    # Step 1: Find best matching Wikipedia title
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": clean_query,
        "format": "json"
    }

    try:
        search_res = requests.get(search_url, params=search_params, headers=HEADERS, timeout=8).json()
        search_results = search_res.get("query", {}).get("search", [])

        if not search_results:
            return {
                "status": "error",
                "message": f"'{clean_query}' ke liye koi result nahi mila. Kripya dusra keyword try karein."
            }

        title = search_results[0]["title"]

        # Step 2: Fetch Page Summary & Related Links
        page_url = "https://en.wikipedia.org/w/api.php"
        page_params = {
            "action": "query",
            "prop": "extracts|links",
            "exintro": True,
            "explaintext": True,
            "titles": title,
            "pllimit": 15,
            "format": "json"
        }

        page_res = requests.get(page_url, params=page_params, headers=HEADERS, timeout=8).json()
        pages = page_res.get("query", {}).get("pages", {})
        
        page_data = next(iter(pages.values()))
        extract = page_data.get("extract", "").strip()

        if not extract:
            return {
                "status": "error",
                "message": f"'{title}' ki summary retrieve nahi ho saki."
            }

        # 3-Layer Processing: TL;DR & Highlights
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', extract) if len(s.strip()) > 10]
        
        # Layer 1: TL;DR
        tldr = " ".join(sentences[:2]) if len(sentences) >= 2 else extract

        # Layer 2: Key Facts / Highlights
        key_facts = sentences[2:6] if len(sentences) > 2 else ["Detailed overview available in full source."]

        # Layer 3: Related Knowledge Nodes
        raw_links = page_data.get("links", [])
        related_nodes = [
            item["title"] for item in raw_links 
            if not item["title"].startswith("Template:") and not item["title"].startswith("Category:") and len(item["title"]) < 25
        ][:6]

        encoded_title = title.replace(" ", "_")
        source_url = f"https://en.wikipedia.org/wiki/{encoded_title}"

        return {
            "status": "success",
            "title": title,
            "tldr": tldr,
            "key_facts": key_facts,
            "related_nodes": related_nodes,
            "source_url": source_url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Server Error: {str(e)}"
        }


# Direct HTML UI route - No static folder path errors
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PySearch - Ultra Fast Knowledge Engine</title>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
            body {
                background-color: #08070d;
                background-image: radial-gradient(circle at 50% 10%, #1e1136 0%, #08070d 60%);
                color: #f1f5f9;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 40px 16px;
            }
            .container { width: 100%; max-width: 680px; text-align: center; }
            .badge {
                display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
                background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 999px; font-size: 0.75rem; letter-spacing: 0.06em;
                color: #38bdf8; margin-bottom: 24px; text-transform: uppercase;
            }
            .logo {
                font-size: 3rem; font-weight: 800;
                background: linear-gradient(90deg, #38bdf8, #ec4899);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 6px;
            }
            .subtitle { color: #94a3b8; font-size: 0.95rem; margin-bottom: 28px; }
            .search-box { width: 100%; position: relative; margin-bottom: 20px; }
            .search-input {
                width: 100%; padding: 16px 120px 16px 20px;
                background: rgba(18, 16, 26, 0.85); border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px; color: #fff; font-size: 1rem; outline: none;
                backdrop-filter: blur(12px); transition: all 0.2s ease;
            }
            .search-input:focus { border-color: #38bdf8; box-shadow: 0 0 20px rgba(56, 189, 248, 0.25); }
            .search-btn {
                position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
                background: linear-gradient(90deg, #0ea5e9, #2563eb); border: none;
                color: white; padding: 10px 20px; border-radius: 999px; font-weight: 600;
                cursor: pointer; transition: opacity 0.2s;
            }
            .search-btn:hover { opacity: 0.9; }
            .tags-container { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 32px; }
            .tag {
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 6px 14px; border-radius: 999px; font-size: 0.85rem; cursor: pointer;
                color: #cbd5e1; transition: all 0.2s;
            }
            .tag:hover { background: rgba(255, 255, 255, 0.12); color: #fff; transform: translateY(-1px); }
            .result-card {
                display: none; width: 100%; background: rgba(18, 16, 26, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 16px;
                padding: 24px; text-align: left; margin-top: 10px; backdrop-filter: blur(16px);
            }
            .result-title { font-size: 1.5rem; color: #fff; margin-bottom: 12px; font-weight: 700; }
            .section-heading {
                font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
                color: #38bdf8; margin: 16px 0 6px 0; font-weight: 700;
            }
            .tldr-text { color: #e2e8f0; line-height: 1.6; font-size: 0.95rem; }
            .facts-list { list-style: none; display: flex; flex-direction: column; gap: 8px; margin-top: 6px; }
            .facts-list li { position: relative; padding-left: 18px; font-size: 0.9rem; color: #94a3b8; line-height: 1.5; }
            .facts-list li::before { content: "•"; position: absolute; left: 0; color: #ec4899; font-weight: bold; }
            .nodes-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
            .node-pill {
                background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2);
                color: #38bdf8; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; cursor: pointer;
            }
            .node-pill:hover { background: rgba(56, 189, 248, 0.2); }
            .source-link { display: inline-block; margin-top: 18px; color: #ec4899; font-size: 0.85rem; text-decoration: none; }
            .source-link:hover { text-decoration: underline; }
            .loader {
                display: none; width: 26px; height: 26px; border: 3px solid rgba(255,255,255,0.2);
                border-radius: 50%; border-top-color: #38bdf8; animation: spin 0.8s linear infinite; margin: 20px auto;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">⚡ Ultra Fast Knowledge Engine</div>
            <h1 class="logo">PySearch</h1>
            <p class="subtitle">Search anything across the universe. No cap, pure signal.</p>

            <div class="search-box">
                <input type="text" id="queryInput" class="search-input" placeholder="Search anything (e.g. Virat Kohli, Python, SpaceX)...">
                <button class="search-btn" onclick="performSearch()">Search 🚀</button>
            </div>

            <div class="tags-container">
                <span class="tag" onclick="quickSearch('Virat Kohli')">🏏 Virat Kohli</span>
                <span class="tag" onclick="quickSearch('Artificial intelligence')">🤖 AI</span>
                <span class="tag" onclick="quickSearch('Python programming')">🐍 Python</span>
                <span class="tag" onclick="quickSearch('SpaceX')">🚀 SpaceX</span>
                <span class="tag" onclick="quickSearch('Narendra Modi')">🇮🇳 Narendra Modi</span>
            </div>

            <div class="loader" id="loader"></div>

            <div class="result-card" id="resultCard">
                <div class="result-title" id="resTitle"></div>
                
                <div class="section-heading">⚡ 10-Second TL;DR</div>
                <p class="tldr-text" id="resTldr"></p>

                <div class="section-heading">📌 Key Takeaways</div>
                <ul class="facts-list" id="resFacts"></ul>

                <div class="section-heading">🕸️ Related Knowledge Nodes</div>
                <div class="nodes-container" id="resNodes"></div>

                <a href="#" id="resLink" target="_blank" class="source-link">Read Full Encyclopedia Source ↗</a>
            </div>
        </div>

        <script>
            const queryInput = document.getElementById("queryInput");
            const loader = document.getElementById("loader");
            const resultCard = document.getElementById("resultCard");

            queryInput.addEventListener("keypress", function(e) {
                if (e.key === "Enter") performSearch();
            });

            function quickSearch(term) {
                queryInput.value = term;
                performSearch();
            }

            async function performSearch() {
                const query = queryInput.value.trim();
                if (!query) return;

                resultCard.style.display = "none";
                loader.style.display = "block";

                try {
                    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    loader.style.display = "none";

                    if (data.status === "error") {
                        alert(data.message);
                        return;
                    }

                    document.getElementById("resTitle").innerText = data.title;
                    document.getElementById("resTldr").innerText = data.tldr;
                    
                    const factsContainer = document.getElementById("resFacts");
                    factsContainer.innerHTML = "";
                    data.key_facts.forEach(fact => {
                        const li = document.createElement("li");
                        li.innerText = fact;
                        factsContainer.appendChild(li);
                    });

                    const nodesContainer = document.getElementById("resNodes");
                    nodesContainer.innerHTML = "";
                    data.related_nodes.forEach(node => {
                        const pill = document.createElement("span");
                        pill.className = "node-pill";
                        pill.innerText = node;
                        pill.onclick = () => quickSearch(node);
                        nodesContainer.appendChild(pill);
                    });

                    const link = document.getElementById("resLink");
                    link.href = data.source_url;

                    resultCard.style.display = "block";
                } catch (err) {
                    loader.style.display = "none";
                    alert("Search failed. Please try again.");
                }
            }
        </script>
    </body>
    </html>
    """
