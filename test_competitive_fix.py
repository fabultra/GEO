#!/usr/bin/env python3
"""
Script de test pour valider le fix des URLs de compétiteurs
"""
import sys
sys.path.append('/app/backend')

from competitive_intelligence import CompetitiveIntelligence
from utils.competitor_extractor import CompetitorExtractor

def test_url_validation():
    """Test de validation des URLs"""
    print("🧪 Test 1: Validation d'URLs")
    print("=" * 60)
    
    ci = CompetitiveIntelligence()
    
    test_urls = [
        "https://example.com",
        "http://test.com",
        "www.noscheme.com",
        "example.com",
        "invalid..url",
        "",
        None,
        "javascript:void(0)",
        "https://good-site.com/page"
    ]
    
    for url in test_urls:
        validated = ci._validate_url(url)
        status = "✅" if validated else "❌"
        url_str = str(url) if url is not None else "None"
        validated_str = str(validated) if validated is not None else "None"
        print(f"{status} Input: {url_str:40} → Output: {validated_str}")
    
    print()

def test_domain_extraction():
    """Test d'extraction de domaine"""
    print("🧪 Test 2: Extraction de domaine")
    print("=" * 60)
    
    ci = CompetitiveIntelligence()
    
    test_urls = [
        "https://www.example.com/page",
        "http://example.com",
        "https://subdomain.example.com/path/to/page",
        "www.test.com"
    ]
    
    for url in test_urls:
        domain = ci._extract_domain(url)
        print(f"URL: {url:50} → Domain: {domain}")
    
    print()

def test_competitor_extraction():
    """Test d'extraction depuis visibility data"""
    print("🧪 Test 3: Extraction depuis visibility data")
    print("=" * 60)
    
    # Mock visibility data
    visibility_data = {
        'queries': [
            {
                'query': 'test query',
                'platforms': {
                    'chatgpt': {
                        'full_response': 'Check out https://competitor1.com and www.competitor2.com for more info.',
                        'competitors_mentioned': [
                            {'name': 'Comp1', 'urls': ['https://competitor1.com']},
                            {'name': 'Comp2', 'urls': ['www.competitor2.com']}
                        ]
                    },
                    'claude': {
                        'full_response': 'Visit https://competitor3.com',
                        'competitors_mentioned': []
                    }
                }
            }
        ],
        'details': [
            {
                'query': 'another query',
                'platform': 'PERPLEXITY',
                'answer': 'See https://competitor1.com and https://competitor4.com'
            }
        ]
    }
    
    urls = CompetitorExtractor.extract_from_visibility_results(visibility_data, max_competitors=5)
    
    print(f"URLs extraites: {len(urls)}")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    print()

def test_domain_filtering():
    """Test de filtrage de notre domaine"""
    print("🧪 Test 4: Filtrage de notre propre domaine")
    print("=" * 60)
    
    urls = [
        "https://mysite.com",
        "https://competitor1.com",
        "https://www.mysite.com",
        "https://competitor2.com",
        "https://mysite.com/page"
    ]
    
    own_domain = "mysite.com"
    
    filtered = CompetitorExtractor.filter_self_domain(urls, own_domain)
    
    print(f"URLs originales: {len(urls)}")
    print(f"URLs après filtrage: {len(filtered)}")
    print(f"Notre domaine filtré: {own_domain}")
    print("\nURLs conservées:")
    for url in filtered:
        print(f"  ✅ {url}")
    
    print()

def main():
    """Lance tous les tests"""
    print("\n🚀 TESTS DU FIX DES URLs DE COMPÉTITEURS")
    print("=" * 60)
    print()
    
    try:
        test_url_validation()
        test_domain_extraction()
        test_competitor_extraction()
        test_domain_filtering()
        
        print("=" * 60)
        print("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERREUR PENDANT LES TESTS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
