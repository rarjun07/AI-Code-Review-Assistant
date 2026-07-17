import { ArrowLeft, SearchX } from 'lucide-react'
import { Link } from 'react-router-dom'

function NotFound() {
  return (
    <section className="not-found">
      <div>
        <span className="empty-state-icon"><SearchX size={23} /></span>
        <p>404 error</p>
        <h1>We could not find that page.</h1>
        <p>The address may be incorrect or the page may have moved.</p>
        <Link className="primary-btn" to="/"><ArrowLeft size={17} /> Back to dashboard</Link>
      </div>
    </section>
  )
}

export default NotFound
