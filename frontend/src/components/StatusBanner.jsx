export default function StatusBanner({ status, errorMsg }) {
  if (status === 'idle') return null

  if (status === 'loading') {
    return (
      <div className="banner banner--loading">
        <span className="spinner" /> Processing files, please wait...
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="banner banner--success">
        Reconciliation complete. Download your report below.
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="banner banner--error">
        Error: {errorMsg}
      </div>
    )
  }

  return null
}
