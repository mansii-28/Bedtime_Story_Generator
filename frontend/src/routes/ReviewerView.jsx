import { useState } from 'react';
import StoryForm from '../components/StoryForm';
import RequestSummary from '../components/RequestSummary';
import StoryDisplay from '../components/StoryDisplay';
import JudgePanel from '../components/JudgePanel';
import ValidatorPanel from '../components/ValidatorPanel';
import ChangeSummaryPanel from '../components/ChangeSummaryPanel';
import TechnicalDetails from '../components/TechnicalDetails';
import GoodNightMessage from '../components/GoodNightMessage';
import { generateStory } from '../api/storyApi';

export default function ReviewerView() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [session, setSession] = useState(null);
  const [isDone, setIsDone] = useState(false);

  const handleGenerateStory = async (formData) => {
    setIsLoading(true);
    setError(null);
    setSession(null);
    
    // Remove empty optional fields
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
      setError(err.message || 'Story generation failed. Please make sure the backend is running and try again.');
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
      <div className="view-container">
        <GoodNightMessage />
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button className="btn-secondary" onClick={handleReset}>Start over</button>
        </div>
      </div>
    );
  }

  return (
    <div className="view-container">
      <header className="reviewer-header">
        <h1>🌙 Bedtime Story Reviewer</h1>
        <p className="subtitle">Technical pipeline evaluation</p>
      </header>

      <main>
        {!session && !isLoading && (
          <StoryForm onSubmit={handleGenerateStory} isLoading={isLoading} />
        )}

        {isLoading && (
          <div className="card text-center" style={{ padding: '3rem 1rem' }}>
            <div className="loading-text mb-2">✨ Creating a calm bedtime story...</div>
            <div style={{ color: 'var(--text-secondary)' }}>
              Checking safety, length, and bedtime suitability...
            </div>
          </div>
        )}

        {error && (
          <div className="card" style={{ borderLeft: '4px solid var(--error-color)' }}>
            <h3 style={{ color: 'var(--error-color)', margin: '0 0 0.5rem 0' }}>⚠️ Generation Failed</h3>
            <p>{error}</p>
            <button className="btn-secondary mt-2" onClick={handleReset}>Try Again</button>
          </div>
        )}

        {session && !isLoading && (
          <div className="results-container">
            <RequestSummary 
              preferences={session.user_preferences} 
              characterRewrites={session.character_rewrites} 
            />
            <StoryDisplay session={session} />
            <ChangeSummaryPanel changeSummaries={session.change_summaries} status={session.status} />
            <JudgePanel judgeVerdicts={session.judge_verdicts} />
            <ValidatorPanel validatorResults={session.validator_results} />
            <TechnicalDetails session={session} />

            <div className="card button-group">
              <button className="btn-primary" style={{ flex: 1 }} onClick={handleReset}>
                Generate another story
              </button>
              <button className="btn-secondary" style={{ flex: 1 }} onClick={handleDone}>
                Done for the day
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
