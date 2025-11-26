#!/usr/bin/env python3
"""
Test Enhanced Semantic Analysis Features
Tests the new deep semantic analysis features mentioned in the review request
"""

import sys
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append('/app/backend')

# Load environment variables
load_dotenv('/app/backend/.env')

from semantic_analyzer import SemanticAnalyzer
from query_generator_v2 import generate_queries_with_analysis

class EnhancedSemanticAnalysisTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_semantic_analyzer_direct(self):
        """Test semantic analyzer directly with sample data"""
        self.log("🧠 Testing Enhanced Semantic Analyzer directly...")
        self.tests_run += 1
        
        # Sample crawl data for sekoia.ca
        sample_crawl_data = {
            'base_url': 'https://sekoia.ca',
            'pages_crawled': 5,
            'pages': [
                {
                    'url': 'https://sekoia.ca',
                    'title': 'SEKOIA - Agence Marketing Digital | Croissance Pilotée par les Données',
                    'meta_description': 'Agence marketing digital spécialisée en SEO, SEM et analytics. Nous aidons les entreprises à croître grâce aux données.',
                    'h1': ['Croissance Digitale Pilotée par les Données'],
                    'h2': ['Services Marketing Digital', 'Expertise SEO', 'Analytics & Données'],
                    'h3': ['Audit SEO', 'Stratégie de Contenu', 'Optimisation Technique'],
                    'paragraphs': [
                        'SEKOIA est une agence marketing digital spécialisée dans la croissance pilotée par les données. Nous aidons les entreprises à optimiser leur présence en ligne grâce à des stratégies SEO avancées, des campagnes SEM performantes et une analyse approfondie des données.',
                        'Notre équipe d\'experts en marketing digital accompagne les PME et grandes entreprises dans leur transformation numérique. Nous proposons des services complets incluant l\'audit SEO, l\'optimisation technique, la création de contenu optimisé et le suivi des performances.',
                        'Basés au Québec, nous servons des clients partout au Canada. Notre approche data-driven nous permet de maximiser le ROI de nos clients et d\'assurer une croissance durable de leur business en ligne.',
                        'Nos services incluent le référencement naturel (SEO), la publicité en ligne (SEM), l\'analytics web, la stratégie de contenu, l\'optimisation de la conversion et le marketing automation.',
                        'Nous résolvons les problèmes de visibilité en ligne, d\'acquisition de trafic qualifié, de conversion faible et de mesure de performance. Notre expertise technique nous permet d\'identifier et corriger les problèmes qui freinent la croissance digitale.'
                    ],
                    'json_ld': [],
                    'word_count': 150
                },
                {
                    'url': 'https://sekoia.ca/services',
                    'title': 'Services Marketing Digital - SEO, SEM, Analytics | SEKOIA',
                    'meta_description': 'Découvrez nos services marketing digital: SEO technique, stratégie de contenu, SEM, analytics et optimisation de conversion.',
                    'h1': ['Nos Services Marketing Digital'],
                    'h2': ['SEO Technique', 'Stratégie de Contenu', 'SEM & Publicité', 'Analytics & Mesure'],
                    'paragraphs': [
                        'Notre service de SEO technique comprend l\'audit complet de votre site, l\'optimisation de la vitesse, la correction des erreurs techniques et l\'amélioration de l\'architecture.',
                        'Nous créons des stratégies de contenu basées sur la recherche de mots-clés, l\'analyse de la concurrence et les besoins de votre audience cible.',
                        'Nos campagnes SEM sur Google Ads et Microsoft Ads sont optimisées pour maximiser le ROI et générer des leads qualifiés.',
                        'Notre service d\'analytics inclut la mise en place de Google Analytics 4, le tracking des conversions et la création de tableaux de bord personnalisés.'
                    ],
                    'word_count': 120
                }
            ]
        }
        
        try:
            analyzer = SemanticAnalyzer()
            result = analyzer.analyze_site(sample_crawl_data)
            
            # Test 1: Industry Classification with Enhanced Features
            industry_classification = result.get('industry_classification', {})
            
            self.log("✅ Testing Industry Classification...")
            required_fields = ['primary_industry', 'sub_industry', 'company_type', 'business_model', 'positioning', 'maturity', 'geographic_scope', 'confidence', 'reasoning']
            
            missing_fields = []
            for field in required_fields:
                if field not in industry_classification:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log(f"❌ Missing enhanced industry classification fields: {missing_fields}")
                return False
            else:
                self.log(f"✅ Industry Classification Enhanced Fields Present:")
                self.log(f"   - Primary Industry: {industry_classification.get('primary_industry')}")
                self.log(f"   - Sub-Industry: {industry_classification.get('sub_industry')}")
                self.log(f"   - Positioning: {industry_classification.get('positioning')}")
                self.log(f"   - Maturity: {industry_classification.get('maturity')}")
                self.log(f"   - Geographic Scope: {industry_classification.get('geographic_scope')}")
                self.log(f"   - Confidence: {industry_classification.get('confidence')}")
                
            # Test 2: Enhanced Entities Extraction
            entities = result.get('entities', {})
            offerings = entities.get('offerings', [])
            problems_solved = entities.get('problems_solved', [])
            
            self.log("✅ Testing Enhanced Entities...")
            
            # Check offerings format (should have description, target_segment, priority)
            if offerings and len(offerings) >= 8:
                sample_offering = offerings[0]
                if isinstance(sample_offering, dict):
                    required_offering_fields = ['name', 'description', 'target_segment', 'priority']
                    offering_missing = [f for f in required_offering_fields if f not in sample_offering]
                    
                    if offering_missing:
                        self.log(f"⚠️  Offerings missing enhanced fields: {offering_missing}")
                    else:
                        self.log(f"✅ Offerings have enhanced format: {len(offerings)} items")
                        self.log(f"   - Sample: {sample_offering.get('name')} ({sample_offering.get('priority')})")
                else:
                    self.log(f"⚠️  Offerings not in enhanced dict format")
            else:
                self.log(f"⚠️  Expected 8+ offerings, got {len(offerings)}")
            
            # Check problems_solved format (should have category, severity, solution_approach)
            if problems_solved and len(problems_solved) >= 10:
                sample_problem = problems_solved[0]
                if isinstance(sample_problem, dict):
                    required_problem_fields = ['problem', 'category', 'severity', 'solution_approach']
                    problem_missing = [f for f in required_problem_fields if f not in sample_problem]
                    
                    if problem_missing:
                        self.log(f"⚠️  Problems missing enhanced fields: {problem_missing}")
                    else:
                        self.log(f"✅ Problems have enhanced format: {len(problems_solved)} items")
                        self.log(f"   - Sample: {sample_problem.get('problem')} ({sample_problem.get('severity')})")
                else:
                    self.log(f"⚠️  Problems not in enhanced dict format")
            else:
                self.log(f"⚠️  Expected 10+ problems, got {len(problems_solved)}")
            
            # Test 3: LDA Topic Modeling
            topics = result.get('topics', [])
            self.log("✅ Testing LDA Topic Modeling...")
            
            if topics and len(topics) >= 5:
                sample_topic = topics[0]
                required_topic_fields = ['topic_id', 'label', 'keywords', 'weight', 'top_words_scores']
                topic_missing = [f for f in required_topic_fields if f not in sample_topic]
                
                if topic_missing:
                    self.log(f"⚠️  Topics missing LDA fields: {topic_missing}")
                else:
                    self.log(f"✅ LDA Topics properly formatted: {len(topics)} topics")
                    self.log(f"   - Sample: {sample_topic.get('label')} (weight: {sample_topic.get('weight')})")
                    self.log(f"   - Keywords: {sample_topic.get('keywords')[:3]}")
            else:
                self.log(f"⚠️  Expected 5+ topics from LDA, got {len(topics)}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Semantic analyzer test failed: {str(e)}")
            return False
    
    def test_query_generation_enhanced(self):
        """Test enhanced query generation with 100 queries and proper distribution"""
        self.log("🔍 Testing Enhanced Query Generation...")
        self.tests_run += 1
        
        # Sample crawl data
        sample_crawl_data = {
            'base_url': 'https://sekoia.ca',
            'pages_crawled': 5,
            'pages': [
                {
                    'url': 'https://sekoia.ca',
                    'title': 'SEKOIA - Agence Marketing Digital | Croissance Pilotée par les Données',
                    'meta_description': 'Agence marketing digital spécialisée en SEO, SEM et analytics.',
                    'paragraphs': [
                        'SEKOIA est une agence marketing digital spécialisée dans la croissance pilotée par les données. Nous aidons les entreprises à optimiser leur présence en ligne grâce à des stratégies SEO avancées, des campagnes SEM performantes et une analyse approfondie des données.',
                        'Notre équipe d\'experts en marketing digital accompagne les PME et grandes entreprises dans leur transformation numérique. Nous proposons des services complets incluant l\'audit SEO, l\'optimisation technique, la création de contenu optimisé et le suivi des performances.',
                        'Nous résolvons les problèmes de visibilité en ligne, d\'acquisition de trafic qualifié, de conversion faible et de mesure de performance.'
                    ]
                }
            ]
        }
        
        try:
            result = generate_queries_with_analysis(sample_crawl_data, num_queries=100)
            
            queries = result.get('queries', [])
            semantic_analysis = result.get('semantic_analysis', {})
            breakdown = result.get('breakdown', {})
            
            # Test query count
            self.log(f"✅ Query Generation Results:")
            self.log(f"   - Total queries generated: {len(queries)}")
            self.log(f"   - Target: 100 queries (80+ minimum)")
            
            if len(queries) >= 80:
                self.log(f"✅ Query count meets minimum requirement")
            else:
                self.log(f"❌ Query count below minimum (got {len(queries)}, need 80+)")
                return False
            
            # Test distribution
            non_branded = breakdown.get('non_branded', 0)
            semi_branded = breakdown.get('semi_branded', 0)
            branded = breakdown.get('branded', 0)
            total = breakdown.get('total', 0)
            
            self.log(f"✅ Query Distribution:")
            self.log(f"   - Non-branded: {non_branded}")
            self.log(f"   - Semi-branded: {semi_branded}")
            self.log(f"   - Branded: {branded}")
            self.log(f"   - Total: {total}")
            
            if total > 0:
                non_branded_pct = (non_branded / total) * 100
                semi_branded_pct = (semi_branded / total) * 100
                branded_pct = (branded / total) * 100
                
                self.log(f"   - Distribution: {non_branded_pct:.1f}% / {semi_branded_pct:.1f}% / {branded_pct:.1f}%")
                self.log(f"   - Target: ~80% / ~15% / ~5%")
                
                # Check if distribution is reasonable (allowing some flexibility)
                if non_branded_pct >= 60 and semi_branded_pct >= 5 and branded_pct >= 3:
                    self.log(f"✅ Distribution is reasonable")
                else:
                    self.log(f"⚠️  Distribution may be off target")
            
            # Test semantic analysis presence
            if semantic_analysis:
                industry = semantic_analysis.get('industry_classification', {}).get('primary_industry', 'unknown')
                entities = semantic_analysis.get('entities', {})
                topics = semantic_analysis.get('topics', [])
                
                self.log(f"✅ Semantic Analysis Integrated:")
                self.log(f"   - Industry detected: {industry}")
                self.log(f"   - Entities extracted: {len(entities.get('offerings', []))} offerings")
                self.log(f"   - Topics identified: {len(topics)} topics")
            else:
                self.log(f"❌ Semantic analysis missing from query generation")
                return False
            
            # Show sample queries
            if queries:
                self.log(f"✅ Sample Queries:")
                for i, query in enumerate(queries[:5]):
                    self.log(f"   - {i+1}. {query}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Query generation test failed: {str(e)}")
            return False
    
    def test_api_integration(self):
        """Test if the enhanced features are available via API"""
        self.log("🌐 Testing API Integration...")
        self.tests_run += 1
        
        try:
            # Get a recent report
            response = requests.get("https://geo-fix-roadmap.preview.emergentagent.com/api/leads", timeout=10)
            if response.status_code != 200:
                self.log(f"❌ Failed to get leads: {response.status_code}")
                return False
            
            leads = response.json()
            
            # Find a report with semantic analysis
            report_id = None
            for lead in leads:
                if lead.get('reports'):
                    for report in lead['reports']:
                        if report.get('semantic_analysis'):
                            report_id = report['id']
                            break
                if report_id:
                    break
            
            if not report_id:
                self.log(f"⚠️  No reports with semantic analysis found in API")
                return False
            
            # Get the report
            response = requests.get(f"https://geo-fix-roadmap.preview.emergentagent.com/api/reports/{report_id}", timeout=10)
            if response.status_code != 200:
                self.log(f"❌ Failed to get report: {response.status_code}")
                return False
            
            report = response.json()
            semantic_analysis = report.get('semantic_analysis', {})
            
            if not semantic_analysis:
                self.log(f"❌ Report has no semantic analysis")
                return False
            
            # Check for enhanced features
            industry_classification = semantic_analysis.get('industry_classification', {})
            entities = semantic_analysis.get('entities', {})
            topics = semantic_analysis.get('topics', [])
            
            self.log(f"✅ API Report Analysis:")
            self.log(f"   - Report ID: {report_id}")
            self.log(f"   - Industry: {industry_classification.get('primary_industry', 'unknown')}")
            self.log(f"   - Confidence: {industry_classification.get('confidence', 0)}")
            self.log(f"   - Offerings: {len(entities.get('offerings', []))}")
            self.log(f"   - Problems: {len(entities.get('problems_solved', []))}")
            self.log(f"   - Topics: {len(topics)}")
            
            # Check query breakdown
            query_breakdown = report.get('query_breakdown', {})
            if query_breakdown:
                total_queries = query_breakdown.get('total', 0)
                self.log(f"   - Total queries: {total_queries}")
                
                if total_queries >= 80:
                    self.log(f"✅ Query count meets requirement")
                else:
                    self.log(f"⚠️  Query count below target: {total_queries}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"❌ API integration test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all enhanced semantic analysis tests"""
        self.log("🚀 Starting Enhanced Semantic Analysis Tests")
        self.log("=" * 60)
        
        # Test 1: Direct semantic analyzer
        self.test_semantic_analyzer_direct()
        
        # Test 2: Enhanced query generation
        self.test_query_generation_enhanced()
        
        # Test 3: API integration
        self.test_api_integration()
        
        # Results
        self.log("=" * 60)
        self.log(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All enhanced semantic analysis tests passed!")
            return 0
        else:
            failure_rate = ((self.tests_run - self.tests_passed) / self.tests_run) * 100
            self.log(f"⚠️  {failure_rate:.1f}% of tests failed")
            return 1

def main():
    """Main test execution"""
    tester = EnhancedSemanticAnalysisTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())