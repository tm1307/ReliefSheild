import React, { useState } from 'react';
import SubmitForm from './components/SubmitForm';
import TrustScore from './components/TrustScore';
import BreakdownCard from './components/BreakdownCard';
import EvidenceGraph from './components/EvidenceGraph';
import ExtractedEntities from './components/ExtractedEntities';
import ShareReport from './components/ShareReport';

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const response = await fetch('/api/v1/appeals/', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      setReport(data);
    } catch (err) {
      console.error('Verification failed:', err);
      setError('Could not reach the verification server. Showing demo report.');
      setReport({
        appeal_id: 0,
        final_score: 45,
        summary: 'This appeal has some concerns that warrant caution before donating. Flagged checks: Payment. We could not independently verify: Claim. Passed checks: Identity, Similarity.',
        breakdown: [
          { check: 'Identity', status: 'Verified', points_deducted: 0, details: 'Found in NGO Darpan mock registry: NGO12345' },
          { check: 'Payment', status: 'Flagged', points_deducted: 30, details: "Payment ID 'random@ybl' appears to be a personal account not matching NGO name" },
          { check: 'Similarity', status: 'Verified', points_deducted: 0, details: 'Text does not strongly match known scams.' },
          { check: 'Claim', status: 'Unverifiable', points_deducted: 5, details: 'No specific verifiable claims extracted from the appeal text.' },
        ],
        evidence_graph: {
          nodes: [
            { id: 0, type: 'appeal', label: 'Submitted Appeal', status: 'neutral', detail: 'Demo appeal text...' },
            { id: 1, type: 'organisation', label: 'Red Cross Society', status: 'verified', detail: 'Found in NGO Darpan registry' },
            { id: 2, type: 'payment', label: 'random@ybl', status: 'flagged', detail: 'Personal account mismatch' },
            { id: 3, type: 'source', label: 'Claim Analysis', status: 'unverifiable', detail: 'No verifiable claims found' },
          ],
          edges: [
            { source: 0, target: 1, label: 'Claims to represent', status: 'verified' },
            { source: 0, target: 2, label: 'Collects donations via', status: 'flagged' },
            { source: 1, target: 2, label: 'Org ↔ Payment MISMATCH', status: 'flagged' },
            { source: 0, target: 3, label: 'Claims', status: 'unverifiable' },
          ],
        },
        extracted_entities: {
          ORG: ['Red Cross Society'],
          LOC: ['Kerala'],
          PAYMENT_ID: ['random@ybl'],
          DOMAIN: [],
          CLAIM: [],
        },
      });
    }
    setLoading(false);
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
            <TrustScore score={report.final_score} summary={report.summary} />

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
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 mt-16 py-6 text-center text-xs text-slate-400">
        ReliefShield · Omni_DisasterMgmt_18 · Team sleep_deprived
      </footer>
    </div>
  );
}

export default App;
