#!/usr/bin/env python3
"""
Diagnostic rapide du backend GEO SaaS basé sur les fichiers existants
"""
import json
import logging
import os
import sys
from datetime import datetime
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_existing_reports():
    """Analyser les rapports existants sur le disque"""
    logger.info("🔍 Analyse des rapports existants")
    
    dashboards_dir = "/app/backend/dashboards"
    reports_dir = "/app/backend/reports"
    
    results = {
        'dashboards_found': 0,
        'reports_found': 0,
        'report_ids': [],
        'dashboard_files': [],
        'report_files': []
    }
    
    # Analyser les dashboards
    if os.path.exists(dashboards_dir):
        dashboard_files = [f for f in os.listdir(dashboards_dir) if f.endswith('.html')]
        results['dashboards_found'] = len(dashboard_files)
        results['dashboard_files'] = dashboard_files[:5]  # Premiers 5
        
        # Extraire les IDs de rapport
        for file in dashboard_files:
            if '_dashboard.html' in file:
                report_id = file.replace('_dashboard.html', '')
                if report_id not in results['report_ids']:
                    results['report_ids'].append(report_id)
    
    # Analyser les rapports Word
    if os.path.exists(reports_dir):
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.docx')]
        results['reports_found'] = len(report_files)
        results['report_files'] = report_files[:5]  # Premiers 5
    
    logger.info(f"📊 Dashboards trouvés: {results['dashboards_found']}")
    logger.info(f"📊 Rapports Word trouvés: {results['reports_found']}")
    logger.info(f"📊 IDs de rapport identifiés: {len(results['report_ids'])}")
    
    return results

def analyze_backend_logs():
    """Analyser les logs backend pour identifier les problèmes"""
    logger.info("🔍 Analyse des logs backend")
    
    log_files = [
        '/var/log/supervisor/backend.err.log',
        '/var/log/supervisor/backend.out.log'
    ]
    
    issues = {
        'critical_errors': [],
        'api_errors': [],
        'timeout_errors': [],
        'model_errors': [],
        'recent_activity': []
    }
    
    for log_file in log_files:
        try:
            result = subprocess.run(['tail', '-n', '100', log_file], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # Erreurs critiques
                    if any(keyword in line for keyword in ['CRITICAL', 'Exception', 'Traceback']):
                        issues['critical_errors'].append(line.strip())
                    
                    # Erreurs API
                    elif any(keyword in line for keyword in ['404', '500', 'HTTP', 'API']):
                        issues['api_errors'].append(line.strip())
                    
                    # Erreurs de timeout
                    elif any(keyword in line for keyword in ['timeout', 'Timeout', 'timed out']):
                        issues['timeout_errors'].append(line.strip())
                    
                    # Erreurs de modèle
                    elif any(keyword in line for keyword in ['model not found', 'models/', 'sequence item']):
                        issues['model_errors'].append(line.strip())
                    
                    # Activité récente
                    elif any(keyword in line for keyword in ['INFO', 'Testing query', 'Analysis']):
                        issues['recent_activity'].append(line.strip())
        
        except Exception as e:
            logger.warning(f"⚠️ Impossible de lire {log_file}: {e}")
    
    # Résumé des problèmes
    logger.info(f"🚨 Erreurs critiques: {len(issues['critical_errors'])}")
    logger.info(f"🌐 Erreurs API: {len(issues['api_errors'])}")
    logger.info(f"⏰ Erreurs timeout: {len(issues['timeout_errors'])}")
    logger.info(f"🤖 Erreurs modèle: {len(issues['model_errors'])}")
    logger.info(f"📋 Activité récente: {len(issues['recent_activity'])}")
    
    return issues

def check_api_models():
    """Vérifier les modèles API configurés"""
    logger.info("🔍 Vérification des modèles API")
    
    env_file = "/app/backend/.env"
    api_keys = {}
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if 'API_KEY' in key:
                        api_keys[key] = value.replace('"', '')[:20] + "..." if len(value) > 20 else value
    except Exception as e:
        logger.error(f"❌ Impossible de lire {env_file}: {e}")
        return {}
    
    logger.info("🔑 Clés API configurées:")
    for key, value in api_keys.items():
        logger.info(f"  • {key}: {value}")
    
    return api_keys

def analyze_visibility_data():
    """Analyser les données de visibilité existantes"""
    logger.info("🔍 Analyse des données de visibilité")
    
    dashboards_dir = "/app/backend/dashboards"
    visibility_files = []
    
    if os.path.exists(dashboards_dir):
        visibility_files = [f for f in os.listdir(dashboards_dir) if 'visibility_dashboard_data.json' in f]
    
    if not visibility_files:
        logger.warning("⚠️ Aucun fichier de données de visibilité trouvé")
        return {}
    
    # Analyser le premier fichier trouvé
    try:
        with open(os.path.join(dashboards_dir, visibility_files[0]), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        queries = data.get('queries', [])
        
        logger.info(f"📊 Visibilité globale: {summary.get('global_visibility', 0):.1%}")
        logger.info(f"📊 Requêtes testées: {len(queries)}")
        logger.info(f"📊 Plateformes: {list(summary.get('by_platform', {}).keys())}")
        
        # Analyser les erreurs dans les requêtes
        platform_errors = {}
        for query in queries[:10]:  # Premiers 10
            for platform, platform_data in query.get('platforms', {}).items():
                if platform_data.get('error'):
                    if platform not in platform_errors:
                        platform_errors[platform] = 0
                    platform_errors[platform] += 1
        
        if platform_errors:
            logger.warning("⚠️ Erreurs par plateforme:")
            for platform, count in platform_errors.items():
                logger.warning(f"  • {platform}: {count} erreurs")
        
        return {
            'visibility_files_found': len(visibility_files),
            'global_visibility': summary.get('global_visibility', 0),
            'queries_tested': len(queries),
            'platform_errors': platform_errors
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse visibilité: {e}")
        return {}

def check_service_status():
    """Vérifier le statut des services"""
    logger.info("🔍 Vérification du statut des services")
    
    try:
        result = subprocess.run(['sudo', 'supervisorctl', 'status'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            services = {}
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        service_name = parts[0]
                        status = parts[1]
                        services[service_name] = status
            
            logger.info("🔧 Statut des services:")
            for service, status in services.items():
                status_icon = "✅" if status == "RUNNING" else "❌"
                logger.info(f"  {status_icon} {service}: {status}")
            
            return services
        else:
            logger.error("❌ Impossible de vérifier le statut des services")
            return {}
    
    except Exception as e:
        logger.error(f"❌ Erreur vérification services: {e}")
        return {}

def generate_diagnostic_report():
    """Générer le rapport de diagnostic complet"""
    logger.info("🚀 DIAGNOSTIC BACKEND GEO SAAS")
    logger.info("="*60)
    
    diagnostic = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'reports': {},
        'logs': {},
        'api_keys': {},
        'visibility': {},
        'issues_found': [],
        'recommendations': []
    }
    
    # 1. Vérifier les services
    diagnostic['services'] = check_service_status()
    
    # 2. Analyser les rapports existants
    diagnostic['reports'] = analyze_existing_reports()
    
    # 3. Analyser les logs
    diagnostic['logs'] = analyze_backend_logs()
    
    # 4. Vérifier les clés API
    diagnostic['api_keys'] = check_api_models()
    
    # 5. Analyser les données de visibilité
    diagnostic['visibility'] = analyze_visibility_data()
    
    # Identifier les problèmes
    issues = []
    recommendations = []
    
    # Problèmes de service
    if diagnostic['services']:
        non_running = [s for s, status in diagnostic['services'].items() if status != 'RUNNING']
        if non_running:
            issues.append(f"Services non actifs: {', '.join(non_running)}")
            recommendations.append("Redémarrer les services non actifs avec supervisorctl")
    
    # Problèmes d'API
    if diagnostic['logs']['model_errors']:
        issues.append(f"Erreurs de modèle API: {len(diagnostic['logs']['model_errors'])} occurrences")
        recommendations.append("Vérifier les modèles Gemini et Claude configurés")
    
    if diagnostic['logs']['api_errors']:
        issues.append(f"Erreurs API: {len(diagnostic['logs']['api_errors'])} occurrences")
        recommendations.append("Vérifier les clés API et quotas")
    
    # Problèmes de performance
    if diagnostic['logs']['timeout_errors']:
        issues.append(f"Erreurs de timeout: {len(diagnostic['logs']['timeout_errors'])} occurrences")
        recommendations.append("Optimiser les timeouts et la performance")
    
    # Problèmes de visibilité
    if diagnostic['visibility'].get('platform_errors'):
        total_errors = sum(diagnostic['visibility']['platform_errors'].values())
        issues.append(f"Erreurs de plateforme de visibilité: {total_errors} total")
        recommendations.append("Corriger les erreurs d'API des plateformes de visibilité")
    
    diagnostic['issues_found'] = issues
    diagnostic['recommendations'] = recommendations
    
    # Rapport final
    logger.info("\n📋 RÉSUMÉ DU DIAGNOSTIC")
    logger.info("="*40)
    
    logger.info(f"🔧 Services actifs: {sum(1 for s in diagnostic['services'].values() if s == 'RUNNING')}/{len(diagnostic['services'])}")
    logger.info(f"📊 Rapports générés: {diagnostic['reports']['dashboards_found']} dashboards, {diagnostic['reports']['reports_found']} DOCX")
    logger.info(f"🔑 Clés API configurées: {len(diagnostic['api_keys'])}")
    logger.info(f"👁️ Visibilité globale: {diagnostic['visibility'].get('global_visibility', 0):.1%}")
    
    if issues:
        logger.info(f"\n🚨 PROBLÈMES IDENTIFIÉS ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            logger.info(f"  {i}. {issue}")
    
    if recommendations:
        logger.info(f"\n💡 RECOMMANDATIONS ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec}")
    
    # Sauvegarder le diagnostic
    with open('/app/backend_diagnostic_report.json', 'w', encoding='utf-8') as f:
        json.dump(diagnostic, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n💾 Diagnostic sauvegardé: /app/backend_diagnostic_report.json")
    
    # Score global
    total_checks = 5  # services, reports, api_keys, visibility, logs
    passed_checks = 0
    
    if diagnostic['services'] and all(s == 'RUNNING' for s in diagnostic['services'].values()):
        passed_checks += 1
    
    if diagnostic['reports']['dashboards_found'] > 0:
        passed_checks += 1
    
    if len(diagnostic['api_keys']) >= 3:  # Au moins 3 clés API
        passed_checks += 1
    
    if diagnostic['visibility'].get('queries_tested', 0) > 0:
        passed_checks += 1
    
    if len(diagnostic['logs']['critical_errors']) == 0:
        passed_checks += 1
    
    score = (passed_checks / total_checks) * 100
    logger.info(f"\n📊 SCORE GLOBAL: {passed_checks}/{total_checks} ({score:.1f}%)")
    
    if score >= 80:
        logger.info("🎉 BACKEND EN BON ÉTAT")
        return 0
    elif score >= 60:
        logger.info("⚠️ BACKEND FONCTIONNEL AVEC PROBLÈMES MINEURS")
        return 0
    else:
        logger.error("❌ BACKEND AVEC PROBLÈMES CRITIQUES")
        return 1

def main():
    return generate_diagnostic_report()

if __name__ == "__main__":
    sys.exit(main())