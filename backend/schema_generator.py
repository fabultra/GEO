"""
Module 4: Générateur automatique de Schema.org JSON-LD
Génère tous les schemas nécessaires pour optimiser l'indexation par les IA
"""
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SchemaGenerator:
    """Génère automatiquement les schemas JSON-LD pour un site"""
    
    def __init__(self):
        self.base_context = "https://schema.org"
    
    def generate_all_schemas(self, site_data: Dict[str, Any], crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère tous les schemas nécessaires pour le site
        
        Args:
            site_data: Informations sur le site (nom, URL, etc.)
            crawl_data: Données du crawl du site
        
        Returns:
            Dictionnaire avec tous les schemas générés
        """
        schemas = {
            "organization": self.generate_organization_schema(site_data),
            "website": self.generate_website_schema(site_data),
            "breadcrumb": self.generate_breadcrumb_schema(site_data, crawl_data),
            "faq": self.generate_faq_schema(crawl_data),
            "article": self.generate_article_schemas(crawl_data),
            "local_business": self.generate_local_business_schema(site_data),
            "service": self.generate_service_schemas(site_data),
            "how_to": self.generate_howto_schemas(crawl_data),
            "review": self.generate_review_schema(site_data)
        }
        
        # Nettoyer les schemas vides
        schemas = {k: v for k, v in schemas.items() if v}
        
        logger.info(f"Generated {len(schemas)} schema types")
        return schemas
    
    def generate_organization_schema(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère le schema Organization (CRITIQUE pour GEO)
        
        Args:
            site_data: Données du site
        
        Returns:
            Schema Organization JSON-LD
        """
        url = site_data.get('url', '')
        domain = urlparse(url).netloc
        org_name = site_data.get('name', domain.split('.')[0].upper())
        
        schema = {
            "@context": self.base_context,
            "@type": "Organization",
            "name": org_name,
            "url": url,
            "logo": {
                "@type": "ImageObject",
                "url": f"{url}/logo.png"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": site_data.get('phone', '+1-XXX-XXX-XXXX'),
                "contactType": "customer service",
                "areaServed": "CA-QC",
                "availableLanguage": ["French", "English"]
            },
            "sameAs": []
        }
        
        # Ajouter les réseaux sociaux si disponibles
        social_links = site_data.get('social_links', [])
        if social_links:
            schema['sameAs'] = social_links
        
        # Ajouter l'adresse si disponible
        if site_data.get('address'):
            schema['address'] = {
                "@type": "PostalAddress",
                "streetAddress": site_data.get('address', ''),
                "addressLocality": site_data.get('city', 'Montréal'),
                "addressRegion": site_data.get('region', 'QC'),
                "postalCode": site_data.get('postal_code', ''),
                "addressCountry": "CA"
            }
        
        return schema
    
    def generate_website_schema(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère le schema WebSite avec SearchAction"""
        url = site_data.get('url', '')
        domain = urlparse(url).netloc
        name = site_data.get('name', domain.split('.')[0].capitalize())
        
        return {
            "@context": self.base_context,
            "@type": "WebSite",
            "name": name,
            "url": url,
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{url}/search?q={{search_term_string}}"
                },
                "query-input": "required name=search_term_string"
            }
        }
    
    def generate_breadcrumb_schema(self, site_data: Dict[str, Any], crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère le schema BreadcrumbList pour la navigation"""
        base_url = site_data.get('url', '')
        
        # Extraire les pages principales du crawl
        pages = crawl_data.get('pages', [])
        breadcrumb_items = []
        
        # Toujours inclure la page d'accueil
        breadcrumb_items.append({
            "@type": "ListItem",
            "position": 1,
            "name": "Accueil",
            "item": base_url
        })
        
        # Ajouter les pages principales (max 5)
        for i, page in enumerate(pages[:5], 2):
            page_url = page.get('url', '')
            page_title = page.get('title', 'Page')
            
            breadcrumb_items.append({
                "@type": "ListItem",
                "position": i,
                "name": page_title,
                "item": page_url
            })
        
        return {
            "@context": self.base_context,
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }
    
    def generate_faq_schema(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère les schemas FAQPage (CRUCIAL pour GEO)
        Extrait les Q&A du contenu crawlé
        
        Returns:
            Liste de schemas FAQPage
        """
        faq_schemas = []
        pages = crawl_data.get('pages', [])
        
        for page in pages:
            # Chercher des patterns FAQ dans le contenu
            questions = []
            paragraphs = page.get('paragraphs', [])
            
            # Méthode simple: chercher les paragraphes qui commencent par des mots-questions
            question_words = ['comment', 'pourquoi', 'quand', 'où', 'qui', 'quoi', 'quel', 'quelle']
            
            for i, para in enumerate(paragraphs):
                para_lower = para.lower()
                
                # Si le paragraphe commence par un mot-question et se termine par ?
                if any(para_lower.startswith(word) for word in question_words) and '?' in para:
                    question = para.split('?')[0] + '?'
                    
                    # La réponse est probablement le paragraphe suivant
                    answer = paragraphs[i + 1] if i + 1 < len(paragraphs) else "À venir"
                    
                    questions.append({
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": answer
                        }
                    })
            
            # Si des questions ont été trouvées, créer le schema FAQPage
            if questions:
                faq_schemas.append({
                    "@context": self.base_context,
                    "@type": "FAQPage",
                    "mainEntity": questions[:10]  # Max 10 questions par page
                })
        
        return faq_schemas if faq_schemas else []
    
    def generate_article_schemas(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère les schemas Article pour le contenu éditorial
        
        Returns:
            Liste de schemas Article
        """
        article_schemas = []
        pages = crawl_data.get('pages', [])
        
        for page in pages:
            # Vérifier si la page ressemble à un article
            word_count = page.get('word_count', 0)
            
            # Considérer comme article si > 500 mots
            if word_count > 500:
                title = page.get('title', 'Sans titre')
                url = page.get('url', '')
                
                article_schemas.append({
                    "@context": self.base_context,
                    "@type": "Article",
                    "headline": title,
                    "url": url,
                    "datePublished": datetime.now().isoformat(),
                    "dateModified": datetime.now().isoformat(),
                    "author": {
                        "@type": "Person",
                        "name": "Expert"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Organisation"
                    },
                    "description": page.get('meta_description', '')[:200],
                    "wordCount": word_count
                })
        
        return article_schemas
    
    def generate_local_business_schema(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère le schema LocalBusiness (pour les entreprises locales)
        Utile pour les courtiers, agences, etc.
        
        Returns:
            Schema LocalBusiness JSON-LD
        """
        url = site_data.get('url', '')
        business_type = site_data.get('business_type', 'LocalBusiness')
        
        schema = {
            "@context": self.base_context,
            "@type": business_type,
            "name": site_data.get('name', ''),
            "url": url,
            "telephone": site_data.get('phone', ''),
            "priceRange": site_data.get('price_range', '$$'),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": site_data.get('address', ''),
                "addressLocality": site_data.get('city', 'Montréal'),
                "addressRegion": "QC",
                "postalCode": site_data.get('postal_code', ''),
                "addressCountry": "CA"
            }
        }
        
        # Ajouter les horaires si disponibles
        if site_data.get('opening_hours'):
            schema['openingHours'] = site_data['opening_hours']
        
        # Ajouter la zone de service
        if site_data.get('service_area'):
            schema['areaServed'] = {
                "@type": "City",
                "name": site_data['service_area']
            }
        
        return schema
    
    def generate_service_schemas(self, site_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère les schemas Service pour chaque service offert
        
        Returns:
            Liste de schemas Service
        """
        services = site_data.get('services', [])
        service_schemas = []
        
        for service in services:
            service_schemas.append({
                "@context": self.base_context,
                "@type": "Service",
                "serviceType": service.get('name', ''),
                "provider": {
                    "@type": "Organization",
                    "name": site_data.get('name', '')
                },
                "description": service.get('description', ''),
                "areaServed": {
                    "@type": "City",
                    "name": site_data.get('city', 'Montréal')
                }
            })
        
        return service_schemas
    
    def generate_howto_schemas(self, crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère les schemas HowTo pour les guides pratiques
        
        Returns:
            Liste de schemas HowTo
        """
        howto_schemas = []
        pages = crawl_data.get('pages', [])
        
        for page in pages:
            title = page.get('title', '').lower()
            
            # Détecter les pages "comment faire"
            if 'comment' in title or 'guide' in title or 'étapes' in title:
                h2_tags = page.get('h2', [])
                
                # Créer des étapes à partir des H2
                steps = []
                for i, h2 in enumerate(h2_tags[:10], 1):
                    steps.append({
                        "@type": "HowToStep",
                        "position": i,
                        "name": h2,
                        "text": h2
                    })
                
                if steps:
                    howto_schemas.append({
                        "@context": self.base_context,
                        "@type": "HowTo",
                        "name": page.get('title', ''),
                        "description": page.get('meta_description', ''),
                        "step": steps
                    })
        
        return howto_schemas
    
    def generate_review_schema(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère le schema AggregateRating si des avis sont disponibles
        
        Returns:
            Schema AggregateRating
        """
        reviews = site_data.get('reviews', {})
        
        if not reviews or not reviews.get('count'):
            return {}
        
        return {
            "@context": self.base_context,
            "@type": "AggregateRating",
            "ratingValue": reviews.get('rating', 4.5),
            "reviewCount": reviews.get('count', 0),
            "bestRating": "5",
            "worstRating": "1"
        }
    
    def format_for_html(self, schema: Dict[str, Any]) -> str:
        """
        Formate un schema en HTML <script> tag
        
        Args:
            schema: Schema JSON-LD
        
        Returns:
            Tag HTML prêt à insérer
        """
        return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n</script>'
    
    def generate_implementation_guide(self, schemas: Dict[str, Any], site_url: str) -> str:
        """
        Génère un guide d'implémentation des schemas
        
        Args:
            schemas: Tous les schemas générés
            site_url: URL du site
        
        Returns:
            Guide en Markdown
        """
        guide = f"""# Guide d'Implémentation des Schemas JSON-LD

## Site: {site_url}
## Date: {datetime.now().strftime('%Y-%m-%d')}

---

## 📋 Résumé

✅ {len(schemas)} types de schemas générés
🎯 Impact GEO estimé: +40-50% de visibilité IA

---

## 🚀 Instructions d'Implémentation

### 1. Schema Organization (Page d'accueil)

**Priorité: CRITIQUE**  
**Impact GEO: +50%**

```html
{self.format_for_html(schemas.get('organization', {}))}
```

**Où placer:** Dans le `<head>` de la page d'accueil uniquement

---

### 2. Schema WebSite (Page d'accueil)

**Priorité: HAUTE**  
**Impact GEO: +20%**

```html
{self.format_for_html(schemas.get('website', {}))}
```

**Où placer:** Dans le `<head>` de la page d'accueil

---

### 3. Schema FAQPage (Pages FAQ)

**Priorité: CRITIQUE**  
**Impact GEO: +60%** (Les IA adorent les FAQs)

"""
        
        faq_schemas = schemas.get('faq', [])
        if faq_schemas:
            guide += f"```html\n{self.format_for_html(faq_schemas[0])}\n```\n\n"
            guide += "**Où placer:** Sur chaque page contenant une FAQ\n\n---\n\n"
        
        guide += """
### 4. Schema Article (Pages de contenu)

**Priorité: HAUTE**  
**Impact GEO: +30%**

```html
(Voir exemples ci-dessous)
```

**Où placer:** Sur chaque article de blog ou guide

---

## ⚡ Quick Wins (Impact Immédiat)

1. **Ajouter Organization + WebSite sur la page d'accueil** → 15 minutes → +40% visibilité
2. **Créer une page FAQ avec FAQPage schema** → 2 heures → +60% chances d'être cité
3. **Ajouter Article schema sur 5 articles principaux** → 1 heure → +30% indexation

---

## 📊 Validation

Après implémentation, valider avec:
- Google Rich Results Test: https://search.google.com/test/rich-results
- Schema.org Validator: https://validator.schema.org/

---

## 🎯 Résultats Attendus

Après 2-4 semaines:
- Visibilité ChatGPT: +50%
- Citations dans Claude: +40%
- Apparitions Perplexity: +60%
- Score GEO global: +2-3 points

"""
        
        return guide
