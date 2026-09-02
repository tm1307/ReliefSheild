import React, { useState, useEffect } from 'react';
import SubmitForm from './components/SubmitForm';
import TrustScore from './components/TrustScore';
import BreakdownCard from './components/BreakdownCard';
import EvidenceGraph from './components/EvidenceGraph';
import ExtractedEntities from './components/ExtractedEntities';
import ShareReport from './components/ShareReport';
import StatsBar from './components/StatsBar';
import ReportHistory from './components/ReportHistory';

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch('https://reliefsheild.onrender.com/api/v1/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Failed to load stats', err));
  }, []);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setReport(null);

    const maxRetries = 8;
    const delayMs = 5000;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const res = await fetch('https://reliefsheild.onrender.com/api/v1/appeals/', {
          method: 'POST',
          body: formData,
        });
        
        if (!res.ok) {
          if (res.status === 502 || res.status === 503) {
            throw new Error('cold_start');
          }
          throw new Error('server_error');
        }
        
        const data = await res.json();
        setReport(data);
        setHistory(prev => {
          const exists = prev.find(item => item.appeal_id === data.appeal_id);
          if (exists) return prev;
          return [data, ...prev].slice(0, 5);
        });
        setLoading(false);
        return; // Success
      } catch (err) {
        if (err.message === 'server_error' || attempt === maxRetries) {
          setError('Failed to connect to verification server. Please ensure the backend is running.');
          setLoading(false);
          return;
        }
        // If it's a cold start or network error, wait and retry silently
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
            <span className="text-white text-xl">🛡️</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">ReliefShield</h1>
            <p className="text-xs text-slate-500">Trust Verification for Donation Appeals</p>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        <StatsBar stats={stats} />

        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-800">
            Verify Before You Donate
          </h2>
          <p className="text-slate-500 max-w-lg mx-auto">
            Submit a disaster relief appeal — as text, a link, or a screenshot — and get an
            evidence-backed trust report in seconds.
          </p>
        </div>

        <SubmitForm onSubmit={handleSubmit} loading={loading} />

        {error && (
          <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm">
            ⚠️ {error}
          </div>
        )}

        {report && (
          <div className="space-y-8 animate-fade-in">
            <TrustScore 
              score={report.final_score} 
              summary={report.summary} 
              risk_level={report.risk_level}
              recommendations={report.recommendations}
            />

            <ShareReport score={report.final_score} breakdown={report.breakdown} />

            <section>
              <h3 className="text-lg font-semibold text-slate-800 mb-4">Verification Breakdown</h3>
              <div className="space-y-3">
                {report.breakdown.map((item, i) => (
                  <BreakdownCard key={i} {...item} />
                ))}
              </div>
            </section>

            {report.evidence_graph && (
              <section>
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Evidence Graph</h3>
                <EvidenceGraph graph={report.evidence_graph} />
              </section>
            )}

            {report.extracted_entities && (
              <ExtractedEntities entities={report.extracted_entities} />
            )}
            
            <ReportHistory history={history} />
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 mt-16 py-6 text-center text-xs text-slate-400">
        ReliefShield © {new Date().getFullYear()} — Advanced Fraud Detection
      </footer>
    </div>
  );
}

export default App;
