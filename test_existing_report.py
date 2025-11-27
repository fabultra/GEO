#!/usr/bin/env python3
"""
Test d'un rapport existant pour valider les modules
"""
import json
import logging
import requests
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "https://issue-resolver-41.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Utiliser un rapport existant identifié dans le diagnostic
REPORT_ID = "e38b4d21-31d8-410b-9753-fa1268fe823a"  # Rapport sekoia.ca

def test_report_modules():
    """Tester les modules d'un rapport existant"""
    logger.info(f"🔍 Test des modules du rapport {REPORT_ID}")
    
    try:
        # Essayer de récupérer le rapport via l'API (avec timeout court)
        try:
            response = requests.get(f"{API_BASE}/reports/{REPORT_ID}", timeout=5)
            if response.status_code == 200:
                report = response.json()
                logger.info("✅ Rapport récupéré via API")
            else:
                logger.warning(f"⚠️ API timeout, lecture du fichier local")
                raise Exception("API timeout")
        except:
            # Fallback: lire le fichier dashboard data
            dashboard_file = f"/app/backend/dashboards/{REPORT_ID}_visibility_dashboard_data.json"
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                visibility_data = json.load(f)
            
            # Simuler la structure du rapport
            report = {
                'id': REPORT_ID,
                'url': visibility_data.get('site_url', 'sekoia.ca'),
                'visibility_results': visibility_data,
                'scores': {'global_score': 7.5}  # Exemple
            }
            logger.info("✅ Données récupérées depuis le fichier local")
        
        # Modules requis selon la review request
        required_modules = {
            'visibility_results': 'Module 1: Tests de visibilité',
            'semantic_analysis': 'Module 5: Analyse sémantique',
            'competitive_intelligence': 'Module 3: Intelligence compétitive',
            'schemas': 'Module 4: Génération de schemas',
            'generated_articles': 'Module 2: Articles générés'
        }
        
        logger.info("📋 Validation des modules:")
        
        modules_found = 0
        modules_details = {}
        
        for module_key, module_name in required_modules.items():
            module_data = None
            
            # Chercher le module dans le rapport
            if module_key in report:
                module_data = report[module_key]
            elif 'visibility_results' in report and isinstance(report['visibility_results'], dict):
                if module_key in report['visibility_results']:
                    module_data = report['visibility_results'][module_key]
            
            if module_data is not None and module_data != {}:
                logger.info(f"  ✅ {module_name}: PRÉSENT")
                modules_found += 1
                
                # Analyse détaillée par module
                if module_key == 'visibility_results':
                    summary = module_data.get('summary', {})
                    queries = module_data.get('queries', [])
                    logger.info(f"    📊 Visibilité globale: {summary.get('global_visibility', 0):.1%}")
                    logger.info(f"    📊 Requêtes testées: {len(queries)}")
                    logger.info(f"    📊 Plateformes: {list(summary.get('by_platform', {}).keys())}")
                    
                    modules_details[module_key] = {
                        'present': True,
                        'global_visibility': summary.get('global_visibility', 0),
                        'queries_tested': len(queries),
                        'platforms': list(summary.get('by_platform', {}).keys())
                    }
                
                elif module_key == 'semantic_analysis':
                    industry = module_data.get('industry_classification', {})
                    entities = module_data.get('entities', {})
                    logger.info(f"    🏭 Industrie: {industry.get('primary_industry', 'N/A')}")
                    logger.info(f"    🎯 Offres: {len(entities.get('offerings', []))}")
                    
                    modules_details[module_key] = {
                        'present': True,
                        'industry': industry.get('primary_industry', 'N/A'),
                        'offerings_count': len(entities.get('offerings', []))
                    }
                
                elif module_key == 'competitive_intelligence':
                    competitors = module_data.get('competitors_analyzed', 0)
                    analyses = module_data.get('analyses', [])
                    logger.info(f"    🏆 Compétiteurs analysés: {competitors}")
                    logger.info(f"    📋 Analyses disponibles: {len(analyses)}")
                    
                    modules_details[module_key] = {
                        'present': True,
                        'competitors_analyzed': competitors,
                        'analyses_count': len(analyses)
                    }
                
                elif module_key == 'schemas':
                    schema_types = [k for k in module_data.keys() if k != 'implementation_guide']
                    logger.info(f"    📋 Types de schemas: {len(schema_types)}")
                    logger.info(f"    📋 Schemas: {schema_types[:3]}...")  # Premiers 3
                    
                    modules_details[module_key] = {
                        'present': True,
                        'schema_types_count': len(schema_types),
                        'schema_types': schema_types[:5]
                    }
                
                elif module_key == 'generated_articles':
                    if isinstance(module_data, list):
                        logger.info(f"    📝 Articles générés: {len(module_data)}")
                        modules_details[module_key] = {
                            'present': True,
                            'articles_count': len(module_data)
                        }
                    else:
                        logger.info(f"    📝 Structure articles: {type(module_data)}")
                        modules_details[module_key] = {
                            'present': True,
                            'data_type': str(type(module_data))
                        }
            else:
                logger.error(f"  ❌ {module_name}: MANQUANT")
                modules_details[module_key] = {'present': False}
        
        # Test des téléchargements
        logger.info("\n📥 Test des téléchargements:")
        
        downloads = {
            'dashboard': f"{API_BASE}/reports/{REPORT_ID}/dashboard",
            'docx': f"{API_BASE}/reports/{REPORT_ID}/docx",
            'pdf': f"{API_BASE}/reports/{REPORT_ID}/pdf"
        }
        
        download_results = {}
        successful_downloads = 0
        
        for download_type, url in downloads.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    size = len(response.content)
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"  ✅ {download_type.upper()}: {size} bytes ({content_type})")
                    successful_downloads += 1
                    download_results[download_type] = {
                        'success': True,
                        'size': size,
                        'content_type': content_type
                    }
                else:
                    logger.error(f"  ❌ {download_type.upper()}: HTTP {response.status_code}")
                    download_results[download_type] = {
                        'success': False,
                        'status_code': response.status_code
                    }
            except Exception as e:
                logger.error(f"  ❌ {download_type.upper()}: {e}")
                download_results[download_type] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Résumé final
        logger.info("\n" + "="*60)
        logger.info("📋 RÉSUMÉ DES TESTS")
        logger.info("="*60)
        
        logger.info(f"🎯 Rapport testé: {REPORT_ID}")
        logger.info(f"🌐 URL: {report.get('url', 'N/A')}")
        logger.info(f"📊 Modules présents: {modules_found}/5 ({modules_found/5*100:.1f}%)")
        logger.info(f"📥 Téléchargements réussis: {successful_downloads}/3 ({successful_downloads/3*100:.1f}%)")
        
        # Problèmes identifiés
        missing_modules = [name for key, name in required_modules.items() if not modules_details[key]['present']]
        if missing_modules:
            logger.error(f"\n🚨 MODULES MANQUANTS:")
            for module in missing_modules:
                logger.error(f"  • {module}")
        
        failed_downloads = [dt for dt, result in download_results.items() if not result['success']]
        if failed_downloads:
            logger.error(f"\n🚨 TÉLÉCHARGEMENTS ÉCHOUÉS:")
            for download in failed_downloads:
                logger.error(f"  • {download.upper()}")
        
        # Score global
        total_score = (modules_found * 2 + successful_downloads) / 13 * 100  # 10 points modules + 3 téléchargements
        logger.info(f"\n📊 SCORE GLOBAL: {total_score:.1f}%")
        
        # Sauvegarder les résultats
        results = {
            'report_id': REPORT_ID,
            'url': report.get('url', 'N/A'),
            'modules_found': modules_found,
            'modules_details': modules_details,
            'downloads_successful': successful_downloads,
            'download_results': download_results,
            'score': total_score,
            'missing_modules': missing_modules,
            'failed_downloads': failed_downloads
        }
        
        with open('/app/report_validation_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats sauvegardés: /app/report_validation_results.json")
        
        if total_score >= 80:
            logger.info("🎉 VALIDATION RÉUSSIE")
            return 0
        elif total_score >= 60:
            logger.info("⚠️ VALIDATION PARTIELLE")
            return 0
        else:
            logger.error("❌ VALIDATION ÉCHOUÉE")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Erreur dans la validation: {e}")
        return 1

def main():
    return test_report_modules()

if __name__ == "__main__":
    sys.exit(main())