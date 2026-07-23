# rate-system

A full-stack music rating web application. Users can search for tracks/albums via the Spotify API, rate them, and (in progress) leave reviews.

## Status

This project is under active development, targeting a public launch in September. The backend is largely complete; current work is on the frontend and connecting it to the backend.

**Done:**
- JWT cookie-based authentication (login, session check)
- Search UI wired to the backend, returning live Spotify results
- Rating form (frontend) and its connection to the ratings endpoint
- Protected route testing

**In progress:**
- 401 handling / token refresh on the client

**Not started:**
- List of Reviews for User
- Styling
- Deployment

## Tech Stack

**Backend:** Django, Django REST Framework, dj-rest-auth, SimpleJWT, django-allauth, django-cors-headers, django-environ

**Frontend:** React 19, Vite, react-router-dom 7

## Architecture Notes

- Auth uses JWT stored in HttpOnly cookies (not localStorage). Login sets the cookies; the frontend confirms auth state by calling `GET /dj-rest-auth/user/`.
- Frontend route guards are a UX convenience only, they don't enforce anything. Actual access control lives in DRF permission classes (`IsAuthenticated`, `IsOwnerOrReadOnly`) on the backend.
- Ratings are looked up by what's being rated, not by user; the rating endpoint is shaped like `ratings/<content_type>/<spotify_id>/`, and the user is resolved server-side from the authenticated request, not passed in the URL.
- Search goes through a Vite dev-server proxy (`/api/search/`) to a Django `SpotifySearchView`, keeping Spotify credentials off the client.