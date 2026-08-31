import streamlit as st
import requests
import re

st.set_page_config(page_title="PySearch ⚡", page_icon="⚡", layout="centered")

# Custom Clean Styling with minimal code
st.title("⚡ PySearch")
st.caption("Real-time live knowledge engine — pure Python power.")

# Search Input Box
query = st.text_input("Search query", placeholder="e.g. Virat Kohli, AI, Narendra Modi...", label_visibility="collapsed")

# Wikipedia Search Function
def search_wiki(q):
    url = "https://en.wikipedia.org/w/api.php"
    params = {"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": 7}
    headers = {"User-Agent": "PySearchStreamlit/1.0"}
    res = requests.get(url, params=params, headers=headers).json()
    return res.get("query", {}).get("search", [])

if query:
    results = search_wiki(query)
    st.write(f"### Results for: `{query}`")
    
    if results:
        for item in results:
            title = item.get("title")
            snippet = re.sub(r'<.*?>', '', item.get("snippet", ""))
            link = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            
            with st.container():
                st.markdown(f"#### [{title}]({link})")
                st.write(snippet + "...")
                st.divider()
    else:
        st.warning("No results found.")
