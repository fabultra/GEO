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
    def __init__(self, base_url="https://ai-seo-toolkit-1.preview.emergentagent.com"):
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
        """Validate that competitive intelligence and schemas are in the report"""
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
        
        self.log("✅ All modules validation completed")
        return True
    
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
    
    def run_comprehensive_test(self) -> int:
        """Run comprehensive API test suite"""
        self.log("🚀 Starting GEO SaaS API Test Suite")
        self.log("=" * 50)
        
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
            report_id = self.wait_for_job_completion(job_id, max_wait_time=180)  # 3 minutes max
            
            if report_id:
                # Test 6: Get report
                if self.test_get_report(report_id):
                    # Test 7: Download PDF
                    self.test_download_pdf(report_id)
                else:
                    self.log("❌ Get report failed")
            else:
                self.log("⚠️  Job did not complete in time - skipping report tests")
        else:
            self.log("⚠️  No job ID found - skipping job-related tests")
            
        # Final results
        self.log("=" * 50)
        self.log(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed!")
            return 0
        else:
            failure_rate = ((self.tests_run - self.tests_passed) / self.tests_run) * 100
            self.log(f"⚠️  {failure_rate:.1f}% of tests failed")
            return 1

def main():
    """Main test execution"""
    tester = GEOSaaSAPITester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    sys.exit(main())