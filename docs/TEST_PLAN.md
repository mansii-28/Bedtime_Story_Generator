# Test Plan

## Verification Strategy

### 1. Automated Unit Tests
Located in `backend/tests/`.
- `test_validators.py`: Verifies word-count logic, genre drift detection, and missing character warnings.
- `test_api_health.py`: Verifies basic FastAPI connectivity.

### 2. Manual Verification
- **Functional**: Run `python3 -m app.main` to verify the CLI still works perfectly after the refactor.
- **End-to-End**: Start the FastAPI server and use the React frontend to generate a story.
- **Safety**: Submit a request with "Iron Man" to verify character rewrite logic (Original -> Replacement mapping).
- **Genre Drift**: Submit a "sci-fi" request and verify that "magic" or "dragon" keywords are either avoided or flagged for revision.

### 3. Load & Rate Limiting
- Use `curl` to rapidly hit the `/api/generate-story` endpoint and verify that a `429 Too Many Requests` is returned after 10 requests within a minute.

## Running Tests
```bash
pytest backend/tests
```
