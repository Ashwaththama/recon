export default function DownloadButton({ url }) {
  return (
    <a
      className="btn btn--download"
      href={url}
      download="reconciliation_report.xlsx"
    >
      ⬇ Download Reconciliation Report
    </a>
  )
}
