const PrivacyPage = () => {
    return(
        <main style={{ maxWidth: "700px", margin: "2rem auto", padding: "0 1rem", lineHeight: 1.6 }}>
      <h1>Privacy Policy</h1>
      <p>Last updated: 26 October 2026</p>

      <p>
        RipeGrapes (ripegrapes.co.uk) is a small music rating site. This page explains
        what information it collects and how it is used.
      </p>

      <h2>What we collect</h2>
      <ul>
        <li>Your username and email address when you sign up.</li>
        <li>Your password, which is stored in hashed form and never in plain text.</li>
        <li>
          If you sign in with Google, the name and email address Google shares with us.
          We do not receive your Google password.
        </li>
        <li>The ratings and reviews you post, and your activity on the site.</li>
        <li>Cookies that keep you logged in.</li>
      </ul>

      <h2>How we use it</h2>
      <p>
        We use this information to run your account, show your ratings and reviews,
        and send account emails such as email verification and password resets. We do
        not sell your data and we do not use it for advertising.
      </p>

      <h2>Services we use</h2>
      <p>Your data is handled by the following providers on our behalf:</p>
      <ul>
        <li>Render, for hosting the site.</li>
        <li>Neon, for the database.</li>
        <li>Mailgun, for sending emails.</li>
        <li>Google, for optional Google sign-in.</li>
        <li>Spotify, for music search. Search terms are sent to Spotify to return results.</li>
      </ul>

      <h2>Cookies</h2>
      <p>
        We use cookies only to keep you signed in and to protect the site against
        forged requests. We do not use advertising or tracking cookies.
      </p>

      <h2>How long we keep it</h2>
      <p>
        We keep your information for as long as your account exists. If you ask us to
        delete your account, we will remove your personal data.
      </p>

      <h2>Your rights</h2>
      <p>
        You can ask to see the data we hold about you, correct it, or have it deleted.
        Contact us at{" "}
        <a href="mailto:privacy@ripegrapes.co.uk">privacy@ripegrapes.co.uk</a>.
      </p>

      <h2>Changes</h2>
      <p>
        If this policy changes, we will update the date at the top of this page.
      </p>
    </main>
    )
}

export default PrivacyPage;