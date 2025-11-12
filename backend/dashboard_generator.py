"""
Générateur de dashboard HTML interactif
"""
from datetime import datetime
from typing import Dict, Any
import json

def generate_dashboard_html(report_data: Dict[str, Any], file_path: str) -> str:
    """Génère un dashboard HTML interactif"""
    
    scores = report_data.get('scores', {})
    visibility = report_data.get('visibility_results', {})
    platform_scores = visibility.get('platform_scores', {})
    
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>GEO Dashboard - {report_data['url']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #1a1a1a;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            color: #1a1a1a;
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .header .url {{
            color: #666;
            font-size: 18px;
        }}
        
        .header .timestamp {{
            color: #999;
            font-size: 14px;
            margin-top: 10px;
        }}
        
        .score-global {{
            text-align: center;
            font-size: 72px;
            font-weight: bold;
            margin: 30px 0;
            padding: 40px;
            border-radius: 12px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }}
        
        .score-critical {{ color: #dc3545; }}
        .score-warning {{ color: #ffc107; }}
        .score-good {{ color: #28a745; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        
        .metric-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}
        
        .metric-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #1a1a1a;
        }}
        
        .trend {{
            margin-top: 10px;
            font-size: 14px;
        }}
        
        .trend.up {{ color: #28a745; }}
        .trend.down {{ color: #dc3545; }}
        
        .platform-bars {{
            margin: 40px 0;
        }}
        
        .platform-bar {{
            margin-bottom: 20px;
        }}
        
        .platform-name {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }}
        
        .bar-container {{
            background: #e9ecef;
            border-radius: 20px;
            height: 30px;
            position: relative;
            overflow: hidden;
        }}
        
        .bar-fill {{
            background: linear-gradient(90deg, #1a1a1a 0%, #4a4a4a 100%);
            height: 100%;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 15px;
            color: white;
            font-weight: bold;
            font-size: 14px;
            transition: width 1s ease;
        }}
        
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
        }}
        
        .section h2 {{
            color: #1a1a1a;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 30px 0;
        }}
        
        .alert {{
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        
        .alert-critical {{
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid #dc3545;
        }}
        
        .alert-warning {{
            background: #fef3c7;
            color: #92400e;
            border-left: 4px solid #ffc107;
        }}
        
        .alert-success {{
            background: #dcfce7;
            color: #166534;
            border-left: 4px solid #28a745;
        }}
        
        .action-list {{
            list-style: none;
        }}
        
        .action-list li {{
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #1a1a1a;
        }}
        
        .action-list li:before {{
            content: "→";
            margin-right: 10px;
            font-weight: bold;
            color: #1a1a1a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 GEO Monitoring Dashboard</h1>
            <div class="url">{report_data['url']}</div>
            <div class="timestamp">Dernière mise à jour: {datetime.now().strftime('%d %B %Y à %H:%M')}</div>
        </div>
        
        <!-- Score Global -->
        <div class="score-global {get_score_class(scores.get('global_score', 0))}">
            Score Global: {scores.get('global_score', 0):.1f}/10
        </div>
        
        <!-- Métriques principales -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Visibilité IA</div>
                <div class="metric-value">{visibility.get('overall_visibility', 0)*100:.0f}%</div>
                <div class="trend">Moyenne sur 5 plateformes</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Tests Effectués</div>
                <div class="metric-value">{visibility.get('total_tests', 0)}</div>
                <div class="trend">{visibility.get('queries_tested', 0)} requêtes testées</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Recommandations</div>
                <div class="metric-value">{len(report_data.get('recommendations', []))}</div>
                <div class="trend">Actions prioritaires</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Quick Wins</div>
                <div class="metric-value">{len(report_data.get('quick_wins', []))}</div>
                <div class="trend">À faire cette semaine</div>
            </div>
        </div>
        
        <!-- Graphique radar des scores -->
        <div class="section">
            <h2>Scores par Critère GEO</h2>
            <div class="chart-container">
                <canvas id="radarChart"></canvas>
            </div>
        </div>
        
        <!-- Visibilité par plateforme -->
        <div class="section">
            <h2>Visibilité par Plateforme IA</h2>
            <div class="platform-bars">
                {generate_platform_bars(platform_scores)}
            </div>
        </div>
        
        <!-- Quick Wins -->
        <div class="section">
            <h2>⚡ Quick Wins - Actions Immédiates</h2>
            <ul class="action-list">
                {generate_quick_wins_list(report_data.get('quick_wins', [])[:5])}
            </ul>
        </div>
        
        <!-- Recommandations prioritaires -->
        <div class="section">
            <h2>🎯 Top 5 Recommandations</h2>
            <ul class="action-list">
                {generate_recommendations_list(report_data.get('recommendations', [])[:5])}
            </ul>
        </div>
    </div>
    
    <script>
        // Radar Chart
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['Structure', 'Densité Info', 'Lisibilité', 'E-E-A-T', 'Éducatif', 'Thématique', 'Opt. IA', 'Visibilité'],
                datasets: [{{
                    label: 'Scores GEO',
                    data: [
                        {scores.get('structure', 0)},
                        {scores.get('infoDensity', 0)},
                        {scores.get('readability', 0)},
                        {scores.get('eeat', 0)},
                        {scores.get('educational', 0)},
                        {scores.get('thematic', 0)},
                        {scores.get('aiOptimization', 0)},
                        {scores.get('visibility', 0)}
                    ],
                    backgroundColor: 'rgba(26, 26, 26, 0.2)',
                    borderColor: 'rgba(26, 26, 26, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(26, 26, 26, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(26, 26, 26, 1)'
                }}]
            }},
            options: {{
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 10,
                        ticks: {{
                            stepSize: 2
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return file_path

def get_score_class(score: float) -> str:
    """Retourne la classe CSS selon le score"""
    if score >= 7:
        return 'score-good'
    elif score >= 5:
        return 'score-warning'
    return 'score-critical'

def generate_platform_bars(platform_scores: Dict[str, float]) -> str:
    """Génère les barres de progression pour chaque plateforme"""
    html = ""
    for platform, score in platform_scores.items():
        percentage = score * 100
        html += f"""
                <div class="platform-bar">
                    <div class="platform-name">{platform}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {percentage}%">
                            {percentage:.0f}%
                        </div>
                    </div>
                </div>
        """
    return html

def generate_quick_wins_list(quick_wins: list) -> str:
    """Génère la liste des quick wins"""
    html = ""
    for qw in quick_wins:
        html += f'<li><strong>{qw["title"]}</strong> - {qw["time_required"]}</li>\n'
    return html

def generate_recommendations_list(recommendations: list) -> str:
    """Génère la liste des recommandations"""
    html = ""
    for rec in recommendations:
        html += f'<li><strong>{rec["title"]}</strong> (Impact: {rec["impact"]})</li>\n'
    return html
