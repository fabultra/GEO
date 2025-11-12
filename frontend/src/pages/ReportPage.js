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
    if (score >= 7) return '#22c55e';  // green
    if (score >= 5) return '#eab308';  // yellow
    if (score >= 3) return '#f97316';  // orange
    return '#ef4444';  // red
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
          <div className="flex space-x-3">
            <Button 
              onClick={() => window.open(`${API}/reports/${reportId}/dashboard`, '_blank')}
              variant="outline"
              data-testid="view-dashboard-btn"
            >
              📊 Dashboard HTML
            </Button>
            <Button 
              onClick={() => window.open(`${API}/reports/${reportId}/docx`, '_blank')}
              variant="outline"
              data-testid="download-docx-btn"
            >
              📄 Rapport Word
            </Button>
            <Button 
              onClick={downloadPDF} 
              className="btn-primary"
              data-testid="download-pdf-btn"
            >
              <Download className="w-4 h-4 mr-2" />
              PDF
            </Button>
          </div>
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
        <Tabs defaultValue="summary" className="glass-effect rounded-2xl p-6">
          <TabsList className="grid w-full grid-cols-8 mb-6 text-sm">
            <TabsTrigger value="summary" data-testid="summary-tab">Synthèse</TabsTrigger>
            <TabsTrigger value="scores" data-testid="scores-tab">Scores</TabsTrigger>
            <TabsTrigger value="recommendations" data-testid="recommendations-tab">Recommandations</TabsTrigger>
            <TabsTrigger value="quickwins" data-testid="quickwins-tab">Quick Wins</TabsTrigger>
            <TabsTrigger value="visibility" data-testid="visibility-tab">🔍 Visibilité</TabsTrigger>
            <TabsTrigger value="competitors" data-testid="competitors-tab">🏆 Compétiteurs</TabsTrigger>
            <TabsTrigger value="schemas" data-testid="schemas-tab">📋 Schemas</TabsTrigger>
            <TabsTrigger value="analysis" data-testid="analysis-tab">Analyse</TabsTrigger>
          </TabsList>

          {/* Executive Summary Tab */}
          <TabsContent value="summary" className="space-y-6">
            <h3 className="text-2xl font-bold mb-4">Synthèse Exécutive</h3>
            
            {report.executive_summary ? (
              <div className="space-y-6">
                {/* Global Assessment */}
                <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-l-4 border-blue-600">
                  <h4 className="font-bold text-lg mb-3 text-blue-900">Évaluation Globale</h4>
                  <p className="text-gray-700 text-base leading-relaxed">
                    {report.executive_summary.global_assessment}
                  </p>
                </div>

                {/* Critical Issues */}
                {report.executive_summary.critical_issues && report.executive_summary.critical_issues.length > 0 && (
                  <div className="p-6 bg-red-50 rounded-xl border-l-4 border-red-600">
                    <h4 className="font-bold text-lg mb-3 text-red-900 flex items-center">
                      <AlertCircle className="w-5 h-5 mr-2" />
                      Problèmes Critiques
                    </h4>
                    <ul className="space-y-2">
                      {report.executive_summary.critical_issues.map((issue, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <span className="text-red-600 font-bold mt-1">•</span>
                          <span className="text-gray-700">{issue}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Key Opportunities */}
                {report.executive_summary.key_opportunities && report.executive_summary.key_opportunities.length > 0 && (
                  <div className="p-6 bg-green-50 rounded-xl border-l-4 border-green-600">
                    <h4 className="font-bold text-lg mb-3 text-green-900 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2" />
                      Opportunités Majeures
                    </h4>
                    <ul className="space-y-2">
                      {report.executive_summary.key_opportunities.map((opp, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <span className="text-green-600 font-bold mt-1">•</span>
                          <span className="text-gray-700">{opp}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* ROI & Investment */}
                <div className="grid md:grid-cols-2 gap-4">
                  {report.executive_summary.estimated_visibility_loss && (
                    <div className="p-6 bg-orange-50 rounded-xl border border-orange-200">
                      <h4 className="font-semibold mb-2 text-orange-900">Visibilité Perdue Estimée</h4>
                      <p className="text-2xl font-bold text-orange-700">
                        {report.executive_summary.estimated_visibility_loss}
                      </p>
                    </div>
                  )}
                  
                  {report.executive_summary.recommended_investment && (
                    <div className="p-6 bg-blue-50 rounded-xl border border-blue-200">
                      <h4 className="font-semibold mb-2 text-blue-900">Investissement Recommandé</h4>
                      <p className="text-sm text-gray-700">
                        {report.executive_summary.recommended_investment}
                      </p>
                    </div>
                  )}
                </div>

                {/* ROI Estimation */}
                {report.roi_estimation && (
                  <div className="p-6 bg-purple-50 rounded-xl border border-purple-200">
                    <h4 className="font-bold text-lg mb-4 text-purple-900">Estimation du ROI</h4>
                    <div className="space-y-3">
                      <div>
                        <span className="font-semibold text-sm text-purple-800">Situation Actuelle:</span>
                        <p className="text-gray-700 mt-1">{report.roi_estimation.current_situation}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-sm text-purple-800">Amélioration Potentielle:</span>
                        <p className="text-gray-700 mt-1">{report.roi_estimation.potential_improvement}</p>
                      </div>
                      <div>
                        <span className="font-semibold text-sm text-purple-800">Calendrier:</span>
                        <p className="text-gray-700 mt-1">{report.roi_estimation.timeline}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Synthèse exécutive non disponible</p>
              </div>
            )}
          </TabsContent>

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

          {/* Quick Wins Tab */}
          <TabsContent value="quickwins">
            <h3 className="text-xl font-bold mb-4 flex items-center">
              <Sparkles className="w-6 h-6 mr-2 text-yellow-600" />
              Quick Wins - Actions Immédiates
            </h3>
            
            <div className="mb-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-sm text-gray-700">
                Ces actions peuvent être implémentées <strong>cette semaine</strong> pour des résultats immédiats.
                Impact élevé avec effort minimal.
              </p>
            </div>
            
            {report.quick_wins && report.quick_wins.length > 0 ? (
              <div className="space-y-4">
                {report.quick_wins.map((qw, idx) => (
                  <div 
                    key={idx} 
                    className="border-2 border-yellow-300 rounded-xl p-6 bg-white hover:shadow-lg transition-shadow"
                    data-testid={`quickwin-${idx}`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-bold text-lg text-gray-900">
                        ⚡ {idx + 1}. {qw.title}
                      </h4>
                      <span className="text-xs bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full font-semibold">
                        {qw.time_required}
                      </span>
                    </div>
                    
                    <div className="mb-3 p-3 bg-green-50 rounded-lg">
                      <span className="text-xs font-semibold text-green-800">Impact Attendu:</span>
                      <p className="text-sm text-gray-700 mt-1">{qw.impact}</p>
                    </div>
                    
                    <p className="text-gray-700">{qw.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Aucun quick win disponible</p>
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

          {/* Competitors Tab - NEW */}
          <TabsContent value="competitors" className="space-y-6">
            <h3 className="text-2xl font-bold mb-4 flex items-center">
              <span className="mr-2">🏆</span>
              Intelligence Compétitive
            </h3>
            
            {report.competitive_intelligence && report.competitive_intelligence.competitors_analyzed > 0 ? (
              <div className="space-y-6">
                {/* Summary */}
                <div className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-l-4 border-purple-600">
                  <h4 className="font-bold text-lg mb-2 text-purple-900">Résumé</h4>
                  <p className="text-gray-700">
                    <strong>{report.competitive_intelligence.competitors_analyzed}</strong> compétiteurs analysés trouvés dans les réponses des IA génératives.
                  </p>
                </div>

                {/* Comparative Metrics Table */}
                {report.competitive_intelligence.comparative_metrics && 
                 report.competitive_intelligence.comparative_metrics.rows && 
                 report.competitive_intelligence.comparative_metrics.rows.length > 0 && (
                  <div className="overflow-x-auto">
                    <h4 className="font-bold text-lg mb-3">📊 Tableau Comparatif</h4>
                    <table className="w-full border-collapse bg-white rounded-lg overflow-hidden shadow">
                      <thead className="bg-gray-800 text-white">
                        <tr>
                          {report.competitive_intelligence.comparative_metrics.headers.map((header, idx) => (
                            <th key={idx} className="px-4 py-3 text-left text-sm font-semibold">
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {report.competitive_intelligence.comparative_metrics.rows.map((row, idx) => (
                          <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            {row.map((cell, cellIdx) => (
                              <td key={cellIdx} className="px-4 py-3 text-sm border-b border-gray-200">
                                {cellIdx === 0 ? (
                                  <span className="font-semibold text-gray-800">{cell}</span>
                                ) : (
                                  <span className="text-gray-700">{cell}</span>
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Actionable Insights */}
                {report.competitive_intelligence.actionable_insights && 
                 report.competitive_intelligence.actionable_insights.length > 0 && (
                  <div>
                    <h4 className="font-bold text-lg mb-4">💡 Recommandations Basées sur l'Analyse Compétitive</h4>
                    <div className="space-y-4">
                      {report.competitive_intelligence.actionable_insights.map((insight, idx) => (
                        <div 
                          key={idx} 
                          className={`p-6 rounded-xl border-l-4 ${
                            insight.priority === 'CRITIQUE' ? 'bg-red-50 border-red-600' :
                            insight.priority === 'HAUTE' ? 'bg-orange-50 border-orange-600' :
                            'bg-blue-50 border-blue-600'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <h5 className="font-bold text-lg">{insight.title}</h5>
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              insight.priority === 'CRITIQUE' ? 'bg-red-600 text-white' :
                              insight.priority === 'HAUTE' ? 'bg-orange-600 text-white' :
                              'bg-blue-600 text-white'
                            }`}>
                              {insight.priority}
                            </span>
                          </div>
                          <div className="space-y-2 text-sm">
                            <p><strong className="text-gray-700">Problème:</strong> <span className="text-gray-600">{insight.problem}</span></p>
                            <p><strong className="text-gray-700">Action:</strong> <span className="text-gray-600">{insight.action}</span></p>
                            <div className="flex justify-between mt-3 pt-3 border-t border-gray-200">
                              <span className="text-green-600 font-semibold">Impact: {insight.impact}</span>
                              <span className="text-blue-600">Temps: {insight.time}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center bg-gray-50 rounded-xl">
                <p className="text-gray-600">Aucune donnée de compétiteurs disponible pour cette analyse.</p>
                <p className="text-sm text-gray-500 mt-2">Les compétiteurs sont extraits automatiquement des réponses des IA génératives.</p>
              </div>
            )}
          </TabsContent>

          {/* Schemas Tab - NEW */}
          <TabsContent value="schemas" className="space-y-6">
            <h3 className="text-2xl font-bold mb-4 flex items-center">
              <span className="mr-2">📋</span>
              Schemas JSON-LD Générés
            </h3>
            
            {report.schemas && Object.keys(report.schemas).length > 0 ? (
              <div className="space-y-6">
                {/* Summary */}
                <div className="p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border-l-4 border-blue-600">
                  <h4 className="font-bold text-lg mb-2 text-blue-900">Impact GEO des Schemas</h4>
                  <p className="text-gray-700">
                    <strong>{Object.keys(report.schemas).filter(k => k !== 'implementation_guide' && k !== 'error').length}</strong> types de schemas générés automatiquement.
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Les schemas JSON-LD améliorent votre visibilité dans les IA de <strong>+40-50%</strong> en rendant votre contenu plus facilement compréhensible.
                  </p>
                </div>

                {/* Implementation Guide */}
                {report.schemas.implementation_guide && (
                  <div className="p-6 bg-yellow-50 rounded-xl border border-yellow-200">
                    <h4 className="font-bold text-lg mb-3 text-yellow-900 flex items-center">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Guide d'Implémentation
                    </h4>
                    <div className="prose prose-sm max-w-none">
                      <pre className="bg-white p-4 rounded-lg text-xs overflow-x-auto border border-gray-200 whitespace-pre-wrap">
                        {report.schemas.implementation_guide}
                      </pre>
                    </div>
                    <div className="mt-4 p-4 bg-white rounded-lg border border-yellow-300">
                      <p className="text-sm font-semibold text-yellow-900 mb-2">⚡ Quick Wins Schemas:</p>
                      <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                        <li>Ajouter Organization + WebSite sur page d'accueil → <span className="font-semibold text-green-600">+40% visibilité</span></li>
                        <li>Créer page FAQ avec FAQPage schema → <span className="font-semibold text-green-600">+60% chances citation</span></li>
                        <li>Ajouter Article schema sur 5 articles → <span className="font-semibold text-green-600">+30% indexation</span></li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Schema Types List */}
                <div>
                  <h4 className="font-bold text-lg mb-4">📦 Schemas Générés</h4>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.keys(report.schemas)
                      .filter(key => key !== 'implementation_guide' && key !== 'error' && report.schemas[key])
                      .map((schemaType, idx) => {
                        const schemaTypeNames = {
                          'organization': '🏢 Organization',
                          'website': '🌐 WebSite',
                          'faq': '❓ FAQPage',
                          'article': '📄 Article',
                          'local_business': '📍 LocalBusiness',
                          'service': '🔧 Service',
                          'how_to': '📖 HowTo',
                          'review': '⭐ Review',
                          'breadcrumb': '🍞 Breadcrumb'
                        };
                        
                        const displayName = schemaTypeNames[schemaType] || schemaType;
                        const schemaData = report.schemas[schemaType];
                        const schemaCount = Array.isArray(schemaData) ? schemaData.length : 1;
                        
                        return (
                          <div key={idx} className="p-4 bg-white rounded-lg border-2 border-gray-200 hover:border-blue-400 transition-colors">
                            <div className="flex items-center justify-between mb-2">
                              <h5 className="font-semibold text-gray-800">{displayName}</h5>
                              {schemaCount > 1 && (
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">
                                  {schemaCount}
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-gray-500 mb-3">
                              {schemaType === 'organization' ? 'Identité de votre organisation' :
                               schemaType === 'website' ? 'Informations générales du site' :
                               schemaType === 'faq' ? 'Questions-réponses structurées' :
                               schemaType === 'article' ? 'Contenu éditorial' :
                               schemaType === 'local_business' ? 'Informations entreprise locale' :
                               schemaType === 'service' ? 'Services offerts' :
                               schemaType === 'how_to' ? 'Guides pratiques étape par étape' :
                               schemaType === 'review' ? 'Évaluations et avis' :
                               schemaType === 'breadcrumb' ? 'Navigation hiérarchique' :
                               'Schema markup'}
                            </p>
                            <details className="text-xs">
                              <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-medium">
                                Voir le code JSON-LD
                              </summary>
                              <pre className="mt-2 p-3 bg-gray-50 rounded border border-gray-200 overflow-x-auto text-[10px]">
                                {JSON.stringify(schemaData, null, 2)}
                              </pre>
                            </details>
                          </div>
                        );
                      })}
                  </div>
                </div>

                {/* Validation Links */}
                <div className="p-6 bg-gray-50 rounded-xl">
                  <h4 className="font-bold mb-3">🔍 Valider vos Schemas</h4>
                  <p className="text-sm text-gray-600 mb-3">Après implémentation, validez vos schemas avec ces outils:</p>
                  <div className="flex flex-wrap gap-3">
                    <a 
                      href="https://search.google.com/test/rich-results" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                    >
                      Google Rich Results Test
                    </a>
                    <a 
                      href="https://validator.schema.org/" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors"
                    >
                      Schema.org Validator
                    </a>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center bg-gray-50 rounded-xl">
                <p className="text-gray-600">Aucun schema généré pour cette analyse.</p>
                <p className="text-sm text-gray-500 mt-2">Les schemas JSON-LD sont générés automatiquement basés sur le contenu de votre site.</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ReportPage;
