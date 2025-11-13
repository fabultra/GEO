"""
API FLASK POUR INTERACTIVITÉ TEMPS RÉEL
Permet d'ajouter des requêtes et de re-tester en temps réel depuis le dashboard
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Import des modules
from query_generator_v2 import IntelligentQueryGenerator
from visibility_tester_v2 import VisibilityTesterV2

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Activer CORS pour permettre les requêtes depuis le dashboard HTML

# Configuration
QUERIES_CONFIG_PATH = '/app/backend/queries_config.json'
VISIBILITY_RESULTS_PATH = '/app/backend/visibility_results.json'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier que l'API est active"""
    return jsonify({
        'status': 'ok',
        'message': 'Visibility API is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/queries/config', methods=['GET'])
def get_queries_config():
    """Récupérer la configuration des requêtes"""
    try:
        with open(QUERIES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except FileNotFoundError:
        return jsonify({'error': 'Configuration file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/queries/add', methods=['POST'])
def add_query():
    """
    Ajouter une requête manuelle et la tester immédiatement
    
    Body JSON:
    {
        "query": "meilleurs courtiers assurance Montréal",
        "priority": "high|medium|low",
        "site_url": "https://example.com",
        "company_name": "Example Inc"
    }
    """
    try:
        data = request.json
        query = data.get('query')
        priority = data.get('priority', 'medium')
        site_url = data.get('site_url')
        company_name = data.get('company_name')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Charger la config existante
        try:
            with open(QUERIES_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            # Créer nouvelle config
            config = {
                'site_url': site_url,
                'auto_generated_queries': [],
                'manual_queries': [],
                'excluded_queries': [],
                'query_metadata': {}
            }
        
        # Ajouter la requête
        if query not in config['manual_queries']:
            config['manual_queries'].append(query)
            config['query_metadata'][query] = {
                'priority': priority,
                'added_manually': True,
                'added_date': datetime.now().isoformat()
            }
            
            # Sauvegarder la config
            with open(QUERIES_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Tester immédiatement la requête (si priority = high)
        test_result = None
        if priority == 'high' and site_url and company_name:
            try:
                tester = VisibilityTesterV2()
                test_result = tester.test_all_queries_detailed([query], site_url, company_name)
                
                # Mettre à jour visibility_results.json
                update_visibility_results(query, test_result)
            except Exception as e:
                logger.error(f"Error testing query: {str(e)}")
                test_result = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'message': f'Query "{query}" added successfully',
            'test_result': test_result,
            'config': config
        })
        
    except Exception as e:
        logger.error(f"Error adding query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queries/retest', methods=['POST'])
def retest_query():
    """
    Re-tester une requête existante
    
    Body JSON:
    {
        "query": "meilleurs courtiers assurance Montréal",
        "site_url": "https://example.com",
        "company_name": "Example Inc"
    }
    """
    try:
        data = request.json
        query = data.get('query')
        site_url = data.get('site_url')
        company_name = data.get('company_name')
        
        if not query or not site_url or not company_name:
            return jsonify({'error': 'query, site_url and company_name are required'}), 400
        
        # Tester la requête
        tester = VisibilityTesterV2()
        test_result = tester.test_all_queries_detailed([query], site_url, company_name)
        
        # Mettre à jour visibility_results.json
        update_visibility_results(query, test_result)
        
        return jsonify({
            'success': True,
            'message': f'Query "{query}" retested successfully',
            'test_result': test_result
        })
        
    except Exception as e:
        logger.error(f"Error retesting query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queries/delete', methods=['POST'])
def delete_query():
    """
    Supprimer une requête manuelle
    
    Body JSON:
    {
        "query": "meilleurs courtiers assurance Montréal"
    }
    """
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Charger la config
        with open(QUERIES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Supprimer la requête
        if query in config['manual_queries']:
            config['manual_queries'].remove(query)
            if query in config['query_metadata']:
                del config['query_metadata'][query]
            
            # Sauvegarder
            with open(QUERIES_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                'success': True,
                'message': f'Query "{query}" deleted successfully'
            })
        else:
            return jsonify({'error': 'Query not found in manual queries'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visibility/results', methods=['GET'])
def get_visibility_results():
    """Récupérer les résultats de visibilité"""
    try:
        with open(VISIBILITY_RESULTS_PATH, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return jsonify(results)
    except FileNotFoundError:
        return jsonify({'error': 'Results file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_visibility_results(query: str, test_result: Dict[str, Any]):
    """Mettre à jour le fichier de résultats avec un nouveau test"""
    try:
        # Charger les résultats existants
        try:
            with open(VISIBILITY_RESULTS_PATH, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except FileNotFoundError:
            results = {
                'site_url': test_result.get('site_url', ''),
                'company_name': test_result.get('company_name', ''),
                'last_updated': datetime.now().isoformat(),
                'queries': [],
                'summary': {
                    'total_queries': 0,
                    'global_visibility': 0.0,
                    'by_platform': {}
                }
            }
        
        # Trouver et mettre à jour la requête existante, ou l'ajouter
        query_found = False
        for i, q in enumerate(results['queries']):
            if q['query'] == query:
                results['queries'][i] = test_result['queries'][0]
                query_found = True
                break
        
        if not query_found:
            results['queries'].append(test_result['queries'][0])
        
        # Mettre à jour le timestamp
        results['last_updated'] = datetime.now().isoformat()
        
        # Recalculer les scores
        results['summary'] = test_result.get('summary', results['summary'])
        
        # Sauvegarder
        with open(VISIBILITY_RESULTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated visibility results for query: {query}")
        
    except Exception as e:
        logger.error(f"Error updating visibility results: {str(e)}")

if __name__ == '__main__':
    # Lancer le serveur Flask
    # Par défaut sur port 5000
    # Pour lancer: python api_visibility.py
    app.run(host='0.0.0.0', port=5000, debug=True)
