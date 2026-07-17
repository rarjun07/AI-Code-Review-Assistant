import { useEffect, useState } from 'react'
import {
  Activity,
  ArrowRight,
  Bot,
  Braces,
  Check,
  Code2,
  FileCode2,
  FileSearch,
  Gauge,
  Layers3,
  LockKeyhole,
  ShieldAlert,
  Sparkles,
  UploadCloud,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../services/api'

function Dashboard() {
  const [uploads, setUploads] = useState([])
  const [reports, setReports] = useState([])
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token')

        if (!token) {
          return
        }

        const headers = { Authorization: `Bearer ${token}` }
        const [uploadsResponse, reportsResponse] = await Promise.all([
          api.get('/upload/history', { headers }),
          api.get('/reports', { headers }),
        ])

        setUploads(uploadsResponse.data)
        setReports(reportsResponse.data)
      } catch {
        setError('We could not refresh your workspace data. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const securityIssueCount = reports.reduce(
    (total, report) => total + (report.bandit_report?.total_issues || 0),
    0
  )
  const aiSuggestionCount = reports.reduce(
    (total, report) => total + (report.ai_review?.findings?.length || 0),
    0
  )
  const latestReport = reports[0]
  const latestMetrics = latestReport?.documentation_report?.metrics || {}
  const latestMaintainability =
    latestReport?.radon_report?.maintainability
      ?.trim()
      .split(' - ')
      .pop() || 'N/A'
  const latestComplexityItems = latestReport?.radon_report?.grades?.length || 0
  const fallbackFunctionCount =
    (latestReport?.documentation_report?.functions?.length || 0) +
    (latestReport?.documentation_report?.classes || []).reduce(
      (total, classItem) => total + (classItem.methods?.length || 0),
      0
    )
  const fallbackClassCount = latestReport?.documentation_report?.classes?.length || 0
  const isAuthenticated = Boolean(localStorage.getItem('token'))

  const summaryCards = [
    {
      label: 'Total reviews',
      value: reports.length,
      note: 'Saved in your library',
      icon: FileSearch,
      tone: 'blue',
    },
    {
      label: 'Files analyzed',
      value: uploads.length,
      note: 'Python files processed',
      icon: FileCode2,
      tone: 'teal',
    },
    {
      label: 'Security findings',
      value: securityIssueCount,
      note: securityIssueCount ? 'Review recommended' : 'No active findings',
      icon: ShieldAlert,
      tone: securityIssueCount ? 'amber' : 'green',
    },
    {
      label: 'AI recommendations',
      value: aiSuggestionCount,
      note: 'Actionable suggestions',
      icon: Bot,
      tone: 'violet',
    },
  ]

  return (
    <section className="dashboard">
      <div className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <span className="eyebrow-pill"><Sparkles size={15} /> AI-assisted quality workspace</span>
          <h2>Review Python code with clarity, not noise.</h2>
          <p>
            Combine trusted static-analysis tools with structured AI guidance.
            Find quality, security, and complexity issues in one focused review.
          </p>

          <div className="hero-actions">
            <Link to="/upload" className="primary-btn">
              <UploadCloud size={19} /> Start a review <ArrowRight size={17} />
            </Link>
            <Link to="/reports" className="secondary-btn">
              <FileSearch size={19} /> Open report library
            </Link>
          </div>

          <div className="hero-trust-row">
            <span><Check size={15} /> Private workspace</span>
            <span><Check size={15} /> Multi-engine analysis</span>
            <span><Check size={15} /> Saved review history</span>
          </div>
        </div>

        <div className="review-preview" aria-label="Code review workflow preview">
          <div className="review-preview-head">
            <span className="preview-file"><Braces size={17} /> payment_service.py</span>
            <span className="preview-status"><i /> Analysis ready</span>
          </div>
          <div className="preview-code">
            <span><b>01</b><code>def process_payment(order):</code></span>
            <span><b>02</b><code>    token = order.payment_token</code></span>
            <span className="preview-code-focus"><b>03</b><code>    return charge(token, order.total)</code></span>
            <span><b>04</b><code /></span>
            <span><b>05</b><code>process_payment(current_order)</code></span>
          </div>
          <div className="preview-findings">
            <div><ShieldAlert size={18} /><span><strong>Security</strong><small>Validate payment token before use</small></span><em>High</em></div>
            <div><Gauge size={18} /><span><strong>Quality</strong><small>Add explicit error handling</small></span><em>Medium</em></div>
            <div><Bot size={18} /><span><strong>AI review</strong><small>2 improvement suggestions</small></span><em>Ready</em></div>
          </div>
        </div>
      </div>

      {error && <p className="feedback-message feedback-error">{error}</p>}

      <section className="dashboard-section">
        <div className="section-heading-row">
          <div>
            <span>Workspace pulse</span>
            <h2>Your review activity</h2>
          </div>
          {isLoading && <span className="loading-chip"><i /> Refreshing data</span>}
        </div>

        <div className="stats-grid">
          {summaryCards.map(({ label, value, note, icon: Icon, tone }) => (
            <article className={`stat-card stat-card-${tone}`} key={label}>
              <span className="stat-icon"><Icon size={21} /></span>
              <span className="stat-label">{label}</span>
              <strong>{isLoading ? '—' : value}</strong>
              <small>{note}</small>
            </article>
          ))}
        </div>
      </section>

      <div className="dashboard-panels">
        <section className="dashboard-panel quality-panel">
          <div className="panel-heading">
            <div>
              <span>Latest code health</span>
              <h2>{latestReport?.filename || 'Quality overview'}</h2>
            </div>
            <span className="panel-icon"><Activity size={21} /></span>
          </div>

          {latestReport ? (
            <div className="quality-metrics">
              <div><span><Gauge size={17} /> Maintainability</span><strong>{latestMaintainability}</strong></div>
              <div><span><Layers3 size={17} /> Complexity items</span><strong>{latestComplexityItems}</strong></div>
              <div><span><Braces size={17} /> Classes</span><strong>{latestMetrics.number_of_classes ?? fallbackClassCount}</strong></div>
              <div><span><Code2 size={17} /> Functions</span><strong>{latestMetrics.number_of_functions ?? fallbackFunctionCount}</strong></div>
              <div><span><FileCode2 size={17} /> Lines of code</span><strong>{latestMetrics.total_lines_of_code ?? 'N/A'}</strong></div>
              <div><span><Activity size={17} /> Avg. function length</span><strong>{latestMetrics.average_function_length ?? 'N/A'}</strong></div>
            </div>
          ) : (
            <div className="panel-empty-state">
              <span><Gauge size={24} /></span>
              <h3>No quality baseline yet</h3>
              <p>Run your first review to see maintainability and complexity metrics here.</p>
              <Link to="/upload">Analyze a Python file <ArrowRight size={16} /></Link>
            </div>
          )}
        </section>

        <section className="dashboard-panel recent-panel">
          <div className="panel-heading">
            <div>
              <span>Recent activity</span>
              <h2>Latest uploads</h2>
            </div>
            <Link to="/reports">View all</Link>
          </div>

          {uploads.length === 0 ? (
            <div className="panel-empty-state compact">
              <span><FileCode2 size={24} /></span>
              <h3>Your workspace is ready</h3>
              <p>{isAuthenticated ? 'Upload a Python file to begin.' : 'Sign in to start building your review history.'}</p>
            </div>
          ) : (
            <div className="recent-upload-list">
              {uploads.slice(0, 4).map((upload) => (
                <article key={upload.id}>
                  <span className="upload-file-icon"><FileCode2 size={19} /></span>
                  <span>
                    <strong>{upload.filename}</strong>
                    <small>{new Date(upload.uploaded_at).toLocaleString()}</small>
                  </span>
                  <span className="upload-ready"><Check size={14} /> Analyzed</span>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="security-strip">
        <span className="security-strip-icon"><LockKeyhole size={22} /></span>
        <div>
          <strong>Built for focused, responsible code review</strong>
          <p>JWT-protected reports, validated Python uploads, and dedicated security analysis with Bandit.</p>
        </div>
        <Link to="/upload">New secure review <ArrowRight size={16} /></Link>
      </section>
    </section>
  )
}

export default Dashboard
