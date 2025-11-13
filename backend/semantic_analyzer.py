"""
MODULE D'ANALYSE SÉMANTIQUE PROFONDE
Détecte automatiquement l'industrie et extrait les entités sémantiques
100% GÉNÉRIQUE - Fonctionne pour toute industrie
Utilise Anthropic Claude pour une analyse profonde
"""
import logging
import re
import os
import json
from typing import Dict, Any, List
from collections import Counter
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Initialiser Anthropic
anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# Dictionnaire de patterns par industrie
INDUSTRY_PATTERNS = {
    'financial_services': {
        'keywords': ['finance', 'financier', 'assurance', 'prêt', 'crédit', 'investissement', 'patrimoine', 'épargne', 'courtier', 'conseiller financier'],
        'service_verbs': ['assurer', 'protéger', 'investir', 'épargner', 'planifier', 'financer'],
        'company_types': ['courtier', 'assureur', 'banque', 'conseiller', 'planificateur']
    },
    'saas': {
        'keywords': ['logiciel', 'plateforme', 'cloud', 'abonnement', 'saas', 'application', 'solution', 'outil', 'dashboard', 'api'],
        'service_verbs': ['gérer', 'automatiser', 'optimiser', 'collaborer', 'analyser', 'centraliser'],
        'company_types': ['logiciel', 'plateforme', 'solution', 'outil']
    },
    'ecommerce': {
        'keywords': ['boutique', 'produits', 'livraison', 'commande', 'panier', 'achat', 'magasin', 'catalogue', 'stock'],
        'service_verbs': ['acheter', 'commander', 'livrer', 'retourner', 'expédier', 'shopping'],
        'company_types': ['boutique', 'magasin', 'commerce', 'e-commerce']
    },
    'construction': {
        'keywords': ['construction', 'rénovation', 'bâtiment', 'chantier', 'entrepreneur', 'travaux', 'maçonnerie', 'plomberie'],
        'service_verbs': ['construire', 'rénover', 'bâtir', 'installer', 'réparer', 'aménager'],
        'company_types': ['entrepreneur', 'constructeur', 'rénovateur', 'artisan']
    },
    'professional_services': {
        'keywords': ['conseil', 'consulting', 'expertise', 'accompagnement', 'formation', 'audit', 'stratégie'],
        'service_verbs': ['conseiller', 'accompagner', 'former', 'auditer', 'optimiser', 'développer'],
        'company_types': ['consultant', 'conseiller', 'expert', 'cabinet']
    },
    'healthcare': {
        'keywords': ['santé', 'médical', 'clinique', 'soins', 'patient', 'traitement', 'thérapie', 'diagnostic'],
        'service_verbs': ['soigner', 'traiter', 'diagnostiquer', 'prévenir', 'guérir', 'consulter'],
        'company_types': ['clinique', 'centre', 'cabinet médical', 'hôpital']
    },
    'hospitality': {
        'keywords': ['hôtel', 'restaurant', 'hébergement', 'réservation', 'séjour', 'cuisine', 'menu', 'chambre'],
        'service_verbs': ['réserver', 'héberger', 'accueillir', 'servir', 'cuisiner', 'loger'],
        'company_types': ['hôtel', 'restaurant', 'auberge', 'gîte']
    },
    'real_estate': {
        'keywords': ['immobilier', 'propriété', 'maison', 'condo', 'hypothèque', 'achat', 'vente', 'location'],
        'service_verbs': ['vendre', 'acheter', 'louer', 'évaluer', 'investir', 'négocier'],
        'company_types': ['courtier immobilier', 'agent immobilier', 'agence']
    },
    'education': {
        'keywords': ['école', 'cours', 'formation', 'apprentissage', 'étudiant', 'enseignement', 'programme', 'diplôme'],
        'service_verbs': ['enseigner', 'former', 'apprendre', 'étudier', 'éduquer', 'certifier'],
        'company_types': ['école', 'centre de formation', 'institut', 'académie']
    },
    'manufacturing': {
        'keywords': ['fabrication', 'production', 'usine', 'manufacture', 'produit', 'qualité', 'certification'],
        'service_verbs': ['fabriquer', 'produire', 'manufacturer', 'assembler', 'transformer'],
        'company_types': ['fabricant', 'manufacturier', 'producteur', 'usine']
    }
}

class SemanticAnalyzer:
    """Analyse sémantique profonde du site - 100% générique"""
    
    def __init__(self):
        self.industry_classification = {}
        self.entities = {}
    
    def analyze_site(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse complète du site
        
        Returns:
            {
                'industry_classification': {...},
                'entities': {...},
                'topics': [...],
                'semantic_clusters': [...]
            }
        """
        try:
            # 1. Détecter l'industrie
            self.industry_classification = self._detect_industry(crawl_data)
            logger.info(f"Industry detected: {self.industry_classification.get('primary_industry')}")
            
            # 2. Extraire les entités sémantiques
            self.entities = self._extract_semantic_entities(crawl_data, self.industry_classification)
            logger.info(f"Extracted {len(self.entities.get('offerings', []))} offerings")
            
            # 3. Identifier les topics
            topics = self._identify_topics(crawl_data)
            
            return {
                'industry_classification': self.industry_classification,
                'entities': self.entities,
                'topics': topics
            }
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {str(e)}")
            return {
                'industry_classification': {'primary_industry': 'generic', 'confidence': 0.0},
                'entities': {},
                'topics': []
            }
    
    def _detect_industry(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Détecter automatiquement l'industrie avec Anthropic - ANALYSE PROFONDE"""
        
        # Combiner TOUTES les pages (minimum 20 pages ou tout le site)
        all_text = ""
        pages = crawl_data.get('pages', [])[:20]  # Analyser 20 pages minimum
        
        # Extraire le contenu complet de chaque page
        page_contents = []
        for page in pages:
            page_text = f"URL: {page.get('url', '')}\n"
            page_text += f"TITRE: {page.get('title', '')}\n"
            page_text += f"META DESCRIPTION: {page.get('meta_description', '')}\n"
            page_text += "CONTENU:\n" + "\n".join(page.get('paragraphs', []))
            page_contents.append(page_text)
            all_text += " " + page_text
        
        # Prendre les 15000 premiers caractères pour l'analyse (beaucoup plus que 4000)
        all_text_sample = all_text[:15000]
        
        # Utiliser Claude pour analyser l'industrie
        try:
            prompt = f"""Analyse ce contenu de site web et détermine :
1. L'industrie principale (choisis parmi: financial_services, saas, ecommerce, construction, professional_services, healthcare, hospitality, real_estate, education, manufacturing, ou 'generic' si aucune ne correspond)
2. Le type d'entreprise précis (ex: "courtier en assurance", "logiciel de gestion", "boutique en ligne", etc.)
3. Le business model (B2B, B2C, ou B2B2C)

CONTENU DU SITE:
{all_text}

Réponds UNIQUEMENT avec un JSON valide dans ce format exact:
{{
  "primary_industry": "nom_industrie",
  "company_type": "type précis",
  "business_model": "B2B ou B2C ou B2B2C",
  "confidence": 0.85
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            logger.info(f"Claude industry detection response: {response_text}")
            
            # Parser le JSON
            result = json.loads(response_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Claude industry detection failed: {str(e)}, falling back to keyword method")
            # Fallback: méthode par mots-clés
            return self._detect_industry_fallback(all_text)
    
    def _detect_industry_fallback(self, all_text: str) -> Dict[str, Any]:
        """Méthode fallback par mots-clés si Claude échoue"""
        
        all_text = all_text.lower()
        
        # Compter les occurrences par industrie
        scores = {}
        for industry, patterns in INDUSTRY_PATTERNS.items():
            score = 0
            
            # Score basé sur keywords
            for keyword in patterns['keywords']:
                score += all_text.count(keyword) * 2
            
            # Score basé sur verbes de service
            for verb in patterns['service_verbs']:
                score += all_text.count(verb)
            
            # Score basé sur types d'entreprise
            for company_type in patterns['company_types']:
                score += all_text.count(company_type) * 3
            
            scores[industry] = score
        
        # Trouver l'industrie dominante
        if scores:
            primary_industry = max(scores, key=scores.get)
            total_score = sum(scores.values())
            confidence = scores[primary_industry] / total_score if total_score > 0 else 0
            
            # Si confidence trop faible, utiliser generic
            if confidence < 0.3 or scores[primary_industry] < 5:
                primary_industry = 'generic'
                confidence = 0.5
        else:
            primary_industry = 'generic'
            confidence = 0.5
        
        # Déterminer le type d'entreprise
        company_type = self._extract_company_type(all_text, primary_industry)
        
        # Déterminer le business model
        business_model = self._detect_business_model(all_text)
        
        return {
            'primary_industry': primary_industry,
            'company_type': company_type,
            'business_model': business_model,
            'confidence': confidence
        }
    
    def _extract_company_type(self, text: str, industry: str) -> str:
        """Extraire le type d'entreprise"""
        
        if industry in INDUSTRY_PATTERNS:
            patterns = INDUSTRY_PATTERNS[industry]
            
            # Chercher le type le plus mentionné
            type_counts = {}
            for company_type in patterns['company_types']:
                count = text.count(company_type)
                if count > 0:
                    type_counts[company_type] = count
            
            if type_counts:
                return max(type_counts, key=type_counts.get)
        
        return 'entreprise'
    
    def _detect_business_model(self, text: str) -> str:
        """Détecter B2B, B2C ou B2B2C"""
        
        b2b_signals = ['entreprise', 'pme', 'organisation', 'professionnel', 'corporate', 'business']
        b2c_signals = ['particulier', 'famille', 'client', 'personnel', 'individu']
        
        b2b_score = sum(text.count(signal) for signal in b2b_signals)
        b2c_score = sum(text.count(signal) for signal in b2c_signals)
        
        if b2b_score > b2c_score * 1.5:
            return 'B2B'
        elif b2c_score > b2b_score * 1.5:
            return 'B2C'
        else:
            return 'B2B2C'
    
    def _extract_semantic_entities(self, crawl_data: Dict[str, Any], industry_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Extraire les entités sémantiques"""
        
        entities = {
            'company_info': {},
            'offerings': [],
            'customer_segments': [],
            'locations': [],
            'problems_solved': [],
            'unique_value_props': []
        }
        
        # Combiner le texte
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        # Informations de base
        pages = crawl_data.get('pages', [])
        if pages:
            title = pages[0].get('title', '')
            entities['company_info'] = {
                'name': self._extract_company_name(title),
                'type': industry_classification['company_type'],
                'industry': industry_classification['primary_industry'],
                'business_model': industry_classification['business_model']
            }
        
        # Extraire offerings
        entities['offerings'] = self._extract_offerings(all_text, industry_classification['primary_industry'])
        
        # Extraire segments clients
        entities['customer_segments'] = self._extract_customer_segments(all_text, industry_classification['business_model'])
        
        # Extraire localisations
        entities['locations'] = self._extract_locations(all_text)
        
        # Extraire problèmes résolus
        entities['problems_solved'] = self._extract_problems_solved(all_text)
        
        return entities
    
    def _extract_company_name(self, title: str) -> str:
        """Extraire le nom de l'entreprise depuis le title"""
        
        if '|' in title:
            return title.split('|')[0].strip()
        elif '-' in title:
            return title.split('-')[0].strip()
        else:
            words = title.split()
            return words[0] if words else ''
    
    def _extract_offerings(self, text: str, industry: str) -> List[Dict[str, Any]]:
        """Extraire services/produits avec Anthropic"""
        
        # Limiter le texte
        text_sample = text[:3000]
        
        try:
            offering_label = "services" if industry not in ['ecommerce', 'manufacturing'] else "produits"
            
            prompt = f"""Analyse ce contenu de site web et extrais les {offering_label} principaux offerts.

CONTENU:
{text_sample}

Liste les 5-10 {offering_label} les plus importants mentionnés sur ce site.
Réponds UNIQUEMENT avec un JSON valide dans ce format:
{{
  "offerings": [
    {{"name": "nom du service/produit", "mentions_count": 5}},
    {{"name": "autre service/produit", "mentions_count": 3}}
  ]
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            result = json.loads(response_text)
            
            return result.get('offerings', [])[:10]
            
        except Exception as e:
            logger.error(f"Claude offerings extraction failed: {str(e)}, using fallback")
            # Fallback: extraire par patterns
            return self._extract_offerings_fallback(text, industry)
    
    def _extract_offerings_fallback(self, text: str, industry: str) -> List[Dict[str, Any]]:
        """Méthode fallback pour extraire offerings"""
        
        offerings = []
        
        # Patterns de recherche selon l'industrie
        if industry == 'saas':
            patterns = [
                r'fonctionnalité[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})',
                r'module[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})',
                r'outil[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})'
            ]
        elif industry == 'ecommerce':
            patterns = [
                r'produit[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})',
                r'catégorie[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})'
            ]
        else:
            patterns = [
                r'service[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})',
                r'solution[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})',
                r'offre[s]? ([a-zàâäéèêëïîôùûüÿæœç\s]{3,30})'
            ]
        
        # Extraire
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches[:5]:
                if match.strip():
                    offerings.append({
                        'name': match.strip(),
                        'mentions_count': text.lower().count(match.strip())
                    })
        
        # Si rien trouvé, extraire mots-clés principaux
        if not offerings:
            words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{5,}\b', text.lower())
            word_freq = Counter(words)
            stop_words = {'dans', 'pour', 'avec', 'vous', 'nous', 'votre', 'notre', 'plus', 'tout'}
            
            for word, count in word_freq.most_common(10):
                if word not in stop_words and count > 2:
                    offerings.append({'name': word, 'mentions_count': count})
        
        return offerings[:10]
    
    def _extract_customer_segments(self, text: str, business_model: str) -> List[str]:
        """Extraire segments clients"""
        
        segments = []
        
        if business_model == 'B2B':
            b2b_segments = ['pme', 'grande entreprise', 'startup', 'organisation', 'entreprise']
            for segment in b2b_segments:
                if segment in text.lower():
                    segments.append(segment)
        
        elif business_model == 'B2C':
            b2c_segments = ['particulier', 'famille', 'jeune', 'professionnel', 'étudiant']
            for segment in b2c_segments:
                if segment in text.lower():
                    segments.append(segment)
        
        else:
            segments = ['entreprise', 'particulier']
        
        return segments[:5]
    
    def _extract_locations(self, text: str) -> List[Dict[str, str]]:
        """Extraire localisations"""
        
        quebec_cities = [
            'Montréal', 'Québec', 'Laval', 'Gatineau', 'Longueuil',
            'Sherbrooke', 'Saguenay', 'Trois-Rivières', 'Terrebonne', 'Brossard'
        ]
        
        locations = []
        for city in quebec_cities:
            if city.lower() in text.lower():
                locations.append({'city': city, 'region': 'Québec'})
        
        if not locations:
            locations.append({'city': None, 'region': 'Québec'})
        
        return locations[:3]
    
    def _extract_problems_solved(self, text: str) -> List[str]:
        """Extraire problèmes résolus avec Anthropic"""
        
        text_sample = text[:3000]
        
        try:
            prompt = f"""Analyse ce contenu de site web et identifie les problèmes/défis que cette entreprise résout pour ses clients.

CONTENU:
{text_sample}

Liste 5-10 problèmes/défis principaux que cette entreprise aide à résoudre.
Formule chaque problème de manière concise (ex: "gagner du temps", "réduire les coûts", "protéger contre les risques").

Réponds UNIQUEMENT avec un JSON valide dans ce format:
{{
  "problems_solved": ["problème 1", "problème 2", "problème 3"]
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            result = json.loads(response_text)
            
            return result.get('problems_solved', [])[:10]
            
        except Exception as e:
            logger.error(f"Claude problems extraction failed: {str(e)}, using fallback")
            # Fallback: extraire par patterns
            return self._extract_problems_fallback(text)
    
    def _extract_problems_fallback(self, text: str) -> List[str]:
        """Méthode fallback pour extraire problèmes"""
        
        problem_patterns = [
            r'résoudre ([a-zàâäéèêëïîôùûüÿæœç\s]{5,30})',
            r'solution pour ([a-zàâäéèêëïîôùûüÿæœç\s]{5,30})',
            r'éliminer ([a-zàâäéèêëïîôùûüÿæœç\s]{5,30})',
            r'éviter ([a-zàâäéèêëïîôùûüÿæœç\s]{5,30})'
        ]
        
        problems = []
        for pattern in problem_patterns:
            matches = re.findall(pattern, text.lower())
            problems.extend([m.strip() for m in matches if m.strip()])
        
        return list(set(problems))[:10] if problems else ["optimiser les processus", "améliorer l'efficacité", "réduire les coûts"]
    
    def _identify_topics(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifier les topics principaux (simplifié)"""
        
        # Extraire tous les mots
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{4,}\b', all_text.lower())
        
        # Filtrer stop words
        stop_words = {'dans', 'pour', 'avec', 'vous', 'nous', 'votre', 'notre', 'plus', 'tout', 'tous', 'être', 'avoir', 'faire'}
        filtered_words = [w for w in words if w not in stop_words]
        
        # Compter fréquence
        word_freq = Counter(filtered_words)
        
        # Top 10 topics
        topics = []
        for word, count in word_freq.most_common(10):
            topics.append({
                'label': word,
                'weight': count / len(filtered_words) if filtered_words else 0
            })
        
        return topics
