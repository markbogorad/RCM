# RCM Scraper

### Week 1
- Contact web scraper with semantic embedding layer (rough draft)

### Week 2
- Data cleaner Stifel

### Week 3
- Dakota X Salesforce data clean and merge
- Salesforce 6/18 clean (state fill, dupe check)

### Week 4
- Email Semantic scoring (project 5)

                ┌──────────────┐
                │ User Inputs  │
                └────┬─────────┘
                     ▼
         ┌────────────────────────┐
         │ scraper_utils.py       │
         │ - Remix emails         │
         │ - Google SERP queries  │
         │ - Reverse discovery    │
         └────┬───────────────────┘
              ▼
     ┌──────────────────────┐
     │ semantic_utils.py    │ ← SBERT
     │ - Embed text         │
     │ - Compute similarity │
     └──────────┬───────────┘
                ▼
       ┌──────────────────────┐
       │ scoring_utils.py     │
       │ - Rank matches       │
       │ - Combine scores     │
       │ - Flag risks         │
       └────────┬─────────────┘
                ▼
    ┌─────────────────────────┐
    │ analytics_utils.py      │
    │ - Most common words     │
    │ - # pages scanned       │
    │ - Domain pattern hits   │
    └─────────────────────────┘

- Automated prospecting tool (project 4)



### Week 5
- Database + agent for quick DDQ and Tracey market reports generation and navigation

### Week 6

### Week 7

### Week 8

### Week 9

### Week 10