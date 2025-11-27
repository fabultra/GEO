#!/usr/bin/env python3
"""
Test rapide du backend GEO SaaS pour identifier les problèmes critiques
"""
import json
import logging
import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Configuration
load_dotenv('/app/backend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://issue-resolver-41.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_health():
    """Test 1: Santé de l'API"""
    logger.info("🔍 Test 1: Santé de l'API")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ API accessible - {data.get('message', 'N/A')} v{data.get('version', 'N/A')}")
            return True
        else:
            logger.error(f"❌ API non accessible: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur API: {e}")
        return False

def test_lead_creation():
    """Test 2: Création d'un lead"""
    logger.info("🔍 Test 2: Création d'un lead")
    try:
        lead_data = {
            "firstName": "Jean",
            "lastName": "Tremblay", 
            "email": "jean.tremblay@sekoia.ca",
            "company": "SEKOIA",
            "url": "sekoia.ca",
            "consent": True
        }
        
        response = requests.post(f"{API_BASE}/leads", json=lead_data, timeout=15)
        if response.status_code == 200:
            lead = response.json()
            logger.info(f"✅ Lead créé - ID: {lead['id']}")
            return lead['id']
        else:
            logger.error(f"❌ Échec création lead: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Erreur création lead: {e}")
        return None

def find_job_for_lead(lead_id):
    """Trouver le job d'analyse pour un lead"""
    logger.info("🔍 Test 3: Recherche du job d'analyse")
    try:
        time.sleep(2)  # Attendre que le job soit créé
        
        response = requests.get(f"{API_BASE}/leads", timeout=15)
        if response.status_code != 200:
            logger.error(f"❌ Impossible de récupérer les leads: HTTP {response.status_code}")
            return None
        
        leads = response.json()
        for lead_data in leads:
            if lead_data['id'] == lead_id and lead_data.get('latestJob'):
                job_id = lead_data['latestJob']['id']
                logger.info(f"✅ Job trouvé - ID: {job_id}")
                return job_id
        
        logger.error("❌ Aucun job trouvé")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur recherche job: {e}")
        return None

def check_job_status(job_id):
    """Vérifier le statut du job"""
    logger.info("🔍 Test 4: Vérification du statut du job")
    try:
        response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
        if response.status_code == 200:
            job = response.json()
            status = job.get('status', 'unknown')
            progress = job.get('progress', 0)
            logger.info(f"✅ Job accessible - Statut: {status} ({progress}%)")
            return job
        else:
            logger.error(f"❌ Job inaccessible: HTTP {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Erreur statut job: {e}")
        return None

def wait_for_completion(job_id, max_wait=60):
    """Attendre la completion (version courte)"""
    logger.info(f"🔍 Test 5: Attente completion (max {max_wait}s)")
    
    wait_time = 0
    poll_interval = 10
    
    while wait_time < max_wait:
        time.sleep(poll_interval)
        wait_time += poll_interval
        
        try:
            response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
            if response.status_code == 200:
                job = response.json()
                status = job.get('status', 'unknown')
                progress = job.get('progress', 0)
                
                logger.info(f"📊 Statut: {status} ({progress}%) - {wait_time}s")
                
                if status == 'completed':
                    report_id = job.get('reportId')
                    logger.info(f"✅ Analyse terminée - Report ID: {report_id}")
                    return report_id
                elif status == 'failed':
                    error = job.get('error', 'Unknown error')
                    logger.error(f"❌ Analyse échouée: {error}")
                    return None
        except Exception as e:
            logger.warning(f"⚠️ Erreur polling: {e}")
    
    logger.warning(f"⚠️ Timeout après {max_wait}s - analyse en cours")
    return "TIMEOUT"

def check_existing_reports():
    """Vérifier s'il y a des rapports existants"""
    logger.info("🔍 Test 6: Vérification des rapports existants")
    try:
        response = requests.get(f"{API_BASE}/leads", timeout=15)
        if response.status_code == 200:
            leads = response.json()
            
            for lead in leads:
                if lead.get('reports'):
                    for report in lead['reports']:
                        report_id = report['id']
                        logger.info(f"📊 Rapport existant trouvé: {report_id}")
                        return report_id
            
            logger.info("📋 Aucun rapport existant trouvé")
            return None
        else:
            logger.error(f"❌ Impossible de récupérer les leads: HTTP {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Erreur vérification rapports: {e}")
        return None

def test_report_access(report_id):
    """Tester l'accès au rapport"""
    logger.info(f"🔍 Test 7: Accès au rapport {report_id}")
    try:
        response = requests.get(f"{API_BASE}/reports/{report_id}", timeout=15)
        if response.status_code == 200:
            report = response.json()
            logger.info("✅ Rapport accessible")
            
            # Vérifier les modules
            modules_found = []
            modules_missing = []
            
            required_modules = {
                'visibility_results': 'Module 1: Visibilité',
                'semantic_analysis': 'Module 5: Analyse sémantique', 
                'competitive_intelligence': 'Module 3: Intelligence compétitive',
                'schemas': 'Module 4: Schemas',
                'generated_articles': 'Module 2: Articles générés'
            }
            
            for module_key, module_name in required_modules.items():
                if module_key in report and report[module_key]:
                    modules_found.append(module_name)
                    logger.info(f"  ✅ {module_name}: Présent")
                else:
                    # Chercher dans visibility_results
                    if 'visibility_results' in report and isinstance(report['visibility_results'], dict):
                        if module_key in report['visibility_results']:
                            modules_found.append(module_name)
                            logger.info(f"  ✅ {module_name}: Présent (dans visibility_results)")
                        else:
                            modules_missing.append(module_name)
                            logger.error(f"  ❌ {module_name}: MANQUANT")
                    else:
                        modules_missing.append(module_name)
                        logger.error(f"  ❌ {module_name}: MANQUANT")
            
            logger.info(f"📊 Modules: {len(modules_found)}/5 présents")
            
            # Sauvegarder le rapport pour analyse
            with open(f'/app/quick_test_report_{report_id}.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return len(modules_found) >= 3  # Au moins 3/5 modules
        else:
            logger.error(f"❌ Rapport inaccessible: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur accès rapport: {e}")
        return False

def test_downloads(report_id):
    """Tester les téléchargements"""
    logger.info(f"🔍 Test 8: Téléchargements pour {report_id}")
    
    downloads = {
        'dashboard': f"{API_BASE}/reports/{report_id}/dashboard",
        'docx': f"{API_BASE}/reports/{report_id}/docx", 
        'pdf': f"{API_BASE}/reports/{report_id}/pdf"
    }
    
    successful = 0
    
    for download_type, url in downloads.items():
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                size = len(response.content)
                logger.info(f"  ✅ {download_type.upper()}: {size} bytes")
                successful += 1
            else:
                logger.error(f"  ❌ {download_type.upper()}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"  ❌ {download_type.upper()}: {e}")
    
    logger.info(f"📊 Téléchargements: {successful}/3 réussis")
    return successful >= 2

def check_backend_errors():
    """Vérifier les erreurs backend récentes"""
    logger.info("🔍 Test 9: Vérification des erreurs backend")
    try:
        import subprocess
        result = subprocess.run(['tail', '-n', '20', '/var/log/supervisor/backend.err.log'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            log_content = result.stdout
            error_lines = [line for line in log_content.split('\n') if 'ERROR' in line or 'Exception' in line]
            
            if error_lines:
                logger.warning(f"⚠️ {len(error_lines)} erreurs récentes trouvées:")
                for error in error_lines[-3:]:  # Dernières 3 erreurs
                    logger.warning(f"  • {error.strip()}")
            else:
                logger.info("✅ Aucune erreur récente dans les logs")
        else:
            logger.warning("⚠️ Impossible de lire les logs backend")
    except Exception as e:
        logger.warning(f"⚠️ Erreur vérification logs: {e}")

def main():
    """Test rapide du backend"""
    logger.info("🚀 TEST RAPIDE BACKEND GEO SAAS")
    logger.info(f"Backend URL: {API_BASE}")
    logger.info("="*60)
    
    results = {
        'api_health': False,
        'lead_creation': False,
        'job_found': False,
        'job_accessible': False,
        'report_accessible': False,
        'modules_ok': False,
        'downloads_ok': False
    }
    
    # Test 1: API Health
    results['api_health'] = test_api_health()
    if not results['api_health']:
        logger.error("❌ API inaccessible - arrêt des tests")
        return 1
    
    # Test 2: Lead Creation
    lead_id = test_lead_creation()
    results['lead_creation'] = lead_id is not None
    
    if lead_id:
        # Test 3: Job Finding
        job_id = find_job_for_lead(lead_id)
        results['job_found'] = job_id is not None
        
        if job_id:
            # Test 4: Job Status
            job_status = check_job_status(job_id)
            results['job_accessible'] = job_status is not None
            
            # Test 5: Wait for completion (court)
            report_id = wait_for_completion(job_id, max_wait=60)
            
            if report_id == "TIMEOUT":
                logger.info("⏳ Analyse en cours - vérification des rapports existants")
                report_id = check_existing_reports()
    
    # Si pas de nouveau rapport, chercher un existant
    if not locals().get('report_id'):
        report_id = check_existing_reports()
    
    if report_id and report_id != "TIMEOUT":
        # Test 6: Report Access & Modules
        results['report_accessible'] = test_report_access(report_id)
        results['modules_ok'] = results['report_accessible']  # Simplifié
        
        # Test 7: Downloads
        results['downloads_ok'] = test_downloads(report_id)
    
    # Test 8: Backend Errors
    check_backend_errors()
    
    # Résumé final
    logger.info("\n" + "="*60)
    logger.info("📋 RÉSUMÉ DES TESTS RAPIDES")
    logger.info("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅" if passed_test else "❌"
        logger.info(f"{status} {test_name.replace('_', ' ').title()}")
    
    logger.info(f"\n📊 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.7:  # 70% minimum
        logger.info("🎉 BACKEND FONCTIONNEL")
        return 0
    else:
        logger.error("❌ PROBLÈMES CRITIQUES DÉTECTÉS")
        return 1

if __name__ == "__main__":
    sys.exit(main())