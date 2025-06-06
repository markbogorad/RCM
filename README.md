# RCM Scraper

## Architecture
1) Smart Discovery tool
    - Semantic search and query refinment algorithms

    | Component                           | Role                                                       |
| ----------------------------------- | ---------------------------------------------------------- |
| **Search API (e.g., SerpAPI/Bing)** | Pull top N links from Google/Bing for a query              |
| **Text Extractor**                  | Fetch raw text from each page (BeautifulSoup + `requests`) |
| **Semantic Scorer**                 | Rank pages by similarity to target research intent         |
| **Query Generator/Refiner**         | Adjust next query based on what got good scores            |
| **(Optional) Caching**              | Avoid re-fetching and re-scoring the same pages            |


2) Content Refinement 
    - Identify correct emails with likelihoods based on some empirical database
    - Identify the gatekeeper (smart algorithm to find the gatekeeper by titles, other searches, etc)
    - Identify investment requirments by public documents -> potential matching component with RAMs offering via some score