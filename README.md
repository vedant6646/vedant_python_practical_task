# Automated Multi-Platform Posting System

FastAPI service that publishes one short message (with exactly one CTA link) to **6 third-party platforms** in parallel and reports a per-platform result. A failure on one platform never blocks the others.

| # | Platform | API used | Credentials |
|---|----------|----------|-------------|
| 1 | Telegraph (telegra.ph) | `createAccount` / `createPage` | **None needed** (works out of the box) |
| 2 | Mastodon | `POST /api/v1/statuses` | `MASTODON_ACCESS_TOKEN` |
| 3 | Bluesky | AT Protocol `createSession` + `createRecord` | `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD` |
| 4 | Telegram (public channel) | Bot API `sendMessage` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| 5 | DEV Community | `POST /api/articles` | `DEVTO_API_KEY` |
| 6 | GitHub Gist (public) | `POST /gists` | `GITHUB_TOKEN` (scope `gist`) |

Platforms without credentials return `status: "failed"` with an `Authentication failed: missing credentials (...)` error; the rest continue.

## Setup (virtual environment)

**Windows**
```bat
setup.bat
venv\Scripts\activate
python main.py
```

**Linux / macOS**
```bash
./setup.sh
source venv/bin/activate
python main.py
```

Manual equivalent:
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # Windows: copy .env.example .env
python main.py
```

Server: `http://localhost:4000` - Swagger docs: `http://localhost:4000/docs`
(`uvicorn app.main:app --host 0.0.0.0 --port 4000` also works.)

Edit `.env` and add keys for the platforms you want. `.env` is git-ignored - never commit it.

## API

`POST /posting`

Validation: message ≤ 200 chars, **exactly one** `http(s)://` link, link must be a valid URL. Invalid input returns **422**.

```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform and grow your online visibility. https://example.com"}'
```

### Sample success response (shape)
```json
{
  "success": true,
  "results": [
    {"platform": "Telegraph", "status": "success", "posted_url": "https://telegra.ph/Check-out-our-latest-11-21",
     "public_access": true, "date": "2026-11-21", "time": "11:16:33", "error": null},
    {"platform": "Mastodon", "status": "failed", "posted_url": null, "public_access": false,
     "date": null, "time": null,
     "error": "Authentication failed: missing credentials (MASTODON_ACCESS_TOKEN)"}
  ]
}
```
`success` is `true` when at least one platform succeeded. `public_access` is verified by an anonymous GET on the posted URL.

### Validation error examples (real output)
```json
// two links
{"success":false,"errors":[{"field":"message","message":"Message must contain exactly one CTA link (2 found)"}]}
// too long
{"success":false,"errors":[{"field":"message","message":"Message must not exceed 200 characters (got 224)"}]}
```

### Server log (real output, no credentials configured)
```
WARNING posting: Mastodon FAILED: Authentication failed: missing credentials (MASTODON_ACCESS_TOKEN)
WARNING posting: Bluesky FAILED: Authentication failed: missing credentials (BLUESKY_APP_PASSWORD)
INFO:     POST /posting HTTP/1.1" 200 OK
INFO:     POST /posting HTTP/1.1" 422 Unprocessable Entity
```
> Add your own screenshots of `/docs` and a successful run (with your keys) in a `screenshots/` folder before submitting.

## Tests
```bash
python -m pytest -q      # 8 passed
```
Covers validation rules and the "one platform fails, others continue" behaviour (mocked platforms, no network).

## Structure
```
main.py                  # python main.py entry point
app/main.py              # FastAPI app + /posting + error handler
app/schemas.py           # Pydantic models & validation
app/config.py            # env-based settings
app/platforms/*.py       # one class per platform (base.py = interface)
app/services/posting_service.py  # concurrent posting, error isolation, public check
tests/test_posting.py
```
To add a platform: subclass `Platform`, implement `publish()`, register it in `app/platforms/__init__.py`.
