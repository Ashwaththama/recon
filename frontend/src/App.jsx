import { useState } from 'react'
import DropZone from './components/DropZone'
import FileCard from './components/FileCard'
import ReconcileButton from './components/ReconcileButton'
import DownloadButton from './components/DownloadButton'
import StatusBanner from './components/StatusBanner'
import { postFiles } from './api/reconcileApi'
import './App.css'

export default function App() {
  const [hrFile, setHrFile] = useState(null)
  const [payrollFile, setPayrollFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const [downloadUrl, setDownloadUrl] = useState(null)

  async function handleReconcile() {
    setStatus('loading')
    setDownloadUrl(null)
    setErrorMsg('')
    try {
      const url = await postFiles(hrFile, payrollFile)
      setDownloadUrl(url)
      setStatus('success')
    } catch (err) {
      setErrorMsg(err.message)
      setStatus('error')
    }
  }

  const canRun = hrFile && payrollFile && status !== 'loading'

  return (
    <div className="app">
      <header className="app__header">
        <h1>HR &amp; Payroll Reconciliation</h1>
        <p>Upload your HR and Payroll data files to generate a reconciliation report.</p>
      </header>

      <main className="app__main">
        <div className="upload-grid">
          <div className="upload-section">
            <h2>HR File</h2>
            <DropZone label="Upload HR Data" onFileSelect={setHrFile} />
            <FileCard file={hrFile} onRemove={() => { setHrFile(null); setStatus('idle') }} />
          </div>

          <div className="upload-section">
            <h2>Payroll File</h2>
            <DropZone label="Upload Payroll Data" onFileSelect={setPayrollFile} />
            <FileCard file={payrollFile} onRemove={() => { setPayrollFile(null); setStatus('idle') }} />
          </div>
        </div>

        <div className="actions">
          <ReconcileButton
            disabled={!canRun}
            loading={status === 'loading'}
            onClick={handleReconcile}
          />
        </div>

        <StatusBanner status={status} errorMsg={errorMsg} />

        {status === 'success' && downloadUrl && (
          <div className="download-section">
            <DownloadButton url={downloadUrl} />
          </div>
        )}
      </main>
    </div>
  )
}
