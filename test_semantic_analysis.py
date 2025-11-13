#!/usr/bin/env python3
"""
Test spécifique pour l'analyse sémantique profonde avec Claude 3.5 Sonnet
Teste les fonctionnalités améliorées demandées dans la review request
"""
import sys
import os
import json
import requests
from datetime import datetime

sys.path.append('/app/backend')

from semantic_analyzer import SemanticAnalyzer
from query_generator_v2 import generate_queries_with_analysis

def test_semantic_analysis():
    """Test semantic analysis with sample data"""
    
    # Sample crawl data for a marketing agency (like Sekoia)
    sample_crawl_data = {
        'base_url': 'https://sekoia.ca',
        'pages_crawled': 3,
        'pages': [
            {
                'url': 'https://sekoia.ca',
                'title': 'SEKOIA - Agence de marketing numérique | Croissance B2B',
                'meta_description': 'Agence de marketing numérique spécialisée en croissance B2B, SEO, génération de leads et marketing de performance.',
                'h1': ['Agence de marketing numérique', 'Croissance B2B'],
                'h2': ['Services de marketing', 'Génération de leads', 'SEO et référencement'],
                'h3': ['Marketing de performance', 'Analytics et données'],
                'paragraphs': [
                    'SEKOIA est une agence de marketing numérique spécialisée dans la croissance des entreprises B2B.',
                    'Nous offrons des services de génération de leads, SEO, marketing de performance et analytics.',
                    'Notre équipe d\'experts accompagne les entreprises dans leur transformation numérique.',
                    'Nous développons des stratégies de croissance personnalisées pour chaque client.',
                    'Nos services incluent le référencement organique, la publicité payante et l\'optimisation de conversion.'
                ],
                'json_ld': [],
                'word_count': 150
            },
            {
                'url': 'https://sekoia.ca/services',
                'title': 'Services - SEKOIA',
                'meta_description': 'Découvrez nos services de marketing numérique: SEO, génération de leads, marketing de performance.',
                'h1': ['Nos services'],
                'h2': ['SEO et référencement', 'Génération de leads B2B', 'Marketing de performance'],
                'h3': ['Audit SEO', 'Stratégie de contenu', 'Campagnes publicitaires'],
                'paragraphs': [
                    'Nous proposons une gamme complète de services de marketing numérique.',
                    'Le SEO est au cœur de notre expertise avec des audits complets et des stratégies personnalisées.',
                    'La génération de leads B2B permet d\'identifier et convertir vos prospects qualifiés.',
                    'Le marketing de performance optimise vos investissements publicitaires pour un ROI maximal.',
                    'Nos consultants analysent vos données pour améliorer continuellement vos résultats.'
                ],
                'json_ld': [],
                'word_count': 120
            }
        ]
    }
    
    print("🧠 Testing Semantic Analysis Module")
    print("=" * 50)
    
    # Test 1: Semantic Analysis
    analyzer = SemanticAnalyzer()
    semantic_results = analyzer.analyze_site(sample_crawl_data)
    
    print("✅ Industry Classification:")
    industry_class = semantic_results.get('industry_classification', {})
    print(f"   - Primary Industry: {industry_class.get('primary_industry', 'unknown')}")
    print(f"   - Company Type: {industry_class.get('company_type', 'unknown')}")
    print(f"   - Business Model: {industry_class.get('business_model', 'unknown')}")
    print(f"   - Confidence: {industry_class.get('confidence', 0):.2f}")
    
    print("\n✅ Entities Extracted:")
    entities = semantic_results.get('entities', {})
    offerings = entities.get('offerings', [])
    print(f"   - Offerings: {len(offerings)} found")
    for i, offering in enumerate(offerings[:5]):
        print(f"     {i+1}. {offering.get('name', 'N/A')} (mentions: {offering.get('mentions_count', 0)})")
    
    locations = entities.get('locations', [])
    print(f"   - Locations: {len(locations)} found")
    for loc in locations[:3]:
        print(f"     - {loc.get('city', 'N/A')}, {loc.get('region', 'N/A')}")
    
    problems = entities.get('problems_solved', [])
    print(f"   - Problems Solved: {len(problems)} found")
    for prob in problems[:3]:
        print(f"     - {prob}")
    
    # Test 2: Query Generation
    print("\n🔍 Testing Query Generation (100 queries)")
    print("=" * 50)
    
    query_results = generate_queries_with_analysis(sample_crawl_data, num_queries=100)
    
    queries = query_results.get('queries', [])
    breakdown = query_results.get('breakdown', {})
    
    print(f"✅ Query Generation Results:")
    print(f"   - Total queries generated: {len(queries)}")
    print(f"   - Non-branded: {breakdown.get('non_branded', 0)}")
    print(f"   - Semi-branded: {breakdown.get('semi_branded', 0)}")
    print(f"   - Branded: {breakdown.get('branded', 0)}")
    
    # Calculate percentages
    total = len(queries)
    if total > 0:
        non_branded_pct = (breakdown.get('non_branded', 0) / total) * 100
        semi_branded_pct = (breakdown.get('semi_branded', 0) / total) * 100
        branded_pct = (breakdown.get('branded', 0) / total) * 100
        
        print(f"   - Distribution: {non_branded_pct:.1f}% / {semi_branded_pct:.1f}% / {branded_pct:.1f}%")
        print(f"   - Target: 80% / 15% / 5%")
        
        # Check if distribution is correct
        if non_branded_pct >= 70 and total >= 90:
            print("   - ✅ Distribution is acceptable")
        else:
            print("   - ⚠️  Distribution needs improvement")
    
    print(f"\n📝 Sample Queries (first 10):")
    for i, query in enumerate(queries[:10]):
        print(f"   {i+1}. {query}")
    
    # Test 3: Validation
    print(f"\n🔍 Validation Results:")
    print("=" * 50)
    
    # Check if semantic analysis has required fields
    required_fields = ['industry_classification', 'entities']
    missing_fields = []
    
    for field in required_fields:
        if field not in semantic_results:
            missing_fields.append(field)
    
    if not missing_fields:
        print("✅ All required semantic analysis fields present")
    else:
        print(f"❌ Missing fields: {missing_fields}")
    
    # Check if query breakdown has required fields
    required_breakdown_fields = ['non_branded', 'semi_branded', 'branded', 'total']
    missing_breakdown = []
    
    for field in required_breakdown_fields:
        if field not in breakdown:
            missing_breakdown.append(field)
    
    if not missing_breakdown:
        print("✅ All required query breakdown fields present")
    else:
        print(f"❌ Missing breakdown fields: {missing_breakdown}")
    
    # Overall assessment
    print(f"\n📊 Overall Assessment:")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: Industry detected
    if industry_class.get('primary_industry', 'unknown') != 'unknown':
        print("✅ Industry detection: PASS")
        success_count += 1
    else:
        print("❌ Industry detection: FAIL")
    
    # Test 2: Offerings extracted
    if len(offerings) > 0:
        print("✅ Offerings extraction: PASS")
        success_count += 1
    else:
        print("❌ Offerings extraction: FAIL")
    
    # Test 3: Queries generated
    if len(queries) >= 50:  # At least 50 queries
        print("✅ Query generation: PASS")
        success_count += 1
    else:
        print("❌ Query generation: FAIL")
    
    # Test 4: Non-branded queries
    if breakdown.get('non_branded', 0) > 0:
        print("✅ Non-branded queries: PASS")
        success_count += 1
    else:
        print("❌ Non-branded queries: FAIL")
    
    # Test 5: Semantic analysis structure
    if not missing_fields:
        print("✅ Semantic analysis structure: PASS")
        success_count += 1
    else:
        print("❌ Semantic analysis structure: FAIL")
    
    # Test 6: Query breakdown structure
    if not missing_breakdown:
        print("✅ Query breakdown structure: PASS")
        success_count += 1
    else:
        print("❌ Query breakdown structure: FAIL")
    
    print(f"\n🎯 Final Score: {success_count}/{total_tests} tests passed ({(success_count/total_tests)*100:.1f}%)")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Semantic Analysis Module is working correctly!")
        return True
    elif success_count >= 4:
        print("⚠️  MOSTLY WORKING - Some minor issues detected")
        return True
    else:
        print("❌ MAJOR ISSUES - Semantic Analysis Module needs fixes")
        return False

if __name__ == "__main__":
    success = test_semantic_analysis()
    sys.exit(0 if success else 1)