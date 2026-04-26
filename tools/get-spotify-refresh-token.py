#!/usr/bin/env python3
"""
Spotify OAuth refresh-token helper for novatorem.

Run AFTER you have created a Spotify Developer App and copied the
Client ID + Secret. This script handles the OAuth dance for you:
  1. Opens your browser to Spotify's authorize URL
  2. Captures the redirect on http://localhost:8888/callback
  3. Exchanges the auth code for a refresh token
  4. Prints the three env vars novatorem needs

Usage:
    python3 get-spotify-refresh-token.py
"""

import base64
import http.server
import json
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "user-read-currently-playing user-read-recently-played"
PORT = 8888

captured = {}


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            captured["code"] = params["code"][0]
            captured["state"] = params.get("state", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorized.</h1><p>You can close this tab and return to the terminal.</p>")
        elif "error" in params:
            captured["error"] = params["error"][0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h1>Authorization failed</h1><p>{captured['error']}</p>".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args, **kwargs):
        pass


def main():
    print("Spotify OAuth refresh-token helper for novatorem")
    print("------------------------------------------------\n")
    client_id = input("Spotify Client ID: ").strip()
    client_secret = input("Spotify Client Secret: ").strip()

    if not client_id or not client_secret:
        sys.exit("Client ID and Secret are both required.")

    state = secrets.token_urlsafe(16)
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    })

    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"\nOpening browser to authorize...\nIf it doesn't open, paste this URL:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for callback on http://localhost:8888/callback ...")
    while "code" not in captured and "error" not in captured:
        pass
    server.shutdown()

    if "error" in captured:
        sys.exit(f"Authorization error: {captured['error']}")
    if captured.get("state") != state:
        sys.exit("State mismatch — possible CSRF. Aborting.")

    code = captured["code"]
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        token_resp = json.loads(resp.read().decode())

    refresh_token = token_resp.get("refresh_token")
    if not refresh_token:
        sys.exit(f"No refresh_token in response: {token_resp}")

    print("\n========================================")
    print("Add these as environment variables on Vercel:")
    print("========================================\n")
    print(f"SPOTIFY_CLIENT_ID={client_id}")
    print(f"SPOTIFY_SECRET_ID={client_secret}")
    print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
    print("\nDone.")


if __name__ == "__main__":
    main()
