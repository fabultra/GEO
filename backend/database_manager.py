"""
Gestionnaire de base de données SQLite pour historique et alertes
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gère l'historique des analyses et les alertes"""
    
    def __init__(self, db_path: str = "/app/data/geo_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table analyses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                site_url TEXT NOT NULL,
                date TEXT NOT NULL,
                global_score REAL,
                structure_score REAL,
                info_density_score REAL,
                readability_score REAL,
                eeat_score REAL,
                educational_score REAL,
                thematic_score REAL,
                ai_optimization_score REAL,
                visibility_score REAL,
                overall_visibility REAL,
                data_json TEXT
            )
        ''')
        
        # Table alertes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_url TEXT NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT NOT NULL,
                data_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_analysis(self, report_data: Dict[str, Any]):
        """Sauvegarde une analyse"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        scores = report_data.get('scores', {})
        visibility = report_data.get('visibility_results', {})
        
        cursor.execute('''
            INSERT INTO analyses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_data['id'],
            report_data['url'],
            datetime.now().isoformat(),
            scores.get('global_score', 0),
            scores.get('structure', 0),
            scores.get('infoDensity', 0),
            scores.get('readability', 0),
            scores.get('eeat', 0),
            scores.get('educational', 0),
            scores.get('thematic', 0),
            scores.get('aiOptimization', 0),
            scores.get('visibility', 0),
            visibility.get('overall_visibility', 0),
            json.dumps(report_data)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Analysis saved for {report_data['url']}")
    
    def get_previous_analysis(self, site_url: str) -> Dict[str, Any]:
        """Récupère l'analyse précédente pour un site"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analyses 
            WHERE site_url = ? 
            ORDER BY date DESC 
            LIMIT 1 OFFSET 1
        ''', (site_url,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'site_url': row[1],
                'date': row[2],
                'global_score': row[3],
                'scores': {
                    'structure': row[4],
                    'infoDensity': row[5],
                    'readability': row[6],
                    'eeat': row[7],
                    'educational': row[8],
                    'thematic': row[9],
                    'aiOptimization': row[10],
                    'visibility': row[11]
                },
                'overall_visibility': row[12]
            }
        
        return None
    
    def generate_alerts(self, current_report: Dict[str, Any], previous_report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère des alertes basées sur les changements"""
        alerts = []
        
        if not previous_report:
            return alerts
        
        current_score = current_report['scores']['global_score']
        previous_score = previous_report['global_score']
        diff = current_score - previous_score
        
        # Alerte critique
        if diff <= -1.0:
            alerts.append({
                'type': 'CRITIQUE',
                'priority': 'high',
                'message': f"🔴 Score global en baisse significative: {diff:.1f} points (de {previous_score:.1f} à {current_score:.1f})"
            })
        
        # Warning
        elif diff <= -0.5:
            alerts.append({
                'type': 'WARNING',
                'priority': 'medium',
                'message': f"🟡 Score global en baisse: {diff:.1f} points (de {previous_score:.1f} à {current_score:.1f})"
            })
        
        # Opportunité
        elif diff >= 1.0:
            alerts.append({
                'type': 'OPPORTUNITÉ',
                'priority': 'low',
                'message': f"🟢 Amélioration significative: +{diff:.1f} points (de {previous_score:.1f} à {current_score:.1f})"
            })
        
        return alerts
    
    def save_alerts(self, site_url: str, alerts: List[Dict[str, str]]):
        """Sauvegarde les alertes"""
        if not alerts:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for alert in alerts:
            cursor.execute('''
                INSERT INTO alerts (site_url, date, type, message, priority, data_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                site_url,
                datetime.now().isoformat(),
                alert['type'],
                alert['message'],
                alert['priority'],
                json.dumps(alert)
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"{len(alerts)} alerts saved for {site_url}")
