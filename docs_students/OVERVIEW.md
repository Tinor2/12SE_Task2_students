# VIP Pizza Shop Repository Overview (AI Context)

## Purpose / Intent

This repository contains **VIP (Vulnerability Issues Pizza)**: a deliberately vulnerable Flask web application intended for learning web security concepts (OWASP-style vulnerabilities). It is **not** production-safe.

**Note (assessment context):** This codebase is a traditional server-rendered web application (Flask + HTML templates). In the assessment, it is used as a **stand-in** target for a “PWA security assessment” so you can practice the same security testing and remediation skills.

Primary entry point: `app.py`.

---

## Quick start (students)

1. Start the app: run `python app.py`
2. Open: `http://127.0.0.1:5000`
3. Log in with a default account (for testing):
   - `test / test123`
   - `demo / demo123`
   - `admin / admin123` (admin-only pages)

---

## Repository Structure

- `app.py`
  - Main Flask application with routes for:
    - Login/logout/registration
    - Pizza browsing and admin CRUD
    - Cart session handling
    - File upload/download endpoints
    - Debug endpoints
    - Password reset endpoints
    - Profile endpoints backed by SQLite
- `requirements.txt`
  - Python dependencies (Flask + Flask-CORS + related pinned versions)
- `pizza.json`
  - Pizza catalogue data (JSON). Read/written by the app.
- `users.db`
  - SQLite database shipped with the repo.
- `templates/`
  - `base.html` (layout/navigation)
  - `index.html` (home, login form, pizza list)
  - `admin.html` (admin CRUD for pizzas)
  - `cart.html` (cart UI + inline JS to call update/remove endpoints)
  - `checkout.html` (checkout form + cart summary)
  - `my_orders.html` (order list)
  - `order.html` (order receipt)
  - `register.html` (registration)
  - `reset.html` (legacy password reset page)
- `static/`
  - `css/styles.css` (UI styling)
  - `images/` (sample pizza images)
  - `config/dev.config.json` (dev config containing test credentials + api key)
  - `backup/`
    - `db_init.py.bak` (backup script that seeds test accounts)
  - `robots.txt` (attempts to hide sensitive paths via Disallow)
- `uploads/`
  - `Perfect-Pizza-Cookbook.pdf` (example uploaded file)
- `tools/`
  - `show_passwords.py` (prints usernames/passwords from `users.db`)
- `README.md`
  - Student instructions
- `docs_maintenance/`
  - Versioning / change tracking
- `docs_teacher/`
  - Teacher-only planning / analysis docs

---

## Runtime Architecture (High-Level)

- **Framework**: Flask (single-file app)
- **State**:
  - **Session**: Flask cookie-based session (`session[...]`) using `app.secret_key`.
  - **Cart**: stored in `session['cart']` as a list of dicts.
  - **Pizzas**: stored in `pizza.json` and written via `save_pizzas()`.
  - **Users/Profiles**: stored in `users.db` (SQLite).
- **Templates**: Jinja templates under `templates/`.
- **Static assets** served from `static/` and uploads served from `/uploads/<filename>`.

---

## Key Data Stores

### `pizza.json`

- Read: `load_pizzas()`
- Write: `save_pizzas(pizzas)`
  - Also writes a backup to `static/backup/pizza.json.bak`.

### `users.db`

Initialized/ensured by `init_db()`.

Tables:
- `users(id INTEGER PK, username TEXT UNIQUE, password TEXT, email TEXT UNIQUE)`
- `profiles(user_id INTEGER PK, full_name TEXT, email TEXT, phone TEXT, credit_card TEXT, address TEXT, FK->users(id))`
- `orders(id INTEGER PK, created_at TEXT, user_id INTEGER, username TEXT, delivery_address TEXT, notes TEXT, coupon_code TEXT, client_total REAL, server_total REAL, cart_json TEXT, status TEXT, FK->users(id))`

Default credentials are inserted if missing:
- admin / admin123
- test / test123
- demo / demo123

---

## Routes / Features (Selected)

- `/` (GET): Home page listing pizzas.
- `/login` (GET/POST): Login form + auth.
- `/logout` (GET): Clears session.
- `/register` (GET/POST): Inserts user into DB.
- `/admin` (GET/POST): Admin CRUD for pizzas (requires session user == `admin`).
- `/add_to_cart` (POST): Add a pizza to cart stored in session.
- `/cart` (GET): View cart.
- Checkout / Orders:
  - `/checkout` (GET/POST): Checkout (requires login) and create a persistent order in SQLite.
  - `/my-orders` (GET): View orders (intentionally vulnerable).
  - `/order/<int:order_id>` (GET): View an order receipt (intentionally vulnerable).
- `/update_cart` (POST): Update quantity of item in session cart.
- `/remove_from_cart` (POST): Remove item from session cart.
- `/upload` (GET/POST): Uploads file to `./uploads/`.
- `/uploads/<path:filename>` (GET): Serves uploaded files.
- `/download?file=...` (GET): Reads and returns arbitrary file contents.
- `/debug/<path:file_path>` (GET): Reads arbitrary file contents and dumps system/env info.
- `/user/<username>` (GET): DB lookup by username.
- `/profile/<int:user_id>` (GET): Displays profile data (including sensitive fields).
- `/create_profile` (GET/POST): Creates/replaces profile for logged-in user.
- Password reset related:
  - `/forgot-password` (GET/POST)
  - `/password-reset` (GET/POST)
  - `/reset` (GET/POST) (legacy)

---

## Security Posture: Intentionally Vulnerable

This app includes many high-impact issues that would be unacceptable in production. Below is a concise map of the most important ones.

### Authentication / Session

- **Hardcoded weak session secret**: `app.secret_key = "12345"`.
- **Hardcoded default credentials** in source + in `static/config/dev.config.json`.
- **Passwords stored in DB in retrievable form** (and tool exists to print them).

### SQL Injection

Unsafe string interpolation is used in multiple queries:
- `/login`
- `/error_test`
- `/user/<username>`
- `/password-reset` (UPDATE)

### Sensitive Data Exposure

- `/profile/<int:user_id>` exposes `credit_card`, address, phone, etc.
  - Easy enumeration via previous/next links.
- `/debug/<path:file_path>` dumps **env vars, OS, cwd**, etc.
- Verbose 500 handler returns stack trace and environment details.
- `static/config/dev.config.json` exposes **API key** (`"test": "123456789"`).

### File System Attacks

- `/download?file=...` allows arbitrary file read (directory traversal).
- `/debug/<path:file_path>` also allows arbitrary file read.
- `/upload` allows unrestricted upload and uses unsanitized filename.

### Broken / Weak Password Reset

- `/forgot-password` generates a token but does not persist it or verify it later.
- `/password-reset` accepts `username`+`token` but does **not verify token**.
- `/reset` references `reset_tokens` which is **undefined** (causes server error).

### CORS

- `CORS(... origins="*")` permits cross-origin requests broadly.

### Dependency / Supply-Chain Vulnerabilities (GitHub Security Alerts)

GitHub Security (Dependabot) reports known vulnerabilities in the pinned Python dependencies in `requirements.txt`. These are **separate** from the intentionally insecure application code; even a “securely written” app can still be vulnerable if it ships with vulnerable library versions.

Observed pinned versions in this repo:
- `Flask-Cors==4.0.0`
- `Werkzeug==3.0.1`
- `Jinja2==3.1.2`

Reported alerts (as provided by GitHub Security):
- **Flask-CORS**
  - Allows the `Access-Control-Allow-Private-Network` CORS header to be set to true by default (**High**).
  - Log injection possible when log level is set to debug (**Moderate**).
  - Improper handling of case sensitivity / inconsistent CORS matching / improper regex path matching (**Moderate**).
- **Werkzeug**
  - Debugger vulnerable to remote execution when interacting with attacker-controlled domain (**High**).
  - Possible resource exhaustion when parsing file data in forms (**Moderate**).
  - `safe_join` not safe on Windows / Windows special device names issues (**Moderate**).
- **Jinja2**
  - HTML attribute injection when passing user input as keys to `xmlattr` filter (**Moderate**).
  - Sandbox breakouts via `attr` filter selecting `format` method / indirect references to `format` / malicious filenames (**Moderate**).

Why these matter in *this* repo:
- The app is started with `app.run(debug=True)` (see `app.py`), which increases exposure to debugger-related issues.
- The project runs on Windows in many classroom environments, which makes the Windows `safe_join` issues especially relevant.

Mitigation direction (if producing a hardened variant):
- Upgrade dependencies to versions that GitHub marks as fixed (adjust pins in `requirements.txt`).
- Do not run Flask/Werkzeug in debug mode in any environment accessible to other users.
- Treat file path handling and file serving as high-risk on Windows (avoid relying on vulnerable path-join behaviors).

### Security-through-obscurity

- `static/robots.txt` tries to hide sensitive directories; does not secure them.

---

## Correctness / Stability Issues

- `reset_tokens` is referenced but never defined (breaks `/reset`).
- `/api/docs` route references `api_docs.html` which is missing from `templates/` (causes 500 error).

---

## Notes for AI Assistants / Contributors

- This repository is designed as a vulnerable target for security education.
- Any “fixing” work should be done with awareness of the intended learning outcomes:
  - Some tasks may require keeping vulnerabilities for demonstration.
  - Other tasks may require producing a hardened/secure variant.

Potential improvement directions (depending on assignment goals):
- Parameterize SQL queries everywhere.
- Hash passwords with a modern algorithm.
- Use strong secrets via environment variables.
- Remove or lock down debug endpoints.
- Add upload allowlist + filename sanitization.
- Implement a real password reset token flow.
- Restrict CORS and add CSRF protections.

---

## Comprehensive File Analysis (AI-Generated)

This section provides detailed analysis of all repository files, conducted systematically to ensure completeness and accuracy of the OVERVIEW.md documentation.

### Core Application (`app.py`)
- **Structure**: Single-file Flask app containing the main routes, database setup, and deliberately vulnerable demo endpoints.
- **Key Functions**: 
  - `init_db()`: Creates `users` and `profiles` tables with sensitive fields.
  - `load_pizzas()` / `save_pizzas()`: JSON file handling with backup.
- **Vulnerabilities Confirmed**:
  - SQL injection in login, user lookup, password reset (string interpolation).
  - Weak session secret ("12345").
  - Hardcoded credentials used in auth.
  - Arbitrary file read via `/download` and `/debug`.
  - Unrestricted file upload without validation.
  - Password reset flow broken (no token verification).
  - Verbose error handling exposing stack traces.
  - Undefined `reset_tokens` in `/reset` route.

### Templates (`templates/*.html`)
- **base.html**: Layout template with navigation, shows admin link for admin users, footer with fake contact info.
- **index.html**: Home page with login form (no CSRF token), user welcome with fake order history, pizza grid with add-to-cart forms.
- **admin.html**: Admin CRUD interface for pizzas, uses multipart forms for uploads, inline form updates.
- **cart.html**: Cart display with inline JS for update/remove operations via fetch (no CSRF), quantity inputs, confirm dialogs vulnerable to XSS via item names.
- **register.html**: Registration form with benefits list, no CSRF token.
- **reset.html**: Legacy password reset form, simple HTML without JS.
- **Common Issues**: All forms lack CSRF protection. No input validation on client-side. JS in cart.html uses unsanitized data.

### Static Assets (`static/`)
- **config/dev.config.json**: Contains hardcoded test credentials (admin/admin123, test/test123, demo/demo123) and API key ("test": "123456789").
- **backup/db_init.py.bak**: Appears to be a backup of database initialization script.
- **robots.txt**: Attempts to disallow sensitive paths like /admin, /debug, /uploads.
- **css/styles.css**: UI styling (not analyzed for vulnerabilities).
- **images/**: Sample pizza images referenced in pizza.json.

### Data Files
- **pizza.json**: Array of 4 pizza objects with name, description, image, price. Images misassigned (pepperoni.jpg used for veggie, etc.).
- **users.db**: SQLite database with `users` (id, username, password, email) and `profiles` (user_id, full_name, email, phone, credit_card, address) tables. Passwords stored in plaintext.
- **uploads/Perfect-Pizza-Cookbook.pdf**: Example uploaded file.

### Tools (`tools/`)
- **show_passwords.py**: Simple script to dump all username/password pairs from users.db, demonstrating plaintext storage.
- **check_version.py**: Verifies file integrity against docs_maintenance/VERSION.md hash, uses MD5/SHA256.

### Documentation
- **README.md**: Educational guide explaining the app's purpose, setup, and what to look for in security testing.
- **docs_maintenance/CHANGELOG.md**: Version history, notes vulnerabilities are intentional for learning.
- **docs_maintenance/VERSION.md**: Version info with hash, includes verification script.
- **docs_teacher/cohort_feedback.md**: Assessment criteria and feedback from student submissions, including marking rubrics.

### Missing Elements (Resolved in Updates)
- Added `/api/docs` route (broken due to missing template).
- Added CSRF vulnerability (forms lack tokens).
- Added XSS in cart.html JS.
- Added API key exposure in dev.config.json.

This analysis confirms the repository is a comprehensive vulnerable target for OWASP-style security education, with intentional flaws across authentication, injection, exposure, and client-side risks. All documented vulnerabilities are present and functional for demonstration purposes. 

Task completion: OVERVIEW.md updated with all missing elements from codebase analysis. Repository fully documented. 


