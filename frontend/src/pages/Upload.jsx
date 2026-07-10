import { useState } from 'react'
import api from '../services/api'

function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [pylintReport, setPylintReport] = useState(null)
  const [banditReport, setBanditReport] = useState(null)
  const [radonReport, setRadonReport] = useState(null)
  const [aiReview, setAiReview] = useState(null)

  const [analysisTime, setAnalysisTime] = useState('')

  const handleUpload = async () => {
    setMessage('')
    setError('')

    setPylintReport(null)
    setBanditReport(null)
    setRadonReport(null)
    setAiReview(null)

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

      setPylintReport(response.data.pylint_report)
      setBanditReport(response.data.bandit_report)
      setRadonReport(response.data.radon_report)
      setAiReview(response.data.ai_review)

      setAnalysisTime(new Date().toLocaleString())
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'File upload failed.')
    }
  }

  const pylintIssues = pylintReport?.issues || []

  const pylintErrors = pylintIssues.filter(
    (issue) => issue.type === 'error'
  ).length

  const pylintWarnings = pylintIssues.filter(
    (issue) => issue.type === 'warning'
  ).length

  const pylintConventions = pylintIssues.filter(
    (issue) => issue.type === 'convention'
  ).length

  const getPylintStatus = () => {
    if (pylintErrors === 0 && pylintIssues.length <= 2) {
      return {
        label: 'Excellent',
        className: 'status-good',
      }
    }

    if (pylintErrors <= 2) {
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

  const getBanditIssueClass = (severity) => {
    if (severity === 'HIGH') return 'issue-error'
    if (severity === 'MEDIUM') return 'issue-warning'
    if (severity === 'LOW') return 'issue-convention'

    return 'issue-default'
  }

  const handleReset = () => {
    setFile(null)
    setMessage('')
    setError('')

    setPylintReport(null)
    setBanditReport(null)
    setRadonReport(null)
    setAiReview(null)

    setAnalysisTime('')
  }

  const pylintStatus = getPylintStatus()

  const analyzedFileName = message.replace(
    'File uploaded and analyzed successfully: ',
    ''
  )

  const maintainabilityGrade =
    radonReport?.maintainability
      ?.trim()
      .split(' - ')
      .pop() || 'N/A'

  return (
    <section className="upload-page">
      <div className="upload-container">
        <h1>Upload Python Code</h1>

        <p>
          Upload a Python (.py) file to analyze code quality,
          security vulnerabilities, complexity, and maintainability.
        </p>

        <div className="file-box">
          <h2>📂 Select Python File</h2>
          <p>Only .py files are allowed for now.</p>

          <input
            type="file"
            accept=".py"
            onChange={(event) => {
              const selectedFile = event.target.files?.[0] || null
              setFile(selectedFile)
            }}
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
            Pylint checks code quality, Bandit detects security
            vulnerabilities, and Radon measures complexity and
            maintainability.
          </p>
        </div>

        {pylintReport && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>📊 Pylint Code Quality Report</h2>

                <p>
                  Static code-quality analysis for the uploaded
                  Python file.
                </p>

                <p>
                  <strong>File:</strong> {analyzedFileName}
                </p>

                <p>
                  <strong>Analysis Time:</strong> {analysisTime}
                </p>
              </div>

              <span
                className={`report-status ${pylintStatus.className}`}
              >
                {pylintStatus.label}
              </span>
            </div>

            <div className="report-stats">
              <div className="score-card">
                <h3>⭐ Score</h3>
                <p>{pylintReport.score || 'N/A'}/10</p>
              </div>

              <div className="total-card">
                <h3>📊 Total Issues</h3>
                <p>{pylintIssues.length}</p>
              </div>

              <div className="error-card">
                <h3>🔴 Errors</h3>
                <p>{pylintErrors}</p>
              </div>

              <div className="warning-card">
                <h3>🟡 Warnings</h3>
                <p>{pylintWarnings}</p>
              </div>

              <div className="convention-card">
                <h3>🟣 Conventions</h3>
                <p>{pylintConventions}</p>
              </div>
            </div>

            <h3>Issues Found</h3>

            {pylintIssues.length === 0 ? (
              <p>No Pylint issues found. Great job!</p>
            ) : (
              <div className="issue-list">
                {pylintIssues.map((issue, index) => (
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
          </div>
        )}

        {banditReport && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>🛡 Bandit Security Report</h2>

                <p>
                  Security vulnerability analysis for the uploaded
                  Python file.
                </p>
              </div>

              <span
                className={`report-status ${
                  banditReport.total_issues === 0
                    ? 'status-good'
                    : 'status-danger'
                }`}
              >
                {banditReport.total_issues === 0
                  ? 'No Security Issues'
                  : 'Security Issues Found'}
              </span>
            </div>

            <div className="report-stats bandit-stats">
              <div className="total-card">
                <h3>📊 Total Issues</h3>
                <p>{banditReport.total_issues}</p>
              </div>

              <div className="error-card">
                <h3>🔴 High Severity</h3>
                <p>{banditReport.high_severity}</p>
              </div>

              <div className="warning-card">
                <h3>🟡 Medium Severity</h3>
                <p>{banditReport.medium_severity}</p>
              </div>

              <div className="score-card">
                <h3>🟢 Low Severity</h3>
                <p>{banditReport.low_severity}</p>
              </div>
            </div>

            <h3>Security Findings</h3>

            {banditReport.issues.length === 0 ? (
              <p>No security vulnerabilities were detected.</p>
            ) : (
              <div className="issue-list">
                {banditReport.issues.map((issue, index) => (
                  <div
                    className={`issue-card ${getBanditIssueClass(
                      issue.issue_severity
                    )}`}
                    key={`${issue.test_id}-${issue.line_number}-${index}`}
                  >
                    <strong>
                      {issue.issue_severity} SEVERITY
                    </strong>

                    <p>{issue.issue_text}</p>

                    <div className="issue-meta">
                      <span>
                        Line: {issue.line_number}
                      </span>

                      <span>
                        Test: {issue.test_id}
                      </span>

                      <span>
                        Confidence: {issue.issue_confidence}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {radonReport && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>📈 Radon Complexity Report</h2>

                <p>
                  Cyclomatic-complexity and maintainability analysis.
                </p>
              </div>

              <span className="report-status status-good">
                Maintainability {maintainabilityGrade}
              </span>
            </div>

            <div className="report-stats radon-stats">
              <div className="score-card">
                <h3>Maintainability Grade</h3>
                <p>{maintainabilityGrade}</p>
              </div>

              <div className="total-card">
                <h3>Complexity Items</h3>
                <p>{radonReport.grades?.length || 0}</p>
              </div>
            </div>

            <h3>Complexity Details</h3>

            {radonReport.complexity ? (
              <pre className="complexity-output">
                {radonReport.complexity}
              </pre>
            ) : (
              <p>
                No functions or classes were found for cyclomatic
                complexity analysis.
              </p>
            )}
          </div>
        )}

        {aiReview && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>AI Code Review</h2>

                <p>
                  AI-generated review based on the uploaded code
                  and static-analysis results.
                </p>
              </div>

              <span
                className={`report-status ${
                  aiReview.status === 'completed'
                    ? 'status-good'
                    : 'status-warning'
                }`}
              >
                {aiReview.overall_rating || 'Not available'}
              </span>
            </div>

            <p>{aiReview.summary}</p>

            <div className="ai-review-grid">
              <div>
                <h3>Strengths</h3>
                <ul>
                  {(aiReview.strengths || []).map((item, index) => (
                    <li key={`strength-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3>Bugs</h3>
                <ul>
                  {(aiReview.bugs || []).map((item, index) => (
                    <li key={`bug-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3>Security</h3>
                <ul>
                  {(aiReview.security_recommendations || []).map(
                    (item, index) => (
                      <li key={`security-${index}`}>{item}</li>
                    )
                  )}
                </ul>
              </div>

              <div>
                <h3>Refactoring</h3>
                <ul>
                  {(aiReview.refactoring_suggestions || []).map(
                    (item, index) => (
                      <li key={`refactor-${index}`}>{item}</li>
                    )
                  )}
                </ul>
              </div>

              <div>
                <h3>Performance</h3>
                <ul>
                  {(aiReview.performance_recommendations || []).map(
                    (item, index) => (
                      <li key={`performance-${index}`}>{item}</li>
                    )
                  )}
                </ul>
              </div>

              <div>
                <h3>Best Practices</h3>
                <ul>
                  {(aiReview.best_practices || []).map(
                    (item, index) => (
                      <li key={`best-practice-${index}`}>{item}</li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}

        {(pylintReport || banditReport || radonReport || aiReview) && (
          <button
            className="secondary-btn analyze-again-btn"
            onClick={handleReset}
          >
            Analyze Another File
          </button>
        )}
      </div>
    </section>
  )
}

export default Upload
