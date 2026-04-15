import { useState } from 'react';
import './index.css';

interface Candidate {
  id: string;
  age: number;
  distance: string;
  interests: string[];
  score: number;
}

function App() {
  const [inputText, setInputText] = useState('I want to invite people for a cleanliness drive in Pittsburgh.');
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasResults, setHasResults] = useState(false);

  // Feedback Layer States
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackInput, setFeedbackInput] = useState('');
  const [appliedConstraints, setAppliedConstraints] = useState<string[]>([]);

  // Real Data states
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [totalMatched, setTotalMatched] = useState(0);
  const [frontendConstraints, setFrontendConstraints] = useState<any>(null);

  const performAIProcess = async (sentencesFeedback: string[]) => {
    setIsProcessing(true);
    setHasResults(false);
    setShowFeedbackForm(false);

    try {
      const response = await fetch('http://localhost:5000/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sentence: inputText,
          feedback: sentencesFeedback
        })
      });
      const data = await response.json();
      setCandidates(data.candidates);
      setTotalMatched(data.total_matched);
      setFrontendConstraints(data.inferred_constraints);
      setHasResults(true);
    } catch (error) {
      console.error("API connection failed:", error);
      alert("Error connecting to the Python Model Backend! Is app.py running?");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleProcess = () => {
    performAIProcess(appliedConstraints);
  };

  const handleApplyFeedback = () => {
    if (!feedbackInput.trim()) return;

    const updatedConstraints = [...appliedConstraints, feedbackInput];
    setAppliedConstraints(updatedConstraints);
    setFeedbackInput('');
    setShowFeedbackForm(false);

    // Re-run processing instantly with the newly applied constraints array
    performAIProcess(updatedConstraints);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">✨ Inteliinvite AI Matcher</h1>
      </header>

      <main className="main-content">
        <aside className="panel left-panel">
          <h2 className="section-title">
            <span>1. User Input</span>
          </h2>

          <div className="input-container">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Describe your volunteer needs in plain English..."
            />
            <button
              className="btn"
              onClick={handleProcess}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="spinner"></div> Processing...
                </>
              ) : 'Generate Matches'}
            </button>
          </div>

          {hasResults && frontendConstraints && (
            <div className="extracted-params">
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-main)' }}>2. AI Reasoning Layer</h3>
              <div className="param-item">
                <span className="param-label">Max Distance</span>
                <span className="param-value">&le; {frontendConstraints.max_distance_km || 50} km</span>
              </div>
              <div className="param-item">
                <span className="param-label">Inferred Interests</span>
                <span className="param-value">
                  {(frontendConstraints.required_interests || []).join(' | ') || 'None'}
                </span>
              </div>

              {frontendConstraints.excluded_interests && frontendConstraints.excluded_interests.length > 0 && (
                <div className="param-item">
                  <span className="param-label">Excluded Interests</span>
                  <span className="param-value" style={{ color: 'var(--danger)' }}>
                    {frontendConstraints.excluded_interests.join(' | ')}
                  </span>
                </div>
              )}

              {/* Display dynamically applied feedback constraints */}
              {appliedConstraints.map((constraint, idx) => (
                <div className="param-item" key={idx}>
                  <span className="param-label">Learned Semantic Rule {idx + 1}</span>
                  <span className="param-value" style={{ color: 'var(--success)' }}>{constraint}</span>
                </div>
              ))}

              <div className="param-item">
                <span className="param-label">Max Age</span>
                <span className="param-value">{frontendConstraints.max_age || 'Any'}</span>
              </div>
              <div className="param-item">
                <span className="param-label">Min Physical Score</span>
                <span className="param-value">{frontendConstraints.min_physical_score || 0} / 10</span>
              </div>
            </div>
          )}
        </aside>

        <section className="panel right-panel">
          <h2 className="section-title">
            <span>3. Retrieval & Ranking</span>
          </h2>

          {!hasResults && !isProcessing && (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '4rem' }}>
              <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</p>
              <p>Waiting for your input.</p>
              <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>Click "Generate Matches" to run semantic search and predictive scoring.</p>
            </div>
          )}

          {isProcessing && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
              <div className="spinner" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent)' }}></div>
            </div>
          )}

          {hasResults && (
            <>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                Found <strong style={{ color: 'var(--text-main)' }}>{totalMatched} candidates</strong> matching constraints. Showing top '{candidates.length}' recommendations using ML prediction score.
              </p>

              <div className="candidate-grid">
                {candidates.map((candidate, i) => (
                  <div className="candidate-card" key={candidate.id} style={{ animationDelay: `${i * 0.1}s` }}>
                    <div className="candidate-header">
                      <div className="candidate-id">{candidate.id}</div>
                      <div className="candidate-score">
                        ★ {(candidate.score * 100).toFixed(0)}% Match
                      </div>
                    </div>

                    <div className="candidate-detail">
                      <span>👤 Age: {candidate.age}</span>
                    </div>
                    <div className="candidate-detail">
                      <span>📍 Dist: {candidate.distance}</span>
                    </div>

                    <div className="candidate-interests">
                      {candidate.interests.map(interest => (
                        <span className="interest-tag" key={interest}>{interest}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {candidates.length === 0 && (
                <div style={{ color: 'var(--text-muted)', textAlign: 'center', margin: '2rem 0' }}>
                  No candidates match the new strict constraints.
                </div>
              )}

              {!showFeedbackForm ? (
                <div className="feedback-actions">
                  <button className="btn btn-secondary" style={{ flex: 1, borderColor: 'var(--success)' }}>
                    ✅ Accept Recommendations
                  </button>
                  <button
                    className="btn btn-secondary"
                    style={{ flex: 1, borderColor: 'var(--danger)' }}
                    onClick={() => setShowFeedbackForm(true)}
                  >
                    ❌ Refine & Retrain
                  </button>
                </div>
              ) : (
                <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '1rem', border: '1px solid var(--danger)' }}>
                  <h4 style={{ color: 'var(--danger)', marginBottom: '1rem' }}>Feedback Loop: Add Constraint</h4>
                  <input
                    type="text"
                    value={feedbackInput}
                    onChange={(e) => setFeedbackInput(e.target.value)}
                    placeholder="E.g., 'Must include Youth interest'"
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: '0.5rem',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      background: 'rgba(0, 0, 0, 0.2)',
                      color: 'white',
                      marginBottom: '1rem'
                    }}
                  />
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="btn" style={{ flex: 1, padding: '0.75rem' }} onClick={handleApplyFeedback}>Apply Rule</button>
                    <button className="btn btn-secondary" style={{ flex: 1, padding: '0.75rem' }} onClick={() => setShowFeedbackForm(false)}>Cancel</button>
                  </div>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
