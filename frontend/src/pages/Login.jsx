function Login() {
  return (
    <section className="auth-page">

      <div className="auth-left">
        <h1>Welcome Back 👋</h1>

        <p>
          Sign in to upload your source code, manage previous reviews,
          and receive AI-powered suggestions.
        </p>

        <ul>
          <li>✔ AI Code Review</li>
          <li>✔ Security Analysis</li>
          <li>✔ Code Quality Reports</li>
          <li>✔ Review History</li>
        </ul>
      </div>

      <div className="auth-card">

        <h2>Login</h2>

        <form className="auth-form">

          <label>Email</label>
          <input
            type="email"
            placeholder="Enter email"
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
          />

          <button type="submit">
            Login
          </button>

        </form>

      </div>

    </section>
  )
}

export default Login