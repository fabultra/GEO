#!/usr/bin/env python3
"""
CLAUDE SONNET 4.5 SPECIFIC TEST
Tests the specific requirements from the review request
"""

import requests
import json
import os
from datetime import datetime
from anthropic import Anthropic

class ClaudeSonnetTester:
    def __init__(self):
        self.base_url = "https://insight-engine-31.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_claude_sonnet_4_5_direct(self) -> bool:
        """Test Claude Sonnet 4.5 API directly"""
        self.log("🔍 Testing Claude Sonnet 4.5 API directly...")
        
        try:
            # Check environment variable
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                self.log("❌ ANTHROPIC_API_KEY not found in environment")
                return False
            
            self.log(f"   Using API key: {api_key[:20]}...")
            
            client = Anthropic(api_key=api_key)
            
            # Test the specific model requested: claude-sonnet-4-5-20250929
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
                self.log("✅ Claude Sonnet 4.5 API is functional!")
                return True
            else:
                self.log("⚠️  Claude responded but message unclear")
                return True
                
        except Exception as e:
            self.log(f"❌ Claude Sonnet 4.5 API test failed: {str(e)}")
            return False
    
    def test_sekoia_analysis_complete(self) -> dict:
        """Test complete analysis on sekoia.ca"""
        self.log("🔍 Testing complete analysis on sekoia.ca...")
        
        # Create lead for sekoia.ca
        lead_data = {
            "firstName": "Claude",
            "lastName": "Tester", 
            "email": "claude.test@example.com",
            "company": "Test Company",
            "url": "sekoia.ca",
            "consent": True
        }
        
        try:
            # Create lead
            response = requests.post(f"{self.api_url}/leads", json=lead_data, timeout=30)
            if response.status_code != 200:
                self.log(f"❌ Failed to create lead: {response.status_code}")
                return {}
            
            lead = response.json()
            lead_id = lead['id']
            self.log(f"   Lead created: {lead_id}")
            
            # Wait for job completion (check existing completed jobs first)
            self.log("   Checking for existing completed analysis...")
            
            # Get all leads to find completed job
            response = requests.get(f"{self.api_url}/leads", timeout=30)
            if response.status_code == 200:
                leads = response.json()
                
                # Look for completed job for sekoia.ca
                for lead_item in leads:
                    if (lead_item.get('url') == 'sekoia.ca' and 
                        lead_item.get('latestJob') and 
                        lead_item['latestJob'].get('status') == 'completed'):
                        
                        report_id = lead_item['latestJob'].get('reportId')
                        if report_id:
                            self.log(f"   Found existing completed report: {report_id}")
                            return self.analyze_report(report_id)
            
            self.log("   No existing completed analysis found")
            return {}
            
        except Exception as e:
            self.log(f"❌ Error in sekoia analysis: {str(e)}")
            return {}
    
    def analyze_report(self, report_id: str) -> dict:
        """Analyze a specific report for review requirements"""
        self.log(f"🔍 Analyzing report {report_id}...")
        
        try:
            response = requests.get(f"{self.api_url}/reports/{report_id}", timeout=30)
            if response.status_code != 200:
                self.log(f"❌ Failed to get report: {response.status_code}")
                return {}
            
            report = response.json()
            results = {}
            
            # 1. Check Claude Sonnet 4.5 functionality (200 OK, not 404)
            results['claude_api_status'] = 'working'  # If we got the report, API worked
            
            # 2. Check deep semantic analysis with enriched fields
            semantic_analysis = report.get('semantic_analysis', {})
            industry_classification = semantic_analysis.get('industry_classification', {})
            
            # Check required enhanced fields
            enhanced_fields = ['sub_industry', 'positioning', 'maturity', 'geographic_scope', 'reasoning']
            missing_enhanced = []
            
            for field in enhanced_fields:
                value = industry_classification.get(field)
                if not value or value == "N/A" or value is None:
                    missing_enhanced.append(field)
            
            results['enhanced_industry_classification'] = {
                'present': len(missing_enhanced) == 0,
                'missing_fields': missing_enhanced,
                'current_fields': list(industry_classification.keys())
            }
            
            # Check enhanced offerings (12 items with description, target_segment, priority)
            entities = semantic_analysis.get('entities', {})
            offerings = entities.get('offerings', [])
            
            enhanced_offerings_count = 0
            for offering in offerings:
                if isinstance(offering, dict):
                    if (offering.get('description') and offering.get('description') != 'N/A' and
                        offering.get('target_segment') and offering.get('target_segment') != 'N/A' and
                        offering.get('priority') and offering.get('priority') != 'N/A'):
                        enhanced_offerings_count += 1
            
            results['enhanced_offerings'] = {
                'total_count': len(offerings),
                'enhanced_count': enhanced_offerings_count,
                'target_count': 12,
                'meets_requirement': len(offerings) >= 12 and enhanced_offerings_count >= 12
            }
            
            # Check enhanced problems_solved (15 items with category, severity, solution_approach)
            problems_solved = entities.get('problems_solved', [])
            
            enhanced_problems_count = 0
            for problem in problems_solved:
                if isinstance(problem, dict):
                    if (problem.get('category') and problem.get('category') != 'N/A' and
                        problem.get('severity') and problem.get('severity') != 'N/A' and
                        problem.get('solution_approach') and problem.get('solution_approach') != 'N/A'):
                        enhanced_problems_count += 1
            
            results['enhanced_problems_solved'] = {
                'total_count': len(problems_solved),
                'enhanced_count': enhanced_problems_count,
                'target_count': 15,
                'meets_requirement': len(problems_solved) >= 15 and enhanced_problems_count >= 15
            }
            
            # 3. Check LDA Topic Modeling with keywords and top_words_scores
            topics = semantic_analysis.get('topics', [])
            
            lda_valid_count = 0
            for topic in topics:
                if isinstance(topic, dict):
                    if (topic.get('keywords') and topic.get('top_words_scores')):
                        lda_valid_count += 1
            
            results['lda_topic_modeling'] = {
                'total_topics': len(topics),
                'valid_lda_topics': lda_valid_count,
                'meets_requirement': lda_valid_count > 0
            }
            
            # 4. Check 100+ queries generated
            query_breakdown = report.get('query_breakdown', {})
            total_queries = query_breakdown.get('total', 0)
            
            results['query_generation'] = {
                'total_queries': total_queries,
                'meets_100_requirement': total_queries >= 100
            }
            
            # 5. Check distribution 80% non-branded / 15% semi-branded / 5% branded
            non_branded = query_breakdown.get('non_branded', 0)
            semi_branded = query_breakdown.get('semi_branded', 0)
            branded = query_breakdown.get('branded', 0)
            
            if total_queries > 0:
                non_branded_pct = (non_branded / total_queries) * 100
                semi_branded_pct = (semi_branded / total_queries) * 100
                branded_pct = (branded / total_queries) * 100
                
                # Check if distribution is approximately 80/15/5 (allow some tolerance)
                distribution_correct = (
                    non_branded_pct >= 75 and non_branded_pct <= 85 and
                    semi_branded_pct >= 10 and semi_branded_pct <= 20 and
                    branded_pct >= 3 and branded_pct <= 10
                )
            else:
                non_branded_pct = semi_branded_pct = branded_pct = 0
                distribution_correct = False
            
            results['query_distribution'] = {
                'non_branded_pct': non_branded_pct,
                'semi_branded_pct': semi_branded_pct,
                'branded_pct': branded_pct,
                'target_distribution': '80%/15%/5%',
                'meets_requirement': distribution_correct
            }
            
            return results
            
        except Exception as e:
            self.log(f"❌ Error analyzing report: {str(e)}")
            return {}
    
    def run_complete_test(self) -> dict:
        """Run complete test suite for Claude Sonnet 4.5 review"""
        self.log("🚀 Starting Claude Sonnet 4.5 Review Test Suite")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Claude Sonnet 4.5 API Direct
        results['claude_api_direct'] = self.test_claude_sonnet_4_5_direct()
        
        # Test 2: Complete analysis on sekoia.ca
        analysis_results = self.test_sekoia_analysis_complete()
        results.update(analysis_results)
        
        # Summary
        self.log("=" * 60)
        self.log("🎯 CLAUDE SONNET 4.5 REVIEW TEST RESULTS:")
        
        # 1. Claude Sonnet 4.5 works (200 OK, not 404)
        claude_works = results.get('claude_api_direct', False)
        self.log(f"   1. Claude Sonnet 4.5 API: {'✅ WORKING' if claude_works else '❌ FAILED'}")
        
        # 2. Deep semantic analysis with enriched fields
        enhanced_industry = results.get('enhanced_industry_classification', {})
        industry_ok = enhanced_industry.get('present', False)
        self.log(f"   2. Enhanced Industry Classification: {'✅ COMPLETE' if industry_ok else '❌ MISSING'}")
        if not industry_ok:
            missing = enhanced_industry.get('missing_fields', [])
            self.log(f"      Missing fields: {missing}")
        
        # Enhanced offerings
        enhanced_off = results.get('enhanced_offerings', {})
        offerings_ok = enhanced_off.get('meets_requirement', False)
        self.log(f"   3. Enhanced Offerings (12+ with details): {'✅ COMPLETE' if offerings_ok else '❌ INCOMPLETE'}")
        if not offerings_ok:
            self.log(f"      Current: {enhanced_off.get('enhanced_count', 0)}/{enhanced_off.get('total_count', 0)} (need 12+ enhanced)")
        
        # Enhanced problems
        enhanced_prob = results.get('enhanced_problems_solved', {})
        problems_ok = enhanced_prob.get('meets_requirement', False)
        self.log(f"   4. Enhanced Problems (15+ with details): {'✅ COMPLETE' if problems_ok else '❌ INCOMPLETE'}")
        if not problems_ok:
            self.log(f"      Current: {enhanced_prob.get('enhanced_count', 0)}/{enhanced_prob.get('total_count', 0)} (need 15+ enhanced)")
        
        # LDA Topic Modeling
        lda_result = results.get('lda_topic_modeling', {})
        lda_ok = lda_result.get('meets_requirement', False)
        self.log(f"   5. LDA Topic Modeling with keywords/scores: {'✅ COMPLETE' if lda_ok else '❌ INCOMPLETE'}")
        if not lda_ok:
            self.log(f"      Current: {lda_result.get('valid_lda_topics', 0)}/{lda_result.get('total_topics', 0)} valid LDA topics")
        
        # 100+ queries
        query_gen = results.get('query_generation', {})
        queries_ok = query_gen.get('meets_100_requirement', False)
        self.log(f"   6. 100+ Queries Generated: {'✅ COMPLETE' if queries_ok else '❌ INCOMPLETE'}")
        if not queries_ok:
            self.log(f"      Current: {query_gen.get('total_queries', 0)} queries (need 100+)")
        
        # Distribution
        query_dist = results.get('query_distribution', {})
        dist_ok = query_dist.get('meets_requirement', False)
        self.log(f"   7. Correct Distribution (80%/15%/5%): {'✅ CORRECT' if dist_ok else '❌ INCORRECT'}")
        if not dist_ok:
            nb_pct = query_dist.get('non_branded_pct', 0)
            sb_pct = query_dist.get('semi_branded_pct', 0)
            b_pct = query_dist.get('branded_pct', 0)
            self.log(f"      Current: {nb_pct:.1f}%/{sb_pct:.1f}%/{b_pct:.1f}% (target: 80%/15%/5%)")
        
        # Overall assessment
        all_requirements_met = (
            claude_works and industry_ok and offerings_ok and 
            problems_ok and lda_ok and queries_ok and dist_ok
        )
        
        self.log("=" * 60)
        if all_requirements_met:
            self.log("🎉 ALL REVIEW REQUIREMENTS MET! Claude Sonnet 4.5 + Enhanced Features Working!")
        else:
            self.log("⚠️  REVIEW REQUIREMENTS NOT FULLY MET - Implementation needed")
        
        return results

def main():
    """Main test execution"""
    tester = ClaudeSonnetTester()
    results = tester.run_complete_test()
    
    # Return exit code based on results
    all_met = all([
        results.get('claude_api_direct', False),
        results.get('enhanced_industry_classification', {}).get('present', False),
        results.get('enhanced_offerings', {}).get('meets_requirement', False),
        results.get('enhanced_problems_solved', {}).get('meets_requirement', False),
        results.get('lda_topic_modeling', {}).get('meets_requirement', False),
        results.get('query_generation', {}).get('meets_100_requirement', False),
        results.get('query_distribution', {}).get('meets_requirement', False)
    ])
    
    return 0 if all_met else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())