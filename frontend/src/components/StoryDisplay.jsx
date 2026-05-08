import StatusBadge from './StatusBadge';

export default function StoryDisplay({ session }) {
  if (!session) return null;

  const { status, final_story, original_story, session_id } = session;
  const isApproved = status === 'approved';

  return (
    <div className="card">
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <span>📖 The Story</span>
        <StatusBadge status={status} />
      </div>
      
      {!isApproved && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(244, 67, 54, 0.1)', borderLeft: '4px solid #f44336', borderRadius: '4px' }}>
          <strong>Note:</strong> This is the best available draft, but it was not approved by the Judge/Validators.
        </div>
      )}

      <div className="story-text">
        {final_story}
      </div>

      <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--card-border)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        <p>Session ID: {session_id}</p>
      </div>
    </div>
  );
}
