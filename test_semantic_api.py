#!/usr/bin/env python3
"""
Test the semantic analysis module through the API
"""
import requests
import json
import time
from datetime import datetime

def test_semantic_analysis_api():
    """Test semantic analysis through the full API"""
    
    base_url = "https://quickwinseo.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🧠 Testing Semantic Analysis Module via API")
    print("=" * 60)
    
    # Test with a known report ID
    report_id = "406d0196-6d9a-498c-b5d6-8c2fb73605e6"
    
    print(f"📊 Fetching report: {report_id}")
    
    try:
        response = requests.get(f"{api_url}/reports/{report_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch report: {response.status_code}")
            return False
        
        report_data = response.json()
        
        # Test 1: Semantic Analysis Present
        print("\n🔍 Testing Semantic Analysis Presence:")
        semantic_analysis = report_data.get('semantic_analysis', {})
        
        if semantic_analysis:
            print("✅ Semantic analysis found in report")
            
            # Test industry classification
            industry_classification = semantic_analysis.get('industry_classification', {})
            if industry_classification:
                primary_industry = industry_classification.get('primary_industry', 'unknown')
                company_type = industry_classification.get('company_type', 'unknown')
                business_model = industry_classification.get('business_model', 'unknown')
                confidence = industry_classification.get('confidence', 0)
                
                print(f"   - Industry: {primary_industry}")
                print(f"   - Company Type: {company_type}")
                print(f"   - Business Model: {business_model}")
                print(f"   - Confidence: {confidence:.2f}")
            else:
                print("❌ Industry classification missing")
                return False
            
            # Test entities
            entities = semantic_analysis.get('entities', {})
            if entities:
                offerings = entities.get('offerings', [])
                locations = entities.get('locations', [])
                problems_solved = entities.get('problems_solved', [])
                customer_segments = entities.get('customer_segments', [])
                
                print(f"   - Offerings: {len(offerings)} extracted")
                print(f"   - Locations: {len(locations)} found")
                print(f"   - Problems solved: {len(problems_solved)} identified")
                print(f"   - Customer segments: {len(customer_segments)} found")
                
                # Show sample offerings
                if offerings:
                    print("   - Sample offerings:")
                    for i, offering in enumerate(offerings[:3]):
                        name = offering.get('name', 'N/A')
                        mentions = offering.get('mentions_count', 0)
                        print(f"     {i+1}. {name} ({mentions} mentions)")
            else:
                print("❌ Entities missing")
                return False
        else:
            print("❌ Semantic analysis missing from report")
            return False
        
        # Test 2: Query Breakdown Present
        print("\n🔍 Testing Query Breakdown:")
        query_breakdown = report_data.get('query_breakdown', {})
        
        if query_breakdown:
            print("✅ Query breakdown found in report")
            
            non_branded = query_breakdown.get('non_branded', 0)
            semi_branded = query_breakdown.get('semi_branded', 0)
            branded = query_breakdown.get('branded', 0)
            total = query_breakdown.get('total', 0)
            
            print(f"   - Non-branded: {non_branded}")
            print(f"   - Semi-branded: {semi_branded}")
            print(f"   - Branded: {branded}")
            print(f"   - Total: {total}")
            
            if total > 0:
                non_branded_pct = (non_branded / total) * 100
                semi_branded_pct = (semi_branded / total) * 100
                branded_pct = (branded / total) * 100
                
                print(f"   - Distribution: {non_branded_pct:.1f}% / {semi_branded_pct:.1f}% / {branded_pct:.1f}%")
                print(f"   - Target: 80% / 15% / 5%")
                
                # Validate distribution
                if total >= 50:  # At least 50 queries
                    print("✅ Sufficient queries generated")
                else:
                    print("⚠️  Low query count")
                
                if non_branded_pct >= 60:  # At least 60% non-branded
                    print("✅ Good non-branded ratio")
                else:
                    print("⚠️  Low non-branded ratio")
        else:
            print("❌ Query breakdown missing from report")
            return False
        
        # Test 3: Test Queries Present
        print("\n🔍 Testing Generated Queries:")
        test_queries = report_data.get('test_queries', [])
        
        if test_queries:
            print(f"✅ Test queries found: {len(test_queries)} queries")
            
            # Show sample queries
            print("   - Sample queries:")
            for i, query in enumerate(test_queries[:5]):
                print(f"     {i+1}. {query}")
            
            # Check for company name in queries (to validate non-branded)
            company_name = entities.get('company_info', {}).get('name', '') if entities else ''
            if company_name:
                branded_count = sum(1 for q in test_queries[:20] if company_name.lower() in q.lower())
                non_branded_sample = 20 - branded_count
                
                print(f"   - Sample analysis (first 20 queries):")
                print(f"     - Non-branded: {non_branded_sample}/20")
                print(f"     - Branded: {branded_count}/20")
                
                if non_branded_sample >= 15:  # At least 75% non-branded in sample
                    print("✅ Queries appear mostly non-branded")
                else:
                    print("⚠️  Many queries contain company name")
        else:
            print("❌ Test queries missing from report")
            return False
        
        # Test 4: Integration with Other Modules
        print("\n🔍 Testing Integration with Other Modules:")
        
        # Check if other modules are still present
        modules_present = 0
        total_modules = 4
        
        if report_data.get('competitive_intelligence'):
            print("✅ Competitive Intelligence module present")
            modules_present += 1
        else:
            print("❌ Competitive Intelligence module missing")
        
        if report_data.get('schemas'):
            print("✅ Schema Generator module present")
            modules_present += 1
        else:
            print("❌ Schema Generator module missing")
        
        if report_data.get('visibility_results'):
            print("✅ Visibility Results module present")
            modules_present += 1
        else:
            print("❌ Visibility Results module missing")
        
        if report_data.get('scores'):
            print("✅ Scoring module present")
            modules_present += 1
        else:
            print("❌ Scoring module missing")
        
        # Final Assessment
        print("\n📊 Final Assessment:")
        print("=" * 60)
        
        success_criteria = 0
        total_criteria = 6
        
        # Criterion 1: Semantic analysis present and complete
        if semantic_analysis and industry_classification and entities:
            print("✅ Semantic analysis: COMPLETE")
            success_criteria += 1
        else:
            print("❌ Semantic analysis: INCOMPLETE")
        
        # Criterion 2: Query breakdown present
        if query_breakdown and total > 0:
            print("✅ Query breakdown: PRESENT")
            success_criteria += 1
        else:
            print("❌ Query breakdown: MISSING")
        
        # Criterion 3: Sufficient queries generated
        if len(test_queries) >= 50:
            print("✅ Query generation: SUFFICIENT")
            success_criteria += 1
        else:
            print("❌ Query generation: INSUFFICIENT")
        
        # Criterion 4: Industry detection working
        if primary_industry != 'unknown' and primary_industry != 'generic':
            print("✅ Industry detection: WORKING")
            success_criteria += 1
        else:
            print("❌ Industry detection: FAILED")
        
        # Criterion 5: Non-branded queries generated
        if non_branded > 0:
            print("✅ Non-branded queries: GENERATED")
            success_criteria += 1
        else:
            print("❌ Non-branded queries: MISSING")
        
        # Criterion 6: Integration with other modules
        if modules_present >= 3:
            print("✅ Module integration: WORKING")
            success_criteria += 1
        else:
            print("❌ Module integration: BROKEN")
        
        print(f"\n🎯 Success Rate: {success_criteria}/{total_criteria} ({(success_criteria/total_criteria)*100:.1f}%)")
        
        if success_criteria >= 5:
            print("🎉 SEMANTIC ANALYSIS MODULE: WORKING CORRECTLY")
            return True
        elif success_criteria >= 3:
            print("⚠️  SEMANTIC ANALYSIS MODULE: PARTIALLY WORKING")
            return True
        else:
            print("❌ SEMANTIC ANALYSIS MODULE: MAJOR ISSUES")
            return False
            
    except Exception as e:
        print(f"❌ Error testing semantic analysis: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_semantic_analysis_api()
    exit(0 if success else 1)