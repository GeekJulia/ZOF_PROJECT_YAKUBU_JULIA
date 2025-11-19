# ZOF_PROJECT_YAKUBU_JULIA
Zero of Functions Solver - CLI + Web GUI
Works with Python 3.10.

## Setup
1. Create virtualenv:
   python3.10 -m venv venv
   source venv/bin/activate  (Windows: venv\Scripts\activate)

2. Install:
   pip install -r requirements.txt

## Run CLI
   python ZOF_CLI.py

## Run Web GUI (development)
   python app.py
Open http://127.0.0.1:5000

## Deployment
- Deploy `app.py` (Flask) to Render or Vercel (via a Flask-compatible adapter or container).
- After deploying, put live URL into `ZOF_hosted_webGUI_link.txt`.

## Notes
- Enter functions using Python expressions with `x` variable, e.g. `x**3 - 2*x - 5`.
- Fixed point requires g(x) (x = g(x)).

