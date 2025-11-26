#!/usr/bin/env python3
"""
Direct test of semantic analysis functionality with working Claude model
"""
import sys
import os
sys.path.append('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from semantic_analyzer import SemanticAnalyzer
from query_generator_v2 import generate_queries_with_analysis

def test_semantic_analysis():
    """Test semantic analysis directly"""
    
    print("🧠 Testing Semantic Analysis with Claude Haiku...")
    
    # Sample crawl data for sekoia.ca
    sample_crawl_data = {
        'base_url': 'https://sekoia.ca',
        'pages_crawled': 3,
        'pages': [
            {
                'url': 'https://sekoia.ca',
                'title': 'SEKOIA | Cybersecurity Solutions',
                'meta_description': 'Advanced cybersecurity solutions for enterprise protection',
                'h1': ['Cybersecurity Excellence', 'Protect Your Business'],
                'h2': ['Threat Detection', 'Incident Response', 'Security Consulting'],
                'h3': ['24/7 Monitoring', 'Expert Analysis', 'Rapid Response'],
                'paragraphs': [
                    'SEKOIA provides comprehensive cybersecurity solutions for enterprises worldwide. Our advanced threat detection and incident response capabilities help organizations protect their critical assets.',
                    'Our team of security experts offers consulting services, security assessments, and managed security services. We specialize in threat intelligence, malware analysis, and digital forensics.',
                    'With 24/7 monitoring and rapid response capabilities, SEKOIA ensures your organization stays protected against evolving cyber threats. Our solutions include SIEM, threat hunting, and vulnerability management.',
                    'We serve enterprise clients across various industries including finance, healthcare, manufacturing, and government sectors. Our expertise covers compliance, risk assessment, and security architecture.',
                    'SEKOIA offers training programs, security awareness sessions, and certification courses for cybersecurity professionals. We help organizations build internal security capabilities.'
                ],
                'json_ld': [],
                'word_count': 150
            },
            {
                'url': 'https://sekoia.ca/services',
                'title': 'Cybersecurity Services | SEKOIA',
                'meta_description': 'Professional cybersecurity services including threat detection, incident response, and security consulting',
                'h1': ['Our Services'],
                'h2': ['Threat Intelligence', 'Managed Security', 'Consulting Services'],
                'h3': ['SOC Services', 'Penetration Testing', 'Compliance Audits'],
                'paragraphs': [
                    'SEKOIA offers a comprehensive range of cybersecurity services designed to protect organizations from sophisticated cyber threats.',
                    'Our threat intelligence platform provides real-time insights into emerging threats and attack patterns.',
                    'Managed security services include 24/7 SOC operations, threat hunting, and incident response.',
                    'Security consulting services cover risk assessments, security architecture design, and compliance auditing.',
                    'We provide penetration testing, vulnerability assessments, and security training programs.'
                ],
                'json_ld': [],
                'word_count': 100
            },
            {
                'url': 'https://sekoia.ca/about',
                'title': 'About SEKOIA | Cybersecurity Experts',
                'meta_description': 'Learn about SEKOIA cybersecurity company and our expert team',
                'h1': ['About SEKOIA'],
                'h2': ['Our Mission', 'Expert Team', 'Global Presence'],
                'h3': ['Leadership', 'Certifications', 'Partnerships'],
                'paragraphs': [
                    'SEKOIA is a leading cybersecurity company founded by security experts with decades of experience in threat detection and incident response.',
                    'Our mission is to help organizations build resilient security postures against evolving cyber threats.',
                    'We have offices in Paris, Montreal, and Singapore, serving clients globally across multiple industries.',
                    'Our team holds industry certifications including CISSP, CISM, CEH, and GCIH.',
                    'We partner with leading technology vendors to deliver comprehensive security solutions.'
                ],
                'json_ld': [],
                'word_count': 80
            }
        ]
    }
    
    try:
        # Test semantic analyzer directly
        analyzer = SemanticAnalyzer()
        semantic_results = analyzer.analyze_site(sample_crawl_data)
        
        print("✅ Semantic Analysis Results:")
        
        # Check industry classification
        industry_classification = semantic_results.get('industry_classification', {})
        print(f"   Industry: {industry_classification.get('primary_industry', 'unknown')}")
        print(f"   Sub-industry: {industry_classification.get('sub_industry', 'N/A')}")
        print(f"   Positioning: {industry_classification.get('positioning', 'N/A')}")
        print(f"   Maturity: {industry_classification.get('maturity', 'N/A')}")
        print(f"   Geographic scope: {industry_classification.get('geographic_scope', 'N/A')}")
        print(f"   Confidence: {industry_classification.get('confidence', 0)}")
        
        # Check entities
        entities = semantic_results.get('entities', {})
        offerings = entities.get('offerings', [])
        problems_solved = entities.get('problems_solved', [])
        
        print(f"   Offerings found: {len(offerings)}")
        if offerings:
            for i, offering in enumerate(offerings[:3]):
                if isinstance(offering, dict):
                    print(f"     {i+1}. {offering.get('name', 'N/A')} - {offering.get('description', 'N/A')}")
                    print(f"        Target: {offering.get('target_segment', 'N/A')}, Priority: {offering.get('priority', 'N/A')}")
        
        print(f"   Problems solved: {len(problems_solved)}")
        if problems_solved:
            for i, problem in enumerate(problems_solved[:3]):
                if isinstance(problem, dict):
                    print(f"     {i+1}. {problem.get('problem', 'N/A')}")
                    print(f"        Category: {problem.get('category', 'N/A')}, Severity: {problem.get('severity', 'N/A')}")
        
        # Check topics
        topics = semantic_results.get('topics', [])
        print(f"   Topics identified: {len(topics)}")
        if topics:
            for i, topic in enumerate(topics[:3]):
                if isinstance(topic, dict):
                    print(f"     {i+1}. {topic.get('label', 'N/A')} - Keywords: {topic.get('keywords', [])}")
        
        # Test query generation
        print("\n🔍 Testing Query Generation...")
        query_results = generate_queries_with_analysis(sample_crawl_data, num_queries=100)
        
        queries = query_results.get('queries', [])
        breakdown = query_results.get('breakdown', {})
        
        print(f"   Total queries generated: {len(queries)}")
        print(f"   Non-branded: {breakdown.get('non_branded', 0)}")
        print(f"   Semi-branded: {breakdown.get('semi_branded', 0)}")
        print(f"   Branded: {breakdown.get('branded', 0)}")
        
        if queries:
            print("   Sample queries:")
            for i, query in enumerate(queries[:5]):
                print(f"     {i+1}. {query}")
        
        # Validate enhanced features
        print("\n🎯 Validating Enhanced Features:")
        
        enhanced_valid = True
        
        # Check industry classification enhanced fields
        required_industry_fields = ['sub_industry', 'positioning', 'maturity', 'geographic_scope', 'reasoning']
        missing_industry_fields = []
        for field in required_industry_fields:
            if not industry_classification.get(field) or industry_classification.get(field) == "N/A":
                missing_industry_fields.append(field)
        
        if missing_industry_fields:
            print(f"   ❌ Industry classification missing: {missing_industry_fields}")
            enhanced_valid = False
        else:
            print("   ✅ Industry classification enhanced fields complete")
        
        # Check offerings enhanced fields
        if len(offerings) < 12:
            print(f"   ❌ Offerings: Only {len(offerings)} found, need 12")
            enhanced_valid = False
        else:
            offerings_valid = True
            for offering in offerings[:3]:
                if isinstance(offering, dict):
                    required_fields = ['description', 'target_segment', 'priority']
                    for field in required_fields:
                        if not offering.get(field) or offering.get(field) == "N/A":
                            offerings_valid = False
                            break
            
            if offerings_valid:
                print("   ✅ Offerings enhanced fields complete")
            else:
                print("   ❌ Offerings missing enhanced fields")
                enhanced_valid = False
        
        # Check problems_solved enhanced fields
        if len(problems_solved) < 15:
            print(f"   ❌ Problems solved: Only {len(problems_solved)} found, need 15")
            enhanced_valid = False
        else:
            problems_valid = True
            for problem in problems_solved[:3]:
                if isinstance(problem, dict):
                    required_fields = ['category', 'severity', 'solution_approach']
                    for field in required_fields:
                        if not problem.get(field) or problem.get(field) == "N/A":
                            problems_valid = False
                            break
            
            if problems_valid:
                print("   ✅ Problems solved enhanced fields complete")
            else:
                print("   ❌ Problems solved missing enhanced fields")
                enhanced_valid = False
        
        # Check LDA topics
        lda_valid = True
        for topic in topics[:2]:
            if isinstance(topic, dict):
                if not topic.get('keywords') or not topic.get('top_words_scores'):
                    lda_valid = False
                    break
        
        if lda_valid and topics:
            print("   ✅ LDA Topic Modeling with keywords and scores complete")
        else:
            print("   ❌ LDA Topic Modeling missing enhanced features")
            enhanced_valid = False
        
        # Check query requirements
        total_queries = breakdown.get('total', 0)
        if total_queries >= 100:
            print("   ✅ Query quantity requirement met (100+)")
        else:
            print(f"   ❌ Query quantity requirement failed: {total_queries} < 100")
            enhanced_valid = False
        
        # Check distribution
        if total_queries > 0:
            non_branded_pct = (breakdown.get('non_branded', 0) / total_queries) * 100
            semi_branded_pct = (breakdown.get('semi_branded', 0) / total_queries) * 100
            branded_pct = (breakdown.get('branded', 0) / total_queries) * 100
            
            distribution_ok = (
                non_branded_pct >= 75 and non_branded_pct <= 85 and
                semi_branded_pct >= 10 and semi_branded_pct <= 20 and
                branded_pct >= 3 and branded_pct <= 10
            )
            
            if distribution_ok:
                print(f"   ✅ Query distribution correct: {non_branded_pct:.1f}%/{semi_branded_pct:.1f}%/{branded_pct:.1f}%")
            else:
                print(f"   ❌ Query distribution incorrect: {non_branded_pct:.1f}%/{semi_branded_pct:.1f}%/{branded_pct:.1f}% (need ~80%/15%/5%)")
                enhanced_valid = False
        
        print(f"\n📊 FINAL RESULT:")
        if enhanced_valid:
            print("🎉 ALL ENHANCED FEATURES WORKING WITH CLAUDE HAIKU!")
            return True
        else:
            print("⚠️  ENHANCED FEATURES INCOMPLETE")
            return False
            
    except Exception as e:
        print(f"❌ Semantic analysis test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_semantic_analysis()
    sys.exit(0 if success else 1)