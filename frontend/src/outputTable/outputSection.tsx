import Card from './card';
import NoInputSection from './noInputSection';
import Loading from './loading';
import FeedbackForm from './feedbackForm';
import type { Candidate } from '../types';

interface OutputSectionProps {
    hasResults: boolean;
    isProcessing: boolean;
    totalMatched: number;
    candidates: Candidate[];
    showFeedbackForm: boolean;
    feedbackInput: string;
    setShowFeedbackForm: (showFeedbackForm: boolean) => void;
    setFeedbackInput: (text: string) => void;
    handleApplyFeedback: () => void;
}

const OutputSection = ({
    hasResults,
    isProcessing,
    totalMatched,
    candidates,
    showFeedbackForm,
    feedbackInput,
    setShowFeedbackForm,
    setFeedbackInput,
    handleApplyFeedback
}: OutputSectionProps) => {
    return (
        <section className="panel right-panel">
            <h2 className="section-title">
                <span>3. Retrieval & Ranking</span>
            </h2>
            {!hasResults && !isProcessing && (
                <NoInputSection />
            )}

            {isProcessing && (
                <Loading />
            )}

            {hasResults && (
                <>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                        Found <strong style={{ color: 'var(--text-main)' }}>{totalMatched} candidates</strong> matching constraints. Showing top '{candidates.length}' recommendations using ML prediction score.
                    </p>

                    <div className="candidate-grid">
                        {candidates.map((candidate, i) => (
                            <Card candidate={candidate} index={i} key={candidate.id} />
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
                        <FeedbackForm feedbackInput={feedbackInput} setFeedbackInput={setFeedbackInput} handleApplyFeedback={handleApplyFeedback} setShowFeedbackForm={setShowFeedbackForm} />
                    )}
                </>
            )}
        </section>
    )
}

export default OutputSection;