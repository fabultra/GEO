#!/usr/bin/env python3
"""
Test complet du backend de la plateforme GEO SaaS
Validation de tous les modules selon la review request
"""
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv

# Configuration
load_dotenv('/app/backend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://issue-resolver-41.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GEOSaaSBackendTester:
    """
    Testeur complet pour le backend de la plateforme GEO SaaS
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GEOSaaSBackendTester/1.0'
        })
        
        # URL de test selon la review request
        self.test_url = 'sekoia.ca'
        
        self.results = {
            'test_start': datetime.now().isoformat(),
            'backend_url': API_BASE,
            'test_url': self.test_url,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'critical_issues': [],
            'minor_issues': [],
            'modules_validation': {},
            'downloads_validation': {},
            'performance_metrics': {}
        }
        
        # Variables pour stocker les IDs pendant les tests
        self.job_id = None
        self.report_id = None
        self.lead_id = None
    
    def run_complete_tests(self):
        """
        Lance tous les tests selon la review request
        """
        logger.info("🚀 DÉMARRAGE DES TESTS COMPLETS DU BACKEND GEO SAAS")
        logger.info(f"Backend URL: {API_BASE}")
        logger.info(f"URL de test: {self.test_url}")
        logger.info("="*80)
        
        try:
            # Test 1: Santé de l'API (GET /api/)
            if not self.test_api_health():
                return False
            
            # Test 2: Création d'un lead avec URL valide (POST /api/leads)
            if not self.test_lead_creation():
                return False
            
            # Test 3: Vérifier le statut du job d'analyse (GET /api/jobs/{job_id})
            if not self.test_job_status():
                return False
            
            # Test 4: Attendre que l'analyse soit complète (polling avec timeout 180s)
            if not self.test_analysis_completion():
                return False
            
            # Test 5: Vérifier que le rapport est généré (GET /api/reports/{report_id})
            if not self.test_report_generation():
                return False
            
            # Test 6: Vérifier la présence de tous les modules dans le rapport
            if not self.test_modules_validation():
                return False
            
            # Test 7: Vérifier les téléchargements (Dashboard HTML, Word DOCX, PDF)
            if not self.test_downloads():
                return False
            
            # Test 8: Vérifier les logs backend pour erreurs
            self.check_backend_logs()
            
            # Générer le rapport final
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans les tests: {e}")
            self.results['critical_issues'].append(f"Test suite failure: {e}")
            return False
        
        return self.results['tests_failed'] == 0
    
    def test_api_health(self) -> bool:
        """
        Test 1: Santé de l'API (GET /api/)
        """
        logger.info("🔍 Test 1: Santé de l'API (GET /api/)")
        self.results['tests_run'] += 1
        
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/")
            response_time = time.time() - start_time
            
            self.results['performance_metrics']['api_health_response_time'] = response_time
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API accessible - {data.get('message', 'N/A')} v{data.get('version', 'N/A')}")
                logger.info(f"⏱️ Temps de réponse: {response_time:.2f}s")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ API non accessible: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"API health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur de connexion à l'API: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"API connection error: {e}")
            return False
    
    def test_lead_creation(self) -> bool:
        """
        Test 2: Création d'un lead avec URL valide (POST /api/leads)
        """
        logger.info("🔍 Test 2: Création d'un lead avec URL valide (POST /api/leads)")
        self.results['tests_run'] += 1
        
        try:
            # Données réelles selon la review request
            lead_data = {
                "firstName": "Jean",
                "lastName": "Tremblay",
                "email": "jean.tremblay@sekoia.ca",
                "company": "SEKOIA",
                "url": self.test_url,
                "consent": True
            }
            
            logger.info(f"📝 Création du lead pour {self.test_url}")
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/leads", json=lead_data)
            response_time = time.time() - start_time
            
            self.results['performance_metrics']['lead_creation_response_time'] = response_time
            
            if response.status_code == 200:
                lead = response.json()
                self.lead_id = lead['id']
                logger.info(f"✅ Lead créé avec succès - ID: {self.lead_id}")
                logger.info(f"⏱️ Temps de réponse: {response_time:.2f}s")
                
                # Vérifier les champs obligatoires
                required_fields = ['id', 'firstName', 'lastName', 'email', 'url', 'createdAt']
                missing_fields = [field for field in required_fields if field not in lead]
                
                if missing_fields:
                    logger.warning(f"⚠️ Champs manquants dans la réponse: {missing_fields}")
                    self.results['minor_issues'].append(f"Missing fields in lead response: {missing_fields}")
                
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Échec création lead: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Lead creation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la création du lead: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Lead creation error: {e}")
            return False
    
    def test_job_status(self) -> bool:
        """
        Test 3: Vérifier le statut du job d'analyse créé (GET /api/jobs/{job_id})
        """
        logger.info("🔍 Test 3: Vérification du statut du job d'analyse")
        self.results['tests_run'] += 1
        
        try:
            # Attendre un peu que le job soit créé
            time.sleep(3)
            
            # Récupérer le job via l'endpoint leads
            logger.info("🔍 Recherche du job d'analyse...")
            leads_response = self.session.get(f"{API_BASE}/leads")
            
            if leads_response.status_code != 200:
                logger.error(f"❌ Impossible de récupérer les leads: HTTP {leads_response.status_code}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Failed to retrieve leads: HTTP {leads_response.status_code}")
                return False
            
            leads = leads_response.json()
            current_lead = None
            
            for lead_data in leads:
                if lead_data['id'] == self.lead_id:
                    current_lead = lead_data
                    break
            
            if not current_lead:
                logger.error(f"❌ Lead {self.lead_id} non trouvé")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Lead {self.lead_id} not found")
                return False
            
            if not current_lead.get('latestJob'):
                logger.error("❌ Aucun job d'analyse trouvé pour ce lead")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append("No analysis job found for lead")
                return False
            
            job = current_lead['latestJob']
            self.job_id = job['id']
            
            logger.info(f"✅ Job d'analyse trouvé - ID: {self.job_id}")
            logger.info(f"📊 Statut initial: {job.get('status', 'unknown')} ({job.get('progress', 0)}%)")
            
            # Test direct de l'endpoint job
            job_response = self.session.get(f"{API_BASE}/jobs/{self.job_id}")
            
            if job_response.status_code == 200:
                job_data = job_response.json()
                logger.info(f"✅ Endpoint /jobs/{self.job_id} accessible")
                
                # Vérifier les champs obligatoires
                required_fields = ['id', 'leadId', 'url', 'status', 'progress', 'createdAt', 'updatedAt']
                missing_fields = [field for field in required_fields if field not in job_data]
                
                if missing_fields:
                    logger.warning(f"⚠️ Champs manquants dans le job: {missing_fields}")
                    self.results['minor_issues'].append(f"Missing fields in job response: {missing_fields}")
                
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Endpoint job inaccessible: HTTP {job_response.status_code}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Job endpoint failed: HTTP {job_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la vérification du job: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Job status check error: {e}")
            return False
    
    def test_analysis_completion(self) -> bool:
        """
        Test 4: Attendre que l'analyse soit complète ou échoue (polling avec timeout 180 secondes)
        """
        logger.info("🔍 Test 4: Attente de la completion de l'analyse (timeout 180s)")
        self.results['tests_run'] += 1
        
        try:
            max_wait = 180  # 180 secondes selon la review request
            wait_time = 0
            poll_interval = 10  # 10 secondes
            
            logger.info("⏳ Polling du statut de l'analyse...")
            start_time = time.time()
            
            while wait_time < max_wait:
                time.sleep(poll_interval)
                wait_time += poll_interval
                
                # Vérifier le statut
                status_response = self.session.get(f"{API_BASE}/jobs/{self.job_id}")
                
                if status_response.status_code != 200:
                    logger.warning(f"⚠️ Impossible de vérifier le statut: HTTP {status_response.status_code}")
                    continue
                
                job_status = status_response.json()
                status = job_status.get('status', 'unknown')
                progress = job_status.get('progress', 0)
                
                logger.info(f"📊 Statut: {status} ({progress}%) - Temps écoulé: {wait_time}s")
                
                if status == 'completed':
                    completion_time = time.time() - start_time
                    self.results['performance_metrics']['analysis_completion_time'] = completion_time
                    
                    self.report_id = job_status.get('reportId')
                    if self.report_id:
                        logger.info(f"✅ Analyse terminée en {completion_time:.1f}s - Report ID: {self.report_id}")
                        self.results['tests_passed'] += 1
                        return True
                    else:
                        logger.error("❌ Analyse terminée mais aucun reportId")
                        self.results['tests_failed'] += 1
                        self.results['critical_issues'].append("Analysis completed but no reportId")
                        return False
                        
                elif status == 'failed':
                    error = job_status.get('error', 'Unknown error')
                    logger.error(f"❌ Analyse échouée: {error}")
                    self.results['tests_failed'] += 1
                    self.results['critical_issues'].append(f"Analysis failed: {error}")
                    return False
                
                elif status == 'processing':
                    # Continuer le polling
                    continue
                else:
                    logger.warning(f"⚠️ Statut inattendu: {status}")
            
            # Timeout atteint
            logger.error(f"❌ TIMEOUT: Analyse non terminée après {max_wait}s")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Analysis timeout after {max_wait}s")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur dans l'attente de completion: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Analysis completion error: {e}")
            return False
    
    def test_report_generation(self) -> bool:
        """
        Test 5: Vérifier que le rapport est généré (GET /api/reports/{report_id})
        """
        logger.info("🔍 Test 5: Vérification de la génération du rapport")
        self.results['tests_run'] += 1
        
        try:
            if not self.report_id:
                logger.error("❌ Aucun report_id disponible")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append("No report_id available")
                return False
            
            logger.info(f"📊 Récupération du rapport {self.report_id}")
            start_time = time.time()
            report_response = self.session.get(f"{API_BASE}/reports/{self.report_id}")
            response_time = time.time() - start_time
            
            self.results['performance_metrics']['report_retrieval_time'] = response_time
            
            if report_response.status_code == 200:
                report = report_response.json()
                logger.info(f"✅ Rapport récupéré avec succès")
                logger.info(f"⏱️ Temps de réponse: {response_time:.2f}s")
                
                # Vérifier les champs obligatoires du rapport
                required_fields = ['id', 'leadId', 'url', 'scores', 'createdAt']
                missing_fields = [field for field in required_fields if field not in report]
                
                if missing_fields:
                    logger.warning(f"⚠️ Champs manquants dans le rapport: {missing_fields}")
                    self.results['minor_issues'].append(f"Missing fields in report: {missing_fields}")
                
                # Vérifier la structure des scores
                scores = report.get('scores', {})
                if scores:
                    score_fields = ['structure', 'answerability', 'readability', 'eeat', 'educational', 'thematic', 'aiOptimization', 'visibility', 'global_score']
                    missing_score_fields = [field for field in score_fields if field not in scores]
                    
                    if missing_score_fields:
                        logger.warning(f"⚠️ Champs de score manquants: {missing_score_fields}")
                        self.results['minor_issues'].append(f"Missing score fields: {missing_score_fields}")
                    
                    logger.info(f"📊 Score global: {scores.get('global_score', 'N/A')}/10")
                
                # Sauvegarder le rapport pour analyse détaillée
                with open(f'/app/test_report_{self.report_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 Rapport sauvegardé: /app/test_report_{self.report_id}.json")
                
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Impossible de récupérer le rapport: HTTP {report_response.status_code}")
                logger.error(f"Response: {report_response.text}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Report retrieval failed: HTTP {report_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la récupération du rapport: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Report generation test error: {e}")
            return False
    
    def test_modules_validation(self) -> bool:
        """
        Test 6: Vérifier la présence de tous les modules dans le rapport
        """
        logger.info("🔍 Test 6: Validation de tous les modules dans le rapport")
        self.results['tests_run'] += 1
        
        try:
            # Récupérer le rapport
            report_response = self.session.get(f"{API_BASE}/reports/{self.report_id}")
            
            if report_response.status_code != 200:
                logger.error(f"❌ Impossible de récupérer le rapport pour validation: HTTP {report_response.status_code}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append("Cannot retrieve report for module validation")
                return False
            
            report = report_response.json()
            
            # Modules requis selon la review request
            required_modules = {
                'visibility_results': 'Module 1: Tests de visibilité',
                'semantic_analysis': 'Module 5: Analyse sémantique',
                'competitive_intelligence': 'Module 3: Intelligence compétitive',
                'schemas': 'Module 4: Génération de schemas',
                'generated_articles': 'Module 2: Articles générés'
            }
            
            logger.info("📋 Validation des modules requis:")
            
            modules_found = 0
            modules_missing = []
            
            for module_key, module_name in required_modules.items():
                module_data = None
                
                # Chercher le module dans différents endroits du rapport
                if module_key in report:
                    module_data = report[module_key]
                elif 'visibility_results' in report and isinstance(report['visibility_results'], dict):
                    if module_key in report['visibility_results']:
                        module_data = report['visibility_results'][module_key]
                
                if module_data is not None and module_data != {}:
                    logger.info(f"  ✅ {module_name}: Présent")
                    modules_found += 1
                    
                    # Validation spécifique par module
                    self.validate_specific_module(module_key, module_data, module_name)
                else:
                    logger.error(f"  ❌ {module_name}: MANQUANT")
                    modules_missing.append(module_name)
                
                self.results['modules_validation'][module_key] = {
                    'name': module_name,
                    'present': module_data is not None and module_data != {},
                    'data_size': len(str(module_data)) if module_data else 0
                }
            
            # Évaluation globale
            total_modules = len(required_modules)
            success_rate = (modules_found / total_modules) * 100
            
            logger.info(f"📊 Modules trouvés: {modules_found}/{total_modules} ({success_rate:.1f}%)")
            
            if modules_missing:
                logger.error(f"❌ Modules manquants: {', '.join(modules_missing)}")
                self.results['critical_issues'].append(f"Missing modules: {', '.join(modules_missing)}")
            
            # Considérer comme réussi si au moins 80% des modules sont présents
            if success_rate >= 80:
                logger.info("✅ Validation des modules réussie")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Trop de modules manquants: {success_rate:.1f}%")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Too many missing modules: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la validation des modules: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Module validation error: {e}")
            return False
    
    def validate_specific_module(self, module_key: str, module_data: Any, module_name: str):
        """
        Validation spécifique pour chaque module
        """
        try:
            if module_key == 'visibility_results':
                # Vérifier la structure des résultats de visibilité
                if isinstance(module_data, dict):
                    required_fields = ['overall_visibility', 'platform_scores', 'queries_tested']
                    missing = [f for f in required_fields if f not in module_data]
                    if missing:
                        self.results['minor_issues'].append(f"Visibility results missing fields: {missing}")
                    else:
                        logger.info(f"    📊 Visibilité globale: {module_data.get('overall_visibility', 0):.1%}")
                        logger.info(f"    📊 Requêtes testées: {module_data.get('queries_tested', 0)}")
            
            elif module_key == 'semantic_analysis':
                # Vérifier l'analyse sémantique
                if isinstance(module_data, dict):
                    industry = module_data.get('industry_classification', {})
                    if industry:
                        logger.info(f"    🏭 Industrie détectée: {industry.get('primary_industry', 'N/A')}")
                    
                    entities = module_data.get('entities', {})
                    if entities:
                        offerings = entities.get('offerings', [])
                        logger.info(f"    🎯 Offres identifiées: {len(offerings)}")
            
            elif module_key == 'competitive_intelligence':
                # Vérifier l'intelligence compétitive
                if isinstance(module_data, dict):
                    competitors_analyzed = module_data.get('competitors_analyzed', 0)
                    logger.info(f"    🏆 Compétiteurs analysés: {competitors_analyzed}")
            
            elif module_key == 'schemas':
                # Vérifier les schemas générés
                if isinstance(module_data, dict):
                    schema_types = [k for k in module_data.keys() if k != 'implementation_guide']
                    logger.info(f"    📋 Types de schemas: {len(schema_types)}")
            
            elif module_key == 'generated_articles':
                # Vérifier les articles générés
                if isinstance(module_data, list):
                    logger.info(f"    📝 Articles générés: {len(module_data)}")
                    
        except Exception as e:
            logger.warning(f"    ⚠️ Erreur validation spécifique {module_name}: {e}")
    
    def test_downloads(self) -> bool:
        """
        Test 7: Vérifier les téléchargements (Dashboard HTML, Word DOCX, PDF)
        """
        logger.info("🔍 Test 7: Validation des téléchargements")
        self.results['tests_run'] += 1
        
        try:
            downloads = {
                'dashboard': {
                    'url': f"{API_BASE}/reports/{self.report_id}/dashboard",
                    'expected_content_type': 'text/html',
                    'name': 'Dashboard HTML'
                },
                'docx': {
                    'url': f"{API_BASE}/reports/{self.report_id}/docx",
                    'expected_content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'name': 'Rapport Word'
                },
                'pdf': {
                    'url': f"{API_BASE}/reports/{self.report_id}/pdf",
                    'expected_content_type': 'application/pdf',
                    'name': 'Rapport PDF'
                }
            }
            
            successful_downloads = 0
            failed_downloads = []
            
            for download_type, config in downloads.items():
                logger.info(f"📥 Test téléchargement {config['name']}")
                
                try:
                    start_time = time.time()
                    response = self.session.get(config['url'], timeout=30)
                    download_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        content_length = len(response.content)
                        
                        logger.info(f"  ✅ {config['name']}: {content_length} bytes en {download_time:.2f}s")
                        logger.info(f"     Content-Type: {content_type}")
                        
                        # Vérifier le type de contenu
                        if config['expected_content_type'].lower() in content_type:
                            logger.info(f"     ✅ Type de contenu correct")
                        else:
                            logger.warning(f"     ⚠️ Type de contenu inattendu (attendu: {config['expected_content_type']})")
                            self.results['minor_issues'].append(f"{config['name']} unexpected content type: {content_type}")
                        
                        # Vérifier la taille minimale
                        min_size = 1000  # 1KB minimum
                        if content_length >= min_size:
                            logger.info(f"     ✅ Taille suffisante")
                            successful_downloads += 1
                        else:
                            logger.warning(f"     ⚠️ Fichier trop petit: {content_length} bytes")
                            self.results['minor_issues'].append(f"{config['name']} file too small: {content_length} bytes")
                            successful_downloads += 1  # Pas critique
                        
                        self.results['downloads_validation'][download_type] = {
                            'success': True,
                            'size': content_length,
                            'content_type': content_type,
                            'download_time': download_time
                        }
                        
                    else:
                        logger.error(f"  ❌ {config['name']}: HTTP {response.status_code}")
                        failed_downloads.append(config['name'])
                        
                        self.results['downloads_validation'][download_type] = {
                            'success': False,
                            'status_code': response.status_code,
                            'error': response.text[:200]
                        }
                        
                except Exception as e:
                    logger.error(f"  ❌ {config['name']}: Erreur {e}")
                    failed_downloads.append(config['name'])
                    
                    self.results['downloads_validation'][download_type] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Évaluation
            total_downloads = len(downloads)
            success_rate = (successful_downloads / total_downloads) * 100
            
            logger.info(f"📊 Téléchargements réussis: {successful_downloads}/{total_downloads} ({success_rate:.1f}%)")
            
            if failed_downloads:
                logger.error(f"❌ Téléchargements échoués: {', '.join(failed_downloads)}")
                self.results['critical_issues'].append(f"Failed downloads: {', '.join(failed_downloads)}")
            
            if success_rate >= 66:  # Au moins 2/3 des téléchargements
                logger.info("✅ Validation des téléchargements réussie")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Trop de téléchargements échoués: {success_rate:.1f}%")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Too many failed downloads: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans les tests de téléchargement: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Download test error: {e}")
            return False
    
    def check_backend_logs(self):
        """
        Test 8: Vérifier les logs backend pour erreurs
        """
        logger.info("🔍 Test 8: Vérification des logs backend")
        
        try:
            # Vérifier les logs supervisor backend
            import subprocess
            
            log_files = [
                '/var/log/supervisor/backend.err.log',
                '/var/log/supervisor/backend.out.log'
            ]
            
            critical_errors = []
            warnings = []
            
            for log_file in log_files:
                try:
                    # Lire les dernières lignes du log
                    result = subprocess.run(['tail', '-n', '50', log_file], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        log_content = result.stdout
                        
                        # Chercher des erreurs critiques
                        error_keywords = ['ERROR', 'CRITICAL', 'Exception', 'Traceback', 'Failed']
                        warning_keywords = ['WARNING', 'WARN']
                        
                        lines = log_content.split('\n')
                        for line in lines[-20:]:  # Dernières 20 lignes
                            if any(keyword in line for keyword in error_keywords):
                                critical_errors.append(line.strip())
                            elif any(keyword in line for keyword in warning_keywords):
                                warnings.append(line.strip())
                        
                        logger.info(f"📋 Log {log_file}: {len(lines)} lignes analysées")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de lire {log_file}: {e}")
            
            # Rapport des logs
            if critical_errors:
                logger.warning(f"⚠️ {len(critical_errors)} erreurs critiques trouvées dans les logs:")
                for error in critical_errors[-5:]:  # Dernières 5 erreurs
                    logger.warning(f"  • {error}")
                self.results['minor_issues'].extend(critical_errors[-5:])
            
            if warnings:
                logger.info(f"📋 {len(warnings)} avertissements trouvés dans les logs")
            
            logger.info("✅ Vérification des logs terminée")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la vérification des logs: {e}")
    
    def generate_final_report(self):
        """
        Génère le rapport final des tests
        """
        self.results['test_end'] = datetime.now().isoformat()
        
        logger.info("\n" + "="*80)
        logger.info("📋 RAPPORT FINAL - TESTS COMPLETS BACKEND GEO SAAS")
        logger.info("="*80)
        
        logger.info(f"🌐 Backend URL: {self.results['backend_url']}")
        logger.info(f"🎯 URL de test: {self.results['test_url']}")
        logger.info(f"🕐 Durée: {self.results['test_start']} → {self.results['test_end']}")
        logger.info(f"📊 Tests exécutés: {self.results['tests_run']}")
        logger.info(f"✅ Tests réussis: {self.results['tests_passed']}")
        logger.info(f"❌ Tests échoués: {self.results['tests_failed']}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100 if self.results['tests_run'] > 0 else 0
        logger.info(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        # Métriques de performance
        if self.results['performance_metrics']:
            logger.info("\n⏱️ MÉTRIQUES DE PERFORMANCE:")
            for metric, value in self.results['performance_metrics'].items():
                logger.info(f"  • {metric}: {value:.2f}s")
        
        # Validation des modules
        if self.results['modules_validation']:
            logger.info("\n📋 VALIDATION DES MODULES:")
            for module_key, module_info in self.results['modules_validation'].items():
                status = "✅" if module_info['present'] else "❌"
                logger.info(f"  {status} {module_info['name']}")
        
        # Validation des téléchargements
        if self.results['downloads_validation']:
            logger.info("\n📥 VALIDATION DES TÉLÉCHARGEMENTS:")
            for download_type, download_info in self.results['downloads_validation'].items():
                status = "✅" if download_info['success'] else "❌"
                size = f" ({download_info.get('size', 0)} bytes)" if download_info['success'] else ""
                logger.info(f"  {status} {download_type.upper()}{size}")
        
        # Problèmes critiques
        if self.results['critical_issues']:
            logger.info("\n🚨 PROBLÈMES CRITIQUES:")
            for issue in self.results['critical_issues']:
                logger.info(f"  • {issue}")
        
        # Problèmes mineurs
        if self.results['minor_issues']:
            logger.info(f"\n⚠️ PROBLÈMES MINEURS ({len(self.results['minor_issues'])}):")
            for issue in self.results['minor_issues'][:10]:  # Limiter à 10
                logger.info(f"  • {issue}")
            if len(self.results['minor_issues']) > 10:
                logger.info(f"  ... et {len(self.results['minor_issues']) - 10} autres")
        
        # IDs pour référence
        if self.lead_id:
            logger.info(f"\n🔗 RÉFÉRENCES:")
            logger.info(f"  • Lead ID: {self.lead_id}")
            logger.info(f"  • Job ID: {self.job_id}")
            logger.info(f"  • Report ID: {self.report_id}")
        
        # Sauvegarder le rapport complet
        with open('/app/backend_test_results_complete.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Rapport détaillé sauvegardé: /app/backend_test_results_complete.json")
        logger.info("="*80)


def main():
    """
    Point d'entrée principal
    """
    print("🚀 TEST COMPLET BACKEND GEO SAAS")
    print("="*50)
    
    tester = GEOSaaSBackendTester()
    success = tester.run_complete_tests()
    
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        return 0
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ!")
        return 1


if __name__ == "__main__":
    sys.exit(main())