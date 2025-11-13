#!/usr/bin/env python3
"""
GEO SaaS Backend API Testing Suite
Tests all API endpoints for the GEO (Generative Engine Optimization) SaaS tool
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

class GEOSaaSAPITester:
    def __init__(self, base_url="https://insight-engine-31.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[bool, Dict]:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
            
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        self.log(f"   {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json() if response.content else {}
                except:
                    response_data = {}
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json() if response.content else {}
                    self.log(f"   Error response: {error_data}")
                except:
                    self.log(f"   Raw response: {response.text[:200]}")
                response_data = {}
                
            return success, response_data
            
        except requests.exceptions.Timeout:
            self.log(f"❌ FAILED - Request timeout (30s)")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log(f"❌ FAILED - Connection error")
            return False, {}
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            return False, {}
    
    def test_root_endpoint(self) -> bool:
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET", 
            "",
            200
        )
        if success:
            self.log(f"   API Message: {response.get('message', 'N/A')}")
        return success
    
    def test_create_lead(self) -> Optional[str]:
        """Test lead creation and return lead ID"""
        test_lead_data = {
            "firstName": "Test",
            "lastName": "User", 
            "email": "test@example.com",
            "company": "Test Company",
            "url": "sekoia.ca",
            "consent": True
        }
        
        success, response = self.run_test(
            "Create Lead",
            "POST",
            "leads",
            200,
            data=test_lead_data
        )
        
        if success and 'id' in response:
            lead_id = response['id']
            self.test_data['lead_id'] = lead_id
            self.test_data['lead_data'] = response
            self.log(f"   Lead created with ID: {lead_id}")
            return lead_id
        return None
    
    def test_get_leads(self) -> bool:
        """Test getting all leads"""
        success, response = self.run_test(
            "Get All Leads",
            "GET",
            "leads", 
            200
        )
        
        if success:
            leads_count = len(response) if isinstance(response, list) else 0
            self.log(f"   Found {leads_count} leads")
            
            # Store job ID if available
            if leads_count > 0 and 'latestJob' in response[0] and response[0]['latestJob']:
                job_id = response[0]['latestJob']['id']
                self.test_data['job_id'] = job_id
                self.log(f"   Found job ID: {job_id}")
                
        return success
    
    def test_job_status(self, job_id: str) -> bool:
        """Test getting job status"""
        success, response = self.run_test(
            "Get Job Status",
            "GET",
            f"jobs/{job_id}",
            200
        )
        
        if success:
            status = response.get('status', 'unknown')
            progress = response.get('progress', 0)
            self.log(f"   Job Status: {status}, Progress: {progress}%")
            
            # Store report ID if job is completed
            if status == 'completed' and 'reportId' in response:
                report_id = response['reportId']
                self.test_data['report_id'] = report_id
                self.log(f"   Report ID: {report_id}")
                
        return success
    
    def test_get_report(self, report_id: str) -> bool:
        """Test getting a report and validate new modules"""
        success, response = self.run_test(
            "Get Report",
            "GET",
            f"reports/{report_id}",
            200
        )
        
        if success:
            url = response.get('url', 'N/A')
            global_score = response.get('scores', {}).get('global_score', 0)
            recommendations_count = len(response.get('recommendations', []))
            self.log(f"   Report for: {url}")
            self.log(f"   Global Score: {global_score}/10")
            self.log(f"   Recommendations: {recommendations_count}")
            
            # CRITICAL: Validate new modules are present
            self.validate_new_modules(response)
            
        return success
    
    def validate_new_modules(self, report_data: Dict[str, Any]) -> bool:
        """Validate that competitive intelligence, schemas, and semantic analysis are in the report"""
        self.log("🔍 Validating new modules in report...")
        
        # Test Module 3: Competitive Intelligence
        competitive_intel = report_data.get('competitive_intelligence', {})
        if competitive_intel:
            competitors_analyzed = competitive_intel.get('competitors_analyzed', 0)
            analyses = competitive_intel.get('analyses', [])
            comparative_metrics = competitive_intel.get('comparative_metrics', {})
            actionable_insights = competitive_intel.get('actionable_insights', [])
            
            self.log(f"✅ Competitive Intelligence found:")
            self.log(f"   - Competitors analyzed: {competitors_analyzed}")
            self.log(f"   - Analyses: {len(analyses)} entries")
            self.log(f"   - Comparative metrics: {'Present' if comparative_metrics else 'Missing'}")
            self.log(f"   - Actionable insights: {len(actionable_insights)} insights")
        else:
            self.log("❌ Competitive Intelligence module MISSING from report")
            return False
        
        # Test Module 4: Schema Generator
        schemas = report_data.get('schemas', {})
        if schemas:
            schema_types = list(schemas.keys())
            implementation_guide = schemas.get('implementation_guide', '')
            
            self.log(f"✅ Schema Generator found:")
            self.log(f"   - Schema types: {schema_types}")
            self.log(f"   - Implementation guide: {'Present' if implementation_guide else 'Missing'}")
            
            # Check for key schema types
            expected_schemas = ['organization', 'website', 'faq', 'article']
            for schema_type in expected_schemas:
                if schema_type in schemas:
                    self.log(f"   - {schema_type}: ✅")
                else:
                    self.log(f"   - {schema_type}: ❌ Missing")
        else:
            self.log("❌ Schema Generator module MISSING from report")
            return False
        
        # Test Module 5: Semantic Analysis & 100 Non-Branded Queries (NEW)
        semantic_analysis = report_data.get('semantic_analysis', {})
        query_breakdown = report_data.get('query_breakdown', {})
        
        if semantic_analysis:
            industry_classification = semantic_analysis.get('industry_classification', {})
            entities = semantic_analysis.get('entities', {})
            topics = semantic_analysis.get('topics', [])
            
            self.log(f"✅ Semantic Analysis found:")
            
            # Validate industry classification
            if industry_classification:
                primary_industry = industry_classification.get('primary_industry', 'unknown')
                company_type = industry_classification.get('company_type', 'unknown')
                business_model = industry_classification.get('business_model', 'unknown')
                confidence = industry_classification.get('confidence', 0)
                
                self.log(f"   - Industry detected: {primary_industry} (confidence: {confidence:.2f})")
                self.log(f"   - Company type: {company_type}")
                self.log(f"   - Business model: {business_model}")
            else:
                self.log("   - ❌ Industry classification MISSING")
                return False
            
            # Validate entities
            if entities:
                offerings = entities.get('offerings', [])
                locations = entities.get('locations', [])
                problems_solved = entities.get('problems_solved', [])
                customer_segments = entities.get('customer_segments', [])
                
                self.log(f"   - Offerings extracted: {len(offerings)} items")
                self.log(f"   - Locations found: {len(locations)} items")
                self.log(f"   - Problems solved: {len(problems_solved)} items")
                self.log(f"   - Customer segments: {len(customer_segments)} items")
                
                # Show sample offerings
                if offerings:
                    sample_offerings = [o.get('name', 'N/A') for o in offerings[:3]]
                    self.log(f"   - Sample offerings: {sample_offerings}")
            else:
                self.log("   - ❌ Entities MISSING")
                return False
            
            # Validate topics
            self.log(f"   - Topics identified: {len(topics)} items")
            
        else:
            self.log("❌ Semantic Analysis module MISSING from report")
            return False
        
        # Validate query breakdown
        if query_breakdown:
            non_branded = query_breakdown.get('non_branded', 0)
            semi_branded = query_breakdown.get('semi_branded', 0)
            branded = query_breakdown.get('branded', 0)
            total = query_breakdown.get('total', 0)
            
            self.log(f"✅ Query Breakdown found:")
            self.log(f"   - Non-branded queries: {non_branded}")
            self.log(f"   - Semi-branded queries: {semi_branded}")
            self.log(f"   - Branded queries: {branded}")
            self.log(f"   - Total queries: {total}")
            
            # Validate the 80/15/5 distribution
            if total >= 100:
                non_branded_pct = (non_branded / total) * 100
                semi_branded_pct = (semi_branded / total) * 100
                branded_pct = (branded / total) * 100
                
                self.log(f"   - Distribution: {non_branded_pct:.1f}% / {semi_branded_pct:.1f}% / {branded_pct:.1f}%")
                
                # Check if distribution is approximately 80/15/5
                if non_branded_pct >= 70 and semi_branded_pct >= 10 and branded_pct >= 3:
                    self.log(f"   - ✅ Distribution is correct (target: 80%/15%/5%)")
                else:
                    self.log(f"   - ⚠️  Distribution may be off target (expected ~80%/15%/5%)")
            else:
                self.log(f"   - ⚠️  Total queries ({total}) is less than expected 100")
        else:
            self.log("❌ Query Breakdown MISSING from report")
            return False
        
        # Test existing modules are still present
        visibility_results = report_data.get('visibility_results', {})
        if visibility_results:
            overall_visibility = visibility_results.get('overall_visibility', 0)
            platform_scores = visibility_results.get('platform_scores', {})
            self.log(f"✅ Visibility Results: {overall_visibility:.1%} overall")
            self.log(f"   - Platform scores: {list(platform_scores.keys())}")
        else:
            self.log("❌ Visibility Results MISSING")
            return False
        
        scores = report_data.get('scores', {})
        if scores:
            self.log(f"✅ Scores present: {len(scores)} criteria")
        else:
            self.log("❌ Scores MISSING")
            return False
        
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            self.log(f"✅ Recommendations: {len(recommendations)} items")
        else:
            self.log("❌ Recommendations MISSING")
            return False
        
        # Validate test queries are present and count is correct
        test_queries = report_data.get('test_queries', [])
        if test_queries:
            self.log(f"✅ Test Queries: {len(test_queries)} queries generated")
            
            # Show sample queries to verify they are non-branded
            if len(test_queries) >= 5:
                sample_queries = test_queries[:5]
                self.log(f"   - Sample queries: {sample_queries}")
                
                # Check if queries look non-branded (simple heuristic)
                company_name = entities.get('company_info', {}).get('name', '') if entities else ''
                if company_name:
                    branded_count = sum(1 for q in sample_queries if company_name.lower() in q.lower())
                    if branded_count <= 1:  # At most 1 branded in first 5 (which should be mostly non-branded)
                        self.log(f"   - ✅ Queries appear to be mostly non-branded")
                    else:
                        self.log(f"   - ⚠️  {branded_count}/5 sample queries contain company name")
        else:
            self.log("❌ Test Queries MISSING")
            return False
        
        self.log("✅ All modules validation completed")
        return True
    
    def test_download_docx(self, report_id: str) -> bool:
        """Test DOCX download"""
        url = f"{self.api_url}/reports/{report_id}/docx"
        self.tests_run += 1
        self.log(f"🔍 Testing DOCX Download...")
        self.log(f"   GET {url}")
        
        try:
            response = requests.get(url, timeout=30)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                self.log(f"✅ PASSED - Status: {response.status_code}")
                self.log(f"   Content-Type: {content_type}")
                self.log(f"   Content-Length: {content_length} bytes")
            else:
                self.log(f"❌ FAILED - Status: {response.status_code}")
                
            return success
            
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            return False
    
    def test_download_dashboard(self, report_id: str) -> bool:
        """Test HTML Dashboard download"""
        url = f"{self.api_url}/reports/{report_id}/dashboard"
        self.tests_run += 1
        self.log(f"🔍 Testing HTML Dashboard...")
        self.log(f"   GET {url}")
        
        try:
            response = requests.get(url, timeout=30)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                self.log(f"✅ PASSED - Status: {response.status_code}")
                self.log(f"   Content-Type: {content_type}")
                self.log(f"   Content-Length: {content_length} bytes")
                
                # Check if it's actually HTML
                if 'html' in content_type.lower():
                    self.log(f"   ✅ Valid HTML dashboard")
                else:
                    self.log(f"   ⚠️  Content type not HTML: {content_type}")
            else:
                self.log(f"❌ FAILED - Status: {response.status_code}")
                
            return success
            
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            return False

    def test_download_pdf(self, report_id: str) -> bool:
        """Test PDF download"""
        url = f"{self.api_url}/reports/{report_id}/pdf"
        self.tests_run += 1
        self.log(f"🔍 Testing PDF Download...")
        self.log(f"   GET {url}")
        
        try:
            response = requests.get(url, timeout=30)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                self.log(f"✅ PASSED - Status: {response.status_code}")
                self.log(f"   Content-Type: {content_type}")
                self.log(f"   Content-Length: {content_length} bytes")
            else:
                self.log(f"❌ FAILED - Status: {response.status_code}")
                
            return success
            
        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}")
            return False
    
    def wait_for_job_completion(self, job_id: str, max_wait_time: int = 300) -> Optional[str]:
        """Wait for analysis job to complete and return report ID"""
        self.log(f"⏳ Waiting for job {job_id} to complete (max {max_wait_time}s)...")
        self.log(f"   This may take 3-5 minutes for complete pipeline processing...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            success, response = self.run_test(
                "Poll Job Status",
                "GET",
                f"jobs/{job_id}",
                200
            )
            
            if not success:
                return None
                
            status = response.get('status', 'unknown')
            progress = response.get('progress', 0)
            
            if status == 'completed':
                report_id = response.get('reportId')
                self.log(f"✅ Job completed! Report ID: {report_id}")
                return report_id
            elif status == 'failed':
                error = response.get('error', 'Unknown error')
                self.log(f"❌ Job failed: {error}")
                return None
            else:
                self.log(f"   Status: {status}, Progress: {progress}%")
                time.sleep(10)  # Wait 10 seconds before next poll
                
        self.log(f"⏰ Job did not complete within {max_wait_time} seconds")
        return None
    
    def test_claude_api_directly(self) -> bool:
        """Test Claude API directly to verify new key works"""
        self.log("🔍 Testing Claude API directly with new key...")
        
        try:
            import os
            from anthropic import Anthropic
            
            # Test the API key
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                self.log("❌ ANTHROPIC_API_KEY not found in environment")
                return False
            
            self.log(f"   Using API key: {api_key[:20]}...")
            
            client = Anthropic(api_key=api_key)
            
            # Test claude-3-5-sonnet-20241022 specifically
            self.log("   Testing claude-3-5-sonnet-20241022...")
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{
                    "role": "user", 
                    "content": "Test message: respond with 'Claude 3.5 Sonnet working' if you receive this."
                }]
            )
            
            response_text = response.content[0].text
            self.log(f"✅ Claude 3.5 Sonnet response: {response_text}")
            
            if "working" in response_text.lower():
                self.log("✅ Claude 3.5 Sonnet API is functional!")
                return True
            else:
                self.log("⚠️  Claude responded but message unclear")
                return True
                
        except Exception as e:
            self.log(f"❌ Claude API test failed: {str(e)}")
            return False
    
    def test_semantic_analysis_enhanced_features(self, report_data: Dict[str, Any]) -> bool:
        """Test enhanced semantic analysis features specifically requested in review"""
        self.log("🔍 Testing ENHANCED semantic analysis features...")
        
        semantic_analysis = report_data.get('semantic_analysis', {})
        if not semantic_analysis:
            self.log("❌ No semantic analysis found in report")
            return False
        
        # Test enhanced industry classification
        industry_classification = semantic_analysis.get('industry_classification', {})
        
        required_fields = ['sub_industry', 'positioning', 'maturity', 'geographic_scope', 'reasoning']
        missing_fields = []
        
        for field in required_fields:
            value = industry_classification.get(field)
            if not value or value == "N/A" or value is None:
                missing_fields.append(field)
        
        if missing_fields:
            self.log(f"❌ ENHANCED industry classification MISSING fields: {missing_fields}")
            self.log(f"   Current fields: {list(industry_classification.keys())}")
            return False
        else:
            self.log("✅ Enhanced industry classification complete")
            self.log(f"   - sub_industry: {industry_classification.get('sub_industry')}")
            self.log(f"   - positioning: {industry_classification.get('positioning')}")
            self.log(f"   - maturity: {industry_classification.get('maturity')}")
            self.log(f"   - geographic_scope: {industry_classification.get('geographic_scope')}")
        
        # Test enhanced offerings (12 items with description, target_segment, priority)
        entities = semantic_analysis.get('entities', {})
        offerings = entities.get('offerings', [])
        
        if len(offerings) < 12:
            self.log(f"❌ ENHANCED offerings: Only {len(offerings)} found, need 12")
            return False
        
        enhanced_offerings_valid = True
        for i, offering in enumerate(offerings[:3]):  # Check first 3
            if not isinstance(offering, dict):
                self.log(f"❌ Offering {i+1} is not a dict: {type(offering)}")
                enhanced_offerings_valid = False
                continue
                
            required_offering_fields = ['description', 'target_segment', 'priority']
            for field in required_offering_fields:
                if field not in offering or not offering[field] or offering[field] == "N/A":
                    self.log(f"❌ Offering {i+1} missing {field}: {offering}")
                    enhanced_offerings_valid = False
        
        if enhanced_offerings_valid:
            self.log(f"✅ Enhanced offerings complete: {len(offerings)} items with full details")
        
        # Test enhanced problems_solved (15 items with category, severity, solution_approach)
        problems_solved = entities.get('problems_solved', [])
        
        if len(problems_solved) < 15:
            self.log(f"❌ ENHANCED problems_solved: Only {len(problems_solved)} found, need 15")
            return False
        
        enhanced_problems_valid = True
        for i, problem in enumerate(problems_solved[:3]):  # Check first 3
            if not isinstance(problem, dict):
                self.log(f"❌ Problem {i+1} is not a dict: {type(problem)}")
                enhanced_problems_valid = False
                continue
                
            required_problem_fields = ['category', 'severity', 'solution_approach']
            for field in required_problem_fields:
                if field not in problem or not problem[field] or problem[field] == "N/A":
                    self.log(f"❌ Problem {i+1} missing {field}: {problem}")
                    enhanced_problems_valid = False
        
        if enhanced_problems_valid:
            self.log(f"✅ Enhanced problems_solved complete: {len(problems_solved)} items with full details")
        
        # Test REAL LDA Topic Modeling with keywords and scores
        topics = semantic_analysis.get('topics', [])
        
        if not topics:
            self.log("❌ No topics found - LDA Topic Modeling missing")
            return False
        
        lda_valid = True
        for i, topic in enumerate(topics[:2]):  # Check first 2
            if not isinstance(topic, dict):
                self.log(f"❌ Topic {i+1} is not a dict")
                lda_valid = False
                continue
                
            required_topic_fields = ['keywords', 'top_words_scores']
            for field in required_topic_fields:
                if field not in topic or not topic[field]:
                    self.log(f"❌ Topic {i+1} missing {field}: {topic}")
                    lda_valid = False
        
        if lda_valid:
            self.log(f"✅ REAL LDA Topic Modeling complete: {len(topics)} topics with keywords and scores")
        
        # Overall validation
        all_enhanced_features = (
            not missing_fields and 
            enhanced_offerings_valid and 
            enhanced_problems_valid and 
            lda_valid
        )
        
        if all_enhanced_features:
            self.log("✅ ALL ENHANCED SEMANTIC ANALYSIS FEATURES COMPLETE!")
            return True
        else:
            self.log("❌ ENHANCED SEMANTIC ANALYSIS FEATURES INCOMPLETE")
            return False
    
    def test_query_generation_requirements(self, report_data: Dict[str, Any]) -> bool:
        """Test 100+ queries with 80%/15%/5% distribution"""
        self.log("🔍 Testing query generation requirements...")
        
        query_breakdown = report_data.get('query_breakdown', {})
        test_queries = report_data.get('test_queries', [])
        
        if not query_breakdown:
            self.log("❌ No query_breakdown found")
            return False
        
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
            return False
        else:
            self.log(f"✅ Quantity requirement met: {total_queries} >= 100")
        
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
                return True
            else:
                self.log(f"❌ DISTRIBUTION REQUIREMENT FAILED: Expected ~80%/15%/5%, got {non_branded_pct:.1f}%/{semi_branded_pct:.1f}%/{branded_pct:.1f}%")
                return False
        
        return False

    def run_comprehensive_test(self) -> int:
        """Run comprehensive API test suite with focus on review requirements"""
        self.log("🚀 Starting GEO SaaS API Test Suite - CLAUDE 3.5 SONNET REVIEW")
        self.log("=" * 60)
        
        # PRIORITY TEST: Claude API Direct Test
        self.log("🎯 PRIORITY: Testing Claude 3.5 Sonnet API directly...")
        claude_api_works = self.test_claude_api_directly()
        
        # Test 1: Root endpoint
        if not self.test_root_endpoint():
            self.log("❌ Root endpoint failed - stopping tests")
            return 1
            
        # Test 2: Create lead (this also starts analysis job)
        lead_id = self.test_create_lead()
        if not lead_id:
            self.log("❌ Lead creation failed - stopping tests")
            return 1
            
        # Test 3: Get all leads (to get job ID)
        if not self.test_get_leads():
            self.log("❌ Get leads failed")
            
        # Test 4: Check job status
        job_id = self.test_data.get('job_id')
        if job_id:
            self.test_job_status(job_id)
            
            # Test 5: Wait for job completion (with timeout)
            self.log("⏳ Waiting for COMPLETE ANALYSIS with enhanced semantic features...")
            report_id = self.wait_for_job_completion(job_id, max_wait_time=400)  # 6+ minutes for full pipeline
            
            if report_id:
                # Test 6: Get report and validate ALL modules
                if self.test_get_report(report_id):
                    
                    # Get report data for enhanced testing
                    success, report_data = self.run_test(
                        "Get Report Data for Enhanced Testing",
                        "GET",
                        f"reports/{report_id}",
                        200
                    )
                    
                    if success:
                        # PRIORITY TESTS: Enhanced Semantic Analysis
                        self.log("🎯 PRIORITY: Testing ENHANCED semantic analysis features...")
                        enhanced_features_ok = self.test_semantic_analysis_enhanced_features(report_data)
                        
                        # PRIORITY TESTS: Query Generation Requirements
                        self.log("🎯 PRIORITY: Testing 100+ queries with 80%/15%/5% distribution...")
                        query_requirements_ok = self.test_query_generation_requirements(report_data)
                        
                        # Store priority test results
                        self.test_data['claude_api_works'] = claude_api_works
                        self.test_data['enhanced_features_ok'] = enhanced_features_ok
                        self.test_data['query_requirements_ok'] = query_requirements_ok
                    
                    # Test 7: Download DOCX (Word Report)
                    self.test_download_docx(report_id)
                    # Test 8: Download HTML Dashboard
                    self.test_download_dashboard(report_id)
                    # Test 9: Download PDF (legacy)
                    self.test_download_pdf(report_id)
                else:
                    self.log("❌ Get report failed")
            else:
                self.log("⚠️  Job did not complete in time - skipping report tests")
        else:
            self.log("⚠️  No job ID found - skipping job-related tests")
            
        # Final results with PRIORITY focus
        self.log("=" * 60)
        self.log("🎯 PRIORITY TEST RESULTS:")
        self.log(f"   Claude 3.5 Sonnet API: {'✅ WORKING' if self.test_data.get('claude_api_works') else '❌ FAILED'}")
        self.log(f"   Enhanced Semantic Analysis: {'✅ COMPLETE' if self.test_data.get('enhanced_features_ok') else '❌ INCOMPLETE'}")
        self.log(f"   100+ Queries (80%/15%/5%): {'✅ CORRECT' if self.test_data.get('query_requirements_ok') else '❌ INCORRECT'}")
        
        self.log("=" * 60)
        self.log(f"📊 Overall Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        # Determine success based on priority tests
        priority_tests_passed = (
            self.test_data.get('claude_api_works', False) and
            self.test_data.get('enhanced_features_ok', False) and
            self.test_data.get('query_requirements_ok', False)
        )
        
        if priority_tests_passed:
            self.log("🎉 ALL PRIORITY TESTS PASSED! Claude 3.5 Sonnet + Enhanced Features Working!")
            return 0
        else:
            self.log("⚠️  PRIORITY TESTS FAILED - Review requirements not met")
            return 1

def main():
    """Main test execution"""
    tester = GEOSaaSAPITester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())