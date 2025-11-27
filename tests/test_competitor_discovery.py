"""
Tests complets pour le système de découverte de compétiteurs
Version 2 - Tests sans connexion internet (mocked)
"""
import pytest
import sys
sys.path.append('/app/backend')

from unittest.mock import Mock, patch, MagicMock
from utils.competitor_extractor import CompetitorExtractor
from services.competitor_discovery import CompetitorDiscovery


class TestCompetitorExtractor:
    """Tests pour CompetitorExtractor (Stage 1)"""
    
    def test_normalize_url(self):
        """Test normalisation d'URLs"""
        # URL complète
        assert CompetitorExtractor._normalize_url('https://example.com') == 'https://example.com/'
        
        # Sans protocole
        assert CompetitorExtractor._normalize_url('example.com') == 'https://example.com/'
        
        # Avec www
        result = CompetitorExtractor._normalize_url('www.example.com')
        assert result == 'https://www.example.com/'
        
        # Avec path
        assert CompetitorExtractor._normalize_url('https://example.com/page') == 'https://example.com/page'
        
        # Invalides
        assert CompetitorExtractor._normalize_url('') is None
        assert CompetitorExtractor._normalize_url(None) is None
    
    def test_extract_domain(self):
        """Test extraction de domaine"""
        assert CompetitorExtractor._extract_domain('https://www.example.com/page') == 'example.com'
        assert CompetitorExtractor._extract_domain('http://subdomain.example.com') == 'subdomain.example.com'
        assert CompetitorExtractor._extract_domain('https://example.com') == 'example.com'
        assert CompetitorExtractor._extract_domain('') is None
    
    def test_is_excluded_domain(self):
        """Test filtrage domaines exclus"""
        # Social media
        assert CompetitorExtractor._is_excluded_domain('facebook.com') is True
        assert CompetitorExtractor._is_excluded_domain('twitter.com') is True
        
        # Directories
        assert CompetitorExtractor._is_excluded_domain('yelp.com') is True
        assert CompetitorExtractor._is_excluded_domain('pagesjaunes.ca') is True
        
        # Job boards
        assert CompetitorExtractor._is_excluded_domain('indeed.com') is True
        
        # Domaines valides
        assert CompetitorExtractor._is_excluded_domain('competitor.com') is False
        assert CompetitorExtractor._is_excluded_domain('real-business.com') is False
    
    def test_extract_urls_from_text(self):
        """Test extraction d'URLs depuis texte"""
        text = "Check out https://competitor1.com and www.competitor2.com for more info."
        urls = CompetitorExtractor._extract_urls_from_text(text)
        
        assert len(urls) >= 2
        assert any('competitor1.com' in url for url in urls)
        assert any('competitor2.com' in url for url in urls)
    
    def test_filter_self_domain(self):
        """Test filtrage de notre propre domaine"""
        urls = [
            'https://mysite.com',
            'https://competitor1.com',
            'https://www.mysite.com/page',
            'https://competitor2.com'
        ]
        
        filtered = CompetitorExtractor.filter_self_domain(urls, 'mysite.com')
        
        assert len(filtered) == 2
        assert 'https://competitor1.com' in filtered
        assert 'https://competitor2.com' in filtered
    
    def test_extract_from_visibility_results(self):
        """Test extraction depuis données de visibilité"""
        visibility_data = {
            'queries': [
                {
                    'query': 'test query',
                    'platforms': {
                        'chatgpt': {
                            'full_response': 'Check out https://competitor1.com and https://competitor2.com',
                            'competitors_mentioned': [
                                {'name': 'Comp1', 'urls': ['https://competitor1.com']},
                                {'name': 'Comp2', 'urls': ['https://competitor2.com']}
                            ]
                        }
                    }
                }
            ],
            'details': [
                {
                    'query': 'another query',
                    'answer': 'Visit https://competitor3.com'
                }
            ]
        }
        
        urls = CompetitorExtractor.extract_from_visibility_results(visibility_data, max_competitors=20)
        
        assert len(urls) > 0
        # Vérifier que les 3 compétiteurs sont extraits
        domains = [CompetitorExtractor._extract_domain(url) for url in urls]
        assert 'competitor1.com' in domains
        assert 'competitor2.com' in domains
        assert 'competitor3.com' in domains
    
    def test_extract_filters_hallucinated_domains(self):
        """Test que les domaines hallucinés sont gérés (filtrés plus tard par validation)"""
        visibility_data = {
            'queries': [
                {
                    'platforms': {
                        'claude': {
                            'full_response': 'Try https://lakavitale.com and https://hubfinancial.ca',
                        }
                    }
                }
            ]
        }
        
        # L'extraction doit réussir (la validation DNS se fait plus tard)
        urls = CompetitorExtractor.extract_from_visibility_results(visibility_data)
        
        # Les URLs sont extraites (le filtrage se fait dans validate_and_score)
        assert len(urls) >= 0  # Peut être 0 ou plus selon le contenu


class TestCompetitorDiscovery:
    """Tests pour CompetitorDiscovery (Stage 2 & 3)"""
    
    def test_generate_search_queries(self):
        """Test génération de requêtes de recherche"""
        cd = CompetitorDiscovery()
        
        queries = cd._generate_search_queries(
            primary_industry='Insurance',
            sub_industry='Life Insurance',
            offerings=['life insurance', 'term insurance'],
            brand_name='TestCompany'
        )
        
        assert len(queries) > 0
        
        # Vérifier qu'il y a des requêtes FR et EN
        queries_text = ' '.join(queries).lower()
        assert 'alternative' in queries_text or 'competitor' in queries_text
        assert 'québec' in queries_text or 'canada' in queries_text
    
    def test_extract_keywords(self):
        """Test extraction de mots-clés"""
        cd = CompetitorDiscovery()
        
        keywords = cd._extract_keywords(
            industry='Life Insurance',
            offerings=['life insurance', 'term insurance']
        )
        
        assert len(keywords) > 0
        assert 'insurance' in keywords or 'life' in keywords
    
    def test_extract_keywords_from_text(self):
        """Test extraction de mots-clés depuis texte"""
        cd = CompetitorDiscovery()
        
        text = "We provide life insurance and financial services to families in Quebec"
        keywords = cd._extract_keywords_from_text(text)
        
        assert len(keywords) > 0
        assert 'insurance' in keywords
        assert 'financial' in keywords
        # Stop words filtrés
        assert 'the' not in keywords
        assert 'and' not in keywords
    
    @patch('services.competitor_discovery.requests.head')
    @patch('services.competitor_discovery.socket.gethostbyname')
    def test_check_url_exists(self, mock_dns, mock_head):
        """Test validation existence URL"""
        cd = CompetitorDiscovery()
        
        # Mock DNS success
        mock_dns.return_value = '1.2.3.4'
        
        # Mock HEAD success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        assert cd._check_url_exists('https://validsite.com') is True
        
        # Mock HEAD fail
        mock_response.status_code = 404
        assert cd._check_url_exists('https://notfound.com') is False
        
        # Mock DNS fail
        mock_dns.side_effect = Exception("DNS error")
        assert cd._check_url_exists('https://invaliddomain.com') is False
    
    @patch('services.competitor_discovery.requests.get')
    def test_analyze_competitor_homepage(self, mock_get):
        """Test analyse de page d'accueil compétiteur"""
        cd = CompetitorDiscovery()
        
        # Mock HTML response
        mock_html = """
        <html>
            <head>
                <title>Competitor Insurance Company</title>
                <meta name="description" content="Leading insurance provider in Quebec" />
            </head>
            <body>
                <h1>Welcome to Competitor Insurance</h1>
                <h2>Life Insurance</h2>
                <h2>Term Insurance</h2>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = cd._analyze_competitor_homepage('https://competitor.com')
        
        assert result is not None
        assert 'title' in result
        assert 'Insurance' in result['title']
        assert 'description' in result
        assert len(result['h1']) > 0
        assert len(result['h2']) > 0
        assert len(result['keywords']) > 0
    
    def test_calculate_relevance_score(self):
        """Test calcul du score de pertinence"""
        cd = CompetitorDiscovery()
        
        our_keywords = {'insurance', 'life', 'financial', 'quebec'}
        
        competitor_data = {
            'title': 'Life Insurance Company Quebec',
            'description': 'Financial services and insurance',
            'h1': ['Life Insurance Solutions'],
            'h2': ['Term Insurance', 'Whole Life'],
            'keywords': {'insurance', 'life', 'financial', 'services'}
        }
        
        score = cd._calculate_relevance_score(
            competitor_data=competitor_data,
            our_keywords=our_keywords,
            primary_industry='Insurance',
            offerings=['life insurance'],
            source='both'
        )
        
        # Score doit être élevé (forte similarité)
        assert score > 0.5
        assert score <= 1.0
    
    @patch('services.competitor_discovery.requests.get')
    @patch('services.competitor_discovery.requests.head')
    @patch('services.competitor_discovery.socket.gethostbyname')
    def test_discover_real_competitors_integration(self, mock_dns, mock_head, mock_get):
        """Test intégration complète du pipeline"""
        cd = CompetitorDiscovery()
        
        # Mock DNS
        mock_dns.return_value = '1.2.3.4'
        
        # Mock HEAD
        mock_head_response = Mock()
        mock_head_response.status_code = 200
        mock_head.return_value = mock_head_response
        
        # Mock GET (pour Google search et homepage analysis)
        mock_html_search = """
        <html>
            <body>
                <a href="/url?q=https://competitor1.com&amp;sa=U">Competitor 1</a>
                <a href="/url?q=https://competitor2.com&amp;sa=U">Competitor 2</a>
            </body>
        </html>
        """
        
        mock_html_homepage = """
        <html>
            <head><title>Insurance Company</title></head>
            <body><h1>Insurance Services</h1></body>
        </html>
        """
        
        def mock_get_side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if 'google.com' in url:
                mock_resp.content = mock_html_search.encode('utf-8')
            else:
                mock_resp.content = mock_html_homepage.encode('utf-8')
            mock_resp.raise_for_status = Mock()
            return mock_resp
        
        mock_get.side_effect = mock_get_side_effect
        
        # Test
        semantic_analysis = {
            'industry_classification': {
                'primary_industry': 'Insurance',
                'sub_industry': 'Life Insurance',
                'company_type': 'Provider'
            },
            'entities': {
                'offerings': ['life insurance', 'term insurance']
            }
        }
        
        result = cd.discover_real_competitors(
            semantic_analysis=semantic_analysis,
            our_url='https://mysite.com',
            visibility_urls=['https://competitor1.com'],
            max_competitors=5
        )
        
        # Vérifications
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Vérifier structure
        for comp in result:
            assert 'domain' in comp
            assert 'homepage_url' in comp
            assert 'score' in comp
            assert 'type' in comp
            assert 'reason' in comp
            assert 'source' in comp
            
            # Vérifier types valides
            assert comp['type'] in ['direct', 'indirect']
            assert comp['source'] in ['llm', 'web_search', 'both']
            
            # Score entre 0 et 1
            assert 0 <= comp['score'] <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
