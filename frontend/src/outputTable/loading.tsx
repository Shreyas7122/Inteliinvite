const Loading = () => {
    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
            <div className="spinner" style={{ width: '40px', height: '40px', borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--accent)' }}></div>
        </div>
    )
}

export default Loading;