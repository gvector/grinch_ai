# =============================================================================
# models/__init__.py
# =============================================================================
"""
Modulo models - Contiene tutti i modelli dati Pydantic.
"""

from models.data_models import (
    # Enums
    NewsCategory,
    TransportType,
    CourageLevel,
    
    # Input
    UserInput,
    
    # News
    NewsArticle,
    ClassifiedNews,
    NewsSearchResult,
    
    # Excuse
    ExcuseRequest,
    GeneratedExcuse,
    TicketData,
    ProofPhoto,
    CompleteExcuse,
    
    # State
    OrchestratorState,
)

__all__ = [
    # Enums
    "NewsCategory",
    "TransportType",
    "CourageLevel",
    
    # Input
    "UserInput",
    
    # News
    "NewsArticle",
    "ClassifiedNews",
    "NewsSearchResult",
    
    # Excuse
    "ExcuseRequest",
    "GeneratedExcuse",
    "TicketData",
    "ProofPhoto",
    "CompleteExcuse",
    
    # State
    "OrchestratorState",
]


# =============================================================================
# tools/__init__.py
# =============================================================================
"""
Modulo tools - Contiene tutti i tool utilizzabili dagli agenti.

I tool sono "capacità specifiche" che gli agenti possono utilizzare:
- WebSearchTool: cerca informazioni online
- TextGeneratorTool: genera testi (scuse, email)
- TicketGeneratorTool: genera biglietti aerei/treno
- ImageGeneratorTool: genera immagini fake
"""

from tools.web_search_tool import WebSearchTool

# Gli altri tool li aggiungeremo man mano
# from tools.text_generator_tool import TextGeneratorTool
# from tools.ticket_generator_tool import TicketGeneratorTool
# from tools.image_generator_tool import ImageGeneratorTool

__all__ = [
    "WebSearchTool",
    # "TextGeneratorTool",
    # "TicketGeneratorTool",
    # "ImageGeneratorTool",
]


# =============================================================================
# agents/__init__.py
# =============================================================================
"""
Modulo agents - Contiene tutti gli agenti del sistema.

Gli agenti sono entità intelligenti che:
- Prendono decisioni autonome
- Coordinano l'uso di più tool
- Raggiungono obiettivi specifici

Agenti Fase 1 (Ricerca Notizie):
- NewsSearcherAgent: cerca notizie online
- NewsClassifierAgent: classifica e valuta notizie

Agenti Fase 2 (Generazione Scusa):
- ExcuseWriterAgent: scrive la scusa
- TicketGeneratorAgent: genera biglietti
- ProofPhotoGeneratorAgent: genera foto fake
"""

from agents.news_searcher import NewsSearcherAgent

# Gli altri agenti li aggiungeremo man mano
# from agents.news_classifier import NewsClassifierAgent
# from agents.excuse_writer import ExcuseWriterAgent
# from agents.ticket_generator import TicketGeneratorAgent
# from agents.proof_photo_generator import ProofPhotoGeneratorAgent

__all__ = [
    "NewsSearcherAgent",
    # "NewsClassifierAgent",
    # "ExcuseWriterAgent",
    # "TicketGeneratorAgent",
    # "ProofPhotoGeneratorAgent",
]


# =============================================================================
# orchestrators/__init__.py
# =============================================================================
"""
Modulo orchestrators - Contiene gli orchestratori che coordinano gli agenti.

Gli orchestratori sono responsabili di:
- Coordinare più agenti in sequenza
- Gestire il flusso dei dati tra agenti
- Tracciare lo stato e gestire errori
- Fornire risultati aggregati

Orchestratori:
- NewsSearchOrchestrator: coordina Fase 1 (ricerca + classificazione notizie)
- ExcuseGeneratorOrchestrator: coordina Fase 2 (generazione scusa completa)
"""

# Gli orchestratori li creeremo dopo
# from orchestrators.news_search_orchestrator import NewsSearchOrchestrator
# from orchestrators.excuse_generator_orchestrator import ExcuseGeneratorOrchestrator

__all__ = [
    # "NewsSearchOrchestrator",
    # "ExcuseGeneratorOrchestrator",
]


# =============================================================================
# SPIEGAZIONE STRUTTURA MODULI
# =============================================================================

"""
COME FUNZIONA LA STRUTTURA:

1. models/ 
   └─ Definisce la struttura dei DATI
   └─ Pydantic models per validazione e type safety
   
2. tools/
   └─ Implementa CAPACITÀ SPECIFICHE
   └─ "Mani" che gli agenti possono usare
   └─ Es: cercare web, generare immagini, inviare email
   
3. agents/
   └─ Implementa LOGICA DECISIONALE
   └─ "Cervelli" che decidono quando e come usare i tool
   └─ Ogni agente ha un obiettivo specifico
   
4. orchestrators/
   └─ Coordinano PIÙ AGENTI
   └─ Gestiscono workflow complessi
   └─ Combinano risultati di più agenti

FLUSSO TIPICO:
User Input → Orchestrator → Agent 1 → Tool → Agent 2 → ... → Final Output


ESEMPIO CONCRETO (Fase 1):

UserInput
   ↓
NewsSearchOrchestrator
   ↓
   ├─ NewsSearcherAgent
   │    └─ usa WebSearchTool
   │    └─ ritorna NewsArticle[]
   ↓
   └─ NewsClassifierAgent
        └─ classifica NewsArticle[]
        └─ ritorna ClassifiedNews
   ↓
NewsSearchResult (output finale Fase 1)


COME IMPORTARE:

# Importa modelli
from models import UserInput, NewsArticle

# Importa tool
from tools import WebSearchTool

# Importa agenti
from agents import NewsSearcherAgent

# Importa orchestratori
from orchestrators import NewsSearchOrchestrator

# O importa tutto da config
from config import settings
"""