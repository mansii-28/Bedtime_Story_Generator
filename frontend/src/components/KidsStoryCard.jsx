export default function KidsStoryCard({ session }) {
  if (!session || session.status !== 'approved') return null;

  // Extract title and story body
  const lines = session.final_story.trim().split('\n');
  const title = lines[0];
  const storyBody = lines.slice(1).join('\n');

  return (
    <div className="kids-story-card">
      <div className="decorative-elements">
        <span className="emoji floating">🌙</span>
        <span className="emoji floating delay-1">⭐</span>
        <span className="emoji floating delay-2">☁️</span>
      </div>
      
      <h2 className="kids-story-title">{title}</h2>
      
      <div className="kids-story-text">
        {storyBody.split('\n').map((paragraph, idx) => (
          paragraph.trim() ? <p key={idx}>{paragraph}</p> : <br key={idx} />
        ))}
      </div>

      <div className="kids-story-footer">
        <span className="emoji">🤖</span>
        <span className="emoji">🐶</span>
        <span className="emoji">🐱</span>
      </div>
    </div>
  );
}
