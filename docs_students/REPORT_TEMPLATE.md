# REPORT_TEMPLATE.md — VIP Pizza Security Testing Report (Student)

Use this template to write your security testing report for the VIP Pizza project.

You may submit a completed version of this template as your final Security Report (export to **Word or PDF**).

**Assumed local URL:** `http://127.0.0.1:5000`

---

## 1) What format is the report?

Submit **one document** (Word or PDF) containing:
- **Title page / cover section**
- **Table of contents (optional but recommended if long)**
- **Findings section** (your vulnerabilities, each in the format below)
- **Conclusion / summary**
- **Appendix (optional)** (extra screenshots, raw outputs, copied requests)

### Recommended structure
- **Part A: Executive summary** (short)
- **Part B: Vulnerability findings (8 total minimum)**
- **Part C: Recommendations** (brief)
- **Part D: Appendix**

---

## 2) How many screenshots do I need?

Minimum evidence per vulnerability:
- **2 screenshots per vulnerability** (recommended)
  - **Screenshot 1 (setup/input):** shows the URL and your payload/input
  - **Screenshot 2 (result):** shows the effect (data leak, login bypass, alert box, changed totals, etc.)

So if you test **8 vulnerabilities**, aim for:
- **At least 16 screenshots** total.

If a vulnerability is best proven by text output (e.g., a log file snippet), you can replace one screenshot with:
- copied output text (still include the URL/steps)

---

## 3) How do I structure severity and impact?

For each vulnerability, you must include:
- **Severity** (Critical / High / Medium / Low)
- **CIA impact** (Confidentiality, Integrity, Availability)
- **1–2 sentence impact statement** that explains the real-world harm

Use the **Severity Guide** at the end of this file.

---

# Part A — Executive Summary (5–10 lines)

## Summary
- **App tested:** VIP Pizza (local Flask app)
- **Date tested:** 
- **Tester name:** 
- **Total vulnerabilities tested:** 8 (minimum)
- **Total confirmed (with evidence):** 
- **Highest severity confirmed:** 

## Most impactful findings (top 3)
1.
2.
3.

---

# Part B — Vulnerability Findings (Repeat this section for each finding)

> Copy/paste this entire section for each vulnerability.

## Finding #__ — [Vulnerability Name]

### 1) Vulnerability name
Example: **IDOR (Broken Access Control) — Order Receipt Enumeration**

### 2) Category (OWASP-style)
Example:
- Broken Access Control
- Injection (SQLi)
- Sensitive Data Exposure
- Security Misconfiguration
- Cross-Site Scripting (XSS)
 
(OWASP Top 10 (2021) examples you may reference: **A01: Broken Access Control**, **A04: Insecure Design**.)

### 3) Severity
Choose one: **Critical / High / Medium / Low**

### 4) Where is it? (endpoint + feature)
- **URL/Endpoint:**
- **HTTP method:** GET / POST
- **Parameters used (if any):**

### 5) Preconditions
What must be true before it works?
- logged in? which account?
- must place an order first?
- must be admin?

### 6) Steps to reproduce (numbered)
Write steps so another student can reproduce it.
1.
2.
3.

### 7) Payload / input used
Write exactly what you typed or changed.
- Payload:
- Location used (form field name, URL parameter, etc.):

### 8) Evidence (screenshots/outputs)
- **Evidence A (screenshot):** shows URL + payload/input
- **Evidence B (screenshot):** shows outcome
- **Evidence C (optional):** copied output / log snippet / DB row

### 9) CIA impact (tick all that apply)
- **Confidentiality:** [ ] Yes  [ ] No
- **Integrity:** [ ] Yes  [ ] No
- **Availability:** [ ] Yes  [ ] No

### 10) Impact statement (1–2 sentences)
Example format:
- “This allows an attacker to view other users’ delivery addresses and notes by changing the order id in the URL, causing a confidentiality breach.”

### 11) Recommendation / fix (brief)
Keep it short and realistic.

**Your fix must clearly distinguish BOTH:**

#### 11a) Input validation (reject/allow rules)
- What checks stop bad input getting accepted? (type, length, allowlist, range, format)

#### 11b) Data sanitisation (make data safe to store/render)
- If unsafe characters/data exist, how will you make it safe to store or show? (escape/encode/filter)

#### 11c) Access control / auth checks (if relevant)
- If this is an access issue (e.g., IDOR/admin-only), what server-side permission/ownership checks would you add?

Examples:
- “Enforce ownership checks on `/order/<id>` so users can only access their own orders.”
- “Use parameterized SQL queries instead of string formatting.”
- “Escape untrusted input and remove `| safe` when rendering notes.”
- “Add CSRF tokens to state-changing forms.”

### 12) Extra notes (optional)
- Any edge cases? any errors?

---

# Part C — Recommendations Summary (short)

List 5–10 bullet points summarising the most important fixes.
- 
- 
- 

---

# Part D — Appendix (optional)

Include any extra evidence here:
- copied HTTP requests
- extra screenshots
- DB screenshots (tables/rows)

---

# Severity Guide (1 page)

Use this quick rubric to decide severity consistently.

## Critical
Use **Critical** if the vulnerability allows one of the following:
- **Authentication bypass / account takeover** (log in as another user or reset passwords)
- **Remote code execution** or **arbitrary file read** of highly sensitive files (e.g., `users.db`, system files)
- **SQL injection** that can dump many records or change data
- **Exposure of secrets** that leads to full compromise (e.g., admin credentials, session forgery)

## High
Use **High** if the vulnerability allows:
- **Access to other users’ sensitive data** (IDOR of profiles/orders)
- **Stored XSS** (script runs for future viewers)
- **CSRF** that performs important actions as a logged-in victim (place orders, change password)
- **Unrestricted upload** that could lead to malicious content being served to users

## Medium
Use **Medium** if the vulnerability allows:
- **Tampering with business logic** but with limited harm (e.g., client total manipulation while server total still exists)
- **Information disclosure** that is helpful but not immediately catastrophic (stack traces, version leaks)
- **Weak authorization checks** that expose limited info (or need special conditions)

## Low
Use **Low** if the vulnerability:
- is mostly a best-practice issue with low direct impact
- requires many unlikely steps
- demonstrates risky patterns without a clear exploit in this app

## Quick CIA mapping hints
- **Confidentiality**: data is exposed (profiles, orders, passwords, system info)
- **Integrity**: data can be changed/tampered (prices, passwords, DB updates)
- **Availability**: app can be slowed/crashed (DoS, memory hog, resource exhaustion)

## Severity decision check (final)
Before finalising, ask:
1. What is the worst realistic harm?
2. How easy is it to exploit?
3. Does it affect many users or just one?
4. Is sensitive data involved?
