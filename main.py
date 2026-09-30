from src.tools.tools import scrape_url, web_search

#print(web_search.invoke({"query": "Latest AI research papers"}))

#output = web_search.invoke({"query": "Latest AI research papers"})
#print(output)

results = scrape_url.invoke({"url": "https://learnprompting.org/blog/resources_latest_research_papers"})
print(results)