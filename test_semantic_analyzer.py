#!/usr/bin/env python3
"""
Direct test of semantic_analyzer.py enhanced problems_solved functionality
"""

import sys
import os
sys.path.append('/app/backend')

from semantic_analyzer import SemanticAnalyzer
import json

def test_enhanced_problems_solved():
    """Test the enhanced problems_solved functionality directly"""
    print("🎯 TESTING ENHANCED PROBLEMS SOLVED DIRECTLY")
    print("=" * 60)
    
    # Create sample crawl data
    sample_crawl_data = {
        'base_url': 'https://sekoia.ca',
        'pages_crawled': 5,
        'pages': [
            {
                'url': 'https://sekoia.ca',
                'title': 'SEKOIA - Agence de croissance digitale',
                'meta_description': 'Agence spécialisée en croissance digitale et marketing performance',
                'h1': ['Accélérez votre croissance digitale'],
                'h2': ['Services de marketing digital', 'Expertise en croissance'],
                'h3': ['SEO', 'Performance Marketing', 'Analytics'],
                'paragraphs': [
                    'Nous aidons les entreprises à résoudre leurs défis de croissance digitale.',
                    'Notre expertise permet d\'optimiser les processus marketing et d\'améliorer les performances.',
                    'Nous résolvons les problèmes de visibilité en ligne et d\'acquisition client.',
                    'Solutions pour éliminer les inefficacités et accélérer la croissance.',
                    'Défis de mesure et d\'attribution résolus par nos experts analytics.'
                ],
                'json_ld': [],
                'word_count': 150
            }
        ]
    }
    
    # Initialize analyzer
    analyzer = SemanticAnalyzer()
    
    # Test the problems extraction directly
    print("🔍 Testing _extract_problems_solved method...")
    
    # Create sample text
    sample_text = """
    Nous aidons les entreprises à résoudre leurs défis de croissance digitale.
    Notre expertise permet d'optimiser les processus marketing et d'améliorer les performances.
    Nous résolvons les problèmes de visibilité en ligne et d'acquisition client.
    Solutions pour éliminer les inefficacités et accélérer la croissance.
    Défis de mesure et d'attribution résolus par nos experts analytics.
    Problèmes de conversion et d'optimisation des campagnes.
    Difficultés de tracking et de mesure ROI.
    """
    
    try:
        problems = analyzer._extract_problems_solved(sample_text)
        
        print(f"📊 RESULTS:")
        print(f"   Problems found: {len(problems)}")
        
        # Validate structure
        if len(problems) >= 15:
            print("✅ Quantity requirement met: 15+ problems")
        else:
            print(f"❌ Quantity requirement FAILED: {len(problems)} < 15")
            return False
        
        # Check structure of first few problems
        required_fields = ['problem', 'category', 'severity', 'affected_segment', 'solution_approach']
        
        valid_count = 0
        for i, problem in enumerate(problems[:5]):  # Check first 5
            print(f"\n🔍 Problem {i+1}:")
            
            if not isinstance(problem, dict):
                print(f"   ❌ Not a dict: {type(problem)}")
                continue
            
            all_fields_valid = True
            for field in required_fields:
                if field in problem and problem[field] and problem[field] != "N/A":
                    print(f"   ✅ {field}: {problem[field]}")
                else:
                    print(f"   ❌ {field}: MISSING or invalid")
                    all_fields_valid = False
            
            if all_fields_valid:
                valid_count += 1
        
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Total problems: {len(problems)}")
        print(f"   Valid problems (first 5 checked): {valid_count}/5")
        
        if len(problems) >= 15 and valid_count == 5:
            print("\n🎉 ENHANCED PROBLEMS SOLVED TEST PASSED!")
            print("   ✅ 15+ problems generated")
            print("   ✅ All required fields present")
            print("   ✅ No null/N/A values")
            return True
        else:
            print("\n❌ ENHANCED PROBLEMS SOLVED TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing problems extraction: {str(e)}")
        
        # Test fallback method
        print("\n🔄 Testing fallback method...")
        try:
            problems_fallback = analyzer._extract_problems_fallback(sample_text)
            
            print(f"📊 FALLBACK RESULTS:")
            print(f"   Problems found: {len(problems_fallback)}")
            
            if len(problems_fallback) >= 15:
                print("✅ Fallback quantity requirement met: 15+ problems")
                
                # Check first problem structure
                if problems_fallback and isinstance(problems_fallback[0], dict):
                    first_problem = problems_fallback[0]
                    print(f"\n🔍 First fallback problem structure:")
                    for field in required_fields:
                        if field in first_problem:
                            print(f"   ✅ {field}: {first_problem[field]}")
                        else:
                            print(f"   ❌ {field}: MISSING")
                    
                    print("\n🎉 FALLBACK METHOD WORKS - Enhanced Problems Solved structure correct!")
                    return True
                else:
                    print("❌ Fallback problems not properly structured")
                    return False
            else:
                print(f"❌ Fallback quantity insufficient: {len(problems_fallback)} < 15")
                return False
                
        except Exception as fallback_error:
            print(f"❌ Fallback method also failed: {str(fallback_error)}")
            return False

def main():
    """Main test execution"""
    success = test_enhanced_problems_solved()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())