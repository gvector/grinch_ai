# config.py
"""
Configurazione centrale per il progetto Excuse Generator.
Gestisce API keys, settings, e parametri globali.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Settings globali del progetto.
    Pydantic legge automaticamente da file .env o variabili ambiente.
    """
    
    # ============================================================================
    # API KEYS - Da inserire nel file .env
    # ============================================================================
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    """
    API Key di Anthropic per usare Claude.
    Ottienila da: https://console.anthropic.com/
    """
    
    # ============================================================================
    # CONFIGURAZIONE MODELLI AI
    # ============================================================================
    
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    """Modello Claude da usare (Sonnet 4 è il migliore per gli agenti)"""
    
    MAX_TOKENS: int = 4096
    """Numero massimo di token per risposta"""
    
    TEMPERATURE: float = 0.7
    """
    Temperatura per generazione (0.0 = deterministico, 1.0 = creativo).
    Per le scuse vogliamo creatività, quindi 0.7 è un buon compromesso.
    """
    
    # ============================================================================
    # CONFIGURAZIONE RICERCA NOTIZIE
    # ============================================================================
    
    NEWS_SEARCH_RESULTS_LIMIT: int = 20
    """Numero massimo di notizie da cercare per ricerca"""
    
    NEWS_RECENCY_DAYS: int = 7
    """Cerca solo notizie degli ultimi N giorni"""
    
    MIN_NEWS_PER_CATEGORY: int = 2
    """Minimo di notizie richieste per categoria"""
    
    MAX_NEWS_PER_CATEGORY: int = 5
    """Massimo di notizie da tenere per categoria"""
    
    # ============================================================================
    # CONFIGURAZIONE GENERAZIONE SCUSE
    # ============================================================================
    
    EXCUSE_MIN_WORDS: int = 50
    """Numero minimo di parole per una scusa"""
    
    EXCUSE_MAX_WORDS: int = 300
    """Numero massimo di parole per una scusa"""
    
    # Mapping livello coraggio → stile scusa
    COURAGE_LEVELS_CONFIG: dict = {
        "prudente": {
            "range": (1, 3),
            "style": "Vago e generico, difficile da verificare",
            "examples": ["non mi sento bene", "imprevisto familiare"],
            "include_details": False
        },
        "moderato": {
            "range": (4, 6),
            "style": "Creativo ma plausibile, con alcuni dettagli",
            "examples": ["problema con trasporti", "emergenza domestica"],
            "include_details": True
        },
        "audace": {
            "range": (7, 10),
            "style": "Elaborato con molti dettagli specifici",
            "examples": ["viaggio improvviso", "evento straordinario"],
            "include_details": True,
            "include_proofs": True
        }
    }
    
    # ============================================================================
    # CONFIGURAZIONE GENERAZIONE IMMAGINI
    # ============================================================================
    
    IMAGE_GENERATION_ENABLED: bool = True
    """Se abilitare la generazione di immagini fake"""
    
    IMAGE_WIDTH: int = 1024
    IMAGE_HEIGHT: int = 1024
    """Dimensioni immagini generate"""
    
    # ============================================================================
    # PATHS - Dove salvare file generati
    # ============================================================================
    
    PROJECT_ROOT: Path = Path(__file__).parent
    """Directory root del progetto"""
    
    OUTPUT_DIR: Path = PROJECT_ROOT / "output"
    """Dove salvare tutti i file generati"""
    
    TICKETS_DIR: Path = OUTPUT_DIR / "tickets"
    """Dove salvare i biglietti generati"""
    
    PHOTOS_DIR: Path = OUTPUT_DIR / "photos"
    """Dove salvare le foto fake"""
    
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    """Dove salvare i log"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Crea le directory se non esistono
        self._create_directories()
    
    def _create_directories(self):
        """Crea tutte le directory necessarie"""
        for dir_path in [
            self.OUTPUT_DIR,
            self.TICKETS_DIR,
            self.PHOTOS_DIR,
            self.LOGS_DIR
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # ============================================================================
    # CONFIGURAZIONE LOGGING
    # ============================================================================
    
    LOG_LEVEL: str = "INFO"
    """Livello di logging (DEBUG, INFO, WARNING, ERROR)"""
    
    LOG_TO_FILE: bool = True
    """Se salvare i log su file oltre che console"""
    
    # ============================================================================
    # CONFIGURAZIONE DATAPIZZA (Framework Agenti)
    # ============================================================================
    
    AGENT_TIMEOUT: int = 120
    """Timeout in secondi per ogni agente"""
    
    MAX_AGENT_ITERATIONS: int = 5
    """Numero massimo di iterazioni per un agente"""
    
    ENABLE_AGENT_MEMORY: bool = True
    """Se abilitare la memoria conversazionale degli agenti"""
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_courage_config(self, courage_level: int) -> dict:
        """
        Ritorna la configurazione per un dato livello di coraggio.
        
        Args:
            courage_level: Valore tra 1 e 10
            
        Returns:
            Dict con configurazione dello stile di scusa
        """
        for category, config in self.COURAGE_LEVELS_CONFIG.items():
            min_val, max_val = config["range"]
            if min_val <= courage_level <= max_val:
                return {**config, "category": category}
        
        # Default: moderato
        return {**self.COURAGE_LEVELS_CONFIG["moderato"], "category": "moderato"}
    
    def validate_api_key(self) -> bool:
        """Verifica che la API key sia configurata"""
        return bool(self.ANTHROPIC_API_KEY and self.ANTHROPIC_API_KEY != "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# ============================================================================
# ISTANZA GLOBALE SETTINGS
# ============================================================================

settings = Settings()

# Validazione iniziale
if not settings.validate_api_key():
    print("⚠️  WARNING: ANTHROPIC_API_KEY non configurata!")
    print("   Crea un file .env con: ANTHROPIC_API_KEY=sk-ant-...")
    print("   Oppure esporta: export ANTHROPIC_API_KEY=sk-ant-...")


# ============================================================================
# CONFIGURAZIONE LOGGING
# ============================================================================

import logging
from datetime import datetime

def setup_logging():
    """Configura il sistema di logging"""
    
    # Formato log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Logger root
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    # Handler file (se abilitato)
    if settings.LOG_TO_FILE:
        log_file = settings.LOGS_DIR / f"excuse_generator_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    return logger

# Setup automatico al caricamento del modulo
logger = setup_logging()
logger.info("🚀 Excuse Generator - Configurazione caricata")
logger.info(f"📁 Output directory: {settings.OUTPUT_DIR}")


# ============================================================================
# UTILITY: Stampare configurazione
# ============================================================================

def print_config():
    """Stampa la configurazione corrente (utile per debug)"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURAZIONE EXCUSE GENERATOR")
    print("="*60)
    print(f"🤖 Modello Claude: {settings.CLAUDE_MODEL}")
    print(f"🔑 API Key configurata: {'✅ Sì' if settings.validate_api_key() else '❌ No'}")
    print(f"📰 Notizie per ricerca: {settings.NEWS_SEARCH_RESULTS_LIMIT}")
    print(f"📅 Recency: ultimi {settings.NEWS_RECENCY_DAYS} giorni")
    print(f"📁 Output directory: {settings.OUTPUT_DIR}")
    print(f"🎨 Generazione immagini: {'✅ Abilitata' if settings.IMAGE_GENERATION_ENABLED else '❌ Disabilitata'}")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Se esegui questo file direttamente, stampa la config
    print_config()