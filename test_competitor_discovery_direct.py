#!/usr/bin/env python3
"""
Test direct du système de découverte de compétiteurs V3
Test des modules sans passer par l'API complète
"""
import sys
import os
import json
import logging
from datetime import datetime

# Ajouter le backend au path
sys.path.append('/app/backend')

from utils.competitor_extractor import CompetitorExtractor
from services.competitor_discovery import CompetitorDiscovery

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_competitor_extractor():
    """
    Test du CompetitorExtractor (Stage 1)
    """
    logger.info("🔍 Test 1: CompetitorExtractor (Stage 1)")
    
    # Données de visibilité simulées
    mock_visibility_data = {
        "queries": [
            {
                "query": "agence marketing digital Québec",
                "platforms": {
                    "chatgpt": {
                        "mentioned": True,
                        "full_response": "Voici quelques agences de marketing digital au Québec: https://www.adviso.ca, https://www.mirum.ca, https://www.lg2.com et https://www.nurun.com. Ces agences offrent des services complets.",
                        "competitors_mentioned": [
                            {"name": "Adviso", "urls": ["https://www.adviso.ca"]},
                            {"name": "Mirum", "urls": ["https://www.mirum.ca"]}
                        ]
                    },
                    "claude": {
                        "mentioned": True,
                        "full_response": "Les principales agences incluent Adviso (www.adviso.ca), LG2 (lg2.com) et Mirum Agency (mirum.ca)."
                    }
                }
            }
        ],
        "details": [
            {
                "query": "marketing automation Quebec",
                "platform": "PERPLEXITY",
                "mentioned": True,
                "answer": "Several companies offer marketing automation in Quebec including https://www.adviso.ca and https://www.mirum.ca"
            }
        ]
    }
    
    # Test extraction
    extracted_urls = CompetitorExtractor.extract_from_visibility_results(
        mock_visibility_data, 
        max_competitors=10
    )
    
    logger.info(f"✅ URLs extraites: {len(extracted_urls)}")
    for i, url in enumerate(extracted_urls, 1):
        logger.info(f"  {i}. {url}")
    
    # Test filtrage domaine propre
    filtered_urls = CompetitorExtractor.filter_self_domain(
        extracted_urls, 
        "https://sekoia.ca"
    )
    
    logger.info(f"✅ URLs après filtrage: {len(filtered_urls)}")
    
    return extracted_urls

def test_competitor_discovery():
    """
    Test du CompetitorDiscovery (Stages 2 & 3)
    """
    logger.info("🔍 Test 2: CompetitorDiscovery (Stages 2 & 3)")
    
    # Analyse sémantique simulée
    mock_semantic_analysis = {
        "industry_classification": {
            "primary_industry": "digital marketing",
            "sub_industry": "growth marketing agency",
            "company_type": "agency"
        },
        "entities": {
            "offerings": [
                {"name": "SEO", "description": "Search engine optimization"},
                {"name": "PPC", "description": "Pay-per-click advertising"},
                {"name": "Analytics", "description": "Web analytics and reporting"}
            ]
        }
    }
    
    # URLs depuis visibilité (simulées)
    visibility_urls = [
        "https://www.adviso.ca",
        "https://www.mirum.ca"
    ]
    
    # Initialiser le service
    discovery = CompetitorDiscovery()
    
    try:
        # Lancer la découverte complète
        competitors = discovery.discover_real_competitors(
            semantic_analysis=mock_semantic_analysis,
            our_url="https://sekoia.ca",
            visibility_urls=visibility_urls,
            max_competitors=5
        )
        
        logger.info(f"✅ Compétiteurs découverts: {len(competitors)}")
        
        # Analyser les résultats
        for i, comp in enumerate(competitors, 1):
            logger.info(f"  {i}. {comp['domain']}")
            logger.info(f"     URL: {comp['homepage_url']}")
            logger.info(f"     Score: {comp['score']}")
            logger.info(f"     Type: {comp['type']}")
            logger.info(f"     Reason: {comp['reason']}")
            logger.info(f"     Source: {comp['source']}")
            logger.info("")
        
        return competitors
        
    except Exception as e:
        logger.error(f"❌ Erreur dans la découverte: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_new_fields_validation(competitors):
    """
    Test 3: Validation des nouveaux champs
    """
    logger.info("🔍 Test 3: Validation des nouveaux champs")
    
    required_fields = ['domain', 'homepage_url', 'score', 'type', 'reason', 'source']
    
    valid_competitors = 0
    
    for comp in competitors:
        has_all_fields = all(field in comp for field in required_fields)
        
        if has_all_fields:
            valid_competitors += 1
            logger.info(f"  ✅ {comp['domain']}: Tous les champs présents")
            
            # Valider les types de données
            if not isinstance(comp['score'], (int, float)):
                logger.warning(f"    ⚠️ Score n'est pas numérique: {type(comp['score'])}")
            
            if comp['type'] not in ['direct', 'indirect']:
                logger.warning(f"    ⚠️ Type invalide: {comp['type']}")
            
            if comp['source'] not in ['llm', 'web_search', 'both']:
                logger.warning(f"    ⚠️ Source invalide: {comp['source']}")
        else:
            missing = [field for field in required_fields if field not in comp]
            logger.error(f"  ❌ {comp.get('domain', 'Unknown')}: Champs manquants: {missing}")
    
    logger.info(f"✅ Compétiteurs valides: {valid_competitors}/{len(competitors)}")
    return valid_competitors == len(competitors)

def test_url_accessibility(competitors):
    """
    Test 4: Validation de l'accessibilité des URLs
    """
    logger.info("🔍 Test 4: Test d'accessibilité des URLs")
    
    import requests
    
    accessible_count = 0
    
    for comp in competitors:
        url = comp['homepage_url']
        try:
            response = requests.head(
                url, 
                timeout=10, 
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; CompetitorTester/1.0)'}
            )
            
            if response.status_code < 400:
                logger.info(f"  ✅ {comp['domain']}: Accessible ({response.status_code})")
                accessible_count += 1
            else:
                logger.warning(f"  ⚠️ {comp['domain']}: Status {response.status_code}")
                
        except Exception as e:
            logger.error(f"  ❌ {comp['domain']}: Erreur - {e}")
    
    accessibility_rate = accessible_count / len(competitors) if competitors else 0
    logger.info(f"✅ Taux d'accessibilité: {accessibility_rate:.1%} ({accessible_count}/{len(competitors)})")
    
    return accessibility_rate >= 0.8

def main():
    """
    Point d'entrée principal
    """
    logger.info("🚀 Test Direct - Système de Découverte de Compétiteurs V3")
    logger.info("="*70)
    
    results = {
        'test_start': datetime.now().isoformat(),
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'details': {}
    }
    
    try:
        # Test 1: CompetitorExtractor
        results['tests_run'] += 1
        extracted_urls = test_competitor_extractor()
        if extracted_urls:
            results['tests_passed'] += 1
            results['details']['extractor'] = 'PASSED'
        else:
            results['tests_failed'] += 1
            results['details']['extractor'] = 'FAILED'
        
        # Test 2: CompetitorDiscovery
        results['tests_run'] += 1
        competitors = test_competitor_discovery()
        if competitors:
            results['tests_passed'] += 1
            results['details']['discovery'] = 'PASSED'
        else:
            results['tests_failed'] += 1
            results['details']['discovery'] = 'FAILED'
            competitors = []  # Pour éviter les erreurs dans les tests suivants
        
        # Test 3: Validation des champs
        results['tests_run'] += 1
        if test_new_fields_validation(competitors):
            results['tests_passed'] += 1
            results['details']['fields_validation'] = 'PASSED'
        else:
            results['tests_failed'] += 1
            results['details']['fields_validation'] = 'FAILED'
        
        # Test 4: Accessibilité des URLs
        results['tests_run'] += 1
        if test_url_accessibility(competitors):
            results['tests_passed'] += 1
            results['details']['url_accessibility'] = 'PASSED'
        else:
            results['tests_failed'] += 1
            results['details']['url_accessibility'] = 'FAILED'
        
        # Rapport final
        results['test_end'] = datetime.now().isoformat()
        results['competitors_found'] = competitors
        
        logger.info("\n" + "="*70)
        logger.info("📋 RAPPORT FINAL - TESTS DIRECTS")
        logger.info("="*70)
        logger.info(f"📊 Tests exécutés: {results['tests_run']}")
        logger.info(f"✅ Tests réussis: {results['tests_passed']}")
        logger.info(f"❌ Tests échoués: {results['tests_failed']}")
        
        success_rate = (results['tests_passed'] / results['tests_run']) * 100 if results['tests_run'] > 0 else 0
        logger.info(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        logger.info("\n📋 Détails par test:")
        for test_name, status in results['details'].items():
            status_icon = "✅" if status == "PASSED" else "❌"
            logger.info(f"  {status_icon} {test_name}: {status}")
        
        if competitors:
            logger.info(f"\n🏆 Compétiteurs trouvés: {len(competitors)}")
            for i, comp in enumerate(competitors, 1):
                logger.info(f"  {i}. {comp['domain']} (score: {comp['score']}, type: {comp['type']})")
        
        # Sauvegarder les résultats
        with open('/app/competitor_discovery_direct_test.json', 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Résultats sauvegardés: /app/competitor_discovery_direct_test.json")
        logger.info("="*70)
        
        return results['tests_failed'] == 0
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 TOUS LES TESTS DIRECTS SONT PASSÉS!")
        sys.exit(0)
    else:
        print("\n❌ CERTAINS TESTS DIRECTS ONT ÉCHOUÉ!")
        sys.exit(1)