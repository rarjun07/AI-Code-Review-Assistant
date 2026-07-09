function Register() {
  return (
    <section className="auth-page">

      <div className="auth-left">
        <h1>Create Your Account</h1>

        <p>
          Join AI Code Review Assistant and start analyzing your Python
          projects using AI and static analysis tools.
        </p>

        <ul>
          <li>✔ Upload Unlimited Files</li>
          <li>✔ AI Suggestions</li>
          <li>✔ Security Reports</li>
          <li>✔ Complexity Analysis</li>
        </ul>
      </div>

      <div className="auth-card">

        <h2>Register</h2>

        <form className="auth-form">

          <label>Full Name</label>
          <input placeholder="Your name" />

          <label>Email</label>
          <input
            type="email"
            placeholder="Email"
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Password"
          />

          <button>
            Create Account
          </button>

        </form>

      </div>

    </section>
  )
}

export default Register