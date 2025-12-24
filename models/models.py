# models/data_models.py
"""
Modelli dati per il sistema Excuse Generator.
Questi modelli definiscono la struttura dei dati che passano tra agenti e orchestratori.
Usiamo Pydantic per validazione automatica e type hints.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS - Definizioni di valori costanti
# ============================================================================

class NewsCategory(str, Enum):
    """
    Le 4 categorie in cui classificare le notizie.
    Usiamo Enum per evitare errori di battitura.
    """
    NAZIONALE_DIVERTENTE = "nazionale_divertente"
    INTERNAZIONALE_DIVERTENTE = "internazionale_divertente"
    NAZIONALE_ASSURDA = "nazionale_assurda"
    INTERNAZIONALE_ASSURDA = "internazionale_assurda"


class TransportType(str, Enum):
    """Tipo di trasporto per la scusa"""
    AEREO = "aereo"
    TRENO = "treno"
    AUTOBUS = "autobus"


class CourageLevel(int, Enum):
    """
    Livello di coraggio della scusa (1-10)
    Più alto = scusa più audace e dettagliata
    """
    PRUDENTE_MIN = 1
    PRUDENTE_MAX = 3
    MODERATO_MIN = 4
    MODERATO_MAX = 6
    AUDACE_MIN = 7
    AUDACE_MAX = 10


# ============================================================================
# INPUT UTENTE - Dati iniziali forniti dall'utente
# ============================================================================

class UserInput(BaseModel):
    """
    Dati iniziali forniti dall'utente nella Fase 1.
    """
    impegno_da_saltare: str = Field(
        ..., 
        description="Descrizione dell'impegno che l'utente vuole evitare",
        example="Riunione di lavoro lunedì alle 14:00"
    )
    courage_level: int = Field(
        default=5,
        ge=1,  # greater or equal
        le=10,  # less or equal
        description="Livello di coraggio della scusa (1=prudente, 10=audace)"
    )
    data_impegno: Optional[datetime] = Field(
        None,
        description="Data dell'impegno (se fornita)"
    )


# ============================================================================
# NOTIZIE - Modelli per gestire le notizie trovate
# ============================================================================

class NewsArticle(BaseModel):
    """
    Una singola notizia trovata online.
    Questo è l'output del NewsSearcherAgent.
    """
    titolo: str = Field(..., description="Titolo della notizia")
    fonte: str = Field(..., description="Fonte/sito della notizia")
    url: str = Field(..., description="Link alla notizia")
    snippet: str = Field(..., description="Breve estratto della notizia")
    data_pubblicazione: Optional[str] = Field(
        None, 
        description="Data di pubblicazione"
    )
    
    # Questi campi vengono riempiti dal NewsClassifierAgent
    categoria: Optional[NewsCategory] = Field(
        None, 
        description="Categoria assegnata dalla classificazione"
    )
    quality_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Punteggio qualità per usabilità come scusa (0-10)"
    )
    motivo_classificazione: Optional[str] = Field(
        None,
        description="Spiegazione del perché è stata classificata così"
    )


class ClassifiedNews(BaseModel):
    """
    Notizie classificate per categoria.
    Output del NewsClassifierAgent.
    """
    categoria: NewsCategory
    notizie: List[NewsArticle] = Field(
        default_factory=list,
        description="Lista di notizie in questa categoria, ordinate per quality_score"
    )
    
    def get_best(self, n: int = 3) -> List[NewsArticle]:
        """Ritorna le migliori N notizie di questa categoria"""
        return sorted(
            self.notizie, 
            key=lambda x: x.quality_score or 0, 
            reverse=True
        )[:n]


class NewsSearchResult(BaseModel):
    """
    Risultato completo della Fase 1 (ricerca + classificazione).
    Output del NewsSearchOrchestrator.
    """
    user_input: UserInput
    notizie_per_categoria: dict[NewsCategory, ClassifiedNews] = Field(
        default_factory=dict,
        description="Notizie organizzate per categoria"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Quando è stata fatta la ricerca"
    )
    
    def get_all_best_news(self, per_category: int = 3) -> List[NewsArticle]:
        """Ritorna le migliori notizie di tutte le categorie"""
        best = []
        for classified in self.notizie_per_categoria.values():
            best.extend(classified.get_best(per_category))
        return sorted(best, key=lambda x: x.quality_score or 0, reverse=True)


# ============================================================================
# SCUSA - Modelli per la generazione della scusa
# ============================================================================

class ExcuseRequest(BaseModel):
    """
    Richiesta di generazione scusa (input Fase 2).
    L'utente ha scelto una notizia e ora vuole la scusa completa.
    """
    notizia_scelta: NewsArticle = Field(
        ..., 
        description="La notizia scelta dall'utente"
    )
    impegno_da_saltare: str = Field(
        ..., 
        description="L'impegno originale da saltare"
    )
    courage_level: int = Field(..., ge=1, le=10)
    
    # Preferenze opzionali
    transport_type: Optional[TransportType] = Field(
        None,
        description="Tipo di trasporto preferito per la scusa"
    )
    include_ticket: bool = Field(
        default=True,
        description="Se generare biglietto aereo/treno"
    )
    include_photo: bool = Field(
        default=False,
        description="Se generare foto fake come prova"
    )


class GeneratedExcuse(BaseModel):
    """
    La scusa generata dall'ExcuseWriterAgent.
    """
    testo_scusa: str = Field(
        ..., 
        description="Il testo completo della scusa da inviare"
    )
    dettagli_storia: dict = Field(
        default_factory=dict,
        description="Dettagli inventati per rendere credibile (date, luoghi, nomi)"
    )
    suggerimenti: List[str] = Field(
        default_factory=list,
        description="Suggerimenti per rendere più credibile la scusa"
    )


class TicketData(BaseModel):
    """
    Dati per generare un biglietto (aereo/treno).
    """
    tipo: TransportType
    partenza: str = Field(..., description="Città/stazione di partenza")
    arrivo: str = Field(..., description="Città/stazione di arrivo")
    data_partenza: datetime
    ora_partenza: str
    numero_volo_treno: str
    nome_passeggero: str
    codice_prenotazione: str
    
    # Output dopo generazione
    ticket_image_path: Optional[str] = Field(
        None,
        description="Path dell'immagine del biglietto generato"
    )


class ProofPhoto(BaseModel):
    """
    Foto fake generata come prova.
    """
    descrizione: str = Field(
        ..., 
        description="Cosa rappresenta la foto (es: 'Selfie in aeroporto')"
    )
    image_path: str = Field(
        ..., 
        description="Path dell'immagine generata"
    )
    prompt_usato: str = Field(
        ...,
        description="Il prompt usato per generare l'immagine"
    )


class CompleteExcuse(BaseModel):
    """
    Output finale completo della Fase 2.
    Contiene tutto: scusa + prove + biglietti.
    """
    excuse_request: ExcuseRequest
    generated_excuse: GeneratedExcuse
    ticket: Optional[TicketData] = None
    proof_photos: List[ProofPhoto] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def to_summary(self) -> str:
        """Crea un riassunto testuale completo"""
        summary = f"=== SCUSA GENERATA ===\n\n"
        summary += f"{self.generated_excuse.testo_scusa}\n\n"
        
        if self.ticket:
            summary += f"🎫 Biglietto {self.ticket.tipo.value}: {self.ticket.partenza} → {self.ticket.arrivo}\n"
        
        if self.proof_photos:
            summary += f"📸 {len(self.proof_photos)} foto allegate\n"
        
        return summary


# ============================================================================
# STATO ORCHESTRATORE - Per tracciare il progresso
# ============================================================================

class OrchestratorState(BaseModel):
    """
    Stato interno dell'orchestratore.
    Utile per debug e per UI che mostrano il progresso.
    """
    fase: Literal["ricerca", "classificazione", "generazione", "completato"]
    step_corrente: str = Field(..., description="Descrizione step in corso")
    progresso_percentuale: int = Field(ge=0, le=100)
    errori: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)