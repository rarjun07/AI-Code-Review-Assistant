function Upload() {
  return (
    <section className="upload-page">

      <div className="upload-container">

        <h1>Upload Python Code</h1>

        <p>
          Upload your Python (.py) files and receive
          AI-powered review with security and quality analysis.
        </p>

        <div className="file-box">

          <h2>📂 Drag & Drop Files</h2>

          <p>
            or click below to browse files
          </p>

          <input type="file" />

        </div>

        <button>
          Upload & Analyze
        </button>

      </div>

    </section>
  )
}

export default Upload