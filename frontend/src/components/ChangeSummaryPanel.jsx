export default function ChangeSummaryPanel({ changeSummaries, status }) {
  if (!changeSummaries || changeSummaries.length === 0) {
    if (status === 'approved') {
      return (
        <div className="card" style={{ background: 'rgba(76, 175, 80, 0.05)', borderLeft: '4px solid var(--success-color)' }}>
          <h3 style={{ color: 'var(--success-color)', margin: '0 0 0.5rem 0' }}>✨ No revision needed</h3>
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>The first draft passed validation and judge review.</p>
        </div>
      );
    }
    return null;
  }

  return (
    <div className="card">
      <h3 className="card-title">🔄 Revision Summaries</h3>
      {changeSummaries.map((cs, idx) => (
        <div key={idx} style={{ marginBottom: idx < changeSummaries.length - 1 ? '2rem' : 0, paddingBottom: idx < changeSummaries.length - 1 ? '1.5rem' : 0, borderBottom: idx < changeSummaries.length - 1 ? '1px solid var(--card-border)' : 'none' }}>
          <h4 style={{ marginBottom: '1rem', color: 'var(--accent-color)' }}>Revision {idx + 1}</h4>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem', marginBottom: '1rem' }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Route:</strong>
            <span style={{ textTransform: 'capitalize' }}>{cs.route_selected}</span>
            
            <strong style={{ color: 'var(--text-secondary)' }}>Reason:</strong>
            <span>{cs.reason_for_route}</span>
            
            <strong style={{ color: 'var(--text-secondary)' }}>Word Count:</strong>
            <span>{cs.old_word_count} → {cs.new_word_count} words</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <strong>Issues Fixed:</strong>
              {cs.issues_fixed && cs.issues_fixed.length > 0 ? (
                <ul className="styled-list success mt-1">
                  {cs.issues_fixed.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>None</p>
              )}
            </div>
            
            <div>
              <strong>Issues Remaining:</strong>
              {cs.issues_remaining && cs.issues_remaining.length > 0 ? (
                <ul className="styled-list warning mt-1">
                  {cs.issues_remaining.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>None</p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
