# VIP Pizza: Vulnerability Cheat Sheet (Quick Start)

**For Students:** Use this guide if you are stuck or need a quick reference for the "Minimum 8" vulnerabilities.
**Warning:** This document gives you the *steps*, but you must read `TESTING.md` to understand *why* these attacks work for your exam responses.

---

## Target 1: Arbitrary File Read (Critical)
**Method:** Blackbox (URL Manipulation)

### Part A: Stealing the Database
1.  **Visit:** `http://127.0.0.1:5000/download?file=users.db`
2.  **Look for:** The browser downloads `users.db` (or displays binary text/garbage).
3.  **Impact:** You now have the entire database of users.

### Part B: Stealing Source Code
1.  **Visit:** `http://127.0.0.1:5000/download?file=app.py`
2.  **Look for:** The Python source code displayed in the browser.
3.  **Bonus:** Search the code for `app.secret_key` to find the session secret (`"12345"`).

---

## Target 2: SQL Injection (Login Bypass) (Critical)
**Method:** Blackbox (Form Manipulation)

Bypass the login screen without knowing the password.

1.  **Go to:** `http://127.0.0.1:5000/login`
2.  **Enter Credentials:**
    *   **Username (Classic Payload):** `' OR '1'='1' --`
    *   **Username (Admin Payload):** `admin' --`
    *   **Password:** `anything`
3.  **Click:** Login

**Success:** You should be logged in as `admin`. Check the "Welcome, admin" message.

---

## Target 3: Stored XSS (Order Notes) (High)
**Method:** Blackbox (Input Fuzzing)

Leave a "trap" in the database that executes code in other users' browsers.

1.  **Login:** Use the attack from Target 2.
2.  **Go to:** `/checkout` (add an item to cart if empty).
3.  **In "Notes" field, paste:**
    ```html
    <script>alert('xss - hacked!')</script>
    ```
4.  **Click:** "Place Order".

**Success:**
*   You are redirected to the receipt.
*   **The Trap:** A browser alert box saying "xss - hacked!" appears.
*   **Persistence:** Refresh the page to confirm it happens every time.

---

## Target 4: IDOR (Order Enumeration) (High)
**Method:** Blackbox (URL Manipulation)

View sensitive order details belonging to other people.

1.  **Place an order** (or use the one from Target 3).
2.  **Check URL:** Note the Order ID (e.g., `/order/5`).
3.  **The Attack:** Change the number to `1` (or `2`, `3`, etc.).
    *   Example: `http://127.0.0.1:5000/order/1`

**Success:**
*   **Success:** The page loads successfully (no 403 Forbidden).
*   **The Breach:** You can see the address, items, and notes for a completely different order.

---

## Target 5: Broken Access Control (My Orders)
**Method:** Blackbox (Parameter Tampering)

Steal another user's entire order history.

1.  **Go to:** `http://127.0.0.1:5000/my-orders`
2.  **The Attack:** Add the `user_id` query parameter to the URL.
    *   **Change URL to:** `http://127.0.0.1:5000/my-orders?user_id=1`
    *   (Try `user_id=2` or `user_id=3` if you are already admin).

**Success:**
*   Accidentally viewing the order history for User #1, #2, etc.
*   The page does not check if the logged-in user matches the requested `user_id`.

---

## Target 6: Parameter Tampering (Price Manipulation) (Medium)
**Method:** Greybox (Browser DevTools)

Buy a pizza for $0.01 by modifying hidden form fields.

1.  **Go to:** `/checkout` (ensure you have items in cart).
2.  **Open DevTools:** Press `F12`.
3.  **The Hack:**
    *   Inspect the **Total** price text.
    *   Find the hidden input nearby: `<input type="hidden" name="total" value="...">`.
    *   Double-click the value and change it to `0.01`.
    *   Press **Enter**.
4.  **Click:** "Place Order".

**Success:**
*   **Receipt Check:** Look for **"Client Total (submitted): $0.01"**.
*   The server accepted your price because it blindly trusted the hidden field.

---

## Target 7: Plaintext Passwords (High)
**Method:** Greybox (Local File Inspection)

Confirm that passwords are stored without encryption.

1.  **Open:** DB Browser for SQLite.
2.  **Load:** `users.db` (in the project folder).
3.  **Browse:** Go to "Browse Data" tab and select `users` table.

**Success:**
*   **The Fail:** You can read the passwords column directly (e.g., `admin123`).
*   In a secure app, this would be random characters (hashed).

---

## Target 8: Default Credentials (High)
**Method:** Blackbox (Auth Guessing)

Gain access using known or weak default accounts.

1.  **Go to:** `http://127.0.0.1:5000/login`
2.  **Try:**
    *   `admin` / `admin123`
    *   `test` / `test123`
    *   `demo` / `demo123`

**Success:**
*   You are logged in successfully.
*   **Why it handles:** The developer left "test" accounts in the production system.
