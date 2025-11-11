import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from 'sonner';
import { BarChart3, FileText, TrendingUp, Zap } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    url: '',
    consent: true
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.url) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/leads`, formData);
      const leadId = response.data.id;
      
      // Get the analysis job
      const jobsResponse = await axios.get(`${API}/leads`);
      const lead = jobsResponse.data.find(l => l.id === leadId);
      
      if (lead && lead.latestJob) {
        toast.success('Analyse lancée avec succès!');
        navigate(`/analysis/${lead.latestJob.id}`);
      } else {
        toast.error('Erreur lors du lancement de l\'analyse');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Erreur lors de la soumission du formulaire');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="flex justify-between items-center mb-16">
            <div className="flex items-center space-x-3">
              <img src="/sekoia-logo.png" alt="SEKOIA" className="h-10" />
            </div>
            <Button 
              variant="outline" 
              onClick={() => navigate('/dashboard')}
              data-testid="dashboard-nav-btn"
              className="border-gray-800 text-gray-800 hover:bg-gray-800 hover:text-white"
            >
              Dashboard
            </Button>
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Text */}
            <div className="animate-fade-in">
              <p className="text-sm font-semibold text-gray-600 mb-4 tracking-wider uppercase">Analyse GEO Professionnelle</p>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight text-gray-900">
                Optimisez votre visibilité dans les
                <span className="block mt-2">moteurs génératifs</span>
              </h1>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Analyse complète de votre site web selon 8 critères GEO. Découvrez comment améliorer votre présence sur ChatGPT, Perplexity et autres IA génératives.
              </p>

              {/* Features */}
              <div className="grid grid-cols-2 gap-6 mb-8">
                <div className="flex items-start space-x-3">
                  <BarChart3 className="w-6 h-6 text-gray-800 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-base text-gray-900">8 Critères GEO</h3>
                    <p className="text-sm text-gray-600">Analyse détaillée</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <FileText className="w-6 h-6 text-gray-800 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-base text-gray-900">Rapport PDF</h3>
                    <p className="text-sm text-gray-600">Export professionnel</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <TrendingUp className="w-6 h-6 text-gray-800 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-base text-gray-900">Recommandations</h3>
                    <p className="text-sm text-gray-600">Actionnables priorisées</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Zap className="w-6 h-6 text-gray-800 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-base text-gray-900">IA Claude</h3>
                    <p className="text-sm text-gray-600">Analyse avancée</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - Form */}
            <div className="glass-effect rounded-2xl p-8 animate-fade-in" style={{animationDelay: '0.2s'}}>
              <h2 className="text-2xl font-bold mb-2 text-gray-900">Analyse GEO gratuite</h2>
              <p className="text-sm text-gray-600 mb-6">Obtenez votre rapport en quelques minutes</p>
              
              <form onSubmit={handleSubmit} className="space-y-4" data-testid="lead-form">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName" className="text-gray-700">Prénom *</Label>
                    <Input
                      id="firstName"
                      data-testid="firstName-input"
                      value={formData.firstName}
                      onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                      placeholder="Jean"
                      required
                      className="border-gray-300 focus:border-gray-800 focus:ring-gray-800"
                    />
                  </div>
                  <div>
                    <Label htmlFor="lastName" className="text-gray-700">Nom *</Label>
                    <Input
                      id="lastName"
                      data-testid="lastName-input"
                      value={formData.lastName}
                      onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                      placeholder="Dupont"
                      required
                      className="border-gray-300 focus:border-gray-800 focus:ring-gray-800"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="email" className="text-gray-700">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    data-testid="email-input"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="jean.dupont@exemple.com"
                    required
                    className="border-gray-300 focus:border-gray-800 focus:ring-gray-800"
                  />
                </div>

                <div>
                  <Label htmlFor="company" className="text-gray-700">Entreprise</Label>
                  <Input
                    id="company"
                    data-testid="company-input"
                    value={formData.company}
                    onChange={(e) => setFormData({...formData, company: e.target.value})}
                    placeholder="Mon Entreprise Inc."
                    className="border-gray-300 focus:border-gray-800 focus:ring-gray-800"
                  />
                </div>

                <div>
                  <Label htmlFor="url" className="text-gray-700">URL de votre site web *</Label>
                  <Input
                    id="url"
                    type="url"
                    data-testid="url-input"
                    value={formData.url}
                    onChange={(e) => setFormData({...formData, url: e.target.value})}
                    placeholder="https://www.exemple.com"
                    required
                    className="border-gray-300 focus:border-gray-800 focus:ring-gray-800"
                  />
                </div>

                <div className="flex items-start space-x-2">
                  <Checkbox
                    id="consent"
                    data-testid="consent-checkbox"
                    checked={formData.consent}
                    onCheckedChange={(checked) => setFormData({...formData, consent: checked})}
                  />
                  <label htmlFor="consent" className="text-sm text-gray-600 leading-tight">
                    J'accepte de recevoir des communications marketing conformément à la Loi 25 et à la LCAP (CASL)
                  </label>
                </div>

                <Button 
                  type="submit" 
                  className="w-full btn-primary" 
                  disabled={loading}
                  data-testid="submit-lead-btn"
                >
                  {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="loading-spinner w-5 h-5"></div>
                      <span>Analyse en cours...</span>
                    </div>
                  ) : (
                    'Lancer l\'analyse GEO'
                  )}
                </Button>
              </form>

              <p className="text-xs text-gray-500 text-center mt-4">
                Votre analyse sera générée en 2-5 minutes
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm">© 2025 SEKOIA. Tous droits réservés.</p>
          <p className="text-xs text-gray-400 mt-2">Outil d'analyse GEO développé par SEKOIA</p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
