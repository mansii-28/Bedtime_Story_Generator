export default function GoodNightMessage() {
  return (
    <div className="card text-center" style={{ padding: '3rem 2rem', marginTop: '2rem', animation: 'pulse 3s infinite ease-in-out' }}>
      <h2 style={{ color: 'var(--accent-color)', fontSize: '2rem', marginBottom: '1rem' }}>🌙 Good Night</h2>
      <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>
        I hope your dreams are gentle, bright, and full of little adventures.
      </p>
    </div>
  );
}
