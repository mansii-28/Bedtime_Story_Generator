import { useState } from 'react';

export default function StoryForm({ onSubmit, isLoading, isKidsMode = false, labels = {}, placeholders = {} }) {
  const [formData, setFormData] = useState({
    genre: '',
    characters: '',
    setting: '',
    theme: '',
    tone: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.genre.trim().length >= 2) {
      onSubmit(formData);
    }
  };

  const defaultLabels = {
    genre: "Genre",
    characters: "Characters (optional)",
    setting: "Setting (optional)",
    theme: "Theme or Moral (optional)",
    tone: "Tone (optional)"
  };

  const defaultPlaceholders = {
    genre: "fantasy, adventure, animal tale, sci-fi",
    characters: "a brave rabbit, Superman, a tiny wizard",
    setting: "moon village, enchanted forest, underwater city",
    theme: "kindness, sharing, courage, never give up",
    tone: "calm and magical, whimsical, cozy, adventurous"
  };

  const l = { ...defaultLabels, ...labels };
  const p = { ...defaultPlaceholders, ...placeholders };

  return (
    <div className={isKidsMode ? "kids-card" : "card"}>
      <h2 className="card-title">{isKidsMode ? "✨ Tell us about your story" : "✨ Customize Your Story"}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="genre">
            {l.genre} {!isKidsMode && <span className="required">*</span>}
          </label>
          <input
            type="text"
            id="genre"
            name="genre"
            value={formData.genre}
            onChange={handleChange}
            placeholder={p.genre}
            required
            minLength={2}
            disabled={isLoading}
            className={isKidsMode ? "kids-input" : ""}
          />
        </div>

        <div className="form-group">
          <label htmlFor="characters">{l.characters}</label>
          <input
            type="text"
            id="characters"
            name="characters"
            value={formData.characters}
            onChange={handleChange}
            placeholder={p.characters}
            disabled={isLoading}
            className={isKidsMode ? "kids-input" : ""}
          />
        </div>

        <div className="form-group">
          <label htmlFor="setting">{l.setting}</label>
          <input
            type="text"
            id="setting"
            name="setting"
            value={formData.setting}
            onChange={handleChange}
            placeholder={p.setting}
            disabled={isLoading}
            className={isKidsMode ? "kids-input" : ""}
          />
        </div>

        <div className="form-group">
          <label htmlFor="theme">{l.theme}</label>
          <input
            type="text"
            id="theme"
            name="theme"
            value={formData.theme}
            onChange={handleChange}
            placeholder={p.theme}
            disabled={isLoading}
            className={isKidsMode ? "kids-input" : ""}
          />
        </div>

        <div className="form-group">
          <label htmlFor="tone">{l.tone}</label>
          <input
            type="text"
            id="tone"
            name="tone"
            value={formData.tone}
            onChange={handleChange}
            placeholder={p.tone}
            disabled={isLoading}
            className={isKidsMode ? "kids-input" : ""}
          />
        </div>

        <button 
          type="submit" 
          className={isKidsMode ? "btn-kids-primary mt-2" : "btn-primary mt-2"}
          disabled={isLoading || formData.genre.trim().length < 2}
        >
          {isLoading ? (isKidsMode ? 'Sprinkling stardust...' : 'Generating...') : (isKidsMode ? 'Create My Story' : 'Generate Story')}
        </button>
      </form>
    </div>
  );
}
