import { useRef, useState } from 'react'

const ACCEPTED = '.csv,.xlsx,.xls'

export default function DropZone({ label, onFileSelect }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onFileSelect(file)
  }

  function handleChange(e) {
    const file = e.target.files[0]
    if (file) onFileSelect(file)
    e.target.value = ''
  }

  return (
    <div
      className={`dropzone${dragging ? ' dropzone--active' : ''}`}
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      <span className="dropzone__icon">📂</span>
      <p className="dropzone__label">{label}</p>
      <p className="dropzone__hint">Drag & drop or click to browse (.csv, .xlsx)</p>
    </div>
  )
}
