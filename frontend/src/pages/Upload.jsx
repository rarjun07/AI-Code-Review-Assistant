import { useState } from 'react'
import api from '../services/api'

function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [report, setReport] = useState(null)
  const [analysisTime, setAnalysisTime] = useState('')

  const handleUpload = async () => {
    setMessage('')
    setError('')
    setReport(null)
    setAnalysisTime('')

    if (!file) {
      setError('Please select a Python file first.')
      return
    }

    const token = localStorage.getItem('token')

    if (!token) {
      setError('Please login first before uploading code.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/upload/code', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      })

      setMessage(
        `File uploaded and analyzed successfully: ${response.data.filename}`
      )
      setReport(response.data.pylint_report)
      setAnalysisTime(new Date().toLocaleString())
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'File upload failed.')
    }
  }

  const issues = report?.issues || []

  const errors = issues.filter(
    (issue) => issue.type === 'error'
  ).length

  const warnings = issues.filter(
    (issue) => issue.type === 'warning'
  ).length

  const conventions = issues.filter(
    (issue) => issue.type === 'convention'
  ).length

  const getReportStatus = () => {
    if (errors === 0 && issues.length <= 2) {
      return {
        label: 'Excellent',
        className: 'status-good',
      }
    }

    if (errors <= 2) {
      return {
        label: 'Needs Improvement',
        className: 'status-warning',
      }
    }

    return {
      label: 'Poor Quality',
      className: 'status-danger',
    }
  }

  const getIssueClass = (type) => {
    if (type === 'error') return 'issue-error'
    if (type === 'warning') return 'issue-warning'
    if (type === 'convention') return 'issue-convention'

    return 'issue-default'
  }

  const handleReset = () => {
    setReport(null)
    setMessage('')
    setError('')
    setFile(null)
    setAnalysisTime('')
  }

  const reportStatus = getReportStatus()

  return (
    <section className="upload-page">
      <div className="upload-container">
        <h1>Upload Python Code</h1>

        <p>
          Upload your Python (.py) files and receive code quality
          analysis using Pylint.
        </p>

        <div className="file-box">
          <h2>📂 Select Python File</h2>
          <p>Only .py files are allowed for now.</p>

          <input
            type="file"
            accept=".py"
            onChange={(event) => setFile(event.target.files[0])}
          />
        </div>

        {file && (
          <p>
            <strong>Selected:</strong> {file.name}
          </p>
        )}

        {message && (
          <p className="success-message">{message}</p>
        )}

        {error && (
          <p className="error-message">{error}</p>
        )}

        <button onClick={handleUpload}>
          Upload & Analyze
        </button>

        <div className="info-card">
          <h3>About This Analysis</h3>

          <p>
            Pylint checks Python code for coding standards,
            possible errors, naming conventions, import problems,
            and general code quality.
          </p>
        </div>

        {report && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>📊 Pylint Code Quality Report</h2>

                <p>
                  Static code analysis result for the uploaded
                  Python file.
                </p>

                <p>
                  <strong>File:</strong>{' '}
                  {message.replace(
                    'File uploaded and analyzed successfully: ',
                    ''
                  )}
                </p>

                <p>
                  <strong>Analysis Time:</strong>{' '}
                  {analysisTime}
                </p>
              </div>

              <span
                className={`report-status ${reportStatus.className}`}
              >
                {reportStatus.label}
              </span>
            </div>

            <div className="report-stats">
              <div className="score-card">
                <h3>⭐ Score</h3>
                <p>{report.score || 'N/A'}/10</p>
              </div>

              <div className="total-card">
                <h3>📊 Total Issues</h3>
                <p>{issues.length}</p>
              </div>

              <div className="error-card">
                <h3>🔴 Errors</h3>
                <p>{errors}</p>
              </div>

              <div className="warning-card">
                <h3>🟡 Warnings</h3>
                <p>{warnings}</p>
              </div>

              <div className="convention-card">
                <h3>🟣 Conventions</h3>
                <p>{conventions}</p>
              </div>
            </div>

            <h3>Issues Found</h3>

            {issues.length === 0 ? (
              <p>No issues found. Great job!</p>
            ) : (
              <div className="issue-list">
                {issues.map((issue, index) => (
                  <div
                    className={`issue-card ${getIssueClass(
                      issue.type
                    )}`}
                    key={`${issue['message-id']}-${issue.line}-${index}`}
                  >
                    <strong>
                      {issue.type.toUpperCase()}
                    </strong>

                    <p>{issue.message}</p>

                    <div className="issue-meta">
                      <span>Line: {issue.line}</span>
                      <span>Rule: {issue.symbol}</span>
                      <span>
                        ID: {issue['message-id']}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <button
              className="secondary-btn analyze-again-btn"
              onClick={handleReset}
            >
              Analyze Another File
            </button>
          </div>
        )}
      </div>
    </section>
  )
}

export default Upload