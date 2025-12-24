# tools/web_search_tool.py
"""
Tool per cercare notizie online.
Questo tool permette agli agenti di cercare informazioni sul web.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic

from config import settings

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Tool che permette di cercare notizie online usando Claude con web search.
    
    Questo è un esempio di "Tool" in Datapizza:
    - È una CAPACITÀ SPECIFICA che gli agenti possono usare
    - Incapsula la logica di interazione con API esterne
    - Ritorna dati strutturati che gli agenti possono elaborare
    """
    
    def __init__(self):
        """Inizializza il tool con il client Anthropic"""
        if not settings.validate_api_key():
            raise ValueError("ANTHROPIC_API_KEY non configurata!")
        
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.name = "web_search"
        self.description = "Cerca notizie recenti online"
        
        logger.info("✅ WebSearchTool inizializzato")
    
    def search_news(
        self, 
        query: str,
        max_results: int = None,
        days_back: int = None
    ) -> List[Dict]:
        """
        Cerca notizie online basandosi sulla query.
        
        Args:
            query: Query di ricerca (es: "notizie assurde Italia")
            max_results: Numero massimo di risultati (default: da config)
            days_back: Cerca negli ultimi N giorni (default: da config)
        
        Returns:
            Lista di dizionari con: titolo, fonte, url, snippet, data
        """
        max_results = max_results or settings.NEWS_SEARCH_RESULTS_LIMIT
        days_back = days_back or settings.NEWS_RECENCY_DAYS
        
        # Costruiamo una query che specifica la recency
        date_filter = f"ultimi {days_back} giorni"
        enhanced_query = f"{query} {date_filter}"
        
        logger.info(f"🔍 Ricerca web: '{enhanced_query}'")
        
        try:
            # Chiamata a Claude con web search abilitato
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search"
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": f"""Cerca online notizie recenti (ultimi {days_back} giorni) relative a: {query}

Restituisci ESATTAMENTE {max_results} notizie nel seguente formato JSON (senza markdown):
[
  {{
    "titolo": "titolo della notizia",
    "fonte": "nome della fonte",
    "url": "link completo",
    "snippet": "breve estratto della notizia (max 200 caratteri)",
    "data_pubblicazione": "data se disponibile, altrimenti 'recente'"
  }}
]

IMPORTANTE:
- Cerca notizie VERE e VERIFICABILI da fonti attendibili
- Prioritizza notizie italiane se pertinenti alla query
- Includi una varietà di fonti
- Restituisci SOLO il JSON array, niente altro"""
                    }
                ]
            )
            
            # Estrai il contenuto della risposta
            results = self._parse_response(response)
            
            logger.info(f"✅ Trovate {len(results)} notizie")
            return results
            
        except Exception as e:
            logger.error(f"❌ Errore durante ricerca web: {str(e)}")
            # Ritorna lista vuota invece di fallire
            return []
    
    def _parse_response(self, response) -> List[Dict]:
        """
        Parsifica la risposta di Claude ed estrae i risultati di ricerca.
        
        Args:
            response: Risposta API di Claude
            
        Returns:
            Lista di dizionari con i risultati
        """
        try:
            import json
            
            # Claude potrebbe rispondere con testo + tool use
            # Cerchiamo il contenuto testuale con il JSON
            full_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    full_text += block.text
            
            # Rimuovi eventuali markdown backticks
            full_text = full_text.strip()
            if full_text.startswith("```json"):
                full_text = full_text[7:]
            if full_text.startswith("```"):
                full_text = full_text[3:]
            if full_text.endswith("```"):
                full_text = full_text[:-3]
            
            full_text = full_text.strip()
            
            # Parse JSON
            results = json.loads(full_text)
            
            if not isinstance(results, list):
                logger.warning("Risposta non è una lista, ritorno lista vuota")
                return []
            
            # Valida che ogni risultato abbia i campi richiesti
            validated_results = []
            required_fields = ["titolo", "fonte", "url", "snippet"]
            
            for result in results:
                if all(field in result for field in required_fields):
                    # Aggiungi timestamp se non presente
                    if "data_pubblicazione" not in result:
                        result["data_pubblicazione"] = "recente"
                    validated_results.append(result)
                else:
                    logger.warning(f"Risultato mancante di campi: {result}")
            
            return validated_results
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Errore parsing JSON: {str(e)}")
            logger.debug(f"Contenuto ricevuto: {full_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"❌ Errore inaspettato nel parsing: {str(e)}")
            return []
    
    def search_by_categories(self, base_query: str) -> Dict[str, List[Dict]]:
        """
        Cerca notizie per tutte e 4 le categorie.
        
        Args:
            base_query: Query base (es: "Italia")
            
        Returns:
            Dict con chiave = categoria, valore = lista notizie
        """
        categories_queries = {
            "nazionale_divertente": f"{base_query} notizie divertenti curiose Italia",
            "internazionale_divertente": f"notizie divertenti curiose mondo internazionali",
            "nazionale_assurda": f"{base_query} notizie assurde strane bizzarre Italia",
            "internazionale_assurda": f"notizie assurde strane bizzarre mondo internazionali"
        }
        
        results = {}
        
        for category, query in categories_queries.items():
            logger.info(f"📰 Ricerca categoria: {category}")
            
            # Cerca meno risultati per categoria per non fare troppe richieste
            news = self.search_news(
                query=query,
                max_results=settings.MAX_NEWS_PER_CATEGORY * 2  # Cerchiamo il doppio poi filtriamo
            )
            
            results[category] = news
        
        return results
    
    def get_article_full_content(self, url: str) -> Optional[str]:
        """
        Opzionale: Recupera il contenuto completo di un articolo.
        Utile se vogliamo più dettagli per generare la scusa.
        
        Args:
            url: URL dell'articolo
            
        Returns:
            Contenuto testuale dell'articolo o None
        """
        try:
            logger.info(f"📄 Recupero contenuto da: {url}")
            
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Vai a questo URL e riassumi il contenuto principale dell'articolo in 2-3 paragrafi:
{url}

Concentrati sui fatti principali e i dettagli più interessanti."""
                    }
                ]
            )
            
            # Estrai testo
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"❌ Errore recupero articolo: {str(e)}")
            return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_web_search():
    """
    Funzione di test per verificare che il tool funzioni.
    Esegui: python tools/web_search_tool.py
    """
    print("\n" + "="*60)
    print("🧪 TEST WEB SEARCH TOOL")
    print("="*60 + "\n")
    
    tool = WebSearchTool()
    
    # Test ricerca semplice
    print("📌 Test 1: Ricerca notizie assurde Italia\n")
    results = tool.search_news("notizie assurde Italia", max_results=3)
    
    if results:
        print(f"✅ Trovate {len(results)} notizie:\n")
        for i, news in enumerate(results, 1):
            print(f"{i}. {news['titolo']}")
            print(f"   Fonte: {news['fonte']}")
            print(f"   URL: {news['url']}")
            print(f"   Snippet: {news['snippet'][:100]}...")
            print()
    else:
        print("❌ Nessuna notizia trovata\n")
    
    # Test ricerca per categorie
    print("\n📌 Test 2: Ricerca per tutte le categorie\n")
    all_results = tool.search_by_categories("Italia")
    
    for category, news_list in all_results.items():
        print(f"📰 {category}: {len(news_list)} notizie")
    
    print("\n" + "="*60)
    print("✅ Test completati!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Se esegui questo file direttamente, lancia i test
    test_web_search()