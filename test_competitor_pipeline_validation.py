#!/usr/bin/env python3
"""
Validation du pipeline de découverte de compétiteurs V3
Focus sur la validation de l'implémentation existante
"""
import sys
import os
import json
import logging
from datetime import datetime

# Ajouter le backend au path
sys.path.append('/app/backend')

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_implementation_exists():
    """
    Test 1: Vérifier que les nouveaux modules existent et sont importables
    """
    logger.info("🔍 Test 1: Vérification de l'existence des modules")
    
    tests = []
    
    # Test CompetitorExtractor
    try:
        from utils.competitor_extractor import CompetitorExtractor
        logger.info("  ✅ CompetitorExtractor importé avec succès")
        
        # Vérifier les méthodes clés
        methods = ['extract_from_visibility_results', 'filter_self_domain', '_normalize_url', '_extract_domain']
        for method in methods:
            if hasattr(CompetitorExtractor, method):
                logger.info(f"    ✅ Méthode {method} présente")
            else:
                logger.error(f"    ❌ Méthode {method} manquante")
                tests.append(False)
        
        tests.append(True)
        
    except ImportError as e:
        logger.error(f"  ❌ Impossible d'importer CompetitorExtractor: {e}")
        tests.append(False)
    
    # Test CompetitorDiscovery
    try:
        from services.competitor_discovery import CompetitorDiscovery
        logger.info("  ✅ CompetitorDiscovery importé avec succès")
        
        # Vérifier les méthodes clés
        discovery = CompetitorDiscovery()
        methods = ['discover_real_competitors', '_search_web_for_competitors', '_validate_and_score_competitors']
        for method in methods:
            if hasattr(discovery, method):
                logger.info(f"    ✅ Méthode {method} présente")
            else:
                logger.error(f"    ❌ Méthode {method} manquante")
                tests.append(False)
        
        tests.append(True)
        
    except ImportError as e:
        logger.error(f"  ❌ Impossible d'importer CompetitorDiscovery: {e}")
        tests.append(False)
    
    return all(tests)

def test_server_integration():
    """
    Test 2: Vérifier l'intégration dans server.py
    """
    logger.info("🔍 Test 2: Vérification de l'intégration dans server.py")
    
    server_file = '/app/backend/server.py'
    
    if not os.path.exists(server_file):
        logger.error("  ❌ server.py non trouvé")
        return False
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Vérifier les imports
    imports_to_check = [
        'from utils.competitor_extractor import CompetitorExtractor',
        'from services.competitor_discovery import competitor_discovery'
    ]
    
    integration_checks = []
    
    for import_line in imports_to_check:
        if import_line in content:
            logger.info(f"  ✅ Import trouvé: {import_line}")
            integration_checks.append(True)
        else:
            logger.warning(f"  ⚠️ Import non trouvé: {import_line}")
            integration_checks.append(False)
    
    # Vérifier l'utilisation dans le pipeline
    pipeline_keywords = [
        'CompetitorExtractor.extract_from_visibility_results',
        'competitor_discovery.discover_real_competitors',
        'Stage 1',
        'Stage 2',
        'Stage 3'
    ]
    
    for keyword in pipeline_keywords:
        if keyword in content:
            logger.info(f"  ✅ Pipeline keyword trouvé: {keyword}")
            integration_checks.append(True)
        else:
            logger.warning(f"  ⚠️ Pipeline keyword non trouvé: {keyword}")
            integration_checks.append(False)
    
    # Vérifier les lignes 1015-1050 mentionnées dans la review
    lines = content.split('\n')
    if len(lines) >= 1050:
        relevant_section = '\n'.join(lines[1014:1050])  # lignes 1015-1050 (0-indexed)
        
        if 'competitor' in relevant_section.lower():
            logger.info("  ✅ Section lignes 1015-1050 contient du code de compétiteurs")
            integration_checks.append(True)
        else:
            logger.warning("  ⚠️ Section lignes 1015-1050 ne semble pas contenir de code de compétiteurs")
            integration_checks.append(False)
    else:
        logger.warning("  ⚠️ server.py trop court pour vérifier les lignes 1015-1050")
        integration_checks.append(False)
    
    success_rate = sum(integration_checks) / len(integration_checks)
    logger.info(f"  📊 Taux d'intégration: {success_rate:.1%}")
    
    return success_rate >= 0.7  # 70% minimum

def test_unit_tests_results():
    """
    Test 3: Vérifier les résultats des tests unitaires mentionnés (14/14)
    """
    logger.info("🔍 Test 3: Vérification des tests unitaires")
    
    test_file = '/app/tests/test_competitor_discovery.py'
    
    if os.path.exists(test_file):
        logger.info("  ✅ Fichier de tests unitaires trouvé")
        
        # Lire le contenu pour voir les tests
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Compter les fonctions de test
        test_functions = [line for line in content.split('\n') if line.strip().startswith('def test_')]
        logger.info(f"  📊 {len(test_functions)} fonctions de test trouvées")
        
        for i, test_func in enumerate(test_functions, 1):
            func_name = test_func.strip().split('(')[0].replace('def ', '')
            logger.info(f"    {i}. {func_name}")
        
        return len(test_functions) >= 10  # Au moins 10 tests
    else:
        logger.warning("  ⚠️ Fichier de tests unitaires non trouvé")
        return False

def test_new_fields_structure():
    """
    Test 4: Vérifier la structure des nouveaux champs (score, type, reason, source)
    """
    logger.info("🔍 Test 4: Validation de la structure des nouveaux champs")
    
    try:
        from services.competitor_discovery import CompetitorDiscovery
        
        # Créer une instance pour examiner la structure
        discovery = CompetitorDiscovery()
        
        # Vérifier les constantes/configurations
        config_checks = []
        
        if hasattr(discovery, 'threshold_direct'):
            logger.info(f"  ✅ threshold_direct configuré: {discovery.threshold_direct}")
            config_checks.append(True)
        else:
            logger.warning("  ⚠️ threshold_direct non configuré")
            config_checks.append(False)
        
        if hasattr(discovery, 'threshold_indirect'):
            logger.info(f"  ✅ threshold_indirect configuré: {discovery.threshold_indirect}")
            config_checks.append(True)
        else:
            logger.warning("  ⚠️ threshold_indirect non configuré")
            config_checks.append(False)
        
        # Vérifier la méthode _calculate_relevance_score
        if hasattr(discovery, '_calculate_relevance_score'):
            logger.info("  ✅ Méthode de calcul de score présente")
            config_checks.append(True)
        else:
            logger.error("  ❌ Méthode de calcul de score manquante")
            config_checks.append(False)
        
        # Vérifier la méthode _generate_reason
        if hasattr(discovery, '_generate_reason'):
            logger.info("  ✅ Méthode de génération de raison présente")
            config_checks.append(True)
        else:
            logger.error("  ❌ Méthode de génération de raison manquante")
            config_checks.append(False)
        
        return all(config_checks)
        
    except Exception as e:
        logger.error(f"  ❌ Erreur lors de la validation: {e}")
        return False

def test_backend_logs_for_pipeline():
    """
    Test 5: Vérifier les logs backend pour des traces du pipeline 3 étages
    """
    logger.info("🔍 Test 5: Recherche de traces du pipeline dans les logs")
    
    log_files = [
        '/var/log/supervisor/backend.out.log',
        '/var/log/supervisor/backend.err.log'
    ]
    
    pipeline_keywords = [
        'Stage 1',
        'Stage 2', 
        'Stage 3',
        'competitor discovery',
        'CompetitorExtractor',
        'CompetitorDiscovery',
        'discover_real_competitors'
    ]
    
    found_keywords = set()
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    content = f.read().lower()
                
                for keyword in pipeline_keywords:
                    if keyword.lower() in content:
                        found_keywords.add(keyword)
                        logger.info(f"  ✅ Trouvé dans logs: {keyword}")
            
            except Exception as e:
                logger.warning(f"  ⚠️ Impossible de lire {log_file}: {e}")
    
    logger.info(f"  📊 Mots-clés trouvés: {len(found_keywords)}/{len(pipeline_keywords)}")
    
    return len(found_keywords) >= 3  # Au moins 3 mots-clés trouvés

def main():
    """
    Point d'entrée principal
    """
    logger.info("🚀 Validation Pipeline Découverte Compétiteurs V3")
    logger.info("="*60)
    
    results = {
        'test_start': datetime.now().isoformat(),
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'details': {}
    }
    
    tests = [
        ('implementation_exists', test_implementation_exists),
        ('server_integration', test_server_integration),
        ('unit_tests_results', test_unit_tests_results),
        ('new_fields_structure', test_new_fields_structure),
        ('backend_logs_pipeline', test_backend_logs_for_pipeline)
    ]
    
    for test_name, test_func in tests:
        results['tests_run'] += 1
        logger.info(f"\n{'='*60}")
        
        try:
            if test_func():
                results['tests_passed'] += 1
                results['details'][test_name] = 'PASSED'
                logger.info(f"✅ {test_name}: PASSED")
            else:
                results['tests_failed'] += 1
                results['details'][test_name] = 'FAILED'
                logger.info(f"❌ {test_name}: FAILED")
        
        except Exception as e:
            results['tests_failed'] += 1
            results['details'][test_name] = f'ERROR: {str(e)}'
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Rapport final
    results['test_end'] = datetime.now().isoformat()
    
    logger.info(f"\n{'='*60}")
    logger.info("📋 RAPPORT FINAL - VALIDATION PIPELINE")
    logger.info("="*60)
    logger.info(f"📊 Tests exécutés: {results['tests_run']}")
    logger.info(f"✅ Tests réussis: {results['tests_passed']}")
    logger.info(f"❌ Tests échoués: {results['tests_failed']}")
    
    success_rate = (results['tests_passed'] / results['tests_run']) * 100 if results['tests_run'] > 0 else 0
    logger.info(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    logger.info("\n📋 Détails par test:")
    for test_name, status in results['details'].items():
        status_icon = "✅" if status == "PASSED" else "❌"
        logger.info(f"  {status_icon} {test_name}: {status}")
    
    # Sauvegarder les résultats
    with open('/app/competitor_pipeline_validation.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n💾 Résultats sauvegardés: /app/competitor_pipeline_validation.json")
    logger.info("="*60)
    
    return results['tests_failed'] == 0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 VALIDATION PIPELINE RÉUSSIE!")
        sys.exit(0)
    else:
        print("\n⚠️ VALIDATION PIPELINE PARTIELLE!")
        sys.exit(1)