export default function ReconcileButton({ disabled, onClick, loading }) {
  return (
    <button
      className={`btn btn--primary${disabled ? ' btn--disabled' : ''}`}
      disabled={disabled}
      onClick={onClick}
    >
      {loading ? 'Processing...' : 'Run Reconciliation'}
    </button>
  )
}
