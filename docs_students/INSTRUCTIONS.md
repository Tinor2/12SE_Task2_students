# docs_students — INSTRUCTIONS

This folder contains the **essential documents students should use** to run the project and demonstrate security testing techniques (OWASP-style thinking).

These documents are designed to support:
- discovery and demonstration of vulnerabilities
- structured evidence collection
- beginner-friendly testing workflows

---

## Files in this folder

### `OVERVIEW.md`
- **What it is**: A map of the project (architecture, files, routes, major components).
- **Why it’s invaluable**:
  - Helps you understand what the app does before you start testing.
  - Supports **whitebox** work without giving away a full “answer key”.
  - Helps you plan your test approach (what to test first, where data lives).

### `TESTING.md`
- **What it is**: A beginner testing guide covering **blackbox**, **greybox**, and **whitebox** approaches.
- **Why it’s invaluable**:
  - Gives step-by-step instructions for testing each vulnerability.
  - Provides a final checklist so you can prove what you tested and what evidence you collected.
  - Includes a **Student Path (Minimum Required)** at the top so you don’t have to test everything.

---

## Recommended tools (what they do + how to use them)

You can complete the task with **just a web browser + screenshots**, but these tools make testing and evidence collection much easier.

### 1) Web browser + DevTools (Chrome / Edge / Firefox)
- **What it does:** Lets you inspect and modify HTML, view requests, and see errors.
- **How you use it in this project:**
  - Inspect requests to `/login`, `/checkout`, `/my-orders`
  - Edit page inputs (e.g. change hidden form fields for parameter tampering)
  - View console errors
- **How to open DevTools:** `F12` or `Ctrl+Shift+I`
- **Download:**
  - Chrome: https://www.google.com/chrome/
  - Edge: https://www.microsoft.com/edge
  - Firefox: https://www.mozilla.org/firefox/

### 2) DB Browser for SQLite
- **What it does:** Opens and views `.db` files (SQLite databases).
- **How you use it in this project:**
  - Open `users.db` and view tables like `users`, `profiles`, `orders`
  - Take screenshots of rows as evidence (e.g. plaintext passwords, order records)
- **Download:** https://sqlitebrowser.org/

### 3) Visual Studio Code (or another code editor)
- **What it does:** Lets you read/edit code and search the project.
- **How you use it in this project:**
  - Whitebox testing: read `app.py` and templates to confirm the cause of a vulnerability
  - Search for routes like `@app.route("/checkout")`
- **Download:** https://code.visualstudio.com/

### 4) Burp Suite Community (optional)
- **What it does:** Intercepts and edits HTTP requests (like a “man-in-the-middle” proxy).
- **How you use it in this project:**
  - Modify form fields in requests (parameter tampering)
  - Replay requests
  - Capture evidence of request/response
- **Download:** https://portswigger.net/burp/communitydownload

### 5) curl (optional)
- **What it does:** Sends HTTP requests from the terminal.
- **How you use it in this project:**
  - Quickly test endpoints without the browser
  - Save request/response output as evidence
- **Download:**
  - Windows (official): https://curl.se/windows/
  - Note: `curl` is included with many modern Windows builds.

---

## Student workflow (recommended)

### Quick start (2 minutes)
1. Start the app: run `python app.py`
2. Open the site: `http://127.0.0.1:5000`
3. If you can see the home page and log in, you’re ready to test.

**Tip:** Some tests require browser Developer Tools (DevTools), e.g. parameter tampering.
- Open DevTools: `F12` or `Ctrl+Shift+I` (Chrome/Edge/Firefox)

1. Read `OVERVIEW.md` to understand the app.
2. Follow `TESTING.md` to systematically test and collect evidence.
   - Example of a good write-up: `docs_students/SAMPLE/SAMPLE_REPORT_TEMPLATE.md`
3. Write your report using your evidence (URLs, payloads, screenshots, outputs).
