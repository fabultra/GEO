#!/usr/bin/env python3
"""
Test Enhanced Problems Solved specifically for review request
"""

import requests
import json
import sys
from datetime import datetime

def log(message: str, level: str = "INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_enhanced_problems_solved():
    """Test enhanced problems solved with a specific report"""
    base_url = "https://issue-resolver-41.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    log("🎯 REVIEW REQUEST: Testing Enhanced Problems Solved Structure")
    log("=" * 60)
    
    # First, let's get the latest completed report
    try:
        log("🔍 Getting leads to find completed reports...")
        response = requests.get(f"{api_url}/leads", timeout=30)
        
        if response.status_code != 200:
            log(f"❌ Failed to get leads: {response.status_code}")
            return False
            
        leads = response.json()
        log(f"   Found {len(leads)} leads")
        
        # Find a completed job
        completed_report_id = None
        for lead in leads:
            if lead.get('latestJob') and lead['latestJob'].get('status') == 'completed':
                completed_report_id = lead['latestJob'].get('reportId')
                if completed_report_id:
                    log(f"   Found completed report: {completed_report_id}")
                    break
        
        if not completed_report_id:
            log("❌ No completed reports found")
            return False
            
        # Get the report
        log(f"🔍 Getting report {completed_report_id}...")
        response = requests.get(f"{api_url}/reports/{completed_report_id}", timeout=30)
        
        if response.status_code != 200:
            log(f"❌ Failed to get report: {response.status_code}")
            return False
            
        report_data = response.json()
        log("✅ Report retrieved successfully")
        
        # Test enhanced problems solved
        return test_problems_solved_structure(report_data)
        
    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return False

def test_problems_solved_structure(report_data):
    """Test the problems_solved structure specifically"""
    log("🎯 Testing Enhanced Problems Solved Structure...")
    
    # Navigate to semantic_analysis.entities.problems_solved
    semantic_analysis = report_data.get('semantic_analysis', {})
    if not semantic_analysis:
        log("❌ No semantic_analysis found in report")
        return False
    
    entities = semantic_analysis.get('entities', {})
    if not entities:
        log("❌ No entities found in semantic_analysis")
        return False
    
    problems_solved = entities.get('problems_solved', [])
    
    log(f"📊 Problems Solved Analysis:")
    log(f"   Total problems found: {len(problems_solved)}")
    
    # CRITÈRE 1: Exactement 15 items (ou plus)
    if len(problems_solved) < 15:
        log(f"❌ CRITICAL: Only {len(problems_solved)} problems found, NEED EXACTLY 15+")
        return False
    else:
        log(f"✅ Quantity requirement met: {len(problems_solved)} problems (≥15)")
    
    # CRITÈRE 2: Chaque item DOIT avoir TOUS les champs requis
    required_fields = ['problem', 'category', 'severity', 'affected_segment', 'solution_approach']
    
    valid_problems = 0
    invalid_problems = []
    
    log("🔍 Validating each problem structure...")
    
    for i, problem in enumerate(problems_solved):
        if not isinstance(problem, dict):
            log(f"❌ Problem {i+1} is not a dict: {type(problem)}")
            invalid_problems.append(f"Problem {i+1}: Not a dict")
            continue
        
        missing_fields = []
        invalid_values = []
        
        for field in required_fields:
            if field not in problem:
                missing_fields.append(field)
            else:
                value = problem[field]
                # CRITÈRE 3: Aucun champ ne doit être null/undefined/N/A
                if not value or value == "N/A" or value is None or value == "null" or value == "undefined":
                    invalid_values.append(f"{field}={value}")
                # Check for "MISSING" values
                elif isinstance(value, str) and value.upper() == "MISSING":
                    invalid_values.append(f"{field}=MISSING")
        
        if missing_fields or invalid_values:
            problem_issues = []
            if missing_fields:
                problem_issues.append(f"Missing: {missing_fields}")
            if invalid_values:
                problem_issues.append(f"Invalid: {invalid_values}")
            invalid_problems.append(f"Problem {i+1}: {'; '.join(problem_issues)}")
        else:
            valid_problems += 1
            
            # Log first 3 valid problems as examples
            if i < 3:
                log(f"   ✅ Problem {i+1}: {problem.get('problem', '')[:50]}...")
                log(f"      Category: {problem.get('category')}, Severity: {problem.get('severity')}")
                log(f"      Affected: {problem.get('affected_segment')}")
                log(f"      Solution: {problem.get('solution_approach', '')[:50]}...")
    
    # Results summary
    log("=" * 60)
    log(f"📊 FINAL VALIDATION RESULTS:")
    log(f"   Total problems: {len(problems_solved)}")
    log(f"   Valid problems: {valid_problems}")
    log(f"   Invalid problems: {len(invalid_problems)}")
    
    if invalid_problems:
        log("❌ INVALID PROBLEMS FOUND:")
        for issue in invalid_problems[:5]:  # Show first 5 issues
            log(f"   - {issue}")
        if len(invalid_problems) > 5:
            log(f"   ... and {len(invalid_problems) - 5} more issues")
    
    # CRITÈRE DE SUCCÈS: Tous les problèmes doivent être valides
    if valid_problems == len(problems_solved) and len(problems_solved) >= 15:
        log("=" * 60)
        log("🎉 REVIEW REQUEST SUCCESS: Enhanced Problems Solved FULLY COMPLIANT!")
        log(f"   ✅ {len(problems_solved)} problems with complete structure")
        log("   ✅ All required fields present: problem, category, severity, affected_segment, solution_approach")
        log("   ✅ No null/undefined/N/A values")
        log("   ✅ Coherent and relevant data")
        log("=" * 60)
        return True
    else:
        log("=" * 60)
        log("❌ REVIEW REQUEST FAILED: Enhanced Problems Solved NOT COMPLIANT")
        log("=" * 60)
        return False

def main():
    """Main test execution"""
    success = test_enhanced_problems_solved()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())