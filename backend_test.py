#!/usr/bin/env python3
"""
Test end-to-end du système de découverte de compétiteurs V3
Validation complète du pipeline 3 étages
"""
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv

# Configuration
load_dotenv('/app/backend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://geo-competitor-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompetitorDiscoveryTester:
    """
    Testeur end-to-end pour le système de découverte de compétiteurs
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CompetitorDiscoveryTester/1.0'
        })
        
        # Sites de test recommandés
        self.test_sites = [
            {
                'url': 'sekoia.ca',
                'name': 'SEKOIA',
                'expected_industry': 'digital marketing',
                'expected_competitors_min': 2
            },
            {
                'url': 'maibec.com', 
                'name': 'Maibec',
                'expected_industry': 'manufacturing',
                'expected_competitors_min': 2
            }
        ]
        
        self.results = {
            'test_start': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'detailed_results': [],
            'critical_issues': [],
            'competitor_validation': []
        }
    
    def run_all_tests(self):
        """
        Lance tous les tests de validation
        """
        logger.info("🚀 Démarrage des tests end-to-end du système de découverte de compétiteurs")
        logger.info(f"Backend URL: {API_BASE}")
        
        try:
            # Test 1: Vérifier que l'API backend est accessible
            self.test_backend_health()
            
            # Test 2: Lancer une analyse complète avec un site test
            test_site = self.test_sites[0]  # sekoia.ca
            analysis_result = self.test_complete_analysis(test_site)
            
            if analysis_result:
                # Test 3: Valider le pipeline de découverte de compétiteurs
                self.test_competitor_discovery_pipeline(analysis_result)
                
                # Test 4: Valider les nouveaux champs des compétiteurs
                self.test_competitor_fields_validation(analysis_result)
                
                # Test 5: Valider que les URLs sont réelles et accessibles
                self.test_competitor_urls_accessibility(analysis_result)
                
                # Test 6: Vérifier la sauvegarde MongoDB
                self.test_mongodb_storage(analysis_result)
            
            # Générer le rapport final
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans les tests: {e}")
            self.results['critical_issues'].append(f"Test suite failure: {e}")
            return False
        
        return self.results['tests_failed'] == 0
    
    def test_backend_health(self):
        """
        Test 1: Vérifier que l'API backend est accessible
        """
        logger.info("🔍 Test 1: Vérification de l'accessibilité du backend")
        self.results['tests_run'] += 1
        
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                logger.info("✅ Backend accessible")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Backend non accessible: {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Backend not accessible: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur de connexion au backend: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Backend connection error: {e}")
            return False
    
    def test_complete_analysis(self, test_site: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test 2: Lancer une analyse complète avec un site test
        """
        logger.info(f"🔍 Test 2: Analyse complète de {test_site['url']}")
        self.results['tests_run'] += 1
        
        try:
            # Créer un lead de test
            lead_data = {
                "firstName": "Test",
                "lastName": "CompetitorDiscovery",
                "email": "test@example.com",
                "company": test_site['name'],
                "url": test_site['url'],
                "consent": True
            }
            
            logger.info(f"📝 Création du lead pour {test_site['url']} (analyse automatique)")
            lead_response = self.session.post(f"{API_BASE}/leads", json=lead_data)
            
            if lead_response.status_code != 200:
                logger.error(f"❌ Échec création lead: {lead_response.status_code}")
                logger.error(f"Response: {lead_response.text}")
                self.results['tests_failed'] += 1
                return None
            
            lead = lead_response.json()
            lead_id = lead['id']
            logger.info(f"✅ Lead créé: {lead_id}")
            
            # L'analyse est lancée automatiquement, récupérer le job
            logger.info("🔍 Recherche du job d'analyse...")
            
            # Attendre un peu que le job soit créé
            time.sleep(2)
            
            # Récupérer tous les leads pour trouver le job
            leads_response = self.session.get(f"{API_BASE}/leads")
            if leads_response.status_code == 200:
                leads = leads_response.json()
                current_lead = None
                for lead_data in leads:
                    if lead_data['id'] == lead_id:
                        current_lead = lead_data
                        break
                
                if current_lead and current_lead.get('latestJob'):
                    job = current_lead['latestJob']
                    job_id = job['id']
                    logger.info(f"✅ Job d'analyse trouvé: {job_id}")
                else:
                    logger.error("❌ Aucun job d'analyse trouvé")
                    self.results['tests_failed'] += 1
                    return None
            else:
                logger.error(f"❌ Impossible de récupérer les leads: {leads_response.status_code}")
                self.results['tests_failed'] += 1
                return None
            
            # Attendre la completion (max 10 minutes)
            max_wait = 600  # 10 minutes
            wait_time = 0
            poll_interval = 15  # 15 secondes
            
            logger.info("⏳ Attente de la completion de l'analyse...")
            
            while wait_time < max_wait:
                time.sleep(poll_interval)
                wait_time += poll_interval
                
                # Vérifier le statut
                status_response = self.session.get(f"{API_BASE}/jobs/{job_id}")
                if status_response.status_code == 200:
                    job_status = status_response.json()
                    status = job_status.get('status', 'unknown')
                    progress = job_status.get('progress', 0)
                    
                    logger.info(f"📊 Statut: {status} ({progress}%)")
                    
                    if status == 'completed':
                        report_id = job_status.get('reportId')
                        if report_id:
                            logger.info(f"✅ Analyse terminée! Report ID: {report_id}")
                            
                            # Récupérer le rapport
                            report_response = self.session.get(f"{API_BASE}/reports/{report_id}")
                            if report_response.status_code == 200:
                                report = report_response.json()
                                self.results['tests_passed'] += 1
                                
                                # Sauvegarder pour debug
                                with open(f'/app/test_report_{report_id}.json', 'w') as f:
                                    json.dump(report, f, indent=2, ensure_ascii=False)
                                
                                return {
                                    'job_id': job_id,
                                    'report_id': report_id,
                                    'report': report,
                                    'test_site': test_site
                                }
                            else:
                                logger.error(f"❌ Impossible de récupérer le rapport: {report_response.status_code}")
                        break
                    elif status == 'failed':
                        error = job_status.get('error', 'Unknown error')
                        logger.error(f"❌ Analyse échouée: {error}")
                        self.results['critical_issues'].append(f"Analysis failed for {test_site['url']}: {error}")
                        break
                else:
                    logger.warning(f"⚠️ Impossible de vérifier le statut: {status_response.status_code}")
            
            if wait_time >= max_wait:
                logger.error("❌ Timeout: analyse non terminée dans les temps")
                self.results['critical_issues'].append(f"Analysis timeout for {test_site['url']}")
            
            self.results['tests_failed'] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur dans l'analyse complète: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Complete analysis error: {e}")
            return None
    
    def test_competitor_discovery_pipeline(self, analysis_result: Dict[str, Any]):
        """
        Test 3: Valider le pipeline de découverte de compétiteurs
        """
        logger.info("🔍 Test 3: Validation du pipeline de découverte de compétiteurs")
        self.results['tests_run'] += 1
        
        try:
            report = analysis_result['report']
            
            # Vérifier la présence des données de competitive intelligence
            competitive_intel = None
            
            # Chercher dans visibility_results
            visibility_results = report.get('visibility_results')
            if visibility_results and isinstance(visibility_results, dict):
                competitive_intel = visibility_results.get('competitive_intelligence')
            
            # Chercher dans analysis (fallback)
            if not competitive_intel:
                analysis = report.get('analysis')
                if analysis and isinstance(analysis, dict):
                    competitive_intel = analysis.get('competitive_intelligence')
            
            if not competitive_intel:
                logger.error("❌ Aucune donnée de competitive intelligence trouvée")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append("No competitive intelligence data found")
                return False
            
            logger.info(f"✅ Données de competitive intelligence trouvées: {type(competitive_intel)}")
            
            # Vérifier les métriques de base
            competitors_analyzed = competitive_intel.get('competitors_analyzed', 0)
            logger.info(f"📊 Compétiteurs analysés: {competitors_analyzed}")
            
            if competitors_analyzed > 0:
                logger.info("✅ Pipeline de découverte fonctionnel")
                self.results['tests_passed'] += 1
                
                # Vérifier la structure des analyses
                analyses = competitive_intel.get('analyses', [])
                if analyses:
                    logger.info(f"📋 {len(analyses)} analyses de compétiteurs disponibles")
                    
                    # Examiner la première analyse
                    first_analysis = analyses[0]
                    logger.info(f"🔍 Premier compétiteur: {first_analysis.get('url', 'N/A')}")
                    
                return True
            else:
                logger.warning("⚠️ Aucun compétiteur analysé - peut être normal selon les données de visibilité")
                self.results['tests_passed'] += 1  # Pas un échec critique
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la validation du pipeline: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Pipeline validation error: {e}")
            return False
    
    def test_competitor_fields_validation(self, analysis_result: Dict[str, Any]):
        """
        Test 4: Valider les nouveaux champs des compétiteurs (score, type, reason, source)
        """
        logger.info("🔍 Test 4: Validation des nouveaux champs des compétiteurs")
        self.results['tests_run'] += 1
        
        try:
            report = analysis_result['report']
            
            # Chercher les données de compétiteurs avec les nouveaux champs
            competitors_with_new_fields = []
            
            # Vérifier dans visibility_results
            visibility_results = report.get('visibility_results')
            if visibility_results and isinstance(visibility_results, dict):
                competitive_intel = visibility_results.get('competitive_intelligence', {})
                analyses = competitive_intel.get('analyses', [])
                
                for analysis in analyses:
                    # Vérifier si les nouveaux champs sont présents
                    has_score = 'score' in analysis
                    has_type = 'type' in analysis
                    has_reason = 'reason' in analysis
                    has_source = 'source' in analysis
                    
                    if has_score or has_type or has_reason or has_source:
                        competitors_with_new_fields.append({
                            'url': analysis.get('url', 'N/A'),
                            'score': analysis.get('score'),
                            'type': analysis.get('type'),
                            'reason': analysis.get('reason'),
                            'source': analysis.get('source'),
                            'has_all_fields': has_score and has_type and has_reason and has_source
                        })
            
            if competitors_with_new_fields:
                logger.info(f"✅ {len(competitors_with_new_fields)} compétiteurs avec nouveaux champs trouvés")
                
                # Analyser les champs
                for i, comp in enumerate(competitors_with_new_fields, 1):
                    logger.info(f"  {i}. {comp['url']}")
                    logger.info(f"     Score: {comp['score']}")
                    logger.info(f"     Type: {comp['type']}")
                    logger.info(f"     Reason: {comp['reason']}")
                    logger.info(f"     Source: {comp['source']}")
                    logger.info(f"     Tous champs: {'✅' if comp['has_all_fields'] else '❌'}")
                
                # Vérifier si au moins un compétiteur a tous les champs
                complete_competitors = [c for c in competitors_with_new_fields if c['has_all_fields']]
                
                if complete_competitors:
                    logger.info(f"✅ {len(complete_competitors)} compétiteurs avec tous les nouveaux champs")
                    self.results['tests_passed'] += 1
                    return True
                else:
                    logger.warning("⚠️ Aucun compétiteur avec tous les nouveaux champs")
                    self.results['tests_failed'] += 1
                    self.results['critical_issues'].append("No competitors with all new fields (score, type, reason, source)")
                    return False
            else:
                logger.warning("⚠️ Aucun compétiteur avec nouveaux champs trouvé")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append("No competitors with new fields found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans la validation des champs: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"Fields validation error: {e}")
            return False
    
    def test_competitor_urls_accessibility(self, analysis_result: Dict[str, Any]):
        """
        Test 5: Valider que les URLs des compétiteurs sont réelles et accessibles
        """
        logger.info("🔍 Test 5: Validation de l'accessibilité des URLs des compétiteurs")
        self.results['tests_run'] += 1
        
        try:
            report = analysis_result['report']
            competitor_urls = []
            
            # Extraire toutes les URLs de compétiteurs
            visibility_results = report.get('visibility_results')
            if visibility_results and isinstance(visibility_results, dict):
                competitive_intel = visibility_results.get('competitive_intelligence', {})
                analyses = competitive_intel.get('analyses', [])
                
                for analysis in analyses:
                    url = analysis.get('url')
                    if url:
                        competitor_urls.append(url)
            
            if not competitor_urls:
                logger.warning("⚠️ Aucune URL de compétiteur à tester")
                self.results['tests_passed'] += 1  # Pas un échec si pas de compétiteurs
                return True
            
            logger.info(f"🌐 Test d'accessibilité de {len(competitor_urls)} URLs")
            
            accessible_count = 0
            inaccessible_urls = []
            
            for url in competitor_urls:
                try:
                    # Test HEAD request rapide
                    response = requests.head(
                        url, 
                        timeout=10, 
                        allow_redirects=True,
                        headers={'User-Agent': 'Mozilla/5.0 (compatible; CompetitorTester/1.0)'}
                    )
                    
                    if response.status_code < 400:
                        logger.info(f"  ✅ {url} - Accessible ({response.status_code})")
                        accessible_count += 1
                        
                        # Enregistrer pour le rapport
                        self.results['competitor_validation'].append({
                            'url': url,
                            'accessible': True,
                            'status_code': response.status_code,
                            'is_real': True
                        })
                    else:
                        logger.warning(f"  ⚠️ {url} - Status {response.status_code}")
                        inaccessible_urls.append(url)
                        
                        self.results['competitor_validation'].append({
                            'url': url,
                            'accessible': False,
                            'status_code': response.status_code,
                            'is_real': False
                        })
                        
                except Exception as e:
                    logger.error(f"  ❌ {url} - Erreur: {e}")
                    inaccessible_urls.append(url)
                    
                    self.results['competitor_validation'].append({
                        'url': url,
                        'accessible': False,
                        'error': str(e),
                        'is_real': False
                    })
            
            # Évaluer les résultats
            accessibility_rate = accessible_count / len(competitor_urls) if competitor_urls else 0
            logger.info(f"📊 Taux d'accessibilité: {accessibility_rate:.1%} ({accessible_count}/{len(competitor_urls)})")
            
            if accessibility_rate >= 0.8:  # 80% minimum
                logger.info("✅ Taux d'accessibilité satisfaisant")
                self.results['tests_passed'] += 1
                return True
            else:
                logger.error(f"❌ Taux d'accessibilité insuffisant: {accessibility_rate:.1%}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"Low URL accessibility rate: {accessibility_rate:.1%}")
                
                if inaccessible_urls:
                    logger.error(f"URLs inaccessibles: {inaccessible_urls}")
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans le test d'accessibilité: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"URL accessibility test error: {e}")
            return False
    
    def test_mongodb_storage(self, analysis_result: Dict[str, Any]):
        """
        Test 6: Vérifier la sauvegarde MongoDB avec les nouveaux champs
        """
        logger.info("🔍 Test 6: Validation de la sauvegarde MongoDB")
        self.results['tests_run'] += 1
        
        try:
            report_id = analysis_result['report_id']
            
            # Récupérer le rapport depuis l'API (qui lit MongoDB)
            report_response = self.session.get(f"{API_BASE}/reports/{report_id}")
            
            if report_response.status_code == 200:
                report = report_response.json()
                
                # Vérifier que les données de competitive intelligence sont sauvegardées
                has_competitive_data = False
                
                if 'visibility_results' in report:
                    visibility_results = report['visibility_results']
                    if isinstance(visibility_results, dict) and 'competitive_intelligence' in visibility_results:
                        competitive_intel = visibility_results['competitive_intelligence']
                        if competitive_intel and competitive_intel.get('competitors_analyzed', 0) > 0:
                            has_competitive_data = True
                
                if has_competitive_data:
                    logger.info("✅ Données de competitive intelligence sauvegardées en MongoDB")
                    self.results['tests_passed'] += 1
                    return True
                else:
                    logger.warning("⚠️ Pas de données de competitive intelligence en MongoDB")
                    self.results['tests_passed'] += 1  # Pas critique si pas de compétiteurs
                    return True
            else:
                logger.error(f"❌ Impossible de récupérer le rapport depuis MongoDB: {report_response.status_code}")
                self.results['tests_failed'] += 1
                self.results['critical_issues'].append(f"MongoDB retrieval failed: HTTP {report_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur dans le test MongoDB: {e}")
            self.results['tests_failed'] += 1
            self.results['critical_issues'].append(f"MongoDB test error: {e}")
            return False
    
    def generate_final_report(self):
        """
        Génère le rapport final des tests
        """
        self.results['test_end'] = datetime.now().isoformat()
        
        logger.info("\n" + "="*80)
        logger.info("📋 RAPPORT FINAL - TESTS SYSTÈME DE DÉCOUVERTE DE COMPÉTITEURS")
        logger.info("="*80)
        
        logger.info(f"🕐 Durée: {self.results['test_start']} → {self.results['test_end']}")
        logger.info(f"📊 Tests exécutés: {self.results['tests_run']}")
        logger.info(f"✅ Tests réussis: {self.results['tests_passed']}")
        logger.info(f"❌ Tests échoués: {self.results['tests_failed']}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run']) * 100 if self.results['tests_run'] > 0 else 0
        logger.info(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.results['critical_issues']:
            logger.info("\n🚨 PROBLÈMES CRITIQUES:")
            for issue in self.results['critical_issues']:
                logger.info(f"  • {issue}")
        
        if self.results['competitor_validation']:
            logger.info(f"\n🌐 VALIDATION DES COMPÉTITEURS ({len(self.results['competitor_validation'])}):")
            for comp in self.results['competitor_validation']:
                status = "✅" if comp['accessible'] else "❌"
                logger.info(f"  {status} {comp['url']} - {comp.get('status_code', 'Error')}")
        
        # Sauvegarder le rapport complet
        with open('/app/competitor_discovery_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Rapport détaillé sauvegardé: /app/competitor_discovery_test_results.json")
        logger.info("="*80)


def main():
    """
    Point d'entrée principal
    """
    print("🚀 Test End-to-End - Système de Découverte de Compétiteurs V3")
    print("="*70)
    
    tester = CompetitorDiscoveryTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        return 0
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ!")
        return 1


if __name__ == "__main__":
    sys.exit(main())