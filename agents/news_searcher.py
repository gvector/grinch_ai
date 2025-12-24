# agents/news_searcher.py
"""
NewsSearcherAgent - Agente responsabile della ricerca di notizie online.

Questo agente:
1. Riceve un input dall'utente (impegno da saltare + livello coraggio)
2. Decide quali query di ricerca fare
3. Usa il WebSearchTool per cercare notizie
4. Ritorna una lista di notizie grezze (non ancora classificate)
"""

import logging
from typing import List, Dict
from datetime import datetime

from datapizza import Agent, Tool
from anthropic import Anthropic

from config import settings
from models.data_models import UserInput, NewsArticle
from tools.web_search_tool import WebSearchTool

logger = logging.getLogger(__name__)


class NewsSearcherAgent(Agent):
    """
    Agente che cerca notizie online adatte per creare scuse.
    
    COSA FA UN AGENTE:
    - Prende decisioni intelligenti su COME usare i tool
    - Ha un "goal" specifico da raggiungere
    - Può fare ragionamenti complessi
    - Coordina l'uso di più tool se necessario
    
    DIFFERENZA TRA AGENT E TOOL:
    - TOOL = "mani" (capacità specifiche: cerca, genera immagini, ecc)
    - AGENT = "cervello" (decide QUANDO e COME usare i tool)
    """
    
    def __init__(self):
        """Inizializza l'agente con i suoi tool"""
        
        # Tool che l'agente può usare
        self.web_search_tool = WebSearchTool()
        
        # Client Anthropic per il ragionamento dell'agente
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # System prompt: definisce il "carattere" e gli obiettivi dell'agente
        self.system_prompt = """Sei un agente specializzato nella ricerca di notizie per creare scuse credibili.

Il tuo compito è:
1. Analizzare l'impegno che l'utente vuole saltare
2. Analizzare il livello di coraggio richiesto
3. Decidere quali tipi di notizie cercare (divertenti, assurde, nazionali, internazionali)
4. Cercare notizie VERE e VERIFICABILI che possano essere usate come base per una scusa
5. Ritornare le notizie trovate in formato strutturato

LINEE GUIDA:
- Per livelli di coraggio bassi (1-3): cerca notizie vaghe e difficili da verificare
- Per livelli medi (4-6): cerca notizie interessanti ma plausibili
- Per livelli alti (7-10): cerca notizie assurde ma vere che giustifichino azioni straordinarie

IMPORTANTE: Cerca SEMPRE notizie VERE. Non inventare mai notizie false."""
        
        logger.info("✅ NewsSearcherAgent inizializzato")
    
    def run(self, user_input: UserInput) -> List[NewsArticle]:
        """
        Esegue la ricerca di notizie basandosi sull'input utente.
        
        Args:
            user_input: Input dell'utente con impegno e livello coraggio
            
        Returns:
            Lista di NewsArticle (non ancora classificate)
        """
        logger.info(f"🤖 NewsSearcherAgent avviato")
        logger.info(f"   Impegno: {user_input.impegno_da_saltare}")
        logger.info(f"   Livello coraggio: {user_input.courage_level}")
        
        try:
            # STEP 1: L'agente decide quali query fare
            search_queries = self._plan_search_queries(user_input)
            
            # STEP 2: Esegue le ricerche usando il tool
            all_news = self._execute_searches(search_queries)
            
            # STEP 3: Converte in NewsArticle
            news_articles = self._convert_to_news_articles(all_news)
            
            logger.info(f"✅ NewsSearcherAgent completato: {len(news_articles)} notizie trovate")
            
            return news_articles
            
        except Exception as e:
            logger.error(f"❌ Errore in NewsSearcherAgent: {str(e)}")
            raise
    
    def _plan_search_queries(self, user_input: UserInput) -> List[str]:
        """
        L'agente ragiona e decide quali query di ricerca fare.
        
        Questo è il "cervello" dell'agente in azione:
        - Analizza il contesto
        - Decide la strategia di ricerca
        - Genera query ottimizzate
        """
        logger.info("🧠 Pianificazione query di ricerca...")
        
        courage_config = settings.get_courage_config(user_input.courage_level)
        
        # Prompt per far decidere all'agente le query
        planning_prompt = f"""Devi cercare notizie per aiutare a creare una scusa per questo impegno:
"{user_input.impegno_da_saltare}"

Livello di coraggio: {user_input.courage_level}/10
Stile richiesto: {courage_config['style']}
Esempi di scuse: {courage_config['examples']}

Genera 4 query di ricerca ottimali, una per ogni categoria:
1. Notizie NAZIONALI DIVERTENTI (Italia, curiose, leggere)
2. Notizie INTERNAZIONALI DIVERTENTI (mondo, curiose, leggere)
3. Notizie NAZIONALI ASSURDE (Italia, strane, incredibili)
4. Notizie INTERNAZIONALI ASSURDE (mondo, strane, incredibili)

Considera il livello di coraggio:
- Basso (1-3): cerca notizie vaghe, difficili da verificare
- Medio (4-6): cerca notizie interessanti e credibili
- Alto (7-10): cerca notizie assurde ma vere, straordinarie

Rispondi SOLO con un array JSON di 4 stringhe (le query), niente altro:
["query1", "query2", "query3", "query4"]"""
        
        try:
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": planning_prompt}
                ]
            )
            
            # Estrai le query dalla risposta
            queries = self._parse_queries_response(response)
            
            logger.info(f"✅ Query pianificate: {len(queries)}")
            for i, q in enumerate(queries, 1):
                logger.debug(f"   {i}. {q}")
            
            return queries
            
        except Exception as e:
            logger.error(f"❌ Errore pianificazione: {str(e)}")
            # Fallback: query predefinite
            return self._get_default_queries(user_input.courage_level)
    
    def _parse_queries_response(self, response) -> List[str]:
        """Parse della risposta di Claude con le query"""
        import json
        
        # Estrai testo
        text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text += block.text
        
        # Pulisci markdown
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Parse JSON
        queries = json.loads(text)
        
        if isinstance(queries, list) and len(queries) >= 4:
            return queries[:4]  # Prendi le prime 4
        else:
            raise ValueError("Formato query non valido")
    
    def _get_default_queries(self, courage_level: int) -> List[str]:
        """Query di fallback se il planning fallisce"""
        base_queries = [
            "notizie divertenti curiose Italia oggi",
            "notizie curiose divertenti mondo internazionali",
            "notizie assurde strane Italia incredibili",
            "notizie bizzarre assurde mondo incredibili"
        ]
        return base_queries
    
    def _execute_searches(self, queries: List[str]) -> List[Dict]:
        """
        Esegue tutte le ricerche usando il WebSearchTool.
        
        Args:
            queries: Lista di query da eseguire
            
        Returns:
            Lista di tutti i risultati (dizionari grezzi)
        """
        all_results = []
        
        for i, query in enumerate(queries, 1):
            logger.info(f"🔍 Ricerca {i}/{len(queries)}: {query}")
            
            results = self.web_search_tool.search_news(
                query=query,
                max_results=settings.MAX_NEWS_PER_CATEGORY
            )
            
            # Aggiungi metadata sulla query
            for result in results:
                result['search_query'] = query
                result['query_index'] = i
            
            all_results.extend(results)
        
        logger.info(f"✅ Ricerche completate: {len(all_results)} risultati totali")
        return all_results
    
    def _convert_to_news_articles(self, raw_news: List[Dict]) -> List[NewsArticle]:
        """
        Converte i risultati grezzi in oggetti NewsArticle.
        
        Args:
            raw_news: Lista di dizionari dalla ricerca
            
        Returns:
            Lista di NewsArticle validati con Pydantic
        """
        articles = []
        
        for news_dict in raw_news:
            try:
                article = NewsArticle(
                    titolo=news_dict.get('titolo', ''),
                    fonte=news_dict.get('fonte', ''),
                    url=news_dict.get('url', ''),
                    snippet=news_dict.get('snippet', ''),
                    data_pubblicazione=news_dict.get('data_pubblicazione', 'recente'),
                    # categoria e quality_score saranno aggiunti dal ClassifierAgent
                )
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"⚠️  Skipping invalid news: {str(e)}")
                continue
        
        return articles


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_news_searcher_agent():
    """
    Test dell'agente.
    Esegui: python agents/news_searcher.py
    """
    print("\n" + "="*60)
    print("🧪 TEST NEWS SEARCHER AGENT")
    print("="*60 + "\n")
    
    # Crea input di test
    test_input = UserInput(
        impegno_da_saltare="Riunione di lavoro lunedì alle 14:00",
        courage_level=6,
    )
    
    print(f"📋 Input Test:")
    print(f"   Impegno: {test_input.impegno_da_saltare}")
    print(f"   Coraggio: {test_input.courage_level}/10")
    print()
    
    # Crea e testa l'agente
    agent = NewsSearcherAgent()
    
    print("🚀 Avvio ricerca...\n")
    results = agent.run(test_input)
    
    print("\n📊 RISULTATI:")
    print(f"   Notizie trovate: {len(results)}")
    print()
    
    # Mostra alcune notizie
    print("📰 Esempio notizie trovate:\n")
    for i, article in enumerate(results[:5], 1):  # Mostra prime 5
        print(f"{i}. {article.titolo}")
        print(f"   Fonte: {article.fonte}")
        print(f"   Snippet: {article.snippet[:100]}...")
        print()
    
    print("="*60)
    print("✅ Test completato!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Se esegui questo file direttamente, lancia il test
    test_news_searcher_agent()