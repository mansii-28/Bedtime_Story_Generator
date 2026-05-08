export default function AuditTrail({ auditTrail }) {
  if (!auditTrail || auditTrail.length === 0) return null;

  return (
    <div className="card">
      <h3 className="card-title">📜 Audit Trail</h3>
      
      <div className="timeline mt-2">
        {auditTrail.map((event, idx) => (
          <div key={idx} className={`timeline-item ${event.status}`}>
            <div className="timeline-header">
              <span className="timeline-step">{event.step.replace(/_/g, ' ').toUpperCase()}</span>
              <span className={`timeline-badge ${event.status}`}>{event.status}</span>
              {event.word_count && (
                <span className="timeline-badge info" style={{ marginLeft: 'auto' }}>
                  {event.word_count} words
                </span>
              )}
            </div>
            
            <div className="timeline-content">
              <div className="timeline-data">
                <span className="timeline-label">Input:</span>
                <span>{event.input_summary}</span>
                
                <span className="timeline-label">Output:</span>
                <span>{event.output_summary}</span>
                
                {event.route_selected && (
                  <>
                    <span className="timeline-label">Route:</span>
                    <span style={{ textTransform: 'capitalize', color: 'var(--accent-color)' }}>{event.route_selected}</span>
                  </>
                )}
                
                {event.reason_for_route && (
                  <>
                    <span className="timeline-label">Reason:</span>
                    <span>{event.reason_for_route}</span>
                  </>
                )}
                
                <span className="timeline-label">Action:</span>
                <span style={{ fontStyle: 'italic' }}>{event.action.replace(/_/g, ' ')}</span>
              </div>
              
              {event.issues && event.issues.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <strong style={{ display: 'block', marginBottom: '0.25rem', color: event.status === 'fail' ? 'var(--error-color)' : 'var(--warning-color)' }}>
                    Issues Noted:
                  </strong>
                  <ul className={`styled-list ${event.status === 'fail' ? 'error' : 'warning'}`}>
                    {event.issues.map((iss, i) => <li key={i}>{iss}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
