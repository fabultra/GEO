import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Download, ArrowLeft, TrendingUp, AlertCircle, CheckCircle2, XCircle, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportPage = () => {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await axios.get(`${API}/reports/${reportId}`);
        setReport(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching report:', error);
        toast.error('Erreur lors du chargement du rapport');
        setLoading(false);
      }
    };

    fetchReport();
  }, [reportId]);

  const downloadPDF = async () => {
    try {
      const response = await axios.get(`${API}/reports/${reportId}/pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rapport-geo-${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Rapport PDF téléchargé!');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error('Erreur lors du téléchargement du PDF');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 7) return 'bg-green-500';
    if (score >= 5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getImpactBadgeClass = (impact) => {
    if (impact === 'high') return 'badge badge-high';
    if (impact === 'medium') return 'badge badge-medium';
    return 'badge badge-low';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Rapport non trouvé</h2>
          <Button onClick={() => navigate('/')} className="btn-primary">
            Retour à l'accueil
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/dashboard')}
            data-testid="back-to-dashboard-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour
          </Button>
          <Button 
            onClick={downloadPDF} 
            className="btn-primary"
            data-testid="download-pdf-btn"
          >
            <Download className="w-4 h-4 mr-2" />
            Télécharger PDF
          </Button>
        </div>

        {/* Title */}
        <div className="glass-effect rounded-2xl p-8 mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2">Rapport GEO</h1>
          <p className="text-gray-600" data-testid="report-url">{report.url}</p>
          <p className="text-sm text-gray-500 mt-2">
            Généré le {new Date(report.createdAt).toLocaleDateString('fr-FR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>

        {/* Global Score */}
        <div className="glass-effect rounded-2xl p-8 mb-8 text-center">
          <h2 className="text-2xl font-bold mb-6">Score Global GEO</h2>
          <div className="flex justify-center mb-4">
            <div className={`score-circle ${getScoreColor(report.scores.global_score)}`} data-testid="global-score">
              {report.scores.global_score.toFixed(1)}/10
            </div>
          </div>
          <p className="text-gray-600">
            {report.scores.global_score >= 7 ? 'Excellent! Votre site est bien optimisé.' :
             report.scores.global_score >= 5 ? 'Bon début, mais des améliorations sont possibles.' :
             'Important potentiel d\'amélioration identifié.'}
          </p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="scores" className="glass-effect rounded-2xl p-6">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="scores" data-testid="scores-tab">Scores</TabsTrigger>
            <TabsTrigger value="recommendations" data-testid="recommendations-tab">Recommandations</TabsTrigger>
            <TabsTrigger value="analysis" data-testid="analysis-tab">Analyse</TabsTrigger>
          </TabsList>

          {/* Scores Tab */}
          <TabsContent value="scores" className="space-y-6">
            <h3 className="text-xl font-bold mb-4">Détail des 8 Critères GEO</h3>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Structure & Formatage', value: report.scores.structure, key: 'structure' },
                { label: 'Densité d\'Information', value: report.scores.infoDensity, key: 'infoDensity' },
                { label: 'Lisibilité Machine/SEO', value: report.scores.readability, key: 'readability' },
                { label: 'E-E-A-T', value: report.scores.eeat, key: 'eeat' },
                { label: 'Contenu Éducatif', value: report.scores.educational, key: 'educational' },
                { label: 'Organisation Thématique', value: report.scores.thematic, key: 'thematic' },
                { label: 'Optimisation IA', value: report.scores.aiOptimization, key: 'aiOptimization' },
                { label: 'Visibilité Actuelle', value: report.scores.visibility, key: 'visibility' }
              ].map((criterion, idx) => (
                <div 
                  key={idx} 
                  className="rounded-xl p-6 text-center transition-transform hover:scale-105 shadow-lg"
                  style={{
                    background: `linear-gradient(135deg, ${getScoreColor(criterion.value)} 0%, ${getScoreColor(criterion.value)}dd 100%)`
                  }}
                  data-testid={`score-${criterion.key}`}
                >
                  <div className="text-white">
                    <div className="text-3xl font-bold mb-2">{criterion.value?.toFixed(1) || '0.0'}</div>
                    <div className="text-xs font-medium uppercase tracking-wide">{criterion.label}</div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Score Legend */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-3 text-sm">Interprétation des scores:</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span>7-10: Excellent</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                  <span>5-6.9: Bon</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-orange-500 rounded"></div>
                  <span>3-4.9: Moyen</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span>0-2.9: Faible</span>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations">
            <h3 className="text-xl font-bold mb-4">
              <TrendingUp className="inline w-6 h-6 mr-2" />
              Recommandations Prioritaires
            </h3>
            
            {report.recommendations && report.recommendations.length > 0 ? (
              <div className="space-y-4">
                {report.recommendations.slice(0, 10).map((rec, idx) => (
                  <div key={idx} className="recommendation-card" data-testid={`recommendation-${idx}`}>
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-lg">{idx + 1}. {rec.title}</h4>
                      <span className={getImpactBadgeClass(rec.impact)}>{rec.impact}</span>
                    </div>
                    
                    <div className="flex space-x-2 mb-3">
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {rec.criterion}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded">
                        Effort: {rec.effort}
                      </span>
                      <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                        Priorité: {rec.priority}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-2">{rec.description}</p>
                    
                    {rec.example && (
                      <div className="bg-gray-50 p-3 rounded-lg mt-2">
                        <p className="text-sm font-medium text-gray-600 mb-1">Exemple:</p>
                        <p className="text-sm text-gray-700">{rec.example}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Aucune recommandation disponible</p>
              </div>
            )}
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis">
            <h3 className="text-xl font-bold mb-4">Analyse Détaillée</h3>
            
            {/* Methodology Section */}
            <div className="mb-8 p-6 bg-blue-50 rounded-xl border border-blue-200">
              <h4 className="font-bold text-blue-900 mb-3 flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                Méthodologie d'analyse
              </h4>
              <div className="text-sm text-gray-700 space-y-2">
                <p>
                  <strong>Modèle IA:</strong> Claude Sonnet 4 (Anthropic)
                </p>
                <p>
                  <strong>Processus:</strong> Crawling automatique → Extraction de contenu → Analyse IA → Scoring 0-10
                </p>
                <p>
                  <strong>Données analysées:</strong> Structure HTML, meta tags, headings (H1-H3), contenu textuel, 
                  JSON-LD, liens internes, densité de mots
                </p>
              </div>
            </div>
            
            {report.analysis ? (
              <div className="space-y-6">
                {report.analysis.strengths && report.analysis.strengths.length > 0 && (
                  <div className="bg-green-50 rounded-xl p-6 border border-green-200">
                    <h4 className="font-semibold text-green-800 mb-3 text-lg flex items-center">
                      <CheckCircle2 className="w-5 h-5 mr-2" />
                      Forces identifiées
                    </h4>
                    <ul className="list-disc list-inside space-y-2">
                      {report.analysis.strengths.map((strength, idx) => (
                        <li key={idx} className="text-gray-700">{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {report.analysis.weaknesses && report.analysis.weaknesses.length > 0 && (
                  <div className="bg-red-50 rounded-xl p-6 border border-red-200">
                    <h4 className="font-semibold text-red-800 mb-3 text-lg flex items-center">
                      <XCircle className="w-5 h-5 mr-2" />
                      Faiblesses détectées
                    </h4>
                    <ul className="list-disc list-inside space-y-2">
                      {report.analysis.weaknesses.map((weakness, idx) => (
                        <li key={idx} className="text-gray-700">{weakness}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {report.analysis.opportunities && report.analysis.opportunities.length > 0 && (
                  <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                    <h4 className="font-semibold text-blue-800 mb-3 text-lg flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2" />
                      Opportunités d'amélioration
                    </h4>
                    <ul className="list-disc list-inside space-y-2">
                      {report.analysis.opportunities.map((opportunity, idx) => (
                        <li key={idx} className="text-gray-700">{opportunity}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Aucune analyse détaillée disponible</p>
              </div>
            )}
            
            {/* Scoring Explanation */}
            <div className="mt-8 p-6 bg-gray-50 rounded-xl">
              <h4 className="font-bold mb-4">Comment interpréter les scores?</h4>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-semibold mb-2">Structure & Formatage</p>
                  <p className="text-gray-600">Hiérarchie HTML, balises sémantiques, organisation logique</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Densité d'Information</p>
                  <p className="text-gray-600">Profondeur du contenu, exhaustivité, données factuelles</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Lisibilité Machine/SEO</p>
                  <p className="text-gray-600">Meta tags, JSON-LD, structured data, balisage sémantique</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">E-E-A-T</p>
                  <p className="text-gray-600">Expertise, Expérience, Autorité, Confiance (sources, auteurs)</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Contenu Éducatif</p>
                  <p className="text-gray-600">Guides, FAQ, tutoriels, glossaires, exemples pratiques</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Organisation Thématique</p>
                  <p className="text-gray-600">Silos, maillage interne, architecture de l'information</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Optimisation IA</p>
                  <p className="text-gray-600">Format conversationnel, réponses rapides, définitions claires</p>
                </div>
                <div>
                  <p className="font-semibold mb-2">Visibilité Actuelle</p>
                  <p className="text-gray-600">Autorité du domaine, fraîcheur, signaux de ranking</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ReportPage;
