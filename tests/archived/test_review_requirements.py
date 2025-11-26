#!/usr/bin/env python3
"""
FOCUSED TEST FOR REVIEW REQUIREMENTS
Tests specifically the enhanced semantic analysis features requested in the review
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('/app/backend/.env')

class ReviewRequirementsTest:
    def __init__(self, base_url="https://geo-fix-roadmap.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_claude_sonnet_4_5_direct(self) -> bool:
        """Test Claude Sonnet 4.5 API directly"""
        self.log("🎯 PRIORITY TEST: Claude Sonnet 4.5 API Direct Test")
        self.tests_run += 1
        
        try:
            from anthropic import Anthropic
            
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                self.log("❌ ANTHROPIC_API_KEY not found in environment")
                return False
            
            self.log(f"   Using API key: {api_key[:20]}...")
            
            client = Anthropic(api_key=api_key)
            
            # Test claude-sonnet-4-5-20250929 specifically
            self.log("   Testing claude-sonnet-4-5-20250929...")
            
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{
                    "role": "user", 
                    "content": "Test message: respond with 'Claude Sonnet 4.5 working' if you receive this."
                }]
            )
            
            response_text = response.content[0].text
            self.log(f"✅ Claude Sonnet 4.5 response: {response_text}")
            
            if "working" in response_text.lower():
                self.log("✅ Claude Sonnet 4.5 API is FUNCTIONAL!")
                self.tests_passed += 1
                return True
            else:
                self.log("⚠️  Claude responded but message unclear")
                self.tests_passed += 1
                return True
                
        except Exception as e:
            self.log(f"❌ Claude API test failed: {str(e)}")
            return False
    
    def create_test_analysis(self) -> Optional[str]:
        """Create a new analysis and return report ID"""
        self.log("🔍 Creating new analysis for sekoia.ca...")
        self.tests_run += 1
        
        test_lead_data = {
            "firstName": "Review",
            "lastName": "Test", 
            "email": "review@test.com",
            "company": "Review Testing",
            "url": "sekoia.ca",
            "consent": True
        }
        
        try:
            # Create lead
            response = requests.post(f"{self.api_url}/leads", json=test_lead_data, timeout=30)
            if response.status_code != 200:
                self.log(f"❌ Lead creation failed: {response.status_code}")
                return None
            
            lead_data = response.json()
            lead_id = lead_data['id']
            self.log(f"✅ Lead created: {lead_id}")
            
            # Wait for job to complete
            self.log("⏳ Waiting for analysis to complete (max 6 minutes)...")
            
            start_time = time.time()
            max_wait = 360  # 6 minutes
            
            while time.time() - start_time < max_wait:
                # Get leads to find job
                leads_response = requests.get(f"{self.api_url}/leads", timeout=30)
                if leads_response.status_code == 200:
                    leads = leads_response.json()
                    
                    # Find our lead
                    for lead in leads:
                        if lead['id'] == lead_id:
                            if lead.get('latestJob'):
                                job = lead['latestJob']
                                status = job.get('status')
                                progress = job.get('progress', 0)
                                
                                self.log(f"   Status: {status}, Progress: {progress}%")
                                
                                if status == 'completed':
                                    report_id = job.get('reportId')
                                    if report_id:
                                        self.log(f"✅ Analysis completed! Report ID: {report_id}")
                                        self.tests_passed += 1
                                        return report_id
                                elif status == 'failed':
                                    error = job.get('error', 'Unknown error')
                                    self.log(f"❌ Analysis failed: {error}")
                                    return None
                            break
                
                time.sleep(15)  # Wait 15 seconds between checks
            
            self.log(f"⏰ Analysis did not complete within {max_wait} seconds")
            return None
            
        except Exception as e:
            self.log(f"❌ Error creating analysis: {str(e)}")
            return None
    
    def test_existing_report(self, report_id: str = "e38b4d21-31d8-410b-9753-fa1268fe823a") -> bool:
        """Test existing report for enhanced features"""
        self.log(f"🔍 Testing existing report: {report_id}")
        self.tests_run += 1
        
        try:
            response = requests.get(f"{self.api_url}/reports/{report_id}", timeout=60)
            if response.status_code != 200:
                self.log(f"❌ Report not found: {response.status_code}")
                return False
            
            report = response.json()
            self.log(f"✅ Report loaded for: {report.get('url', 'N/A')}")
            
            # Test enhanced semantic analysis features
            return self.validate_enhanced_features(report)
            
        except Exception as e:
            self.log(f"❌ Error testing report: {str(e)}")
            return False
    
    def validate_enhanced_features(self, report_data: Dict[str, Any]) -> bool:
        """Validate enhanced semantic analysis features from review request"""
        self.log("🎯 VALIDATING ENHANCED SEMANTIC ANALYSIS FEATURES...")
        
        semantic_analysis = report_data.get('semantic_analysis', {})
        if not semantic_analysis:
            self.log("❌ No semantic analysis found in report")
            return False
        
        all_tests_passed = True
        
        # 1. Test Enhanced Industry Classification
        self.log("1️⃣ Testing Enhanced Industry Classification...")
        industry_classification = semantic_analysis.get('industry_classification', {})
        
        required_fields = ['sub_industry', 'positioning', 'maturity', 'geographic_scope', 'reasoning']
        missing_fields = []
        
        for field in required_fields:
            value = industry_classification.get(field)
            if not value or value == "N/A" or value is None:
                missing_fields.append(field)
        
        if missing_fields:
            self.log(f"❌ ENHANCED industry classification MISSING fields: {missing_fields}")
            self.log(f"   Available fields: {list(industry_classification.keys())}")
            all_tests_passed = False
        else:
            self.log("✅ Enhanced industry classification COMPLETE")
            self.log(f"   - sub_industry: {industry_classification.get('sub_industry')}")
            self.log(f"   - positioning: {industry_classification.get('positioning')}")
            self.log(f"   - maturity: {industry_classification.get('maturity')}")
            self.log(f"   - geographic_scope: {industry_classification.get('geographic_scope')}")
        
        # 2. Test Enhanced Offerings (12+ items with description, target_segment, priority)
        self.log("2️⃣ Testing Enhanced Offerings...")
        entities = semantic_analysis.get('entities', {})
        offerings = entities.get('offerings', [])
        
        if len(offerings) < 12:
            self.log(f"❌ ENHANCED offerings: Only {len(offerings)} found, need 12+")
            all_tests_passed = False
        else:
            self.log(f"✅ Offerings quantity: {len(offerings)} items (≥12)")
        
        # Check first few offerings for enhanced fields
        enhanced_offerings_count = 0
        for i, offering in enumerate(offerings[:3]):
            if isinstance(offering, dict):
                required_fields = ['description', 'target_segment', 'priority']
                has_all_fields = all(
                    field in offering and offering[field] and offering[field] != "N/A" 
                    for field in required_fields
                )
                if has_all_fields:
                    enhanced_offerings_count += 1
                else:
                    self.log(f"   Offering {i+1} missing enhanced fields: {offering}")
        
        if enhanced_offerings_count == 0:
            self.log(f"❌ ENHANCED offerings: 0/{len(offerings[:3])} have description/target_segment/priority")
            all_tests_passed = False
        else:
            self.log(f"✅ Enhanced offerings: {enhanced_offerings_count}/{len(offerings[:3])} have full details")
        
        # 3. Test Enhanced Problems Solved (15+ items with category, severity, solution_approach)
        self.log("3️⃣ Testing Enhanced Problems Solved...")
        problems_solved = entities.get('problems_solved', [])
        
        if len(problems_solved) < 15:
            self.log(f"❌ ENHANCED problems_solved: Only {len(problems_solved)} found, need 15+")
            all_tests_passed = False
        else:
            self.log(f"✅ Problems solved quantity: {len(problems_solved)} items (≥15)")
        
        # Check first few problems for enhanced fields
        enhanced_problems_count = 0
        for i, problem in enumerate(problems_solved[:3]):
            if isinstance(problem, dict):
                required_fields = ['category', 'severity', 'solution_approach']
                has_all_fields = all(
                    field in problem and problem[field] and problem[field] != "N/A" 
                    for field in required_fields
                )
                if has_all_fields:
                    enhanced_problems_count += 1
                else:
                    self.log(f"   Problem {i+1} missing enhanced fields: {problem}")
        
        if enhanced_problems_count == 0:
            self.log(f"❌ ENHANCED problems_solved: 0/{len(problems_solved[:3])} have category/severity/solution_approach")
            all_tests_passed = False
        else:
            self.log(f"✅ Enhanced problems solved: {enhanced_problems_count}/{len(problems_solved[:3])} have full details")
        
        # 4. Test REAL LDA Topic Modeling with keywords and top_words_scores
        self.log("4️⃣ Testing REAL LDA Topic Modeling...")
        topics = semantic_analysis.get('topics', [])
        
        if not topics:
            self.log("❌ No topics found - LDA Topic Modeling missing")
            all_tests_passed = False
        else:
            self.log(f"✅ Topics found: {len(topics)} items")
            
            # Check if topics have keywords and top_words_scores
            lda_topics_count = 0
            for i, topic in enumerate(topics[:2]):
                if isinstance(topic, dict):
                    has_keywords = 'keywords' in topic and topic['keywords']
                    has_scores = 'top_words_scores' in topic and topic['top_words_scores']
                    
                    if has_keywords and has_scores:
                        lda_topics_count += 1
                        self.log(f"   Topic {i+1}: keywords={len(topic['keywords'])}, scores={len(topic['top_words_scores'])}")
                    else:
                        self.log(f"   Topic {i+1} missing: keywords={has_keywords}, scores={has_scores}")
            
            if lda_topics_count == 0:
                self.log(f"❌ REAL LDA: 0/{len(topics[:2])} topics have keywords and top_words_scores")
                all_tests_passed = False
            else:
                self.log(f"✅ REAL LDA Topic Modeling: {lda_topics_count}/{len(topics[:2])} topics complete")
        
        # 5. Test 100+ Queries with 80%/15%/5% Distribution
        self.log("5️⃣ Testing 100+ Queries with Distribution...")
        query_breakdown = report_data.get('query_breakdown', {})
        
        if not query_breakdown:
            self.log("❌ No query_breakdown found")
            all_tests_passed = False
        else:
            total_queries = query_breakdown.get('total', 0)
            non_branded = query_breakdown.get('non_branded', 0)
            semi_branded = query_breakdown.get('semi_branded', 0)
            branded = query_breakdown.get('branded', 0)
            
            self.log(f"   Total queries: {total_queries}")
            self.log(f"   Non-branded: {non_branded}")
            self.log(f"   Semi-branded: {semi_branded}")
            self.log(f"   Branded: {branded}")
            
            # Check quantity requirement
            if total_queries < 100:
                self.log(f"❌ QUANTITY REQUIREMENT FAILED: {total_queries} < 100 required")
                all_tests_passed = False
            else:
                self.log(f"✅ Quantity requirement met: {total_queries} ≥ 100")
            
            # Check distribution requirement (80%/15%/5%)
            if total_queries > 0:
                non_branded_pct = (non_branded / total_queries) * 100
                semi_branded_pct = (semi_branded / total_queries) * 100
                branded_pct = (branded / total_queries) * 100
                
                self.log(f"   Distribution: {non_branded_pct:.1f}% / {semi_branded_pct:.1f}% / {branded_pct:.1f}%")
                
                # Check if close to 80/15/5 (allow some tolerance)
                distribution_ok = (
                    non_branded_pct >= 75 and non_branded_pct <= 85 and
                    semi_branded_pct >= 10 and semi_branded_pct <= 20 and
                    branded_pct >= 3 and branded_pct <= 10
                )
                
                if distribution_ok:
                    self.log("✅ Distribution requirement met: ~80%/15%/5%")
                else:
                    self.log(f"❌ DISTRIBUTION REQUIREMENT FAILED: Expected ~80%/15%/5%, got {non_branded_pct:.1f}%/{semi_branded_pct:.1f}%/{branded_pct:.1f}%")
                    all_tests_passed = False
        
        # Final result
        if all_tests_passed:
            self.log("🎉 ALL ENHANCED SEMANTIC ANALYSIS FEATURES COMPLETE!")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ ENHANCED SEMANTIC ANALYSIS FEATURES INCOMPLETE")
            return False
    
    def run_review_test(self) -> int:
        """Run focused test for review requirements"""
        self.log("🚀 STARTING REVIEW REQUIREMENTS TEST")
        self.log("=" * 60)
        
        # Test 1: Claude Sonnet 4.5 Direct
        claude_works = self.test_claude_sonnet_4_5_direct()
        
        # Test 2: Enhanced Features on Existing Report
        enhanced_features_work = self.test_existing_report()
        
        # If existing report doesn't have enhanced features, try creating new one
        if not enhanced_features_work:
            self.log("🔄 Existing report lacks enhanced features, creating new analysis...")
            new_report_id = self.create_test_analysis()
            if new_report_id:
                enhanced_features_work = self.test_existing_report(new_report_id)
        
        # Final Results
        self.log("=" * 60)
        self.log("🎯 REVIEW REQUIREMENTS TEST RESULTS:")
        self.log(f"   1. Claude Sonnet 4.5 API: {'✅ WORKING' if claude_works else '❌ FAILED'}")
        self.log(f"   2. Enhanced Semantic Analysis: {'✅ COMPLETE' if enhanced_features_work else '❌ INCOMPLETE'}")
        
        self.log("=" * 60)
        self.log(f"📊 Overall Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if claude_works and enhanced_features_work:
            self.log("🎉 ALL REVIEW REQUIREMENTS MET!")
            return 0
        else:
            self.log("⚠️  REVIEW REQUIREMENTS NOT FULLY MET")
            return 1

def main():
    """Main test execution"""
    tester = ReviewRequirementsTest()
    return tester.run_review_test()

if __name__ == "__main__":
    sys.exit(main())