interface CardProps {
    candidate: {
        id: string;
        age: number;
        distance: string;
        interests: string[];
        score: number;
    };
    index: number;
}

const Card = ({ candidate, index }: CardProps) => {
    return (
        <div className="candidate-card" key={candidate.id} style={{ animationDelay: `${index * 0.1}s` }}>
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
    )
}

export default Card;