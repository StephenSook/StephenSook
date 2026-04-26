# Live Spotify Now-Playing — novatorem setup

Total time: ~5–7 minutes. After this, your README shows the track you're currently listening to in real time.

## 1. Create a Spotify Developer App

1. Go to https://developer.spotify.com/dashboard
2. Log in with `lilsook2006@gmail.com`
3. Click **Create app**
4. Fill in:
   - **App name:** `GitHub Profile Now Playing`
   - **App description:** `Now-playing widget on github.com/StephenSook`
   - **Redirect URI:** `http://localhost:8888/callback`
   - **APIs used:** Web API
5. Save → open your app → **Settings** → copy **Client ID** and **Client Secret**

## 2. Get the refresh token (one-time)

Run from the repo root:

```bash
cd tools
python3 get-spotify-refresh-token.py
```

It will:
- Prompt for Client ID + Client Secret
- Open your browser to Spotify
- Capture the callback automatically
- Print three env vars (Client ID, Secret, Refresh Token)

Keep that output — you'll paste it into Vercel next.

## 3. Fork novatorem

1. Go to https://github.com/kittinanx/Action-NowPlaying-Spotify or https://github.com/JaGowda/novatorem (any maintained novatorem fork)
2. Click **Fork** → fork it onto `StephenSook`

> Quick option: from terminal —
> ```
> gh repo fork kittinanx/Action-NowPlaying-Spotify --clone=false
> ```

## 4. Deploy to Vercel

1. Go to https://vercel.com/new → **Import Git Repository** → select your novatorem fork
2. Framework preset: **Other**
3. Expand **Environment Variables**, add the three values from step 2:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_SECRET_ID`
   - `SPOTIFY_REFRESH_TOKEN`
4. Click **Deploy**
5. Once deployed, copy the production URL (e.g. `https://novatorem-stephensook.vercel.app`)

## 5. Wire it into the README

Open `README.md` and find the **Now Playing** section. Replace the placeholder badge with:

```html
<div align="center">
  <a href="https://open.spotify.com/user/31ozwwqttjufzxrv7k3qoovvpd34">
    <img src="https://YOUR-VERCEL-URL.vercel.app/api/spotify" alt="Live Spotify Now Playing" />
  </a>
</div>
```

Commit + push. Done — README now shows live track.

## Troubleshooting

- **Widget shows nothing** — make sure you're actively playing on Spotify (or recently played). The endpoint returns the last-known state.
- **`INVALID_CLIENT`** — the redirect URI in your Spotify app must match `http://localhost:8888/callback` exactly.
- **`401`** — refresh token expired (rare). Re-run the helper script to mint a new one.
- **Image cached on GitHub** — GitHub's camo proxy caches images. Append `?v=2` to bust cache, or wait ~5 minutes.
