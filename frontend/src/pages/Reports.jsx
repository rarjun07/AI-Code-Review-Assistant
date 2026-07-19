import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowUpDown,
  BookOpen,
  Bot,
  Download,
  FileCode2,
  FileSearch,
  Gauge,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  UploadCloud,
} from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../services/api'

function Reports() {
  const [searchParams] = useSearchParams()
  const [reports, setReports] = useState([])
  const [selectedReport, setSelectedReport] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [pendingDeleteId, setPendingDeleteId] = useState(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const deleteActionRef = useRef(null)
  const [searchTerm, setSearchTerm] = useState(
    () => searchParams.get('search') || ''
  )
  const [filterType, setFilterType] = useState('all')
  const [sortOrder, setSortOrder] = useState('newest')

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

  useEffect(() => {
    if (!pendingDeleteId) {
      return undefined
    }

    const closeDeleteConfirmation = (event) => {
      if (event.key === 'Escape') {
        setPendingDeleteId(null)
        return
      }

      if (
        event.type === 'pointerdown' &&
        deleteActionRef.current &&
        !deleteActionRef.current.contains(event.target)
      ) {
        setPendingDeleteId(null)
      }
    }

    document.addEventListener('keydown', closeDeleteConfirmation)
    document.addEventListener('pointerdown', closeDeleteConfirmation)

    return () => {
      document.removeEventListener('keydown', closeDeleteConfirmation)
      document.removeEventListener('pointerdown', closeDeleteConfirmation)
    }
  }, [pendingDeleteId])

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

  const deleteReport = async (reportId) => {
    try {
      setError('')
      setNotice('')
      setIsDeleting(true)

      const token = localStorage.getItem('token')

      const response = await api.delete(`/reports/${reportId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      const remainingReports = reports.filter(
        (report) => report.id !== reportId
      )

      setReports(remainingReports)

      if (selectedReport?.id === reportId) {
        setSelectedReport(remainingReports[0] || null)
      }

      setPendingDeleteId(null)
      setNotice(response.data.message)
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to delete report.'
      )
    } finally {
      setIsDeleting(false)
    }
  }

  const exportReport = async (reportId, format) => {
    try {
      setError('')

      const token = localStorage.getItem('token')

      const response = await api.get(
        `/reports/${reportId}/export/${format}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob',
        }
      )

      const extension = format === 'markdown' ? 'md' : format
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')

      link.href = url
      link.download = `ai-code-review-report-${reportId}.${extension}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(
        err.response?.data?.detail || `Failed to export ${format} report.`
      )
    }
  }

  const pylintIssues =
    selectedReport?.pylint_report?.issues || []
  const codeSmells = pylintIssues.filter((issue) =>
    ['warning', 'convention', 'refactor'].includes(issue.type)
  )

  const banditIssues =
    selectedReport?.bandit_report?.issues || []

  const aiReview = selectedReport?.ai_review
  const documentationReport = selectedReport?.documentation_report

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

  const renderAiList = (items) => {
    if (!items || items.length === 0) {
      return <p className="ai-empty-text">No items reported.</p>
    }

    return (
      <ul>
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    )
  }

  const getSeverityClass = (severity) => {
    const normalizedSeverity = severity?.toLowerCase()

    if (normalizedSeverity === 'critical') return 'severity-critical'
    if (normalizedSeverity === 'high') return 'severity-high'
    if (normalizedSeverity === 'medium') return 'severity-medium'
    if (normalizedSeverity === 'low') return 'severity-low'

    return 'severity-info'
  }

  const severitySummary = aiReview?.severity_summary || {}
  const aiFindings = aiReview?.findings || []

  const filteredReports = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase()

    return reports
      .filter((report) => {
        const matchesSearch =
          !normalizedSearch ||
          report.filename?.toLowerCase().includes(normalizedSearch) ||
          String(report.id).includes(normalizedSearch)

        if (!matchesSearch) {
          return false
        }

        if (filterType === 'security') {
          return report.bandit_report?.total_issues > 0
        }

        if (filterType === 'clean') {
          return (
            (report.pylint_report?.issues?.length || 0) === 0 &&
            (report.bandit_report?.total_issues || 0) === 0
          )
        }

        if (filterType === 'ai') {
          return report.ai_review?.status === 'completed'
        }

        if (filterType === 'documentation') {
          return report.documentation_report?.status === 'completed'
        }

        return true
      })
      .sort((firstReport, secondReport) => {
        if (sortOrder === 'oldest') {
          return (
            new Date(firstReport.created_at) -
            new Date(secondReport.created_at)
          )
        }

        if (sortOrder === 'filename') {
          return firstReport.filename.localeCompare(
            secondReport.filename
          )
        }

        return (
          new Date(secondReport.created_at) -
          new Date(firstReport.created_at)
        )
      })
  }, [filterType, reports, searchTerm, sortOrder])

  return (
    <section className="reports-page">
      <div className="reports-container">
        <div className="reports-header page-intro">
          <div>
            <span className="page-kicker"><Sparkles size={15} /> Review library</span>
            <h2>Every analysis, organized and ready to act on.</h2>
            <p>Compare findings, revisit recommendations, and export a clean review for your team.</p>
          </div>
          <Link className="primary-btn" to="/upload"><UploadCloud size={18} /> New review</Link>
        </div>

        <div className="reports-controls">
          <label>
            <span><Search size={15} /> Search</span>
            <input
              type="search"
              placeholder="Search by filename or report ID"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>

          <label>
            <span><SlidersHorizontal size={15} /> Filter</span>
            <select
              value={filterType}
              onChange={(event) => setFilterType(event.target.value)}
            >
              <option value="all">All reports</option>
              <option value="security">Security issues</option>
              <option value="clean">Clean reports</option>
              <option value="ai">AI reviewed</option>
              <option value="documentation">Documented</option>
            </select>
          </label>

          <label>
            <span><ArrowUpDown size={15} /> Sort</span>
            <select
              value={sortOrder}
              onChange={(event) => setSortOrder(event.target.value)}
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="filename">Filename A-Z</option>
            </select>
          </label>
        </div>

        {error && (
          <p className="feedback-message feedback-error">{error}</p>
        )}

        {notice && (
          <p className="feedback-message feedback-success">{notice}</p>
        )}

        <div className="reports-layout">
          <aside className="reports-list">
            <div className="reports-list-header">
              <h2>Saved Reports</h2>
              <span>
                {filteredReports.length} of {reports.length}
              </span>
            </div>

            {reports.length === 0 ? (
              <div className="report-list-empty">
                <span className="empty-state-icon"><FileSearch size={23} /></span>
                <h3>No reports yet</h3>
                <p>
                  Upload and analyze a Python file to create your
                  first report.
                </p>
                <Link to="/upload">Start a review</Link>
              </div>
            ) : filteredReports.length === 0 ? (
              <div className="report-list-empty">
                <span className="empty-state-icon"><Search size={23} /></span>
                <h3>No matching reports</h3>
                <p>
                  Change the search text or filter to see more
                  reports.
                </p>
              </div>
            ) : (
              filteredReports.map((report) => (
                <button
                  className={`report-list-card ${
                    selectedReport?.id === report.id
                      ? 'report-list-card-active'
                      : ''
                  }`}
                  key={report.id}
                  onClick={() => openReport(report.id)}
                >
                  <div className="report-list-title">
                    <span><FileCode2 size={18} /></span>
                    <div><h3>{report.filename}</h3><p>Report #{report.id}</p></div>
                  </div>
                  <div className="report-list-badges">
                    {report.bandit_report?.total_issues > 0 && (
                      <span className="badge-danger">Security</span>
                    )}
                    {report.ai_review?.status === 'completed' && (
                      <span className="badge-info">AI</span>
                    )}
                    {report.documentation_report?.status ===
                      'completed' && (
                      <span className="badge-docs">Docs</span>
                    )}
                  </div>
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
                <span className="empty-state-icon"><FileSearch size={23} /></span>
                <h2>Select a report</h2>
                <p>
                  Choose a saved report from the left side to view
                  complete analysis details.
                </p>
              </div>
            ) : (
              <>
                <div className="report-card report-summary-card">
                  <div className="report-summary-header">
                    <h2><FileSearch size={21} /> Report summary</h2>

                    <div className="report-summary-actions">
                      <button
                        className="export-report-btn"
                        type="button"
                        onClick={() =>
                          exportReport(selectedReport.id, 'pdf')
                        }
                      >
                        <Download size={15} /> PDF
                      </button>
                      <button
                        className="export-report-btn"
                        type="button"
                        onClick={() =>
                          exportReport(selectedReport.id, 'markdown')
                        }
                      >
                        <Download size={15} /> Markdown
                      </button>
                      <button
                        className="export-report-btn"
                        type="button"
                        onClick={() =>
                          exportReport(selectedReport.id, 'html')
                        }
                      >
                        <Download size={15} /> HTML
                      </button>
                      <div
                        className="delete-report-action"
                        ref={deleteActionRef}
                      >
                        <button
                          className="delete-report-btn"
                          type="button"
                          aria-expanded={
                            pendingDeleteId === selectedReport.id
                          }
                          aria-haspopup="dialog"
                          aria-controls="delete-report-confirmation"
                          onClick={() => {
                            setNotice('')
                            setPendingDeleteId((currentId) =>
                              currentId === selectedReport.id
                                ? null
                                : selectedReport.id
                            )
                          }}
                        >
                          <Trash2 size={15} /> Delete
                        </button>

                        {pendingDeleteId === selectedReport.id && (
                          <div
                            className="delete-confirmation-popover"
                            id="delete-report-confirmation"
                            role="dialog"
                            aria-labelledby="delete-confirmation-title"
                          >
                            <strong id="delete-confirmation-title">
                              Delete this report?
                            </strong>
                            <p>
                              Report #{selectedReport.id} and its uploaded
                              file will be permanently removed.
                            </p>
                            <div className="delete-confirmation-actions">
                              <button
                                className="delete-cancel-btn"
                                type="button"
                                disabled={isDeleting}
                                onClick={() => setPendingDeleteId(null)}
                              >
                                Cancel
                              </button>
                              <button
                                className="delete-confirm-btn"
                                type="button"
                                disabled={isDeleting}
                                onClick={() =>
                                  deleteReport(selectedReport.id)
                                }
                              >
                                <Trash2 size={14} />
                                {isDeleting ? 'Deleting...' : 'Delete'}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

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
                      <h2><FileCode2 size={21} /> Pylint code quality</h2>
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

                <div className="report-card report-card-code-smells">
                  <div className="report-section-header">
                    <div>
                      <h2>Code Smells</h2>
                      <p>
                        Maintainability and style issues found from
                        Pylint warnings, conventions, and refactor
                        hints.
                      </p>
                    </div>

                    <span
                      className={`report-status ${
                        codeSmells.length === 0
                          ? 'status-good'
                          : 'status-warning'
                      }`}
                    >
                      {codeSmells.length} Found
                    </span>
                  </div>

                  {codeSmells.length === 0 ? (
                    <p>No code smells were detected.</p>
                  ) : (
                    <div className="issue-list">
                      {codeSmells.map((issue, index) => (
                        <div
                          className={`issue-card code-smell-card ${getPylintIssueClass(
                            issue.type
                          )}`}
                          key={`smell-${issue['message-id']}-${issue.line}-${index}`}
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
                      <h2><ShieldCheck size={21} /> Bandit security analysis</h2>
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
                      <h2><Gauge size={21} /> Radon complexity analysis</h2>
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

                {aiReview && (
                  <div className="report-card report-card-ai">
                    <div className="report-section-header">
                      <div>
                        <h2><Bot size={21} /> AI code review</h2>
                        <p>
                          AI-powered recommendations based on code
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

                    {aiReview.status === 'completed' ? (
                      <>
                        <p>{aiReview.summary}</p>

                        <div className="severity-summary-grid">
                          <div className="severity-critical">
                            <span>Critical</span>
                            <strong>
                              {severitySummary.critical || 0}
                            </strong>
                          </div>

                          <div className="severity-high">
                            <span>High</span>
                            <strong>
                              {severitySummary.high || 0}
                            </strong>
                          </div>

                          <div className="severity-medium">
                            <span>Medium</span>
                            <strong>
                              {severitySummary.medium || 0}
                            </strong>
                          </div>

                          <div className="severity-low">
                            <span>Low</span>
                            <strong>
                              {severitySummary.low || 0}
                            </strong>
                          </div>

                          <div className="severity-info">
                            <span>Info</span>
                            <strong>
                              {severitySummary.info || 0}
                            </strong>
                          </div>
                        </div>

                        <h3>Severity Findings</h3>

                        {aiFindings.length === 0 ? (
                          <p>
                            No AI findings with severity levels
                            were reported.
                          </p>
                        ) : (
                          <div className="severity-finding-list">
                            {aiFindings.map((finding, index) => (
                              <div
                                className={`severity-finding-card ${getSeverityClass(
                                  finding.severity
                                )}`}
                                key={`${finding.title}-${index}`}
                              >
                                <div className="severity-finding-header">
                                  <span>
                                    {finding.severity || 'Info'}
                                  </span>
                                  <strong>
                                    {finding.category || 'General'}
                                  </strong>
                                </div>

                                <h4>{finding.title}</h4>
                                <p>{finding.description}</p>

                                {finding.suggestion && (
                                  <p>
                                    <strong>Suggestion:</strong>{' '}
                                    {finding.suggestion}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="ai-review-grid">
                          <div>
                            <h3>Strengths</h3>
                            {renderAiList(aiReview.strengths)}
                          </div>

                          <div>
                            <h3>Bugs</h3>
                            {renderAiList(aiReview.bugs)}
                          </div>

                          <div>
                            <h3>Security</h3>
                            {renderAiList(
                              aiReview.security_recommendations
                            )}
                          </div>

                          <div>
                            <h3>Optimization</h3>
                            {renderAiList(
                              aiReview.optimization_suggestions
                            )}
                          </div>

                          <div>
                            <h3>Refactoring</h3>
                            {renderAiList(
                              aiReview.refactoring_suggestions
                            )}
                          </div>

                          <div>
                            <h3>Performance</h3>
                            {renderAiList(
                              aiReview.performance_recommendations
                            )}
                          </div>

                          <div>
                            <h3>Better Naming</h3>
                            {renderAiList(
                              aiReview.naming_suggestions
                            )}
                          </div>

                          <div>
                            <h3>Best Practices</h3>
                            {renderAiList(aiReview.best_practices)}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="ai-review-alert">
                        <strong>AI review could not run.</strong>
                        <p>{aiReview.summary}</p>
                      </div>
                    )}
                  </div>
                )}

                {documentationReport && (
                  <div className="report-card report-card-documentation">
                    <div className="report-section-header">
                      <div>
                        <h2><BookOpen size={21} /> Generated documentation</h2>
                        <p>
                          Function and class documentation generated
                          from the uploaded Python file.
                        </p>
                      </div>

                      <span
                        className={`report-status ${
                          documentationReport.status === 'completed'
                            ? 'status-good'
                            : 'status-warning'
                        }`}
                      >
                        {documentationReport.status === 'completed'
                          ? 'Generated'
                          : 'Needs Fix'}
                      </span>
                    </div>

                    <p>{documentationReport.summary}</p>

                    <div className="documentation-stats">
                      <div>
                        <span>Functions</span>
                        <strong>
                          {documentationReport.functions?.length || 0}
                        </strong>
                      </div>

                      <div>
                        <span>Classes</span>
                        <strong>
                          {documentationReport.classes?.length || 0}
                        </strong>
                      </div>
                    </div>

                    <h3>Functions</h3>

                    {documentationReport.functions?.length ? (
                      <div className="documentation-list">
                        {documentationReport.functions.map((item) => (
                          <div
                            className="documentation-item"
                            key={`function-${item.name}-${item.line_number}`}
                          >
                            <h4>{item.name}</h4>
                            <p>{item.summary}</p>
                            <span>Line {item.line_number}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>No top-level functions found.</p>
                    )}

                    <h3>Classes</h3>

                    {documentationReport.classes?.length ? (
                      <div className="documentation-list">
                        {documentationReport.classes.map((item) => (
                          <div
                            className="documentation-item"
                            key={`class-${item.name}-${item.line_number}`}
                          >
                            <h4>{item.name}</h4>
                            <p>{item.docstring}</p>
                            <span>
                              Line {item.line_number} ·{' '}
                              {item.method_count} method(s)
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>No classes found.</p>
                    )}

                    <h3>README Summary</h3>

                    {documentationReport.markdown ? (
                      <pre className="readme-summary">
                        {documentationReport.markdown}
                      </pre>
                    ) : (
                      <p>No README summary generated.</p>
                    )}
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </section>
  )
}

export default Reports
