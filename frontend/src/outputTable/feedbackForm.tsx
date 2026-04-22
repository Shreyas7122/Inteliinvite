interface FeedbackFormProps {
    feedbackInput: string;
    setFeedbackInput: (text: string) => void;
    handleApplyFeedback: () => void;
    setShowFeedbackForm: (showFeedbackForm: boolean) => void;
}

const FeedbackForm = ({
    feedbackInput,
    setFeedbackInput,
    handleApplyFeedback,
    setShowFeedbackForm
}: FeedbackFormProps) => {
    return (
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
    )
}

export default FeedbackForm;