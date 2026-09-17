const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const REDIRECT_URI = "http://127.0.0.1:5173/auth/google/login/callback/";

function GoogleLoginButton() {
  const handleLogin = () => {
    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    authUrl.searchParams.set('client_id', GOOGLE_CLIENT_ID);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', 'openid email profile');
    authUrl.searchParams.set('access_type', 'offline');
    authUrl.searchParams.set('prompt', 'consent');

    window.location.href = authUrl.toString();
  };

  return <button onClick={handleLogin}>Login with Google</button>;
}

// Callback page component
export async function handleGoogleCallback() {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');

  const response = await fetch('/api/dj-rest-auth/google/', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  });
  if (!response.ok){
    const error = await response.json();
    return { success: false, error};
  }
  const data = await response.json();
  return { success: true, data};
}

export default GoogleLoginButton;