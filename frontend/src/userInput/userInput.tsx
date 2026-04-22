interface UserInputProps {
    handleProcess: () => void;
    isProcessing: boolean;
    hasResults: boolean;
    frontendConstraints: any;
    appliedConstraints: string[];
    inputText: string;
    setInputText: (text: string) => void;
}

function UserInput({
    handleProcess,
    isProcessing,
    hasResults,
    frontendConstraints,
    appliedConstraints,
    inputText,
    setInputText
}: UserInputProps) {
    return (
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
    )
}

export default UserInput;