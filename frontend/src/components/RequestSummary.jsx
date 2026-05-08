export default function UserRequestSummary({ preferences, characterRewrites }) {
  if (!preferences) return null;

  const { genre, characters, setting, theme, tone } = preferences;

  const renderField = (label, value) => (
    <div style={{ marginBottom: '0.5rem' }}>
      <strong>{label}:</strong> <span style={{ color: value ? 'inherit' : 'var(--text-secondary)' }}>{value || 'Not specified'}</span>
    </div>
  );

  return (
    <div className="card">
      <h3 className="card-title">📝 Your Request</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div>
          {renderField('Genre', genre)}
          {renderField('Characters', characters)}
          {renderField('Setting', setting)}
        </div>
        <div>
          {renderField('Theme', theme)}
          {renderField('Tone', tone)}
        </div>
      </div>

      {characterRewrites && Object.keys(characterRewrites).length > 0 && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--card-border)' }}>
          <strong style={{ color: 'var(--accent-color)' }}>Safety Adjustments:</strong>
          <ul className="styled-list info mt-1">
            {Object.entries(characterRewrites).map(([oldChar, newChar]) => (
              <li key={oldChar}>
                Character rewrite: {oldChar} → <strong style={{ color: 'var(--text-primary)' }}>{newChar.charAt(0).toUpperCase() + newChar.slice(1)}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
