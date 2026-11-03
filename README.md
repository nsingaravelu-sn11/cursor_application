# Demo Monitoring Infrastructure

Internal web shell for watching Linux servers. This repository currently contains the project skeleton and a placeholder home page.

## Requirements

- Python 3.10 or newer. Developed and checked on Python 3.10.12.

## Run the placeholder page

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | Interface the development server binds to. |
| `PORT` | `5000` | Port the development server binds to. |
| `FLASK_DEBUG` | off | Set to `1`, `true`, `yes`, or `on` to enable the Flask debugger. |

Any other `FLASK_DEBUG` value leaves the debugger off.

Example overrides are in `.env.example`. Copy that file to `.env` for local use. The application process reads variables from the environment; it does not load `.env` by itself.

## Security notes for this step

- The debugger stays off unless `FLASK_DEBUG` is set to an explicit on-value.
- The default bind address is loopback. Set `HOST` when you intend to listen on an internal interface.
- `.gitignore` excludes `.env`, database files (`*.db`, `*.sqlite`, `*.sqlite3`), and key files (`*.pem`, `*.key`, `*.p12`, `*.pfx`).
- Do not commit passwords, SSH keys, or a database file.
