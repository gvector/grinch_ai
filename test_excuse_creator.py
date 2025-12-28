from datetime import datetime
import sys
import os

from agents.excuse_creator import ExcuseCreatorAgent
from storage.schemas import ExcuseRequest, ExcuseTone, NewsArticle, NewsCategory


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_simple_excuse():
    """Test excuse generation without news"""
    print("=" * 60)
    print("🧪 Test 1: Generate excuse without news")
    print("=" * 60 + "\n")
    
    agent = ExcuseCreatorAgent()
    
    request = ExcuseRequest(
        situation="in ritardo per un meeting",
        context="meeting di lavoro alle 9:00",
        recipient="capo",
        tone=ExcuseTone.PROFESSIONAL
    )
    
    print(f"📝 Request:")
    print(f"  Situation: {request.situation}")
    print(f"  Context: {request.context}")
    print(f"  Tone: {request.tone.value}\n")
    
    print("🤖 Generating excuses...\n")
    
    try:
        excuses = agent.generate_excuses(request)
        
        print(f"\n✅ Generated {len(excuses)} excuses:\n")
        for i, excuse in enumerate(excuses, 1):
            print(f"{i}. {excuse.text}")
            print(f"   📊 Plausibility: {excuse.plausibility_score:.2f} | "
                  f"Creativity: {excuse.creativity_score:.2f} | "
                  f"Risk: {excuse.risk_level}")
            print(f"   💡 Why: {excuse.explanation}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_excuse_with_news():
    """Test excuse generation with absurd news"""
    print("\n" + "=" * 60)
    print("🧪 Test 2: Generate excuse with absurd news")
    print("=" * 60 + "\n")
    
    agent = ExcuseCreatorAgent()
    
    # Mock absurd news article
    news = NewsArticle(
        title="Piccione ruba smartphone e blocca centro città",
        summary="Un piccione ha rubato uno smartphone da un tavolino di un bar in centro, causando un inseguimento che ha bloccato il traffico per 30 minuti. La polizia è intervenuta con un'unità speciale.",
        url="https://news.example.com/piccione",
        source="La Gazzetta di Milano",
        published_at=datetime.now(),
        category=NewsCategory.NATIONAL_ABSURD,
        relevance_score=0.8,
        absurdity_score=0.95
    )
    
    request = ExcuseRequest(
        situation="ritardo di 30 minuti",
        context="dovevo incontrare un cliente",
        recipient="cliente",
        tone=ExcuseTone.APOLOGETIC,
        preferred_news_category=NewsCategory.NATIONAL_ABSURD
    )
    
    print(f"📰 News Article:")
    print(f"  [{news.category.value}] {news.title}")
    print(f"  {news.summary}")
    print(f"  🎭 Absurdity: {news.absurdity_score:.2f}\n")
    
    print(f"📝 Request:")
    print(f"  Situation: {request.situation}")
    print(f"  Recipient: {request.recipient}\n")
    
    print("🤖 Generating excuses based on news...\n")
    
    try:
        excuses = agent.generate_excuses(request, [news])
        
        print(f"\n✅ Generated {len(excuses)} excuses:\n")
        for i, excuse in enumerate(excuses, 1):
            print(f"{i}. {excuse.text}")
            print(f"   📊 Plausibility: {excuse.plausibility_score:.2f} | "
                  f"Creativity: {excuse.creativity_score:.2f} | "
                  f"Risk: {excuse.risk_level}")
            print(f"   💡 Why: {excuse.explanation}")
            if excuse.news_reference:
                print(f"   📰 Based on: {excuse.news_reference.title}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n🎭 EXCUSE CREATOR AGENT - Test Suite\n")
    
    results = []
    
    # Run tests
    results.append(("Simple Excuse", test_simple_excuse()))
    results.append(("Excuse with News", test_excuse_with_news()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✨ All tests completed successfully!")
        print("📋 Next: We'll create the News Collector Agent\n")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.\n")


if __name__ == "__main__":
    main()