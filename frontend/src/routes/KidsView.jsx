import { useState } from 'react';
import StoryForm from '../components/StoryForm';
import KidsStoryCard from '../components/KidsStoryCard';
import GoodNightMessage from '../components/GoodNightMessage';
import { generateStory } from '../api/storyApi';

export default function KidsView() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [session, setSession] = useState(null);
  const [isDone, setIsDone] = useState(false);

  const handleGenerateStory = async (formData) => {
    setIsLoading(true);
    setError(null);
    setSession(null);
    
    const payload = { genre: formData.genre };
    ['characters', 'setting', 'theme', 'tone'].forEach(field => {
      if (formData[field].trim()) {
        payload[field] = formData[field].trim();
      }
    });

    try {
      const data = await generateStory(payload);
      setSession(data);
    } catch (err) {
      setError(err.message || 'Story generation failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSession(null);
    setError(null);
    setIsDone(false);
  };

  const handleDone = () => {
    setIsDone(true);
  };

  if (isDone) {
    return (
      <div className="kids-view-container">
        <div className="kids-goodnight-wrapper">
          <GoodNightMessage />
          <div className="mt-4 text-center">
            <button className="btn-kids-secondary" onClick={handleReset}>Start over</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="kids-view-container">
      <header className="kids-header">
        <h1>Tonight’s Bedtime Story</h1>
        <div className="kids-stars">✨ ✨ ✨</div>
      </header>

      <main className="kids-main">
        {!session && !isLoading && (
          <div className="kids-form-wrapper">
            <StoryForm 
              onSubmit={handleGenerateStory} 
              isLoading={isLoading}
              isKidsMode={true}
              labels={{
                genre: "What kind of story would you like?",
                characters: "Any favorite character?",
                setting: "Where should the story happen?",
                theme: "What should the story teach?",
                tone: "How should the story feel?"
              }}
              placeholders={{
                genre: "e.g. funny animals, space adventure",
                characters: "e.g. a brave robot, a tiny fairy",
                setting: "e.g. the moon, a magical forest",
                theme: "e.g. kindness, being brave",
                tone: "e.g. calm, happy, silly"
              }}
            />
          </div>
        )}

        {isLoading && (
          <div className="kids-loading-card">
            <div className="stardust-loader">✨</div>
            <div className="loading-text">Sprinkling stardust on your story...</div>
          </div>
        )}

        {error && (
          <div className="kids-error-card">
            <p>Oops! {error}</p>
            <button className="btn-kids-primary" onClick={handleReset}>Try Again</button>
          </div>
        )}

        {session && !isLoading && (
          <div className="kids-story-wrapper">
            {session.status === 'approved' ? (
              <>
                <KidsStoryCard session={session} />
                <div className="kids-action-group">
                  <button className="btn-kids-primary" onClick={handleReset}>
                    Generate another story
                  </button>
                  <button className="btn-kids-secondary" onClick={handleDone}>
                    Good night
                  </button>
                </div>
              </>
            ) : (
              <div className="kids-error-card">
                <p>We couldn’t make the story just right. Please try again.</p>
                <button className="btn-kids-primary" onClick={handleReset}>Try Again</button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
