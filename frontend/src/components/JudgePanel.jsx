export default function JudgePanel({ judgeVerdicts }) {
  if (!judgeVerdicts || judgeVerdicts.length === 0) return null;

  // Show the latest verdict
  const latestVerdict = judgeVerdicts[judgeVerdicts.length - 1];
  const { overall_pass, verdict, reasoning_summary, scores, must_fix, should_fix } = latestVerdict;

  return (
    <div className="card">
      <h3 className="card-title">⚖️ Judge's Verdict</h3>
      
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div><strong>Overall:</strong> <span style={{ color: overall_pass ? 'var(--success-color)' : 'var(--error-color)' }}>{overall_pass ? 'Pass' : 'Fail'}</span></div>
        <div><strong>Verdict:</strong> <span style={{ textTransform: 'capitalize' }}>{verdict.replace(/_/g, ' ')}</span></div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <strong>Reasoning:</strong>
        <p style={{ marginTop: '0.25rem', color: 'var(--text-secondary)' }}>{reasoning_summary}</p>
      </div>

      {scores && (
        <div style={{ marginBottom: '1.5rem' }}>
          <strong>Dimension Scores (1-5):</strong>
          <div className="scores-grid">
            {Object.entries(scores).map(([key, value]) => (
              <div key={key} className="score-item">
                <span>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="score-value">{value}/5</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {must_fix && must_fix.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <strong style={{ color: 'var(--error-color)' }}>Must Fix:</strong>
          <ul className="styled-list error mt-1">
            {must_fix.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}

      {should_fix && should_fix.length > 0 && (
        <div>
          <strong style={{ color: 'var(--warning-color)' }}>Should Fix (Optional):</strong>
          <ul className="styled-list warning mt-1">
            {should_fix.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
