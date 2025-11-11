import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Progress } from '../components/ui/progress';
import { Button } from '../components/ui/button';
import { CheckCircle2, Loader2, XCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AnalysisPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const pollJobStatus = async () => {
      try {
        const response = await axios.get(`${API}/jobs/${jobId}`);
        setJob(response.data);
        setLoading(false);

        if (response.data.status === 'completed' && response.data.reportId) {
          setTimeout(() => {
            navigate(`/report/${response.data.reportId}`);
          }, 2000);
        } else if (response.data.status === 'processing' || response.data.status === 'pending') {
          setTimeout(pollJobStatus, 2000);
        }
      } catch (error) {
        console.error('Error polling job:', error);
        setLoading(false);
      }
    };

    pollJobStatus();
  }, [jobId, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="glass-effect rounded-2xl p-8 max-w-2xl w-full" data-testid="analysis-status-container">
        <div className="text-center">
          {job?.status === 'processing' || job?.status === 'pending' ? (
            <>
              <Loader2 className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-spin" />
              <h2 className="text-2xl font-bold mb-4">Analyse en cours...</h2>
              <p className="text-gray-600 mb-6">Nous analysons votre site web avec l'IA Claude</p>
              
              <Progress value={job.progress} className="mb-4" data-testid="analysis-progress" />
              <p className="text-sm text-gray-500">{job.progress}% complété</p>

              <div className="mt-8 text-left space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="text-sm">Crawling du site web</span>
                </div>
                <div className="flex items-center space-x-3">
                  {job.progress >= 40 ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : (
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                  )}
                  <span className="text-sm">Extraction du contenu</span>
                </div>
                <div className="flex items-center space-x-3">
                  {job.progress >= 70 ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : (
                    <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  )}
                  <span className="text-sm">Analyse IA des 8 critères GEO</span>
                </div>
                <div className="flex items-center space-x-3">
                  {job.progress >= 90 ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : (
                    <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                  )}
                  <span className="text-sm">Génération du rapport</span>
                </div>
              </div>
            </>
          ) : job?.status === 'completed' ? (
            <>
              <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4">Analyse terminée!</h2>
              <p className="text-gray-600 mb-6">Redirection vers votre rapport...</p>
            </>
          ) : (
            <>
              <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-4">Échec de l'analyse</h2>
              <p className="text-gray-600 mb-6">{job?.error || 'Une erreur est survenue'}</p>
              <Button onClick={() => navigate('/')} className="btn-primary">
                Retour à l'accueil
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
