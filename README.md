# RCM 

### Week 1
- Contact web scraper with semantic embedding layer (rough draft)

### Week 2
- Data cleaner Stifel

### Week 3
- Dakota X Salesforce data clean and merge
- Salesforce 6/18 clean (state fill, dupe check)

### Week 4
- Email Semantic scoring (project 5)
- Agent for quick DDQ and Tracey market reports generation and navigation
- Documentation for agent

### Week 5
- Dakota - salesforce clean revisited - 3 lists
- Dakota wider DB creation (including AUM & etc) for project 4
- Automated prospecting tool (project 4) rough draft
     - Lead scoring here
     - 3 tier levels of clients
     - Copiot agent for looking in inbox to cross check
     - A layer of who was previously reached out to and who was mentioned
     - RGFO penetration overlay
     - Weave in agents for LLM level inference

### Week 6
- Prospecting demos (Kevin and Mark)
- Prospecting tool refactor
     - Ideas: switch to operate on Salesforce data, integrate in Salesforce via Visualforce/iframe/embedding, have key visuals
- API swap test for email tool - 1k max searches (not working well) and improved bulk feature
- Muni research ideas + rough draft
- Scale up agent 
- Travel outreach agent

### Week 7
- Data clean final
- Prospecting tool rough draft
- Email scraper to agent conversion

### Week 8

### Week 9

### Week 10
- Presentation
     - RAM pitch (2 mins)
     - What I did with tech - story to sales pitch
     - Sales process
     - Where RAM differentiates itself and the final application
- Do project 1 sometime here (sales pitch), maybe pitch high yeild muni

### RAM Pitch
- About RAM
- RAMs equity research process

### Other
- Quant project Jai and Nikhil
     - A study on minimizing tracking error for balance fund
     - Black-Litterman for including investor expectations
     - Factor models
     - Quant audits

- Fixed income project Alex and Brent?
- Ideas: write a technical paper with a backtest on muni stuff
     - Case study on muni index vs t-bill spread
     - model default rates and recovery rates, maybe throw in MC simulations here
     - something on trading pressure being skewed short term due to money managers running ladder strategies
     - show some kind of carry style signal for muni trading but for spread, compare it to T bills




                          ┌──────────────────────────────┐
                          │ 🔐 Access Control             │
                          │ - Password gate              │
                          │ - App entry & routing        │
                          │ → prospect_search.py         │
                          └────────────▲─────────────────┘
                                       │
                          ┌────────────┴─────────────────┐
                          │ 📡 Data Access                │
                          │ - SOQL query to Salesforce   │
                          │ - Secret management          │
                          │ → data_loader.py             │
                          └────────────▲─────────────────┘
                                       │
                          ┌────────────┴─────────────────┐
                          │ 🧠 Semantic Scoring           │
                          │ - Embed + rank contacts      │
                          │ - Group by firm              │
                          │ → semantic_ranker.py         │
                          │ → contact_utils.py           │
                          └────────────▲─────────────────┘
                                       │
                          ┌────────────┴─────────────────┐
                          │ 🗺️ Visualization              │
                          │ - Map (pydeck) + tables       │
                          │ - Streamlit view layout       │
                          │ → geo_utils.py                │
                          │ → prospect_search.py          │
                          └────────────▲─────────────────┘
                                       │
                          ┌────────────┴─────────────────┐
                          │ 🌐 Contact Discovery          │
                          │ - Scraping + SerpAPI         │
                          │ - Email extraction (regex)   │
                          │ → scraper_utils.py           │
                          └────────────▲─────────────────┘
                                       │
                          ┌────────────┴─────────────────┐
                          │ 🤖 AI Outreach                │
                          │ - LLM-generated messages     │
                          │ - Groq / Together API calls  │
                          │ → outreach_utils.py          │
                          └──────────────────────────────┘
