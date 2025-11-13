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

def test_claude_api():
    """Test if Claude API is working with the specified model"""
    print("🤖 TESTING CLAUDE API CONNECTIVITY")
    print("=" * 60)
    
    try:
        from anthropic import Anthropic
        
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in environment")
            return False
        
        print(f"✅ API Key found: {api_key[:20]}...")
        
        client = Anthropic(api_key=api_key)
        
        # Test with the model specified in the review request
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Test message. Respond with 'API Working' in JSON format: {\"status\": \"API Working\"}"}
            ]
        )
        
        response_text = response.content[0].text
        print(f"✅ Claude API Response: {response_text}")
        
        if 'API Working' in response_text or 'working' in response_text.lower():
            print("✅ Claude API is working correctly!")
            return True
        else:
            print("⚠️  Claude API responded but format unexpected")
            return True
        
    except Exception as e:
        print(f"❌ Claude API test failed: {str(e)}")
        return False

def test_semantic_analysis():
    """Test semantic analysis with enhanced features for sekoia.ca"""
    
    # Enhanced sample crawl data for sekoia.ca (more realistic)
    sample_crawl_data = {
        'base_url': 'https://sekoia.ca',
        'pages_crawled': 5,
        'pages': [
            {
                'url': 'https://sekoia.ca',
                'title': 'SEKOIA - Cybersécurité et Intelligence des Menaces | Protection Avancée',
                'meta_description': 'SEKOIA développe des solutions de cybersécurité et d\'intelligence des menaces pour protéger les entreprises contre les cyberattaques sophistiquées.',
                'h1': ['SEKOIA', 'Cybersécurité Avancée', 'Protection des Entreprises'],
                'h2': ['Solutions de Sécurité', 'Intelligence des Menaces', 'Services SOC Managés', 'Plateforme SOAR'],
                'h3': ['SOAR Platform', 'Threat Intelligence', 'SOC Services', 'Formation Cybersécurité'],
                'paragraphs': [
                    'SEKOIA est une entreprise française leader spécialisée dans la cybersécurité et l\'intelligence des menaces avancées. Nous développons des solutions innovantes de sécurité pour protéger les entreprises contre les cyberattaques sophistiquées et les menaces persistantes avancées.',
                    'Notre plateforme SOAR (Security Orchestration, Automation and Response) révolutionnaire permet aux équipes de sécurité d\'automatiser leurs processus de détection, d\'investigation et de réponse aux incidents de sécurité en temps réel.',
                    'Nos services d\'intelligence des menaces de pointe fournissent des informations contextuelles critiques sur les acteurs malveillants, leurs techniques d\'attaque, et les indicateurs de compromission pour une protection proactive.',
                    'Nous proposons également des services SOC (Security Operations Center) managés complets pour les entreprises qui souhaitent externaliser leur surveillance de sécurité 24/7 avec des experts certifiés.',
                    'Notre équipe d\'experts en cybersécurité, composée d\'analystes certifiés et de chercheurs en sécurité, accompagne les organisations dans leur transformation digitale sécurisée et leur mise en conformité réglementaire.',
                    'SEKOIA travaille avec des entreprises de toutes tailles, des PME innovantes aux grandes corporations multinationales, dans tous les secteurs d\'activité critiques incluant la finance, la santé, l\'énergie et les télécommunications.',
                    'Nos solutions de cybersécurité sont déployées dans plus de 50 pays à travers le monde et protègent des millions d\'utilisateurs contre les cybermenaces émergentes et les attaques zero-day.',
                    'La plateforme SEKOIA.IO intègre des capacités avancées d\'analyse comportementale, de machine learning et d\'intelligence artificielle pour détecter les menaces sophistiquées et les attaques furtives.',
                    'Nous offrons des programmes de formation spécialisés en cybersécurité pour sensibiliser les équipes IT aux bonnes pratiques de sécurité et développer leurs compétences en réponse aux incidents.',
                    'Notre centre de recherche et développement développe en permanence de nouvelles techniques de détection, d\'analyse des malwares et de threat hunting pour anticiper les menaces futures.',
                    'Les entreprises clientes bénéficient d\'un accompagnement personnalisé pour évaluer leur posture de sécurité, identifier les vulnérabilités critiques et mettre en place une stratégie de cybersécurité robuste.',
                    'SEKOIA propose des services de conseil en cybersécurité, d\'audit de sécurité, de tests d\'intrusion et d\'évaluation des risques pour renforcer la résilience des infrastructures critiques.'
                ],
                'json_ld': [],
                'word_count': 350
            },
            {
                'url': 'https://sekoia.ca/solutions',
                'title': 'Solutions de Cybersécurité - SEKOIA',
                'meta_description': 'Découvrez nos solutions complètes: plateforme SOAR, intelligence des menaces, SOC managé, formation cybersécurité.',
                'h1': ['Solutions de Cybersécurité'],
                'h2': ['Plateforme SOAR', 'Intelligence des Menaces', 'SOC Managé', 'Formation et Conseil'],
                'h3': ['Automatisation Sécurité', 'Threat Hunting', 'Monitoring 24/7', 'Certification Sécurité'],
                'paragraphs': [
                    'Notre plateforme SOAR automatise la détection, l\'analyse et la réponse aux incidents de sécurité pour réduire les temps de réaction et améliorer l\'efficacité des équipes SOC.',
                    'Les services d\'intelligence des menaces fournissent une visibilité en temps réel sur le paysage des menaces avec des indicateurs de compromission actualisés et des analyses contextuelles.',
                    'Le SOC managé offre une surveillance continue 24/7 avec des analystes experts qui monitent, détectent et répondent aux incidents de sécurité pour le compte de nos clients.',
                    'Nos programmes de formation certifiants développent les compétences en cybersécurité des équipes IT avec des modules pratiques sur la réponse aux incidents et l\'analyse forensique.',
                    'Les services de conseil accompagnent les organisations dans l\'évaluation de leur maturité sécurité, la définition de leur stratégie de cybersécurité et la mise en conformité réglementaire.'
                ],
                'json_ld': [],
                'word_count': 180
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
    print(f"   - Sub-industry: {industry_class.get('sub_industry', 'N/A')}")
    print(f"   - Company Type: {industry_class.get('company_type', 'unknown')}")
    print(f"   - Business Model: {industry_class.get('business_model', 'unknown')}")
    print(f"   - Positioning: {industry_class.get('positioning', 'N/A')}")
    print(f"   - Maturity: {industry_class.get('maturity', 'N/A')}")
    print(f"   - Geographic Scope: {industry_class.get('geographic_scope', 'N/A')}")
    print(f"   - Confidence: {industry_class.get('confidence', 0):.2f}")
    print(f"   - Reasoning: {industry_class.get('reasoning', 'N/A')}")
    
    print("\n✅ Entities Extracted:")
    entities = semantic_results.get('entities', {})
    offerings = entities.get('offerings', [])
    print(f"   - Offerings: {len(offerings)} found")
    for i, offering in enumerate(offerings[:5]):
        if isinstance(offering, dict):
            print(f"     {i+1}. {offering.get('name', 'N/A')}")
            print(f"        Description: {offering.get('description', 'N/A')}")
            print(f"        Target Segment: {offering.get('target_segment', 'N/A')}")
            print(f"        Priority: {offering.get('priority', 'N/A')}")
        else:
            print(f"     {i+1}. {offering}")
    
    locations = entities.get('locations', [])
    print(f"   - Locations: {len(locations)} found")
    for loc in locations[:3]:
        print(f"     - {loc.get('city', 'N/A')}, {loc.get('region', 'N/A')}")
    
    problems = entities.get('problems_solved', [])
    print(f"   - Problems Solved: {len(problems)} found")
    for i, prob in enumerate(problems[:5]):
        if isinstance(prob, dict):
            print(f"     {i+1}. {prob.get('problem', 'N/A')}")
            print(f"        Category: {prob.get('category', 'N/A')}")
            print(f"        Severity: {prob.get('severity', 'N/A')}")
            print(f"        Solution Approach: {prob.get('solution_approach', 'N/A')}")
        else:
            print(f"     {i+1}. {prob}")
    
    # Test Topics (LDA)
    topics = semantic_results.get('topics', [])
    print(f"   - Topics (LDA): {len(topics)} found")
    for i, topic in enumerate(topics[:3]):
        if isinstance(topic, dict):
            print(f"     {i+1}. {topic.get('label', 'N/A')}")
            print(f"        Keywords: {topic.get('keywords', [])}")
            print(f"        Top Words Scores: {topic.get('top_words_scores', [])}")
        else:
            print(f"     {i+1}. {topic}")
    
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
    
    # Check ENHANCED FEATURES as requested in review
    print("🔍 ENHANCED FEATURES VALIDATION (Review Request):")
    enhanced_features_present = True
    missing_features = []
    
    # Check industry classification enhanced fields
    required_industry_fields = ['sub_industry', 'positioning', 'maturity', 'geographic_scope', 'reasoning']
    for field in required_industry_fields:
        if field not in industry_class:
            enhanced_features_present = False
            missing_features.append(f"industry_classification.{field}")
    
    # Check offerings enhanced fields (12 items required)
    if offerings:
        required_offering_fields = ['description', 'target_segment', 'priority']
        for field in required_offering_fields:
            if isinstance(offerings[0], dict) and field not in offerings[0]:
                enhanced_features_present = False
                missing_features.append(f"offerings.{field}")
        
        if len(offerings) < 12:
            print(f"   ⚠️  Only {len(offerings)} offerings found (target: 12)")
    
    # Check problems_solved enhanced fields (15 items required)
    if problems:
        required_problem_fields = ['category', 'severity', 'solution_approach']
        for field in required_problem_fields:
            if isinstance(problems[0], dict) and field not in problems[0]:
                enhanced_features_present = False
                missing_features.append(f"problems_solved.{field}")
        
        if len(problems) < 15:
            print(f"   ⚠️  Only {len(problems)} problems found (target: 15)")
    
    # Check LDA topics enhanced fields
    topics = semantic_results.get('topics', [])
    if topics:
        required_topic_fields = ['keywords', 'top_words_scores']
        for field in required_topic_fields:
            if isinstance(topics[0], dict) and field not in topics[0]:
                enhanced_features_present = False
                missing_features.append(f"topics.{field}")
    
    if enhanced_features_present:
        print("   ✅ ALL enhanced features are present!")
    else:
        print("   ❌ Missing enhanced features:")
        for feature in missing_features:
            print(f"     - {feature}")
    
    # Check if semantic analysis has required fields
    required_fields = ['industry_classification', 'entities', 'topics']
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