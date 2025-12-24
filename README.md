# Struttura Progetto Rivista
```
excuse-generator/
│
├── .env
├── requirements.txt
├── README.md
│
├── app.py                 # Streamlit main app
│
├── config/
│   ├── settings.py        # Configurazioni, chiavi
│   └── prompts.py         # System prompts per agenti
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py    # DataPizza Pipeline
│   ├── news_collector.py  # Agent + Tools
│   ├── excuse_creator.py
│   └── evidence_builder.py
│
├── tools/
│   ├── __init__.py
│   ├── news_api.py        # NewsAPI, GNews wrapper
│   ├── scraper.py         # Playwright per weird news
│   └── image_search.py    # [Unsplash](https://unsplash.com/developers)/[Pexels](https://www.pexels.com/api/)
│
├── storage/
│   ├── qdrant_manager.py  # Gestione vector DB
│   ├── redis_cache.py     # Cache manager
│   └── schemas.py         # Pydantic models
│
├── utils/
│   ├── auth.py            # Verifica chiavi
│   └── helpers.py
│
└── data/
    └── qdrant_data/       # Local Qdrant storage
```

# System Workflow

1. **INPUT UTENTE**

   ↓
2. **ORCHESTRATOR** analizza richiesta

   ↓
3. **NEWS SCRAPER** → raccoglie notizie fresh (parallelo su più fonti)

   ↓
4. **ORCHESTRATOR** filtra/seleziona notizie rilevanti

   ↓
5. **EXCUSE GENERATOR** → crea opzioni di scuse

   ↓
6. **UTENTE** sceglie scusa preferita

   ↓
7. **EVIDENCE CREATOR** → trova/crea prove (se richiesto)

   ↓
8. **COMMUNICATION AGENT** → draft messaggio

   ↓
9. **REVIEW UTENTE** → edit/approve

   ↓
10. **INVIO** (opzionale) + SALVATAGGIO in memoria
