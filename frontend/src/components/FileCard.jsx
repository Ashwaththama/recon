export default function FileCard({ file, onRemove }) {
  if (!file) return null

  const size = file.size < 1024 * 1024
    ? `${(file.size / 1024).toFixed(1)} KB`
    : `${(file.size / (1024 * 1024)).toFixed(2)} MB`

  return (
    <div className="file-card">
      <span className="file-card__icon">📄</span>
      <span className="file-card__name">{file.name}</span>
      <span className="file-card__size">({size})</span>
      <button className="file-card__remove" onClick={onRemove} title="Remove file">✕</button>
    </div>
  )
}
