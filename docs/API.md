# API Reference

## Endpoints

### `GET /health`
Returns the status of the service and the configured LLM model.

**Response:**
```json
{
  "status": "ok",
  "service": "bedtime-story-generator",
  "model": "gpt-3.5-turbo"
}
```

### `POST /api/generate-story`
Generates a bedtime story based on user preferences.

**Rate Limit**: 10 requests per minute per IP.

**Request Body:**
```json
{
  "genre": "sci-fi",
  "characters": "a small robot",
  "setting": "a moon colony",
  "theme": "courage",
  "tone": "calm and magical"
}
```

**Response (`StorySession`):**
A comprehensive flat JSON object representing the entire pipeline lifecycle.

| Field | Type | Description |
|---|---|---|
| `session_id` | `string` | Unique ID for tracking. |
| `status` | `string` | `approved` or `failed_validation`. |
| `final_story` | `string` | The final prose (or best draft if failed). |
| `original_story` | `string` | The first unrevised draft. |
| `character_rewrites` | `object` | Mapping of User Input -> Safe Replacement. |
| `audit_trail` | `array` | Every agent thought and decision step. |
| `validator_results`| `array` | Metrics and warnings from deterministic checks. |
| `judge_verdicts` | `array` | Scoring (1-5) and feedback from the Judge. |
| `change_summaries` | `array` | Summaries of what changed during revisions. |

## Example Usage

```bash
curl -X POST http://localhost:8000/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{"genre": "sci-fi", "characters": "Iron Man"}'
```

## Error Codes
- **422 Unprocessable Entity**: Invalid input (e.g., genre < 2 chars).
- **429 Too Many Requests**: Rate limit exceeded (10/min).
- **500 Internal Server Error**: Pipeline failure or missing `OPENAI_API_KEY`.
