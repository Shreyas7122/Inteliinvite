import { useState } from 'react';
import './index.css';
import UserInput from './userInput/userInput';
import OutputSection from './outputTable/outputSection';
import type { Candidate } from './types';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [hasResults, setHasResults] = useState(false);
  const [inputText, setInputText] = useState('I want to invite people for a cleanliness drive in Pittsburgh.');

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
        <UserInput inputText={inputText} setInputText={setInputText} handleProcess={handleProcess} isProcessing={isProcessing} hasResults={hasResults} frontendConstraints={frontendConstraints} appliedConstraints={appliedConstraints} />
        <OutputSection candidates={candidates} totalMatched={totalMatched} hasResults={hasResults} isProcessing={isProcessing} showFeedbackForm={showFeedbackForm} feedbackInput={feedbackInput} setShowFeedbackForm={setShowFeedbackForm} setFeedbackInput={setFeedbackInput} handleApplyFeedback={handleApplyFeedback} />
      </main>
    </div>
  );
}

export default App;
