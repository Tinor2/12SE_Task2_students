# TESTING.md — VIP Pizza Vulnerability Testing Guide (Beginner)

This document shows **beginner-friendly** ways to test the VIP Pizza project using:
- **Blackbox testing** (no code access)
- **Greybox testing** (some knowledge: endpoints, hints, docs)
- **Whitebox testing** (read the source code)

It covers **original vulnerabilities** already in the project *and* the **new exam-gap vulnerabilities** you implemented.

**Important safety rules (read first):**
- Only test this app on your own machine in a controlled classroom/lab.
- Do not test other systems or networks.
- Record evidence (screenshots, URLs, payloads, outputs). Do **not** write “I think it worked” without proof.

**Assumed local URL:** `http://127.0.0.1:5000`

---

## Student Path (Minimum Required)

If you feel overwhelmed by the size of this document, follow this pathway.

### Minimum requirements
- You must **test 8 vulnerabilities total**.
- At least **3 of your confirmed vulnerabilities must be High/Critical** (use the Severity Guide in `docs_students/REPORT_TEMPLATE.md`).
- You may describe findings using OWASP Top 10 (2021) categories (e.g. **A01: Broken Access Control**, **A04: Insecure Design**).
- For every vulnerability you claim, include evidence:
  - URL/endpoint
  - exact payload/input
  - screenshot or copied output
  - 1–2 sentence impact explanation

**Example (recommended):** If you’re not sure what a good write-up looks like, open:
- `docs_students/SAMPLE/SAMPLE_REPORT_TEMPLATE.md`

### Recommended minimum 8 set (fastest path)
If you just want a clear target, aim for these 8 findings (and make sure **at least 3** are **High/Critical**):
1. Arbitrary file read (download): `/download?file=users.db` (see: [4.10](#410-arbitrary-file-read-downloadedfile))
2. SQL injection (login): `/login` (see: [4.4](#44-sql-injection-login-login))
3. Stored XSS (order notes): `/checkout` → `/order/<id>` (see: [3.7C](#c-stored-xss-order-notes))
4. IDOR (order receipts): `/order/<id>` (see: [3.7B](#b-idor-view-other-peoples-orders))
5. Broken access control (my orders): `/my-orders?user_id=...` (see: [3.7E](#e-broken-access-control--sql-injection-risk-my-orders))
6. Parameter tampering (checkout total): edit `total` field (see: [3.7D](#d-parameter-tampering-change-the-client-total))
7. Plaintext passwords (DB): `users.db` → `users` table (see: [4.3](#43-plaintext-passwords-in-usersdb))
8. Default credentials: `admin/admin123`, `test/test123`, `demo/demo123` (see: [4.1](#41-default-credentials-weak-authentication))

### Quick jump links (recommended order)
- [Setup](#1-setup-do-this-before-any-testing)
- [Checkout / Orders (new)](#37-checkout--orders-new-feature)
- [SQL Injection: login](#44-sql-injection-login-login)
- [IDOR: profile enumeration](#49-idor--profile-enumeration-profileintuserid)
- [Arbitrary file read: download](#410-arbitrary-file-read-downloadedfile)
- [Unrestricted file upload](#412-unrestricted-file-upload-upload-and-direct-serving-uploadsfilename)
- [Race condition: Slow Inventory](#31-race-condition-slow-inventory-buyintpizza_index)
- [Forever Log (privacy)](#33-privacy--indefinite-retention-forever-log-sensitive_access_logtxt)

---

## 1) Setup (Do this before any testing)

### 1.1 Start the app
- Run `python app.py`
- Confirm you can open:
  - `/` (home page)
  - `/api/docs` (if available)

### 1.2 Accounts to use
- Default accounts (known weak credentials):
  - `admin / admin123`
  - `test / test123`
  - `demo / demo123`

### 1.3 Beginner tool list
You can do almost everything with:
- A web browser
- Browser DevTools (Elements tab + Network tab)
- A text editor

Optional helpful tools:
- **DB Browser for SQLite** (view `users.db`)
- **curl** (simple HTTP requests)
- **Burp Suite Community** (intercept/modify requests)

### 1.4 Evidence standard (recommended)
For every finding, capture:
- **Evidence A:** exact URL / endpoint
- **Evidence B:** exact input/payload
- **Evidence C:** screenshot or output text
- **Evidence D:** explain impact in 1–2 sentences

---

## 2) Testing Methods (What “black/grey/white” means)

### 2.1 Blackbox (no code)
You behave like an attacker:
- click UI
- guess URLs
- change parameters
- look for errors/data leaks

### 2.2 Greybox (some information)
You use known endpoints/docs:
- use `/api/docs`
- use teacher-provided routes
- use a list of “things to try”

### 2.3 Whitebox (read the code)
You open `app.py` and templates to confirm:
- which endpoint exists
- which parameters are used
- whether values are validated/sanitized
- whether sensitive data is returned

---

## 3) Exam-gap Vulnerabilities (New Features 2026)

### 3.1 Race Condition: Slow Inventory (`/buy/<int:pizza_index>`)

#### Blackbox
1. Open 2 browser windows.
2. In both, prepare the URL `/buy/0`.
3. Trigger them very close together (press Enter quickly in both).
4. Observe messages like:
   - `Bought Pepperoni Pizza! Remaining: ...`
5. Refresh and re-run a few times.

**What to look for:**
- Inconsistent remaining stock results (timing dependent).

#### Greybox
- Open `pizza.json` and watch `qty` change after each purchase.

#### Whitebox
- In `app.py`, locate `buy_pizza()`.
- Confirm:
  - `time.sleep(2)` exists
  - stock is read then written without locking

**Evidence ideas:** screenshot of both windows showing successful buys + `pizza.json` showing unexpected qty.

---

### 3.2 Memory Leak / DoS: Memory Hog (`/view-item/<int:index>` and `/admin/memory-stats`)

#### Blackbox
1. Visit `/view-item/1`.
2. Refresh it 10–30 times.
3. Log in as admin.
4. Visit `/admin/memory-stats`.

**What to look for:**
- Memory burden increases (MB increases).
- App slows down over time.

#### Greybox
- Try from different browsers/devices to create multiple IP entries (if applicable).

#### Whitebox
- In `app.py`, find `MEMORY_STORE`.
- Confirm the route appends a 1MB string and never deletes it.

**Evidence ideas:** screenshot of `/admin/memory-stats` before/after refreshing.

---

### 3.3 Privacy / Indefinite Retention: Forever Log (`sensitive_access_log.txt`)

#### Blackbox
1. Log in and log out several times (different accounts if possible).
2. On the server machine, locate `sensitive_access_log.txt`.

**What to look for:**
- The file grows forever.
- Contains IP + username + timestamp.

#### Greybox
- Note whether the log is written for both:
  - default credential login
  - database user login

#### Whitebox
- In `app.py`, inspect the `/login` route.
- Confirm logging happens on both successful branches.

**Evidence ideas:** copy/paste a few lines of the log + screenshot (redact if required by teacher).

---

### 3.4 Accountability / No Audit Trail: Ghost Admin delete-user (`/admin/delete-user/<username>`)

#### Blackbox
1. Register a new user via `/register`.
2. Log in as `admin`.
3. Visit `/admin/delete-user/<that_username>`.
4. Attempt login as that user again.

**What to look for:**
- User is deleted.
- There is no audit log created about who performed deletion.

#### Greybox
- Check the server folder for any new log file. There should be none for this action.

#### Whitebox
- In `app.py`, inspect `ghost_delete()`.
- Confirm:
  - deletes from `users.db`
  - no print/logging of actor/time

**Evidence ideas:**
- Screenshot of delete response + failed login attempt.

---

### 3.5 TLS identity failure: Blind Webhook (`/admin/test-webhook?url=...`)

#### Blackbox
1. Log in as admin.
2. Visit: `/admin/test-webhook?url=https://expired.badssl.com/`

**What to look for:**
- It may succeed even though the certificate is invalid.

**Note:** this depends on outbound internet access.

#### Greybox
- Try different URLs (teacher-approved). Record results.

#### Whitebox
- In `app.py`, inspect `test_webhook()`.
- Confirm:
  - `ctx.verify_mode = ssl.CERT_NONE`
  - hostname checking is disabled

**Evidence ideas:** screenshot of success message when using an invalid certificate site.

---

### 3.6 Lab reset endpoint (`/admin/reset-lab`)
This is not a vulnerability by itself, but it supports classroom testing.

#### Blackbox
1. Log in as admin.
2. Trigger some state changes:
   - refresh `/view-item/1` many times
   - buy pizzas via `/buy/0`
3. Visit `/admin/reset-lab`.

**What to look for:**
- Memory stats returns to near baseline
- `pizza.json` `qty` returns to 5
- `sensitive_access_log.txt` is deleted

---

### 3.7 Checkout / Orders (New Feature)

This section tests the new checkout flow that creates persistent orders in `users.db`.

**Important:** You must be logged in to use `/checkout`.

#### Blackbox

##### A) Create an order (baseline)
1. Log in as `test / test123`.
2. Add 1–2 pizzas to cart.
3. Open `/cart`.
4. Click **Proceed to Checkout**.
5. Click **Place Order**.
6. You should be redirected to `/order/<number>`.

**Evidence ideas:** screenshot of the receipt page showing the order id.

##### B) IDOR: view other people’s orders
1. After placing an order, note your order URL (example: `/order/5`).
2. In the browser address bar, change it to nearby numbers:
   - `/order/1`, `/order/2`, `/order/3`...
3. If you can see details for an order you did not create, IDOR is confirmed.

**What to look for:** delivery address, totals, notes, username.

##### C) Stored XSS: order notes
1. Go to `/checkout`.
2. In the **Notes** field, enter:
   - `<script>alert('xss')</script>`
3. Place the order.
4. If an alert box appears when viewing `/order/<id>`, stored XSS is confirmed.

##### D) Parameter tampering: change the client total
1. Go to `/checkout`.
2. Open Browser DevTools.
3. In DevTools, go to the **Elements** tab.
4. Find the hidden input field named `total` (example: `id="client-total"`).
5. Change its value to `0.01`.
6. Click **Place Order**.
7. Open `/my-orders` and/or the receipt `/order/<id>`.

**What to look for:**
- Receipt shows **Client Total (submitted)** as the attacker value.
- Receipt also shows **Server Total (calculated)**.

##### E) Broken access control + SQL injection risk: `/my-orders`
1. Visit `/my-orders`.
2. Try changing the URL to:
   - `/my-orders?user_id=1`
   - `/my-orders?user_id=2`

**What to look for:**
- You can see orders that are not yours.

**Optional (teacher-approved):**
- Try an SQLi-style payload in `user_id` (URL encoded) and record any errors or unexpected results.

#### Greybox
1. Open `users.db` in DB Browser for SQLite.
2. Look for a table named `orders`.
3. Confirm your new order rows are being inserted.

#### Whitebox
1. In `app.py`, find:
   - `def checkout()`
   - `def my_orders()`
   - `def view_order(order_id)`
2. Confirm:
   - `/checkout` POST does not use CSRF tokens
   - client total comes from `request.form.get('total')`
   - `/my-orders` uses an f-string query with `user_id`
   - `templates/order.html` renders notes using `| safe`

---

## 4) Core Vulnerabilities (Original Project)

### 4.1 Default credentials (weak authentication)

#### Blackbox
1. Try logging in with:
   - `admin/admin123`, `test/test123`, `demo/demo123`
2. Record that admin access is possible with known defaults.

#### Blackbox (admin: excessive data exposure)
If you can log in as `admin`, you can test a privacy issue.
1. Log in as `admin/admin123`.
2. Visit `/` (home page).
3. Find the **Admin Security Snapshot** panel.
4. Look for:
   - recent login events
   - an “All orders (excessive data exposure)” list
5. Confirm it shows sensitive information (examples):
   - other users’ usernames/emails
   - delivery addresses
   - notes/coupon codes
   - raw cart JSON

**Evidence ideas:** screenshot of the admin panel showing multiple sensitive fields for an order + 1–2 sentence privacy impact.

#### Greybox
- Find references in docs/config such as `static/config/dev.config.json`.

#### Whitebox
- In `app.py`, locate `DEFAULT_CREDENTIALS`.

---

### 4.2 Weak session secret (`app.secret_key = "12345"`)

#### Blackbox
- You usually can’t prove this from the UI alone.

#### Greybox
- If given access, note whether the app is using cookie-based sessions.

#### Whitebox
- In `app.py`, find `app.secret_key`.

**Evidence idea:** screenshot/code reference showing the hardcoded secret.

---

### 4.3 Plaintext passwords in `users.db`

#### Blackbox
- Not always visible through UI.

#### Greybox
1. Open `users.db` with DB Browser for SQLite.
2. Look for the `users` table.

#### Whitebox
- In `app.py`, find where users are inserted and passwords are stored.

**Evidence idea:** screenshot of table showing readable passwords.

---

### 4.4 SQL Injection: login (`/login`)

#### Blackbox
1. Go to the login form.
2. Try a common payload (record exactly what you used), e.g.:
   - Username: `' OR '1'='1' -- `
   - Password: `anything`
3. Observe whether login bypass occurs.

**Note:** SQLi can be finicky depending on quoting/comments; keep trying with careful spacing.

#### Greybox
- Use DevTools Network tab to confirm the request is `POST /login`.

#### Whitebox
- In `app.py`, locate the login query built with an f-string.

---

### 4.5 SQL Injection: user lookup (`/user/<username>`)

#### Blackbox
1. Visit `/user/admin`.
2. Try suspicious inputs (URL encoded) such as:
   - `/user/'%20OR%20'1'%3D'1`
3. Observe errors/data leakage.

#### Greybox
- Use `/api/docs` if it lists this route.

#### Whitebox
- In `app.py`, find the `get_user()` query string interpolation.

---

### 4.6 SQL Injection: password reset update (`/password-reset`)

#### Blackbox
1. Open `/forgot-password` and request a reset for a known username.
2. Follow the provided reset link.
3. Attempt to reset passwords.

**What to look for:**
- Weak/invalid token logic
- Potential injection behaviors (careful recording)

#### Greybox
- Use DevTools to capture request body.

#### Whitebox
- In `app.py`, find `password_reset()` and confirm it builds an `UPDATE` query with f-string.

---

### 4.7 Broken password reset token validation (`/password-reset`)

#### Blackbox
1. Visit `/password-reset?username=admin&token=anything`.
2. Try setting a new password.

**What to look for:**
- Token not meaningfully validated.

#### Whitebox
- Confirm there is no real token store/check.

---

### 4.8 Legacy reset crash (`/reset` uses undefined `reset_tokens`)

#### Blackbox
1. Visit `/reset`.
2. Submit the form.

**What to look for:**
- 500 error / stack trace.

#### Whitebox
- In `app.py`, confirm `reset_tokens` is never defined.

---

### 4.9 IDOR / profile enumeration (`/profile/<int:user_id>`)

#### Blackbox
1. Visit `/profile/1`, then `/profile/2`, etc.
2. Observe whether you can see other users’ sensitive data.

**Tip:** If profiles are missing, first populate one:
- Log in, then visit `/create_profile` and submit once.

#### Whitebox
- Confirm the route has no auth checks and returns sensitive fields.

---

### 4.10 Arbitrary file read: `/download?file=...`

#### Blackbox
1. Visit `/download?file=app.py`.
2. Visit `/download?file=users.db`.

**What to look for:**
- File contents returned directly.

#### Whitebox
- Confirm it passes attacker-controlled input to `send_file()` (or previously `open()`).

---

### 4.11 Arbitrary file read + system info leak: `/debug/<path>`

#### Blackbox
1. Visit `/debug/app.py`.
2. Observe: code + system info (OS, env, cwd).

#### Whitebox
- Confirm it returns environment variables and reads arbitrary paths.

---

### 4.12 Unrestricted file upload: `/upload` and direct serving `/uploads/<filename>`

#### Blackbox
1. Visit `/upload`.
2. Upload a harmless file (e.g., a `.txt`).
3. Access it at `/uploads/<filename>`.

**Example:** If you know a filename already exists on the server, try:
- `/uploads/Perfect-Pizza-Cookbook.pdf`

**What to look for:**
- Upload allowed without restriction.
- Uploaded file is served back.

#### Whitebox
- Confirm it uses `file.filename` directly and saves into `./uploads/`.

---

### 4.13 Missing CSRF protections (forms + AJAX)

#### Blackbox
- Hard to fully exploit without writing an attacker page, but you can still **prove absence**.

#### Greybox
1. Open the HTML source of:
   - `/` (login form)
   - `/register`
   - `/admin` (after admin login)
2. Confirm there is **no CSRF token input**.

#### Whitebox
- Inspect templates in `templates/` and confirm no CSRF token exists.

---

### 4.14 Permissive CORS (`origins: "*"`)

#### Blackbox
- Not obvious via UI.

#### Greybox
- Use browser DevTools response headers (Network tab) and look for:
  - `Access-Control-Allow-Origin: *`

#### Whitebox
- In `app.py`, find `CORS(app, resources={r"/*": {"origins": "*"}})`.

---

### 4.15 Client-side injection risk: cart confirm dialog (`templates/cart.html`)

#### Blackbox
- Add items to cart and observe JS behaviors.

#### Greybox
- Inspect the cart page JS in the browser (View Source).

#### Whitebox
- Open `templates/cart.html` and find `confirm('Remove ' + itemName + ...)`.

---

### 4.16 Exposed dev config secrets (`static/config/dev.config.json`)

#### Blackbox
1. Visit `/static/config/dev.config.json`.

**What to look for:**
- API keys, credentials, or sensitive info exposed.

#### Whitebox
- Open the JSON file and record findings.

---

## 5) Final Checklist (fill this in)

Use this section as your assessment log. Add screenshots/links in your report.

### 5.1 Exam-gap vulnerabilities (new)
- [ ] Tested **Race Condition** `/buy/<index>`
  - Evidence URL(s):
  - Evidence screenshot/file:
  - Notes:
- [ ] Tested **Memory Hog** `/view-item/<index>`
  - Evidence URL(s):
  - Evidence screenshot/file:
  - Notes:
- [ ] Tested **Memory Stats** `/admin/memory-stats`
  - Evidence URL(s):
  - Evidence screenshot/file:
  - Notes:
- [ ] Tested **Forever Log** `sensitive_access_log.txt`
  - Evidence file snippet:
  - Notes:
- [ ] Tested **Ghost Admin delete-user** `/admin/delete-user/<username>`
  - Evidence URL(s):
  - Evidence screenshot/file:
  - Notes:
- [ ] Tested **Blind Webhook** `/admin/test-webhook?url=...`
  - Evidence URL(s):
  - Notes (internet available? yes/no):
- [ ] Tested **Reset Lab** `/admin/reset-lab`
  - Evidence:
  - Notes:

- [ ] Tested **Checkout: IDOR** `/order/<id>`
  - Evidence URL(s):
  - Notes:
- [ ] Tested **Checkout: Stored XSS** (order notes)
  - Payload used:
  - Evidence:
- [ ] Tested **Checkout: Client Total Tampering** (`total` field)
  - Evidence:
  - Notes:
- [ ] Tested **My Orders: Broken Access Control** (`/my-orders?user_id=...`)
  - Evidence:
  - Notes:
- [ ] Tested **My Orders: SQL Injection Risk** (optional, teacher-approved)
  - Payload used:
  - Evidence:
  - Notes:

### 5.2 Core vulnerabilities (original)
- [ ] Default credentials work (admin/test/demo)
  - Evidence:
- [ ] Weak `app.secret_key` (whitebox)
  - Evidence:
- [ ] Plaintext passwords in `users.db` (grey/whitebox)
  - Evidence:
- [ ] SQL Injection in `/login`
  - Payload used:
  - Evidence:
- [ ] SQL Injection in `/user/<username>`
  - Payload used:
  - Evidence:
- [ ] SQL Injection in `/password-reset`
  - Payload used:
  - Evidence:
- [ ] Broken token validation in `/password-reset`
  - Evidence:
- [ ] Legacy reset crash `/reset`
  - Evidence:
- [ ] IDOR profile enumeration `/profile/<id>`
  - Evidence:
- [ ] Arbitrary file read `/download?file=...`
  - Evidence:
- [ ] Arbitrary file read + system info `/debug/<path>`
  - Evidence:
- [ ] Unrestricted upload `/upload` + served `/uploads/<file>`
  - Evidence:
- [ ] Missing CSRF tokens in forms/templates
  - Evidence:
- [ ] Permissive CORS `Access-Control-Allow-Origin: *`
  - Evidence:
- [ ] Cart JS client-side injection risk (`templates/cart.html`)
  - Evidence:
- [ ] Exposed static config `/static/config/dev.config.json`
  - Evidence:

### 5.3 Summary for your report
- Total vulnerabilities tested: ____
- Total vulnerabilities confirmed (with evidence): ____
- Highest severity confirmed: ____
- 3 most impactful findings:
  1.
  2.
  3.
