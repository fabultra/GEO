"""
GÉNÉRATEUR DE DASHBOARD INTERACTIF POUR VISIBILITÉ IA
Crée un dashboard HTML/CSS/JS interactif avec modals et formulaires
"""
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_interactive_dashboard(visibility_results: Dict[str, Any], output_path: str) -> str:
    """
    Génère un dashboard HTML interactif complet
    
    Args:
        visibility_results: Résultats des tests de visibilité
        output_path: Chemin où sauvegarder le dashboard
    
    Returns:
        Chemin du fichier généré
    """
    
    # Sauvegarder les données JSON pour le JavaScript
    json_path = output_path.replace('.html', '_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(visibility_results, f, ensure_ascii=False, indent=2)
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard GEO - Tests de Visibilité IA</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            text-align: center;
        }}
        
        .header h1 {{
            color: #1a1a1a;
            font-size: 42px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .header .site-info {{
            font-size: 18px;
            color: #666;
            margin: 10px 0;
        }}
        
        .score-global {{
            font-size: 72px;
            font-weight: bold;
            text-align: center;
            margin: 30px 0;
            padding: 50px;
            border-radius: 20px;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        
        .score-critical {{ color: #dc3545; }}
        .score-warning {{ color: #ffc107; }}
        .score-good {{ color: #28a745; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-tile {{
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .metric-tile::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }}
        
        .metric-tile:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
        }}
        
        .metric-tile:hover::before {{
            transform: scaleX(1);
        }}
        
        .metric-tile.clickable::after {{
            content: '🔍';
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 20px;
            opacity: 0.3;
            transition: opacity 0.3s;
        }}
        
        .metric-tile:hover.clickable::after {{
            opacity: 1;
        }}
        
        .metric-label {{
            font-size: 13px;
            color: #999;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 42px;
            font-weight: 700;
            margin: 15px 0;
            color: #1a1a1a;
        }}
        
        .metric-change {{
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .trend-up {{ color: #28a745; }}
        .trend-down {{ color: #dc3545; }}
        .trend-neutral {{ color: #6c757d; }}
        
        .platform-table {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        
        .platform-table h2 {{
            color: #1a1a1a;
            margin-bottom: 30px;
            font-size: 28px;
            font-weight: 700;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        th:first-child {{
            border-top-left-radius: 12px;
        }}
        
        th:last-child {{
            border-top-right-radius: 12px;
        }}
        
        td {{
            padding: 18px;
            border-bottom: 1px solid #e9ecef;
            transition: background 0.2s;
        }}
        
        tr:hover td {{
            background: #f8f9fa;
        }}
        
        td.clickable-cell {{
            cursor: pointer;
            position: relative;
        }}
        
        td.clickable-cell:hover {{
            background: #e9ecef;
        }}
        
        .status-visible {{
            color: #28a745;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .status-invisible {{
            color: #dc3545;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .modal.active {{
            display: flex;
        }}
        
        .modal-content {{
            background: white;
            border-radius: 24px;
            padding: 50px;
            max-width: 900px;
            max-height: 85vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.3s ease;
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(30px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        
        .modal-close {{
            position: absolute;
            top: 25px;
            right: 25px;
            font-size: 36px;
            cursor: pointer;
            color: #999;
            transition: color 0.2s, transform 0.2s;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}
        
        .modal-close:hover {{
            color: #dc3545;
            background: #fee;
            transform: rotate(90deg);
        }}
        
        .detail-section {{
            margin: 30px 0;
        }}
        
        .detail-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 15px;
            color: #1a1a1a;
        }}
        
        .reason-card {{
            background: #f8f9fa;
            border-left: 5px solid #dc3545;
            padding: 25px;
            margin: 20px 0;
            border-radius: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .reason-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .reason-card.severity-critical {{
            border-color: #dc3545;
            background: linear-gradient(to right, #fff5f5 0%, #ffffff 100%);
        }}
        
        .reason-card.severity-high {{
            border-color: #ff8c00;
            background: linear-gradient(to right, #fff8f0 0%, #ffffff 100%);
        }}
        
        .reason-card.severity-medium {{
            border-color: #ffc107;
            background: linear-gradient(to right, #fffef0 0%, #ffffff 100%);
        }}
        
        .reason-card h4 {{
            margin: 0 0 15px 0;
            color: #1a1a1a;
            font-size: 18px;
        }}
        
        .reason-card p {{
            margin: 10px 0;
            line-height: 1.6;
            color: #555;
        }}
        
        .action-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            margin: 12px 8px 12px 0;
            transition: all 0.3s;
            font-size: 15px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .action-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        
        .action-button:active {{
            transform: translateY(0);
        }}
        
        .add-query-form {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin: 30px 0;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }}
        
        .add-query-form h2 {{
            color: #1a1a1a;
            margin-bottom: 25px;
            font-size: 28px;
            font-weight: 700;
        }}
        
        .form-group {{
            margin: 25px 0;
        }}
        
        .form-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
            font-size: 15px;
        }}
        
        .form-group input,
        .form-group select {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        
        .form-group input:focus,
        .form-group select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .query-list {{
            list-style: none;
            padding: 0;
            margin-top: 20px;
        }}
        
        .query-item {{
            background: linear-gradient(to right, #f8f9fa 0%, #ffffff 100%);
            padding: 20px;
            margin: 15px 0;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #667eea;
        }}
        
        .query-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .delete-query {{
            color: #dc3545;
            cursor: pointer;
            font-size: 24px;
            transition: opacity 0.2s, transform 0.2s;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}
        
        .delete-query:hover {{
            opacity: 0.7;
            background: #fee;
            transform: scale(1.1);
        }}
        
        .loading {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        /* Nouveaux styles pour analyse compétitive enrichie */
        .analysis-section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .analysis-section h2 {{
            color: #1f2937;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 15px;
        }}
        
        .query-types-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .query-type-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .query-type-card h3 {{
            margin: 0 0 10px 0;
            color: #1e40af;
            text-transform: capitalize;
        }}
        
        .metric-large {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3b82f6;
            margin: 10px 0;
        }}
        
        .metric-label {{
            color: #64748b;
            font-size: 0.9em;
        }}
        
        .queries-list {{
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .queries-list ul {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        
        .queries-list li {{
            margin: 3px 0;
            color: #475569;
        }}
        
        .competitors-mini {{
            margin-top: 15px;
        }}
        
        .competitor-badge {{
            display: inline-block;
            background: #e0f2fe;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 0.85em;
            color: #0369a1;
        }}
        
        .competitive-summary {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .metric-box {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 50px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        .metric-box .metric-large {{
            color: white;
            font-size: 3em;
        }}
        
        .metric-box p {{
            margin-top: 10px;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .competitor-card-detailed {{
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 5px solid #10b981;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .competitor-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        .competitor-header h3 {{
            margin: 0;
            color: #1f2937;
        }}
        
        .visibility-badge {{
            background: #10b981;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
        }}
        
        .competitor-metrics {{
            display: flex;
            gap: 30px;
            margin: 15px 0;
        }}
        
        .competitor-metrics .metric {{
            color: #475569;
        }}
        
        .urls-section, .strengths-section {{
            margin: 15px 0;
            padding: 15px;
            background: #f8fafc;
            border-radius: 6px;
        }}
        
        .urls-list, .strengths-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .urls-list li {{
            margin: 8px 0;
        }}
        
        .urls-list a {{
            color: #2563eb;
            text-decoration: none;
            word-break: break-all;
        }}
        
        .urls-list a:hover {{
            text-decoration: underline;
        }}
        
        .strengths-list li {{
            margin: 8px 0;
            color: #059669;
        }}
        
        .mention-breakdown {{
            margin: 15px 0;
        }}
        
        .mention-types {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}
        
        .badge {{
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge-info {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .badge-neutral {{
            background: #f1f5f9;
            color: #475569;
        }}
        
        .queries-details {{
            margin-top: 15px;
            padding: 10px;
            background: #fafafa;
            border-radius: 4px;
            cursor: pointer;
        }}
        
        .queries-details summary {{
            font-weight: 500;
            color: #3b82f6;
        }}
        
        .queries-details ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .insights-section {{
            margin-top: 30px;
        }}
        
        .insight-card {{
            background: white;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 5px solid #f59e0b;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .insight-card.severity-critical {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        
        .insight-card.severity-high {{
            border-left-color: #f59e0b;
            background: #fffbeb;
        }}
        
        .insight-card.severity-medium {{
            border-left-color: #3b82f6;
            background: #eff6ff;
        }}
        
        .insight-header {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .severity-badge {{
            background: #ef4444;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .insight-type {{
            background: #e5e7eb;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            color: #374151;
        }}
        
        .insight-card h3 {{
            margin: 10px 0;
            color: #1f2937;
        }}
        
        .insight-details {{
            color: #4b5563;
            margin: 10px 0;
        }}
        
        .insight-action {{
            background: #f0fdf4;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
            border-left: 3px solid #10b981;
        }}
        
        .insight-action p {{
            margin: 5px 0;
            color: #065f46;
        }}
        
        .urls-to-analyze {{
            margin: 15px 0;
            padding: 15px;
            background: #eff6ff;
            border-radius: 6px;
        }}
        
        .urls-to-analyze ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .insight-example {{
            margin: 15px 0;
            padding: 10px;
            background: #f9fafb;
            border-left: 3px solid #6b7280;
            font-style: italic;
            color: #374151;
        }}
        
        .perceived-strengths {{
            margin: 15px 0;
            padding: 15px;
            background: #fef3c7;
            border-radius: 6px;
        }}
        
        .perceived-strengths ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔍 Tests de Visibilité IA</h1>
            <div class="site-info"><strong>Site:</strong> {visibility_results.get('site_url', 'N/A')}</div>
            <div class="site-info"><strong>Entreprise:</strong> {visibility_results.get('company_name', 'N/A')}</div>
            <div class="site-info"><strong>Dernière mise à jour:</strong> {datetime.now().strftime('%d %B %Y à %H:%M')}</div>
        </div>
        
        <!-- Score Global -->
        <div class="score-global score-{get_score_class(visibility_results.get('summary', {}).get('global_visibility', 0))}">
            Score de Visibilité: <span id="visibility-score">{visibility_results.get('summary', {}).get('global_visibility', 0) * 100:.1f}</span>%
        </div>
        
        <!-- Métriques cliquables -->
        <div class="metrics-grid" id="metrics-grid">
            <!-- Sera rempli par JavaScript -->
        </div>
        
        <!-- Tableau des requêtes -->
        <div class="platform-table">
            <h2>📋 Requêtes Testées & Résultats</h2>
            <table>
                <thead>
                    <tr>
                        <th>Requête</th>
                        <th>ChatGPT</th>
                        <th>Claude</th>
                        <th>Perplexity</th>
                        <th>Gemini</th>
                        <th>Google AI</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="queries-tbody">
                    <!-- Sera rempli par JavaScript -->
                </tbody>
            </table>
        </div>
        
        <!-- Formulaire ajout de requête -->
        <div class="add-query-form">
            <h2>➕ Ajouter une Requête Personnalisée</h2>
            <p style="color: #666; margin-bottom: 20px;">
                Ajoutez vos propres requêtes pour tester votre visibilité sur des termes spécifiques.
            </p>
            <form id="add-query-form">
                <div class="form-group">
                    <label for="new-query">Requête à tester</label>
                    <input type="text" id="new-query" placeholder="Ex: meilleurs courtiers assurance Montréal" required>
                </div>
                
                <div class="form-group">
                    <label for="query-priority">Priorité</label>
                    <select id="query-priority">
                        <option value="high">Haute - Test immédiat</option>
                        <option value="medium" selected>Moyenne - Test dans 1h</option>
                        <option value="low">Basse - Test prochain run (2 semaines)</option>
                    </select>
                </div>
                
                <button type="submit" class="action-button">
                    Ajouter et Tester
                </button>
            </form>
            
            <h3 style="margin-top: 40px; color: #1a1a1a; font-size: 22px;">Requêtes Personnalisées Actives</h3>
            <ul class="query-list" id="custom-queries-list">
                <li class="query-item" style="background: #f0f0f0; border-left-color: #999;">
                    <span style="color: #999;">Aucune requête personnalisée pour le moment</span>
                </li>
            </ul>
        </div>
    </div>
    
    <!-- Modal de détails -->
    <div class="modal" id="details-modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modal-body">
                <!-- Contenu dynamique -->
            </div>
        </div>
    </div>
    
    <script>
        // Charger les données depuis le JSON
        let queryData = {json.dumps(visibility_results, ensure_ascii=False)};
        
        // Initialiser le dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            renderMetrics();
            renderTable();
        }});
        
        // Afficher les métriques
        function renderMetrics() {{
            const metrics = document.getElementById('metrics-grid');
            const summary = queryData.summary || {{}};
            const platforms = summary.by_platform || {{}};
            
            // Métrique globale
            metrics.innerHTML = `
                <div class="metric-tile clickable" onclick="showGlobalDetails()">
                    <div class="metric-label">Visibilité Globale</div>
                    <div class="metric-value">${{(summary.global_visibility * 100).toFixed(1)}}%</div>
                    <div class="metric-change trend-neutral">Moyenne 5 plateformes</div>
                </div>
            `;
            
            // Métriques par plateforme
            const platformNames = {{
                'chatgpt': 'ChatGPT',
                'claude': 'Claude',
                'perplexity': 'Perplexity',
                'gemini': 'Gemini',
                'google_ai': 'Google AI'
            }};
            
            for (const [key, name] of Object.entries(platformNames)) {{
                const score = (platforms[key] || 0) * 100;
                const trendClass = score > 20 ? 'trend-up' : score > 0 ? 'trend-neutral' : 'trend-down';
                
                metrics.innerHTML += `
                    <div class="metric-tile clickable" onclick="showPlatformDetails('${{key}}')">
                        <div class="metric-label">${{name}}</div>
                        <div class="metric-value">${{score.toFixed(1)}}%</div>
                        <div class="metric-change ${{trendClass}}">${{score > 0 ? '✓' : '✗'}} Testé</div>
                    </div>
                `;
            }}
        }}
        
        // Afficher le tableau
        function renderTable() {{
            const tbody = document.getElementById('queries-tbody');
            tbody.innerHTML = '';
            
            const queries = queryData.queries || [];
            
            queries.forEach((queryObj, index) => {{
                const platforms = queryObj.platforms || {{}};
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${{queryObj.query}}</strong></td>
                    ${{renderPlatformCell(queryObj.query, 'chatgpt', platforms.chatgpt)}}
                    ${{renderPlatformCell(queryObj.query, 'claude', platforms.claude)}}
                    ${{renderPlatformCell(queryObj.query, 'perplexity', platforms.perplexity)}}
                    ${{renderPlatformCell(queryObj.query, 'gemini', platforms.gemini)}}
                    ${{renderPlatformCell(queryObj.query, 'google_ai', platforms.google_ai)}}
                    <td>
                        <button class="action-button" onclick="retestQuery('${{queryObj.query}}')" style="padding: 8px 16px; font-size: 13px;">
                            🔄 Re-tester
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            }});
        }}
        
        function renderPlatformCell(query, platform, data) {{
            const mentioned = data && data.mentioned;
            const statusClass = mentioned ? 'status-visible' : 'status-invisible';
            const statusText = mentioned ? '✅ Visible' : '❌ Invisible';
            
            return `
                <td class="clickable-cell ${{statusClass}}" onclick="showQueryDetails('${{query}}', '${{platform}}')">
                    ${{statusText}}
                </td>
            `;
        }}
        
        // Afficher détails d'une requête
        function showQueryDetails(query, platform) {{
            const queryObj = queryData.queries.find(q => q.query === query);
            if (!queryObj) return;
            
            const platformData = queryObj.platforms[platform];
            if (!platformData) return;
            
            let modalContent = `
                <h2 style="margin-bottom: 10px;">🔍 Détails: "${{query}}"</h2>
                <h3 style="color: #666; margin-bottom: 30px;">Plateforme: ${{platform.toUpperCase()}}</h3>
                
                <div class="detail-section">
                    <div class="detail-title">Statut</div>
                    <p style="font-size: 24px; font-weight: 600;">
                        ${{platformData.mentioned ? 
                            `✅ <span style="color: #28a745;">Visible</span>${{platformData.position ? ` - Position ${{platformData.position}}` : ''}}` : 
                            `❌ <span style="color: #dc3545;">Invisible</span>`
                        }}
                    </p>
                </div>
            `;
            
            if (platformData.mentioned && platformData.context_snippet) {{
                modalContent += `
                    <div class="detail-section">
                        <div class="detail-title">Contexte de la Mention</div>
                        <p style="background: #f8f9fa; padding: 20px; border-radius: 12px; line-height: 1.8;">
                            "${{platformData.context_snippet}}"
                        </p>
                    </div>
                `;
                
                if (platformData.competitors_mentioned && platformData.competitors_mentioned.length > 0) {{
                    modalContent += `
                        <div class="detail-section">
                            <div class="detail-title">Compétiteurs Également Cités</div>
                            <ul style="padding-left: 20px;">
                                ${{platformData.competitors_mentioned.map(c => `<li style="margin: 8px 0;">${{c}}</li>`).join('')}}
                            </ul>
                        </div>
                    `;
                }}
            }} else {{
                // Afficher les raisons d'invisibilité
                const reasons = platformData.invisibility_reasons || [];
                
                if (reasons.length > 0) {{
                    modalContent += `
                        <div class="detail-section">
                            <div class="detail-title">🚨 Pourquoi Vous Êtes Invisible</div>
                    `;
                    
                    reasons.forEach(reason => {{
                        modalContent += `
                            <div class="reason-card severity-${{reason.severity.toLowerCase()}}">
                                <h4>${{reason.explanation}}</h4>
                                <p><strong>Action:</strong> ${{reason.action}}</p>
                                ${{reason.example_title ? `<p style="font-style: italic; color: #666;">Exemple: ${{reason.example_title}}</p>` : ''}}
                                <p><strong>Impact estimé:</strong> <span style="color: #28a745; font-weight: 600;">${{reason.estimated_impact}}</span></p>
                            </div>
                        `;
                    }});
                    
                    modalContent += `</div>`;
                }}
                
                // Compétiteurs qui apparaissent
                if (platformData.competitors_mentioned && platformData.competitors_mentioned.length > 0) {{
                    modalContent += `
                        <div class="detail-section">
                            <div class="detail-title">🏆 Qui Apparaît à Votre Place</div>
                            <ul style="padding-left: 20px;">
                                ${{platformData.competitors_mentioned.map(c => `<li style="margin: 8px 0;">${{c}}</li>`).join('')}}
                            </ul>
                            <p style="margin-top: 15px; color: #666; font-style: italic;">Analysez ces compétiteurs pour comprendre ce qu'ils font mieux.</p>
                        </div>
                    `;
                }}
            }}
            
            // Réponse complète (collapsible)
            if (platformData.full_response) {{
                modalContent += `
                    <div class="detail-section">
                        <details style="cursor: pointer;">
                            <summary style="font-weight: 600; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                📄 Voir la Réponse Complète du LLM
                            </summary>
                            <pre style="background: #f8f9fa; padding: 25px; border-radius: 12px; overflow-x: auto; white-space: pre-wrap; margin-top: 15px; line-height: 1.6;">
${{platformData.full_response}}
                            </pre>
                        </details>
                    </div>
                `;
            }}
            
            modalContent += `
                <button class="action-button" onclick="closeModal()" style="margin-top: 25px;">Fermer</button>
            `;
            
            document.getElementById('modal-body').innerHTML = modalContent;
            document.getElementById('details-modal').classList.add('active');
        }}
        
        // Afficher détails globaux
        function showGlobalDetails() {{
            const summary = queryData.summary || {{}};
            
            let modalContent = `
                <h2>📊 Analyse Globale de Visibilité</h2>
                
                <div class="detail-section">
                    <p style="font-size: 18px;"><strong>Visibilité Globale:</strong> ${{(summary.global_visibility * 100).toFixed(1)}}%</p>
                    <p style="font-size: 18px;"><strong>Requêtes testées:</strong> ${{queryData.queries ? queryData.queries.length : 0}}</p>
                </div>
                
                <div class="detail-section">
                    <div class="detail-title">🎯 Recommandations Prioritaires</div>
                    <div class="reason-card severity-critical">
                        <h4>Créer du contenu éducatif</h4>
                        <p>Votre faible visibilité indique un manque de contenu informatif et éducatif. Créez 10-15 articles de 2000+ mots sur des sujets pertinents.</p>
                    </div>
                    <div class="reason-card severity-high">
                        <h4>Ajouter des statistiques et données</h4>
                        <p>Les IA privilégient le contenu riche en données. Ajoutez 10-15 statistiques avec sources dans chaque page principale.</p>
                    </div>
                    <div class="reason-card severity-high">
                        <h4>Implémenter des schemas JSON-LD</h4>
                        <p>Ajoutez Organization, Article et FAQPage schemas pour améliorer la compréhension par les IA.</p>
                    </div>
                </div>
                
                <button class="action-button" onclick="closeModal()">Fermer</button>
            `;
            
            document.getElementById('modal-body').innerHTML = modalContent;
            document.getElementById('details-modal').classList.add('active');
        }}
        
        // Afficher détails d'une plateforme
        function showPlatformDetails(platform) {{
            const platformNames = {{
                'chatgpt': 'ChatGPT',
                'claude': 'Claude',
                'perplexity': 'Perplexity',
                'gemini': 'Gemini',
                'google_ai': 'Google AI'
            }};
            
            const summary = queryData.summary || {{}};
            const visibility = ((summary.by_platform || {{}})[platform] || 0) * 100;
            
            let modalContent = `
                <h2>📊 Analyse ${{platformNames[platform]}}</h2>
                
                <div class="detail-section">
                    <p style="font-size: 20px; font-weight: 600;">Visibilité: ${{visibility.toFixed(1)}}%</p>
                </div>
                
                <div class="detail-section">
                    <div class="detail-title">📋 Requêtes Testées</div>
                    <p>Cliquez sur n'importe quelle requête dans le tableau pour voir les détails spécifiques à ${{platformNames[platform]}}.</p>
                </div>
                
                <button class="action-button" onclick="closeModal()">Fermer</button>
            `;
            
            document.getElementById('modal-body').innerHTML = modalContent;
            document.getElementById('details-modal').classList.add('active');
        }}
        
        // Fermer modal
        function closeModal() {{
            document.getElementById('details-modal').classList.remove('active');
        }}
        
        // Fermer modal en cliquant en dehors
        document.getElementById('details-modal').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeModal();
            }}
        }});
        
        // Ajouter une requête personnalisée
        document.getElementById('add-query-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            const newQuery = document.getElementById('new-query').value;
            const priority = document.getElementById('query-priority').value;
            
            alert(`Fonctionnalité en développement!\\n\\nRequête "${{newQuery}}" sera testée avec priorité ${{priority}}.\\n\\nPour l'instant, ajoutez manuellement la requête dans queries_config.json et relancez l'analyse.`);
            
            document.getElementById('new-query').value = '';
        }});
        
        // Re-tester une requête
        function retestQuery(query) {{
            if (confirm(`Re-tester la requête "${{query}}" sur toutes les plateformes ?\\n\\nNote: Cette fonctionnalité nécessite l'API Flask active.`)) {{
                alert('Fonctionnalité en développement!\\n\\nPour l'instant, relancez une analyse complète pour re-tester les requêtes.');
            }}
        }}
    </script>
</body>
</html>"""
    
    # Écrire le fichier HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Interactive dashboard generated: {output_path}")
    
    return output_path


def get_score_class(score: float) -> str:
    """Retourner la classe CSS selon le score"""
    if score >= 0.5:
        return 'score-good'
    elif score >= 0.2:
        return 'score-warning'
    else:
        return 'score-critical'
