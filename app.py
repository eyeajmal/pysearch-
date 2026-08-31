import os
import re
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% if query %}{{ query }} ⚡ PySearch{% else %}PySearch ⚡ No Cap Search{% endif %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

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
            position: fixed;
            width: 320px;
            height: 320px;
            top: -60px;
            left: -60px;
            background: radial-gradient(circle, rgba(121, 40, 202, 0.35) 0%, rgba(0,0,0,0) 70%);
            z-index: -1;
            filter: blur(40px);
            pointer-events: none;
        }
        .glow-blob-2 {
            position: fixed;
            width: 350px;
            height: 350px;
            bottom: -100px;
            right: -60px;
            background: radial-gradient(circle, rgba(0, 240, 255, 0.25) 0%, rgba(0,0,0,0) 70%);
            z-index: -1;
            filter: blur(50px);
            pointer-events: none;
        }

        /* Home View */
        .home-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 90vh;
            padding: 24px 16px;
            text-align: center;
        }

        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 14px;
            background: rgba(0, 240, 255, 0.1);
            border: 1px solid rgba(0, 240, 255, 0.25);
            border-radius: 30px;
            font-size: 11px;
            font-weight: 700;
            color: var(--neon-blue);
            margin-bottom: 18px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .genz-logo {
            font-size: clamp(42px, 12vw, 76px);
            font-weight: 900;
            letter-spacing: -2px;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #00f0ff 0%, #7928ca 50%, #ff007f 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .tagline {
            color: var(--text-muted);
            font-size: 14px;
            max-width: 340px;
            margin-bottom: 30px;
            font-weight: 500;
            line-height: 1.4;
        }

        /* Responsive Search Bar Container */
        .search-box-wrap {
            width: 100%;
            max-width: 580px;
            margin: 0 auto;
        }

        .glass-input-box {
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.05);
            border: 1.5px solid var(--card-border);
            backdrop-filter: blur(16px);
            border-radius: 50px;
            padding: 4px 6px 4px 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }

        .glass-input-box:focus-within {
            border-color: var(--neon-blue);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.25);
        }

        .glass-input-box input {
            flex: 1;
            min-width: 0;
            background: transparent;
            border: none;
            outline: none;
            color: #ffffff;
            font-size: 15px;
            font-family: inherit;
            font-weight: 500;
            padding-right: 8px;
        }

        .glass-input-box input::placeholder {
            color: #6b7280;
            font-size: 14px;
        }

        .glass-btn {
            background: linear-gradient(135deg, #00f0ff 0%, #7928ca 100%);
            color: #ffffff;
            border: none;
            padding: 11px 20px;
            border-radius: 40px;
            font-weight: 800;
            font-size: 14px;
            cursor: pointer;
            white-space: nowrap;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 240, 255, 0.35);
            transition: transform 0.15s;
        }

        .glass-btn:active {
            transform: scale(0.96);
        }

        /* Trending Chips */
        .trending-chips {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 22px;
            max-width: 480px;
        }

        .chip {
            padding: 6px 13px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
            font-size: 12.5px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }

        .chip:hover, .chip:active {
            color: var(--neon-blue);
            border-color: var(--neon-blue);
            background: rgba(0, 240, 255, 0.08);
        }

        /* Results Layout */
        .results-page {
            max-width: 820px;
            margin: 0 auto;
            padding: 20px 16px 60px;
        }

        .nav-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .nav-logo {
            font-size: 24px;
            font-weight: 900;
            text-decoration: none;
            background: linear-gradient(135deg, #00f0ff, #ff007f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
            flex-shrink: 0;
        }

        .nav-header .search-box-wrap {
            flex: 1;
            min-width: 240px;
        }

        .meta-stats {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--neon-green);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .meta-stats::before {
            content: '';
            width: 7px;
            height: 7px;
            background-color: var(--neon-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--neon-green);
            display: inline-block;
        }

        .result-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
            backdrop-filter: blur(12px);
        }

        .card-url {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--neon-blue);
            margin-bottom: 6px;
            display: block;
            text-decoration: none;
            opacity: 0.85;
            word-break: break-all;
        }

        .card-title {
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 8px;
            line-height: 1.3;
        }

        .card-snippet {
            font-size: 13.5px;
            line-height: 1.5;
            color: var(--text-muted);
        }

        .empty-box {
            text-align: center;
            padding: 40px 16px;
            background: var(--card-bg);
            border: 1px dashed var(--card-border);
            border-radius: 18px;
        }

        /* Mobile specific fixes */
        @media (max-width: 480px) {
            .glass-input-box {
                padding: 3px 4px 3px 14px;
            }
            .glass-btn {
                padding: 10px 16px;
                font-size: 13px;
            }
            .glass-input-box input {
                font-size: 14px;
            }
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
                    <input type="text" name="q" placeholder="Search anything (e.g. Virat, Modi)..." required autofocus>
                    <button type="submit" class="glass-btn">Search 🚀</button>
                </form>
            </div>

            <div class="trending-chips">
                <a href="/?q=Virat+Kohli" class="chip">🏏 Virat Kohli</a>
                <a href="/?q=Artificial+Intelligence" class="chip">🤖 AI</a>
                <a href="/?q=Narendra+Modi" class="chip">🇮🇳 Narendra Modi</a>
                <a href="/?q=Python+programming" class="chip">🐍 Python</a>
                <a href="/?q=SpaceX" class="chip">🚀 SpaceX</a>
            </div>
        </div>
    {% else %}
        <div class="results-page">
            <div class="nav-header">
                <a href="/" class="nav-logo">PySearch⚡</a>
                <div class="search-box-wrap">
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
                    <h3 style="color: var(--neon-pink); margin-bottom: 6px;">404 Vibe Check Failed 💀</h3>
                    <p style="color: var(--text-muted); font-size: 13px;">No results found for "<b>{{ query }}</b>".</p>
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
