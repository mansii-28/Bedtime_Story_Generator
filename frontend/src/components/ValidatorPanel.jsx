export default function ValidatorPanel({ validatorResults }) {
  if (!validatorResults || validatorResults.length === 0) return null;

  // Show the latest result
  const latestResult = validatorResults[validatorResults.length - 1];
  const { passed, metrics, failures, warnings } = latestResult;

  return (
    <div className="card">
      <h3 className="card-title">🔍 Validator Results</h3>
      
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <div><strong>Status:</strong> <span style={{ color: passed ? 'var(--success-color)' : 'var(--error-color)' }}>{passed ? 'Passed' : 'Failed'}</span></div>
        <div><strong>Word Count:</strong> {metrics?.word_count || 0}</div>
      </div>

      {failures && failures.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <strong style={{ color: 'var(--error-color)' }}>Failures:</strong>
          <ul className="styled-list error mt-1">
            {failures.map((item, i) => <li key={i}>{item}</li>)}
          </ul>
        </div>
      )}

      {warnings && warnings.length > 0 && (
        <div>
          <strong style={{ color: 'var(--warning-color)' }}>Warnings:</strong>
          <ul className="styled-list warning mt-1">
            {warnings.map((item, i) => (
              <li key={i}>{typeof item === 'string' ? item : item.message}</li>
            ))}
          </ul>
        </div>
      )}
      
      {passed && (!warnings || warnings.length === 0) && (
        <div style={{ color: 'var(--success-color)' }}>All validation checks passed perfectly.</div>
      )}
    </div>
  );
}
