import os
import re
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Complete Gen-Z Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if query %}{{ query }} ⚡ PySearch{% else %}PySearch ⚡ No Cap Search{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800;900&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-dark: #090a0f;
            --card-bg: rgba(255, 255, 255, 0.04);
            --card-border: rgba(255, 255, 255, 0.1);
            --neon-blue: #00f0ff;
            --neon-pink: #ff007f;
            --neon-purple: #7928ca;
            --neon-green: #00ff88;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        .glow-blob-1 {
            position: fixed; width: 450px; height: 450px; top: -100px; left: -100px;
            background: radial-gradient(circle, rgba(121, 40, 202, 0.35) 0%, rgba(0,0,0,0) 70%);
            z-index: -1; filter: blur(40px); pointer-events: none;
        }
        .glow-blob-2 {
            position: fixed; width: 500px; height: 500px; bottom: -150px; right: -100px;
            background: radial-gradient(circle, rgba(0, 240, 255, 0.25) 0%, rgba(0,0,0,0) 70%);
            z-index: -1; filter: blur(50px); pointer-events: none;
        }
        .home-wrap {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 90vh; padding: 20px; text-align: center;
        }
        .hero-tag {
            display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px;
            background: rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 30px; font-size: 13px; font-weight: 600; color: var(--neon-blue);
            margin-bottom: 20px; letter-spacing: 0.5px; text-transform: uppercase;
        }
        .genz-logo {
            font-size: clamp(48px, 9vw, 84px); font-weight: 900; letter-spacing: -2px; margin-bottom: 8px;
            background: linear-gradient(135deg, #00f0ff 0%, #7928ca 50%, #ff007f 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 30px rgba(121, 40, 202, 0.3);
        }
        .tagline { color: var(--text-muted); font-size: 16px; margin-bottom: 35px; font-weight: 500; }
        .search-box-wrap { width: 100%; max-width: 640px; position: relative; }
        .glass-input-box {
            display: flex; align-items: center; background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border); backdrop-filter: blur(16px);
            border-radius: 50px; padding: 6px 8px 6px 22px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-input-box:focus-within {
            border-color: var(--neon-blue);
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
            transform: scale(1.01);
        }
        .glass-input-box input {
            flex: 1; background: transparent; border: none; outline: none;
            color: #ffffff; font-size: 17px; font-family: inherit; font-weight: 500;
        }
        .glass-input-box input::placeholder { color: #6b7280; }
        .glass-btn {
            background: linear-gradient(135deg, #00f0ff 0%, #7928ca 100%);
            color: #ffffff; border: none; padding: 14px 28px; border-radius: 40px;
            font-weight: 800; font-size: 15px; cursor: pointer; letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(0, 240, 255, 0.4);
        }
        .trending-chips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-top: 25px; }
        .chip {
            padding: 6px 14px; border-radius: 20px; background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08); color: var(--text-muted);
            font-size: 13px; text-decoration: none; font-weight: 600;
        }
        .chip:hover { color: var(--neon-blue); border-color: var(--neon-blue); background: rgba(0, 240, 255, 0.08); }
        .results-page { max-width: 900px; margin: 0 auto; padding: 30px 24px 80px; }
        .nav-header { display: flex; align-items: center; gap: 24px; margin-bottom: 30px; flex-wrap: wrap; }
        .nav-logo {
            font-size: 28px; font-weight: 900; text-decoration: none;
            background: linear-gradient(135deg, #00f0ff, #ff007f);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .meta-stats {
            font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--neon-green);
            margin-bottom: 25px; display: flex; align-items: center; gap: 8px;
        }
        .result-card {
            background: var(--card-bg); border: 1px solid var(--card-border);
            border-radius: 20px; padding: 22px; margin-bottom: 18px; backdrop-filter: blur(12px);
        }
        .result-card:hover {
            transform: translateY(-3px); border-color: rgba(0, 240, 255, 0.4);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .card-url {
            font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--neon-blue);
            margin-bottom: 8px; display: block; text-decoration: none; word-break: break-all;
        }
        .card-title {
            font-size: 21px; font-weight: 800; color: #ffffff; text-decoration: none; display: inline-block; margin-bottom: 10px;
        }
        .card-title:hover { color: var(--neon-pink); }
        .card-snippet { font-size: 14.5px; line-height: 1.6; color: var(--text-muted); }
        .empty-box {
            text-align: center; padding: 60px 20px; background: var(--card-bg);
            border: 1px dashed var(--card-border); border-radius: 24px;
        }
    </style>
</head>
<body>
    <div class="glow-blob-1"></div>
    <div class="glow-blob-2"></div>
    {% if not query %}
        <div class="home-wrap">
            <div class="hero-tag">⚡ Ultra Fast Knowledge Engine</div>
            <h1 class="genz-logo">PySearch</h1>
            <p class="tagline">Search anything across the universe. No cap, pure signal.</p>
            <div class="search-box-wrap">
                <form class="glass-input-box" action="/" method="GET">
                    <input type="text" name="q" placeholder="Search anyone (e.g. Virat Kohli, Narendra Modi, AI)..." required autofocus>
                    <button type="submit" class="glass-btn">Search 🚀</button>
                </form>
            </div>
            <div class="trending-chips">
                <a href="/?q=Virat+Kohli" class="chip">🏏 Virat Kohli</a>
                <a href="/?q=Artificial+Intelligence" class="chip">🤖 AI & Future</a>
                <a href="/?q=Narendra+Modi" class="chip">🇮🇳 Narendra Modi</a>
                <a href="/?q=Python+programming" class="chip">🐍 Python Code</a>
                <a href="/?q=SpaceX" class="chip">🚀 SpaceX</a>
            </div>
        </div>
    {% else %}
        <div class="results-page">
            <div class="nav-header">
                <a href="/" class="nav-logo">PySearch⚡</a>
                <div class="search-box-wrap" style="max-width: 600px;">
                    <form class="glass-input-box" action="/" method="GET">
                        <input type="text" name="q" value="{{ query }}" required autofocus>
                        <button type="submit" class="glass-btn">Search</button>
                    </form>
                </div>
            </div>
            <div class="meta-stats">Found {{ results|length }} live verified entities for "{{ query }}"</div>
            {% if results %}
                {% for res in results %}
                    <div class="result-card">
                        <a class="card-url" href="{{ res.url }}" target="_blank">{{ res.url }}</a>
                        <a class="card-title" href="{{ res.url }}" target="_blank">{{ res.title }}</a>
                        <div class="card-snippet">{{ res.snippet }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="empty-box">
                    <h3 style="color: var(--neon-pink); margin-bottom: 8px;">No Results Found 💀</h3>
                    <p style="color: var(--text-muted); font-size: 14px;">Try searching for another topic or name.</p>
                </div>
            {% endif %}
        </div>
    {% endif %}
</body>
</html>
"""

def live_web_search(query):
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 8
    }
    headers = {"User-Agent": "PySearchEngine/3.0 (contact@example.com)"}
    results = []
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=6)
        data = response.json()
        for item in data.get("query", {}).get("search", []):
            title = item.get("title")
            raw_snippet = item.get("snippet", "")
            clean_snippet = re.sub(r'<.*?>', '', raw_snippet)
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            results.append({"title": title, "url": url, "snippet": clean_snippet + "..."})
    except Exception as e:
        print(f"API Error: {e}")
    return results

@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = live_web_search(query)
    return render_template_string(HTML_TEMPLATE, query=query, results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
