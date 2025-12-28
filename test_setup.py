from config import settings
from storage import (
    ExcuseRequest, 
    Excuse, 
    Evidence, 
    ExcuseTone,
    storage
)
from utils import (
    generate_excuse_id,
    sanitize_text,
    extract_keywords
)
from utils.llm_client import llm_client
from datetime import datetime


def test_configuration():
    """Test that configuration loads correctly"""
    print("🔧 Testing Configuration...")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  Model: {settings.current_model}")
    print(f"  Max Excuses: {settings.max_excuses_per_request}")
    if settings.llm_provider == "openai":
        print(f"  API Key Present: {bool(settings.openai_api_key)}")
    else:
        print(f"  Ollama URL: {settings.ollama_base_url}")
    print("  ✅ Configuration loaded\n")


def test_llm_connection():
    """Test LLM connection"""
    print("🤖 Testing LLM Connection...")
    print(f"  Provider: {settings.llm_provider}")
    print(f"  Model: {settings.current_model}")
    
    try:
        if llm_client.test_connection():
            print("  ✅ LLM connection successful\n")
            return True
        else:
            print("  ⚠️  LLM responded but test failed\n")
            return False
    except Exception as e:
        print(f"  ❌ LLM connection failed: {e}")
        if settings.llm_provider == "ollama":
            print("  💡 Make sure Ollama is running: ollama serve")
            print(f"  💡 And your model is pulled: ollama pull {settings.ollama_model}")
        print()
        return False


def test_schemas():
    """Test that Pydantic schemas work"""
    print("📝 Testing Schemas...")
    
    # Test ExcuseRequest
    request = ExcuseRequest(
        situation="late to meeting",
        context="work meeting at 9am",
        recipient="manager",
        tone=ExcuseTone.PROFESSIONAL
    )
    print(f"  Request: {request.situation}")
    
    # Test Excuse
    excuse = Excuse(
        id=generate_excuse_id(),
        text="I was delayed by unexpected traffic",
        plausibility_score=0.8,
        creativity_score=0.5,
        risk_level="low",
        explanation="Common and believable excuse",
        created_at=datetime.now()
    )
    print(f"  Excuse ID: {excuse.id}")
    print(f"  Plausibility: {excuse.plausibility_score}")
    print("  ✅ Schemas working\n")
    
    return excuse


def test_storage(excuse: Excuse):
    """Test the in-memory storage"""
    print("💾 Testing Storage...")
    
    # Save excuse
    excuse_id = storage.save_excuse(excuse)
    print(f"  Saved excuse: {excuse_id}")
    
    # Retrieve excuse
    retrieved = storage.get_excuse(excuse_id)
    print(f"  Retrieved: {retrieved.text if retrieved else 'None'}")
    
    # Save evidence
    evidence = Evidence(
        excuse_id=excuse_id,
        evidence_type="link",
        content="https://news.example.com/traffic",
        description="Traffic report",
        credibility_score=0.9
    )
    storage.save_evidence(evidence)
    
    # Retrieve evidence
    evidences = storage.get_evidence(excuse_id)
    print(f"  Evidence count: {len(evidences)}")
    print("  ✅ Storage working\n")


def test_utilities():
    """Test utility functions"""
    print("🔨 Testing Utilities...")
    
    text = "  I need an excuse for   being late  "
    cleaned = sanitize_text(text)
    print(f"  Sanitized: '{cleaned}'")
    
    keywords = extract_keywords("I need an excuse for being late to my important meeting")
    print(f"  Keywords: {keywords}")
    
    excuse_id = generate_excuse_id()
    print(f"  Generated ID: {excuse_id}")
    print("  ✅ Utilities working\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 EXCUSE GENERATOR - Setup Test")
    print("=" * 50 + "\n")
    
    try:
        test_configuration()
        llm_ok = test_llm_connection()
        excuse = test_schemas()
        test_storage(excuse)
        test_utilities()
        
        print("=" * 50)
        if llm_ok:
            print("✨ All tests passed! Setup is complete.")
        else:
            print("⚠️  Setup complete but LLM connection failed.")
            print("   Fix the LLM connection before proceeding.")
        print("=" * 50)
        print("\n📋 Next steps:")
        if settings.llm_provider == "ollama":
            print("  1. Make sure Ollama is running (ollama serve)")
            print(f"  2. Pull your model: ollama pull {settings.ollama_model}")
            print("  3. We'll build the DataPizza agents next")
        else:
            print("  1. Verify your OpenAI API key in .env")
            print("  2. We'll build the DataPizza agents next")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please make sure all dependencies are installed:")
        print("  pip install -r requirements.txt\n")


if __name__ == "__main__":
    main()