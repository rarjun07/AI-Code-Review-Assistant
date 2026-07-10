import { useEffect, useState } from 'react'
import api from '../services/api'

function Reports() {
  const [reports, setReports] = useState([])
  const [selectedReport, setSelectedReport] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const token = localStorage.getItem('token')

        if (!token) {
          setError('Please login first to view reports.')
          return
        }

        const response = await api.get('/reports', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setReports(response.data)

        if (response.data.length > 0) {
          setSelectedReport(response.data[0])
        }
      } catch (err) {
        setError(
          err.response?.data?.detail || 'Failed to load reports.'
        )
      }
    }

    fetchReports()
  }, [])

  const openReport = async (reportId) => {
    try {
      setError('')

      const token = localStorage.getItem('token')

      const response = await api.get(`/reports/${reportId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      setSelectedReport(response.data)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to load report.'
      )
    }
  }

  const pylintIssues =
    selectedReport?.pylint_report?.issues || []

  const banditIssues =
    selectedReport?.bandit_report?.issues || []

  const maintainabilityGrade =
    selectedReport?.radon_report?.maintainability
      ?.trim()
      .split(' - ')
      .pop() || 'N/A'

  const getPylintIssueClass = (type) => {
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

  return (
    <section className="reports-page">
      <div className="reports-container">
        <div className="reports-header">
          <h1>Static Analysis Reports</h1>

          <p>
            View previously saved Pylint, Bandit, and Radon
            analysis results.
          </p>
        </div>

        {error && (
          <p className="error-message">{error}</p>
        )}

        <div className="reports-layout">
          <aside className="reports-list">
            <h2>Saved Reports</h2>

            {reports.length === 0 ? (
              <div className="report-list-empty">
                <h3>No reports yet</h3>
                <p>
                  Upload and analyze a Python file to create your
                  first report.
                </p>
              </div>
            ) : (
              reports.map((report) => (
                <button
                  className={`report-list-card ${
                    selectedReport?.id === report.id
                      ? 'report-list-card-active'
                      : ''
                  }`}
                  key={report.id}
                  onClick={() => openReport(report.id)}
                >
                  <h3>📄 {report.filename}</h3>
                  <p>Report ID: {report.id}</p>
                  <p>
                    {new Date(report.created_at).toLocaleString()}
                  </p>
                </button>
              ))
            )}
          </aside>

          <main className="report-details">
            {!selectedReport ? (
              <div className="report-card">
                <h2>Select a report</h2>
                <p>
                  Choose a saved report from the left side to view
                  complete analysis details.
                </p>
              </div>
            ) : (
              <>
                <div className="report-card report-summary-card">
                  <h2>📊 Report Summary</h2>

                  <div className="report-summary-grid">
                    <div>
                      <span>File</span>
                      <strong>{selectedReport.filename}</strong>
                    </div>

                    <div>
                      <span>Report ID</span>
                      <strong>{selectedReport.id}</strong>
                    </div>

                    <div>
                      <span>Created</span>
                      <strong>
                        {new Date(
                          selectedReport.created_at
                        ).toLocaleString()}
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="report-card report-card-pylint">
                  <div className="report-section-header">
                    <div>
                      <h2>📊 Pylint Code Quality</h2>
                      <p>
                        Coding standards, errors, warnings, and
                        conventions.
                      </p>
                    </div>

                    <span className="report-score-badge">
                      {selectedReport.pylint_report?.score || 'N/A'}
                      /10
                    </span>
                  </div>

                  <div className="report-mini-stats">
                    <div>
                      <span>Total Issues</span>
                      <strong>{pylintIssues.length}</strong>
                    </div>

                    <div>
                      <span>Errors</span>
                      <strong>
                        {
                          pylintIssues.filter(
                            (issue) => issue.type === 'error'
                          ).length
                        }
                      </strong>
                    </div>

                    <div>
                      <span>Warnings</span>
                      <strong>
                        {
                          pylintIssues.filter(
                            (issue) => issue.type === 'warning'
                          ).length
                        }
                      </strong>
                    </div>

                    <div>
                      <span>Conventions</span>
                      <strong>
                        {
                          pylintIssues.filter(
                            (issue) =>
                              issue.type === 'convention'
                          ).length
                        }
                      </strong>
                    </div>
                  </div>

                  <h3>Pylint Findings</h3>

                  {pylintIssues.length === 0 ? (
                    <p>No Pylint issues were found.</p>
                  ) : (
                    <div className="issue-list">
                      {pylintIssues.map((issue, index) => (
                        <div
                          className={`issue-card ${getPylintIssueClass(
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

                <div className="report-card report-card-bandit">
                  <div className="report-section-header">
                    <div>
                      <h2>🛡 Bandit Security Analysis</h2>
                      <p>
                        Security vulnerability findings and severity
                        levels.
                      </p>
                    </div>

                    <span
                      className={`report-status ${
                        selectedReport.bandit_report
                          ?.total_issues === 0
                          ? 'status-good'
                          : 'status-danger'
                      }`}
                    >
                      {selectedReport.bandit_report
                        ?.total_issues === 0
                        ? 'No Security Issues'
                        : 'Security Issues Found'}
                    </span>
                  </div>

                  <div className="report-mini-stats">
                    <div>
                      <span>Total Issues</span>
                      <strong>
                        {selectedReport.bandit_report
                          ?.total_issues || 0}
                      </strong>
                    </div>

                    <div>
                      <span>High</span>
                      <strong>
                        {selectedReport.bandit_report
                          ?.high_severity || 0}
                      </strong>
                    </div>

                    <div>
                      <span>Medium</span>
                      <strong>
                        {selectedReport.bandit_report
                          ?.medium_severity || 0}
                      </strong>
                    </div>

                    <div>
                      <span>Low</span>
                      <strong>
                        {selectedReport.bandit_report
                          ?.low_severity || 0}
                      </strong>
                    </div>
                  </div>

                  <h3>Security Findings</h3>

                  {banditIssues.length === 0 ? (
                    <p>
                      No security vulnerabilities were detected.
                    </p>
                  ) : (
                    <div className="issue-list">
                      {banditIssues.map((issue, index) => (
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
                            <span>Test: {issue.test_id}</span>
                            <span>
                              Confidence:{' '}
                              {issue.issue_confidence}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="report-card report-card-radon">
                  <div className="report-section-header">
                    <div>
                      <h2>📈 Radon Complexity Analysis</h2>
                      <p>
                        Maintainability and cyclomatic-complexity
                        results.
                      </p>
                    </div>

                    <span className="report-status status-good">
                      Grade {maintainabilityGrade}
                    </span>
                  </div>

                  <div className="report-mini-stats report-mini-stats-two">
                    <div>
                      <span>Maintainability</span>
                      <strong>{maintainabilityGrade}</strong>
                    </div>

                    <div>
                      <span>Complexity Items</span>
                      <strong>
                        {selectedReport.radon_report?.grades
                          ?.length || 0}
                      </strong>
                    </div>
                  </div>

                  <h3>Complexity Details</h3>

                  {selectedReport.radon_report?.complexity ? (
                    <pre className="complexity-output">
                      {
                        selectedReport.radon_report
                          .complexity
                      }
                    </pre>
                  ) : (
                    <p>
                      No functions or classes were found for
                      cyclomatic-complexity analysis.
                    </p>
                  )}
                </div>
              </>
            )}
          </main>
        </div>
      </div>
    </section>
  )
}

export default Reports