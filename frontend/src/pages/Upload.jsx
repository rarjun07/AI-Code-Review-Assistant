import { useState } from 'react'
import api from '../services/api'

function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleUpload = async () => {
    setMessage('')
    setError('')

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

      setMessage(`File uploaded successfully: ${response.data.filename}`)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'File upload failed.')
    }
  }

  return (
    <section className="upload-page">
      <div className="upload-container">
        <h1>Upload Python Code</h1>

        <p>
          Upload your Python (.py) files and receive AI-powered review
          with security and quality analysis.
        </p>

        <div className="file-box">
          <h2>📂 Select Python File</h2>
          <p>Only .py files are allowed for now.</p>

          <input
            type="file"
            accept=".py"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        {file && <p><strong>Selected:</strong> {file.name}</p>}
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}

        <button onClick={handleUpload}>
          Upload & Analyze
        </button>
      </div>
    </section>
  )
}

export default Upload