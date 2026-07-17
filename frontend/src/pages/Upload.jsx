import { useState } from 'react'
import {
  Bot,
  Check,
  FileCode2,
  FileUp,
  Gauge,
  Info,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from 'lucide-react'
import api from '../services/api'

function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const [pylintReport, setPylintReport] = useState(null)
  const [banditReport, setBanditReport] = useState(null)
  const [radonReport, setRadonReport] = useState(null)
  const [aiReview, setAiReview] = useState(null)
  const [documentationReport, setDocumentationReport] = useState(null)

  const [analysisTime, setAnalysisTime] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleUpload = async () => {
    setMessage('')
    setError('')

    setPylintReport(null)
    setBanditReport(null)
    setRadonReport(null)
    setAiReview(null)
    setDocumentationReport(null)

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
    setIsAnalyzing(true)

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
      setDocumentationReport(response.data.documentation_report)

      setAnalysisTime(new Date().toLocaleString())
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'File upload failed.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const pylintIssues = pylintReport?.issues || []
  const codeSmells = pylintIssues.filter((issue) =>
    ['warning', 'convention', 'refactor'].includes(issue.type)
  )

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
    setDocumentationReport(null)

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

  return (
    <section className="upload-page">
      <header className="page-intro">
        <div>
          <span className="page-kicker"><Sparkles size={15} /> New analysis</span>
          <h2>Turn a Python file into an actionable review.</h2>
          <p>Select a source file and we will run five focused review stages in one workflow.</p>
        </div>
        <span className="page-intro-badge"><ShieldCheck size={17} /> Validated uploads</span>
      </header>

      <ol className="workflow-stepper" aria-label="Review workflow">
        <li className={file ? 'complete' : 'active'}><span>{file ? <Check size={16} /> : '1'}</span><div><strong>Select file</strong><small>Python source</small></div></li>
        <li className={isAnalyzing ? 'active' : ''}><span>2</span><div><strong>Run analysis</strong><small>Five review engines</small></div></li>
        <li className={pylintReport ? 'complete' : ''}><span>{pylintReport ? <Check size={16} /> : '3'}</span><div><strong>Review findings</strong><small>Prioritized results</small></div></li>
      </ol>

      <div className="upload-container">
        <div className="upload-intake-grid">
          <div className="upload-intake-main">
            <div className="file-box">
              <span className="file-box-icon"><FileUp size={30} /></span>
              <label className="file-box-label" htmlFor="python-file">
                Choose a Python source file
              </label>
              <p id="python-file-help">Use a .py file up to 1 MB. Your filename is safely normalized.</p>

              <input
                id="python-file"
                name="python-file"
                type="file"
                accept=".py"
                aria-describedby="python-file-help"
                disabled={isAnalyzing}
                onChange={(event) => {
                  const selectedFile = event.target.files?.[0] || null
                  setFile(selectedFile)
                }}
              />
            </div>

            {file && (
              <div className="selected-file-row">
                <span><FileCode2 size={19} /></span>
                <div><strong>{file.name}</strong><small>Ready for analysis</small></div>
                <Check size={18} />
              </div>
            )}

            {message && <p className="feedback-message feedback-success">{message}</p>}
            {error && <p className="feedback-message feedback-error">{error}</p>}

            <button className="analyze-btn" onClick={handleUpload} disabled={isAnalyzing}>
              <UploadCloud size={19} />
              {isAnalyzing ? 'Analyzing your code...' : 'Run complete analysis'}
            </button>

            {isAnalyzing && (
              <div className="analysis-progress" role="status">
                <span className="progress-spinner" />
                <div>
                  <strong>Review in progress</strong>
                  <p>Running code quality, security, complexity, documentation, and AI checks.</p>
                </div>
              </div>
            )}
          </div>

          <aside className="analysis-toolkit">
            <span className="analysis-toolkit-kicker"><Info size={15} /> Included in every review</span>
            <h3>Five perspectives. One report.</h3>
            <ul>
              <li><span><Check size={15} /></span><div><strong>Pylint</strong><small>Quality and standards</small></div></li>
              <li><span><ShieldCheck size={15} /></span><div><strong>Bandit</strong><small>Security vulnerabilities</small></div></li>
              <li><span><Gauge size={15} /></span><div><strong>Radon</strong><small>Complexity and maintainability</small></div></li>
              <li><span><Bot size={15} /></span><div><strong>AI review</strong><small>Prioritized recommendations</small></div></li>
              <li><span><FileCode2 size={15} /></span><div><strong>Documentation</strong><small>Functions, classes, and metrics</small></div></li>
            </ul>
          </aside>
        </div>

        {pylintReport && (
          <div className="report-card">
            <div className="report-header">
              <div>
                <h2>Pylint code quality</h2>

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
                <h3>Score</h3>
                <p>{pylintReport.score || 'N/A'}/10</p>
              </div>

              <div className="total-card">
                <h3>Total issues</h3>
                <p>{pylintIssues.length}</p>
              </div>

              <div className="error-card">
                <h3>Errors</h3>
                <p>{pylintErrors}</p>
              </div>

              <div className="warning-card">
                <h3>Warnings</h3>
                <p>{pylintWarnings}</p>
              </div>

              <div className="convention-card">
                <h3>Conventions</h3>
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

        {pylintReport && (
          <div className="report-card report-card-code-smells">
            <div className="report-header">
              <div>
                <h2>Code Smells</h2>

                <p>
                  Maintainability and style issues detected from
                  Pylint warnings, conventions, and refactor hints.
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
                    className={`issue-card code-smell-card ${getIssueClass(
                      issue.type
                    )}`}
                    key={`smell-${issue['message-id']}-${issue.line}-${index}`}
                  >
                    <strong>{issue.type.toUpperCase()}</strong>

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
                <h2>Bandit security analysis</h2>

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
                <h3>Total issues</h3>
                <p>{banditReport.total_issues}</p>
              </div>

              <div className="error-card">
                <h3>High severity</h3>
                <p>{banditReport.high_severity}</p>
              </div>

              <div className="warning-card">
                <h3>Medium severity</h3>
                <p>{banditReport.medium_severity}</p>
              </div>

              <div className="score-card">
                <h3>Low severity</h3>
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
                <h2>Radon complexity analysis</h2>

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

            {aiReview.status === 'completed' ? (
              <>
                <p>{aiReview.summary}</p>

                <div className="severity-summary-grid">
                  <div className="severity-critical">
                    <span>Critical</span>
                    <strong>{severitySummary.critical || 0}</strong>
                  </div>

                  <div className="severity-high">
                    <span>High</span>
                    <strong>{severitySummary.high || 0}</strong>
                  </div>

                  <div className="severity-medium">
                    <span>Medium</span>
                    <strong>{severitySummary.medium || 0}</strong>
                  </div>

                  <div className="severity-low">
                    <span>Low</span>
                    <strong>{severitySummary.low || 0}</strong>
                  </div>

                  <div className="severity-info">
                    <span>Info</span>
                    <strong>{severitySummary.info || 0}</strong>
                  </div>
                </div>

                <h3>Severity Findings</h3>

                {aiFindings.length === 0 ? (
                  <p>No AI findings with severity levels were reported.</p>
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
                          <span>{finding.severity || 'Info'}</span>
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
                    {renderAiList(aiReview.security_recommendations)}
                  </div>

                  <div>
                    <h3>Optimization</h3>
                    {renderAiList(aiReview.optimization_suggestions)}
                  </div>

                  <div>
                    <h3>Refactoring</h3>
                    {renderAiList(aiReview.refactoring_suggestions)}
                  </div>

                  <div>
                    <h3>Performance</h3>
                    {renderAiList(aiReview.performance_recommendations)}
                  </div>

                  <div>
                    <h3>Better Naming</h3>
                    {renderAiList(aiReview.naming_suggestions)}
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
            <div className="report-header">
              <div>
                <h2>Generated Documentation</h2>

                <p>
                  Automatic documentation generated from the
                  uploaded Python source code.
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
                      Line {item.line_number} · {item.method_count}{' '}
                      method(s)
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

        {(pylintReport ||
          banditReport ||
          radonReport ||
          aiReview ||
          documentationReport) && (
          <button
            className="secondary-btn analyze-again-btn"
            onClick={handleReset}
          >
            <RotateCcw size={17} /> Analyze another file
          </button>
        )}
      </div>
    </section>
  )
}

export default Upload
