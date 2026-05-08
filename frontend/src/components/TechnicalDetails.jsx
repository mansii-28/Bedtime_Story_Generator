import AuditTrail from './AuditTrail';

export default function TechnicalDetails({ session }) {
  if (!session) return null;

  return (
    <div className="card" style={{ background: 'rgba(0,0,0,0.15)', border: '1px dashed var(--card-border)' }}>
      <h3 className="card-title" style={{ borderBottom: 'none', marginBottom: 0 }}>⚙️ Technical Details</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
        This app uses a bounded LLM agent pipeline: request normalization, planning, story generation, deterministic validation, LLM judging, and controlled revision with a maximum of 2 attempts.
      </p>
      
      <details style={{ marginBottom: '1rem' }}>
        <summary style={{ fontWeight: '600', color: 'var(--text-primary)' }}>View Audit Trail</summary>
        <div style={{ marginTop: '1rem' }}>
          <AuditTrail auditTrail={session.audit_trail} />
        </div>
      </details>

      {session.original_story && session.original_story !== session.final_story && (
        <details style={{ marginBottom: '1rem' }}>
          <summary style={{ fontWeight: '600', color: 'var(--text-primary)' }}>View Original First Draft</summary>
          <div className="story-text" style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '4px', fontSize: '1rem' }}>
            {session.original_story}
          </div>
        </details>
      )}

      <details>
        <summary style={{ fontWeight: '600', color: 'var(--text-primary)' }}>View Raw Session Data</summary>
        <pre style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflowX: 'auto', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          {JSON.stringify({ ...session, original_story: '...', final_story: '...', audit_trail: '[...]' }, null, 2)}
        </pre>
      </details>
    </div>
  );
}
