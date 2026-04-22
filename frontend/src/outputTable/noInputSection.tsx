
const NoInputSection = () => {
    return (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '4rem' }}>
            <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</p>
            <p>Waiting for your input.</p>
            <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>Click "Generate Matches" to run semantic search and predictive scoring.</p>
        </div>
    )
}

export default NoInputSection;