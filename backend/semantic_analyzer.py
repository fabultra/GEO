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
        
        # ANALYSE PROFONDE avec Claude - Multi-étapes
        try:
            # ÉTAPE 1: Analyse contextuelle approfondie
            prompt = f"""Tu es un expert en analyse sémantique de sites web. Analyse EN PROFONDEUR ce site web.

CONTENU DU SITE (20 pages):
{all_text_sample}

ANALYSE DEMANDÉE:
1. **Industrie principale** - Identifie l'industrie précise parmi: financial_services, saas, ecommerce, construction, professional_services, healthcare, hospitality, real_estate, education, manufacturing, ou generic
2. **Sous-industrie** - Spécifie la niche exacte (ex: "insurance brokerage", "project management software", "sustainable fashion")
3. **Type d'entreprise** - Décris précisément ce qu'ils font (ex: "courtier en assurance familiale", "logiciel de gestion de projet cloud")
4. **Business model** - B2B, B2C ou B2B2C avec justification
5. **Positionnement** - Comment ils se différencient (premium, volume, spécialisé, etc.)
6. **Maturité** - startup, scale-up, établi, leader de marché
7. **Scope géographique** - local, régional, national, international

RÉFLÉCHIS en profondeur sur le contexte métier, les clients cibles, et le positionnement.

Réponds UNIQUEMENT avec un JSON valide:
{{
  "primary_industry": "industrie",
  "sub_industry": "sous-niche précise",
  "company_type": "description détaillée",
  "business_model": "B2B/B2C/B2B2C",
  "positioning": "premium/volume/specialized/etc",
  "maturity": "startup/scaleup/established/leader",
  "geographic_scope": "local/regional/national/international",
  "confidence": 0.XX,
  "reasoning": "Justification de l'analyse en 2-3 phrases"
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            logger.info(f"Claude industry detection response: {response_text[:200]}...")
            
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
        """Extraire services/produits avec Anthropic - ANALYSE PROFONDE"""
        
        # Prendre beaucoup plus de texte pour le contexte
        text_sample = text[:12000]  # 12K au lieu de 3K
        
        try:
            offering_label = "services" if industry not in ['ecommerce', 'manufacturing'] else "produits"
            
            prompt = f"""Tu es un expert en analyse d'offres commerciales. Analyse EN PROFONDEUR ce site web.

CONTENU DU SITE:
{text_sample}

TÂCHE: Extrais les {offering_label} principaux avec une compréhension CONTEXTUELLE.

Pour chaque {offering_label[:-1]}, identifie:
1. **Nom clair et précis** (pas de fragments)
2. **Description courte** (1 phrase)
3. **Segment cible** (qui en bénéficie)
4. **Niveau de priorité** (core/secondary/complementary)
5. **Prix indicatif** si mentionné

RÉFLÉCHIS sur:
- Quelle est leur offre PRINCIPALE vs complémentaire?
- Comment ils packagisent leurs {offering_label}?
- Quel est leur cœur de métier?

Liste 8-12 {offering_label} par ordre d'importance.

Réponds UNIQUEMENT avec un JSON valide:
{{
  "offerings": [
    {{
      "name": "nom précis du service/produit",
      "description": "description courte",
      "target_segment": "PME/particuliers/etc",
      "priority": "core/secondary/complementary",
      "mentions_count": 10
    }}
  ]
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            result = json.loads(response_text)
            
            return result.get('offerings', [])[:12]
            
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
    
    def _extract_problems_solved(self, text: str) -> List[Dict[str, Any]]:
        """Extraire problèmes résolus avec Anthropic - ANALYSE PROFONDE DES PAIN POINTS"""
        
        text_sample = text[:12000]  # Plus de contexte
        
        try:
            prompt = f"""Tu es un expert en analyse des besoins clients et pain points. Analyse EN PROFONDEUR ce site.

CONTENU DU SITE:
{text_sample}

TÂCHE: Identifie les problèmes/défis/pain points que cette entreprise résout.

Pour chaque problème:
1. **Problème précis** - Formulation claire du pain point
2. **Catégorie** - operational/financial/strategic/risk/growth/compliance
3. **Gravité** - critical/high/medium/low
4. **Segment affecté** - Qui souffre de ce problème
5. **Solution proposée** - Comment l'entreprise le résout

RÉFLÉCHIS sur:
- Quels sont les VRAIS problèmes clients (pas juste features)
- Quelle est la hiérarchie des pain points (urgent vs important)
- Quel est le coût de l'inaction pour le client

Liste 10-15 problèmes par ordre de gravité.

Réponds UNIQUEMENT avec un JSON valide:
{{
  "problems_solved": [
    {{
      "problem": "description du problème",
      "category": "operational/financial/etc",
      "severity": "critical/high/medium/low",
      "affected_segment": "qui souffre",
      "solution_approach": "comment c'est résolu"
    }}
  ]
}}"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip()
            result = json.loads(response_text)
            
            return result.get('problems_solved', [])[:15]
            
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
        """Identifier les topics principaux avec VRAI Topic Modeling LDA"""
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import LatentDirichletAllocation
            
            # Extraire TOUS les paragraphes de TOUTES les pages
            documents = []
            for page in crawl_data.get('pages', [])[:20]:  # 20 pages
                for paragraph in page.get('paragraphs', []):
                    if len(paragraph) > 50:  # Au moins 50 caractères
                        documents.append(paragraph)
            
            if len(documents) < 5:
                logger.warning("Not enough documents for LDA, using fallback")
                return self._identify_topics_fallback(crawl_data)
            
            # Stop words français élargis
            stop_words_fr = {
                'dans', 'pour', 'avec', 'vous', 'nous', 'votre', 'notre', 'plus', 'tout', 'tous', 
                'toute', 'cette', 'sont', 'être', 'avoir', 'faire', 'leur', 'leurs', 'elle', 'elles',
                'celui', 'celle', 'ceux', 'celles', 'peut', 'peuvent', 'aussi', 'très', 'même',
                'chez', 'sans', 'sous', 'alors', 'donc', 'mais', 'aussi', 'encore', 'jamais',
                'toujours', 'souvent', 'parfois', 'ainsi', 'après', 'avant', 'depuis', 'pendant'
            }
            
            # TF-IDF Vectorization
            vectorizer = TfidfVectorizer(
                max_features=200,
                ngram_range=(1, 2),  # Unigrams et bigrams
                min_df=2,  # Minimum 2 documents
                max_df=0.8,  # Maximum 80% des documents
                stop_words=list(stop_words_fr)
            )
            
            doc_term_matrix = vectorizer.fit_transform(documents)
            
            # LDA Topic Modeling
            n_topics = min(8, len(documents) // 3)  # Adaptatif
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                max_iter=20,
                learning_method='online',
                random_state=42,
                n_jobs=-1
            )
            
            lda.fit(doc_term_matrix)
            
            # Extraire topics avec contexte Claude
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(lda.components_):
                # Top 10 mots par topic
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                
                # Demander à Claude de labéliser intelligemment
                topic_label = self._label_topic_with_claude(top_words)
                
                topics.append({
                    'topic_id': topic_idx,
                    'label': topic_label,
                    'keywords': top_words[:8],
                    'weight': float(topic.sum()),
                    'top_words_scores': [float(topic[i]) for i in top_indices[:5]]
                })
            
            # Trier par poids
            topics = sorted(topics, key=lambda x: x['weight'], reverse=True)
            
            logger.info(f"LDA identified {len(topics)} topics")
            return topics
            
        except Exception as e:
            logger.error(f"LDA topic modeling failed: {str(e)}, using fallback")
            return self._identify_topics_fallback(crawl_data)
    
    def _label_topic_with_claude(self, keywords: List[str]) -> str:
        """Utiliser Claude pour labéliser intelligemment un topic"""
        try:
            prompt = f"""Ces mots-clés représentent un thème principal d'un site web:
{', '.join(keywords)}

Donne un label CONCIS (2-4 mots) qui capture l'essence de ce thème.
Exemples: "Services financiers", "Gestion de projet", "E-commerce mode"

Réponds UNIQUEMENT avec le label (pas de JSON, pas d'explication):"""

            message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )
            
            label = message.content[0].text.strip()
            return label
            
        except Exception:
            # Fallback: utiliser le premier mot-clé
            return keywords[0] if keywords else "Topic"
    
    def _identify_topics_fallback(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback simple si LDA échoue"""
        
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{4,}\b', all_text.lower())
        
        stop_words = {'dans', 'pour', 'avec', 'vous', 'nous', 'votre', 'notre', 'plus', 'tout', 'tous', 'être', 'avoir', 'faire'}
        filtered_words = [w for w in words if w not in stop_words]
        
        word_freq = Counter(filtered_words)
        
        topics = []
        for word, count in word_freq.most_common(10):
            topics.append({
                'topic_id': len(topics),
                'label': word,
                'keywords': [word],
                'weight': count / len(filtered_words) if filtered_words else 0
            })
        
        return topics
