# pyrefly: ignore [missing-import]
from langchain.tools import tool
from bs4 import BeautifulSoup
# pyrefly: ignore [missing-import]
from tavily import TavilyClient
import requests
import os
from dotenv import load_dotenv
# from rich import print 
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool   # it is a decorator : it is telling that the below function is going to use as a tool
def web_search(query : str) ->str:
    """ Search the web for recent and reliable information of a topic . Return titles , URL's and snippets"""
    results = tavily.search(query = query, max_results = 5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n\n"    
        )

    return "\n---\n".join(out)

# print(web_search.invoke("what are the most recent news about war?"))


@tool
def scrape_url(url :str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout = 8 , headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["Script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip =True)[:3000]
    except Exception as e:
        return f"could not scrape URL: {str(e)}"

print(scrape_url.invoke("https://indianexpress.com/article/entertainment/telugu/prabhas-at-45-between-the-mr-perfect-of-the-masses-and-darling-of-the-box-office-lies-a-rebel-of-a-few-words-9634018/"))


