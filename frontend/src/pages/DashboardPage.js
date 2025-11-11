import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { ArrowLeft, FileText, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const response = await axios.get(`${API}/leads`);
        setLeads(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching leads:', error);
        toast.error('Erreur lors du chargement des données');
        setLoading(false);
      }
    };

    fetchLeads();
  }, []);

  const getStatusIcon = (status) => {
    if (status === 'completed') return <CheckCircle2 className="w-5 h-5 text-green-600" />;
    if (status === 'failed') return <XCircle className="w-5 h-5 text-red-600" />;
    return <Clock className="w-5 h-5 text-blue-600 animate-spin" />;
  };

  const getStatusText = (status) => {
    if (status === 'completed') return 'Terminé';
    if (status === 'failed') return 'Échoué';
    if (status === 'processing') return 'En cours';
    return 'En attente';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold">Dashboard SEKOIA</h1>
            <p className="text-gray-600 mt-2">Tous vos rapports d'analyse</p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => navigate('/')}
            data-testid="back-to-home-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Accueil
          </Button>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="glass-effect rounded-xl p-6">
            <div className="text-3xl font-bold text-blue-600">{leads.length}</div>
            <div className="text-sm text-gray-600 mt-1">Total analyses</div>
          </div>
          <div className="glass-effect rounded-xl p-6">
            <div className="text-3xl font-bold text-green-600">
              {leads.filter(l => l.latestJob?.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600 mt-1">Terminées</div>
          </div>
          <div className="glass-effect rounded-xl p-6">
            <div className="text-3xl font-bold text-yellow-600">
              {leads.filter(l => l.latestJob?.status === 'processing' || l.latestJob?.status === 'pending').length}
            </div>
            <div className="text-sm text-gray-600 mt-1">En cours</div>
          </div>
        </div>

        {/* Leads Table */}
        <div className="glass-effect rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-6">Analyses Récentes</h2>
          
          {leads.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">Aucune analyse pour le moment</p>
              <Button 
                onClick={() => navigate('/')} 
                className="btn-primary mt-4"
              >
                Créer votre première analyse
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full" data-testid="leads-table">
                <thead>
                  <tr className="border-b-2">
                    <th className="text-left py-3 px-2 font-semibold">Client</th>
                    <th className="text-left py-3 px-2 font-semibold">URL</th>
                    <th className="text-left py-3 px-2 font-semibold">Date</th>
                    <th className="text-left py-3 px-2 font-semibold">Statut</th>
                    <th className="text-left py-3 px-2 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead, idx) => (
                    <tr key={lead.id} className="border-b hover:bg-gray-50" data-testid={`lead-row-${idx}`}>
                      <td className="py-4 px-2">
                        <div>
                          <div className="font-medium">{lead.firstName} {lead.lastName}</div>
                          <div className="text-sm text-gray-500">{lead.email}</div>
                        </div>
                      </td>
                      <td className="py-4 px-2">
                        <div className="text-sm truncate max-w-xs">{lead.url}</div>
                      </td>
                      <td className="py-4 px-2 text-sm text-gray-600">
                        {new Date(lead.createdAt).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="py-4 px-2">
                        <div className="flex items-center space-x-2">
                          {lead.latestJob && getStatusIcon(lead.latestJob.status)}
                          <span className="text-sm">
                            {lead.latestJob ? getStatusText(lead.latestJob.status) : 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-2">
                        {lead.reports && lead.reports.length > 0 ? (
                          <Button 
                            size="sm" 
                            onClick={() => navigate(`/report/${lead.reports[0].id}`)}
                            data-testid={`view-report-btn-${idx}`}
                          >
                            Voir le rapport
                          </Button>
                        ) : lead.latestJob?.status === 'processing' || lead.latestJob?.status === 'pending' ? (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => navigate(`/analysis/${lead.latestJob.id}`)}
                          >
                            Voir progression
                          </Button>
                        ) : (
                          <span className="text-sm text-gray-400">Aucun rapport</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
