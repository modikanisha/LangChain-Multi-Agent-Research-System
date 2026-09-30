from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print 
from bs4 import BeautifulSoup
import trafilatura
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)
    #print(results)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

# Downloads a page, extracts its readable text, and falls back to basic HTML cleanup.
@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    """
    # Download the page; the timeout prevents this tool from waiting indefinitely.
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"},
        timeout=20,
    )
    # Raise an error for HTTP failures such as 404 or 500 responses.
    response.raise_for_status()

    # Keep the HTML for both extraction methods and parse it to find the page title.
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else response.url

    # Try to extract the main article text, excluding most page navigation and clutter.
    content = trafilatura.extract(html, url=response.url)
    if not content:
        # If article extraction fails, remove common non-content elements and use page text.
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        content = soup.get_text(separator="\n", strip=True)

    # Return a clear message instead of an empty result when neither method finds text.
    if not content:
        return f"No readable content found at {response.url}"

    # Remove blank lines and trim each line to make the returned text easier to read.
    content = "\n".join(line.strip() for line in content.splitlines() if line.strip())

    # Keep large pages within a reasonable result size for downstream tools.
    max_characters = 20000
    if len(content) > max_characters:
        content = content[:max_characters].rstrip() + "\n\n[Content truncated]"

    # Include the title and final URL so callers know where the text came from.
    return f"Title: {title}\nURL: {response.url}\n\n{content}"