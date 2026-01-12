from flask import Flask, render_template, request, redirect, session, jsonify, url_for, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import flask
import json
import sqlite3
import os
import sys
import traceback
import time  
import ssl
import urllib.request
import urllib.parse

app = Flask(__name__)
app.secret_key = "12345"  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PIZZA_JSON_PATH = os.path.join(BASE_DIR, "pizza.json")
BACKUP_DIR = os.path.join(BASE_DIR, "static", "backup")
USERS_DB_PATH = os.path.join(BASE_DIR, "users.db")


CORS(app, resources={r"/*": {"origins": "*"}})


DEFAULT_CREDENTIALS = {
    "admin": "admin123",  
    "test": "test123",    
    "demo": "demo123"     
}

MEMORY_STORE = {}

# Initialise database
def init_db():
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    
    # Create users table with email field (if not exists)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT UNIQUE
        )
    """)
    
    # Add profiles table with sensitive information
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            credit_card TEXT,
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            user_id INTEGER,
            username TEXT,
            delivery_address TEXT,
            notes TEXT,
            coupon_code TEXT,
            client_total REAL,
            server_total REAL,
            cart_json TEXT,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Add default users if they don't exist
    for username, password in DEFAULT_CREDENTIALS.items():
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            # Add email for each default user
            email = f"{username}@example.com"
            c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                     (username, password, email))
    
    conn.commit()
    conn.close()


def _get_current_user_id():
    if not session.get('user'):
        return None
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (session.get('user'),))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def _calculate_cart_total(cart_items):
    total = 0.0
    for item in cart_items:
        try:
            total += float(item.get('price', 0)) * int(item.get('quantity', 0))
        except Exception:
            pass
    return round(total, 2)

# Load pizza data
def load_pizzas():
    try:
        with open(PIZZA_JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save pizza data
def save_pizzas(pizzas):
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Save to both main file and backup
    with open(PIZZA_JSON_PATH, "w") as f:
        json.dump(pizzas, f, indent=4)
    
    with open(os.path.join(BACKUP_DIR, "pizza.json.bak"), "w") as f:
        json.dump(pizzas, f, indent=4)

# Vulnerable download route for directory traversal
@app.route("/download")
def download():
    filename = request.args.get("file")
    try:
        return send_file(filename)
    except Exception as e:
        return str(e)

# Verbose error route
@app.route("/error_test")
def error_test():
    username = request.args.get("username")
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    c.execute(query)  
    return f"Executed query: {query}"

# Unrestricted file upload
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        file.save(f"./uploads/{file.filename}")
        return "File uploaded!"
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
    '''

@app.route("/")
def index():
    pizzas = load_pizzas()
    last_order = None
    last_order_items = []
    recent_login_events = []
    tampered_orders_count = 0
    recent_tampered_orders = []
    recent_all_orders_excessive = []

    if session.get('user'):
        user_id = _get_current_user_id()
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            SELECT id, created_at, status, cart_json, client_total, server_total
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )
        row = c.fetchone()
        conn.close()

        if row:
            last_order = {
                'id': row[0],
                'created_at': row[1],
                'status': row[2],
                'cart_json': row[3],
                'client_total': row[4],
                'server_total': row[5]
            }
            try:
                last_order_items = json.loads(last_order.get('cart_json') or '[]')
            except Exception:
                last_order_items = []

        if session.get('user') == 'admin':
            try:
                with open(os.path.join(BASE_DIR, "sensitive_access_log.txt"), "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    recent_login_events = [line.strip() for line in lines[-10:] if line.strip()]
            except Exception:
                recent_login_events = []

            try:
                conn = sqlite3.connect(USERS_DB_PATH)
                c = conn.cursor()
                c.execute(
                    """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE client_total != server_total
                    """
                )
                tampered_orders_count = int((c.fetchone() or [0])[0])

                c.execute(
                    """
                    SELECT id, created_at, username, client_total, server_total
                    FROM orders
                    WHERE client_total != server_total
                    ORDER BY id DESC
                    LIMIT 5
                    """
                )
                recent_tampered_orders = c.fetchall()
                conn.close()
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                tampered_orders_count = 0
                recent_tampered_orders = []

            try:
                conn = sqlite3.connect(USERS_DB_PATH)
                c = conn.cursor()
                c.execute(
                    """
                    SELECT
                        o.id,
                        o.created_at,
                        o.user_id,
                        o.username,
                        u.email,
                        p.full_name,
                        p.phone,
                        p.credit_card,
                        p.address,
                        o.delivery_address,
                        o.notes,
                        o.coupon_code,
                        o.client_total,
                        o.server_total,
                        o.status,
                        o.cart_json
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    LEFT JOIN profiles p ON o.user_id = p.user_id
                    ORDER BY o.id DESC
                    LIMIT 10
                    """
                )
                recent_all_orders_excessive = c.fetchall()
                conn.close()
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                recent_all_orders_excessive = []

    return render_template(
        "index.html",
        pizzas=pizzas,
        last_order=last_order,
        last_order_items=last_order_items,
        recent_login_events=recent_login_events,
        tampered_orders_count=tampered_orders_count,
        recent_tampered_orders=recent_tampered_orders,
        recent_all_orders_excessive=recent_all_orders_excessive,
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get('next')
    if next_url:
        parsed = urllib.parse.urlparse(next_url)
        if parsed.scheme or parsed.netloc:
            next_url = None

    def _post_login_redirect():
        if next_url:
            return redirect(next_url)
        if session.get('user') == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('index'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Try default credentials first
        if username in DEFAULT_CREDENTIALS and DEFAULT_CREDENTIALS[username] == password:
            session['user'] = username
            with open("sensitive_access_log.txt", "a") as f:
                f.write(f"{datetime.now()} | IP: {request.remote_addr} | User: {session.get('user')}\n")
            return _post_login_redirect()

        # If not default, check database
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]  
            with open("sensitive_access_log.txt", "a") as f:
                f.write(f"{datetime.now()} | IP: {request.remote_addr} | User: {session.get('user')}\n")
            return _post_login_redirect()
        else:
            return "Invalid credentials! <a href='/'>Try again</a>"

    return render_template("login.html", next=next_url)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form["username"]
        token = request.form["token"]
        if reset_tokens.get(username) == token:
            return "Password reset successful!"
    return render_template("reset.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    pizza_name = request.form.get("pizza_name")
    pizzas = load_pizzas()
    pizza = next((p for p in pizzas if p["name"] == pizza_name), None)
    
    if pizza:
        cart_item = {
            "name": pizza["name"],
            "description": pizza["description"],
            "image": pizza["image"],
            "price": pizza["price"],
            "quantity": 1
        }
        
        if 'cart' not in session:
            session['cart'] = []
        
        existing_item = next((item for item in session['cart'] if item["name"] == pizza_name), None)
        if existing_item:
            existing_item["quantity"] += 1
        else:
            session['cart'].append(cart_item)
        
        session.modified = True
        return redirect(url_for('cart'))
    
    return "Pizza not found!", 404

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session or session["user"] != "admin":
        return "Access Denied! <a href='/'>Go back</a>"

    pizzas = load_pizzas()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form.get("price", 0))  
        image_file = request.files.get("image")

        if image_file:
            image_filename = f"static/images/{image_file.filename}"
            image_file.save(image_filename)
        else:
            image_filename = None

        if "update" in request.form:
            pizza_id = int(request.form["update"])
            pizzas[pizza_id]["name"] = name
            pizzas[pizza_id]["description"] = description
            pizzas[pizza_id]["price"] = price  
            if image_filename:
                pizzas[pizza_id]["image"] = image_filename
        elif "delete" in request.form:
            pizza_id = int(request.form["delete"])
            if 0 <= pizza_id < len(pizzas):  
                pizzas.pop(pizza_id)
                save_pizzas(pizzas)
                return redirect("/admin")
        else:
            pizzas.append({
                "name": name,
                "description": description,
                "price": price,  
                "image": image_filename
            })

        save_pizzas(pizzas)
        return redirect("/admin")

    return render_template("admin.html", pizzas=pizzas)


@app.route("/cart")
def cart():
    cart_items = session.get('cart', [])
    return render_template("cart.html", cart_items=cart_items)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not session.get('user'):
        return redirect(url_for('login', next=request.path))

    cart_items = session.get('cart', [])
    server_total = _calculate_cart_total(cart_items)

    if request.method == "POST":
        delivery_address = request.form.get('delivery_address', '')
        notes = request.form.get('notes', '')
        coupon_code = request.form.get('coupon_code', '')

        client_total_raw = request.form.get('total', '0')
        try:
            client_total = float(client_total_raw)
        except Exception:
            client_total = 0.0

        user_id = _get_current_user_id()
        created_at = datetime.now().isoformat()
        status = "PLACED"
        cart_json = json.dumps(cart_items)

        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO orders
            (created_at, user_id, username, delivery_address, notes, coupon_code, client_total, server_total, cart_json, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, user_id, session.get('user'), delivery_address, notes, coupon_code, client_total, server_total, cart_json, status)
        )
        order_id = c.lastrowid
        conn.commit()
        conn.close()

        session['cart'] = []
        session.modified = True

        return redirect(url_for('view_order', order_id=order_id))

    return render_template("checkout.html", cart_items=cart_items, server_total=server_total)


@app.route("/my-orders")
def my_orders():
    if not session.get('user'):
        return redirect(url_for('index'))

    user_id = request.args.get('user_id')
    if not user_id:
        user_id = _get_current_user_id()

    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    query = f"SELECT id, created_at, username, client_total, server_total, status FROM orders WHERE user_id = {user_id} ORDER BY id DESC"
    c.execute(query)
    orders = c.fetchall()
    conn.close()

    return render_template("my_orders.html", orders=orders, executed_query=query)


@app.route("/order/<int:order_id>")
def view_order(order_id):
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, created_at, username, delivery_address, notes, coupon_code, client_total, server_total, cart_json, status
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    )
    order_row = c.fetchone()
    conn.close()

    if not order_row:
        return "Order not found", 404

    order = {
        'id': order_row[0],
        'created_at': order_row[1],
        'username': order_row[2],
        'delivery_address': order_row[3],
        'notes': order_row[4],
        'coupon_code': order_row[5],
        'client_total': order_row[6],
        'server_total': order_row[7],
        'cart_json': order_row[8],
        'status': order_row[9]
    }

    try:
        cart_items = json.loads(order.get('cart_json') or '[]')
    except Exception:
        cart_items = []

    return render_template("order.html", order=order, cart_items=cart_items)

@app.route("/view-item/<int:index>")
def view_item(index):
    user_ip = request.remote_addr
    if user_ip not in MEMORY_STORE:
        MEMORY_STORE[user_ip] = []
    MEMORY_STORE[user_ip].append("A" * 1000000)
    return f"Viewed item {index}. Visit /admin/memory-stats to view server memory burden."

@app.route("/admin/memory-stats")
def memory_stats():
    if session.get('user') != 'admin':
        return "Unauthorized"
    size = sys.getsizeof(str(MEMORY_STORE))
    size_mb = round(size / (1024 * 1024), 2)
    return f"Server Memory Burden: {size_mb} MB across {len(MEMORY_STORE)} IP addresses."

@app.route('/buy/<int:pizza_index>')
def buy_pizza(pizza_index):
    pizzas = load_pizzas()
    if pizza_index < 0 or pizza_index >= len(pizzas):
        return "Invalid pizza selection"
    target_pizza = pizzas[pizza_index]
    current_qty = target_pizza.get('qty', 5)
    if current_qty > 0:
        time.sleep(2)
        target_pizza['qty'] = current_qty - 1
        save_pizzas(pizzas)
        return f"Bought {target_pizza['name']}! Remaining: {target_pizza['qty']}"
    return "Sold out!"

@app.route("/update_cart", methods=["POST"])
def update_cart():
    item_name = request.form.get("item")
    quantity = request.form.get("quantity")
    
    if 'cart' in session:
        for item in session['cart']:
            if item["name"] == item_name:
                item["quantity"] = int(quantity)
                session.modified = True
                break
    
    return "Updated", 200

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    item_name = request.form.get("item")
    
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item["name"] != item_name]
        session.modified = True
    
    return "Removed", 200

@app.route("/api/docs")
def api_docs():
    return render_template("api_docs.html")

@app.route('/admin/delete-user/<username>')
def ghost_delete(username):
    if session.get('user') == 'admin':
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return f"User '{username}' silently deleted. No logs created."
    return "Unauthorized"

@app.route('/admin/test-webhook')
def test_webhook():
    if session.get('user') != 'admin':
        return "Unauthorized"
    target = request.args.get('url', 'https://example.com')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        urllib.request.urlopen(target, context=ctx)
        return f"Successfully connected to {target} (Insecurely!)"
    except Exception as e:
        return str(e)

@app.route("/user/<username>")
def get_user(username):
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}'"
        c.execute(query)  
        user = c.fetchone()
        conn.close()
        
        if user:
            return f"Found user: {user}"
        return "User not found"
    except Exception as e:
        return f"""
            <h2>Database Error</h2>
            <p>Query: {query}</p>
            <p>Error: {str(e)}</p>
        """, 500

@app.route("/debug/<path:file_path>")
def debug_file(file_path):
    try:
        import platform
        system_info = {
            'os': platform.system(),
            'version': platform.version(),
            'python': sys.version,
            'user': os.getlogin(),
            'cwd': os.getcwd(),
            'env': dict(os.environ)
        }
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        return f"""
            <h2>File Content</h2>
            <pre>{content}</pre>
            <h3>System Information</h3>
            <pre>{json.dumps(system_info, indent=2)}</pre>
        """
    except Exception as e:
        return f"""
            <h2>Error Reading File</h2>
            <p>Path: {file_path}</p>
            <p>Error: {str(e)}</p>
            <h3>System Information</h3>
            <pre>{json.dumps(system_info, indent=2)}</pre>
        """, 500

@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_details = {
        'error_type': str(type(error).__name__),
        'error_message': str(error),
        'stack_trace': traceback.format_exc(),
        'python_version': sys.version,
        'flask_version': flask.__version__,
        'debug_mode': app.debug,
        'database_path': 'users.db'
    }
    return f"""
        <h1>Internal Server Error</h1>
        <pre>
        Error Type: {error_details['error_type']}
        Message: {error_details['error_message']}
        
        Full Stack Trace:
        {error_details['stack_trace']}
        
        System Information:
        Python Version: {error_details['python_version']}
        Flask Version: {error_details['flask_version']}
        Debug Mode: {error_details['debug_mode']}
        Database: {error_details['database_path']}
        </pre>
    """, 500

@app.errorhandler(404)
def page_not_found(e):
    error_message = """
    Page not found. Please check our documentation for valid URLs.
    """
    return error_message, 404

@app.route("/profile/<int:user_id>")
def view_profile(user_id):
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT u.username, p.* 
        FROM users u 
        LEFT JOIN profiles p ON u.id = p.user_id 
        WHERE u.id = ?
    """, (user_id,))
    
    data = c.fetchone()
    conn.close()
    
    if data:
        return f"""
            <h2>User Profile</h2>
            <pre>
            Username: {data[0]}
            Full Name: {data[2]}
            Email: {data[3]}
            Phone: {data[4]}
            Credit Card: {data[5]}
            Address: {data[6]}
            </pre>
            <p><a href="/profile/{user_id - 1}">Previous User</a> | 
               <a href="/profile/{user_id + 1}">Next User</a></p>
        """
    return "Profile not found", 404

@app.route("/create_profile", methods=["GET", "POST"])
def create_profile():
    if request.method == "POST":
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (session.get('user'),))
        user = c.fetchone()
        
        if user:
            c.execute("""
                INSERT OR REPLACE INTO profiles 
                (user_id, full_name, email, phone, credit_card, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user[0],
                request.form.get('full_name', 'John Doe'),
                request.form.get('email', 'john@example.com'),
                request.form.get('phone', '123-456-7890'),
                request.form.get('credit_card', '4111-1111-1111-1111'),
                request.form.get('address', '123 Main St, City, Country')
            ))
            conn.commit()
            conn.close()
            return redirect(f"/profile/{user[0]}")
            
    return """
        <h2>Create Profile</h2>
        <form method="POST">
            <p>Full Name: <input name="full_name" value="John Doe"></p>
            <p>Email: <input name="email" value="john@example.com"></p>
            <p>Phone: <input name="phone" value="123-456-7890"></p>
            <p>Credit Card: <input name="credit_card" value="4111-1111-1111-1111"></p>
            <p>Address: <input name="address" value="123 Main St, City, Country"></p>
            <p><input type="submit" value="Create Profile"></p>
        </form>
    """

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        
        timestamp = int(time.time())
        token = f"{username}_{timestamp}"  
        
        reset_link = f"http://127.0.0.1:5000/password-reset?username={username}&token={token}"
        
        return f"""
            <h2>Password Reset Requested</h2>
            <p>A password reset link has been generated.</p>
            <p>Normally this would be emailed, but for testing, here's the link:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p><a href="/">Back to login</a></p>
        """
    
    return """
        <h2>Forgot Password</h2>
        <form method="POST">
            <p>Username: <input type="text" name="username" required></p>
            <p><input type="submit" value="Reset Password"></p>
        </form>
    """

@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    username = request.args.get("username") or request.form.get("username")
    token = request.args.get("token") or request.form.get("token")
    
    if not username or not token:
        return "Missing username or token", 400
    
    if request.method == "POST":
        new_password = request.form.get("new_password")
        if not new_password:
            return "Missing new password", 400
        
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        query = f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
        c.execute(query)
        conn.commit()
        conn.close()
        
        return """
            <h2>Password Updated</h2>
            <p>Your password has been updated successfully.</p>
            <p><a href="/">Login with new password</a></p>
        """
    
    return f"""
        <h2>Reset Password</h2>
        <form method="POST">
            <input type="hidden" name="username" value="{username}">
            <input type="hidden" name="token" value="{token}">
            <p>New Password: <input type="password" name="new_password" required></p>
            <p><input type="submit" value="Update Password"></p>
        </form>
    """

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/admin/reset-lab')
def reset_lab():
    if session.get('user') != 'admin':
        return "Unauthorized"

    global MEMORY_STORE
    MEMORY_STORE = {}

    pizzas = load_pizzas()
    for p in pizzas:
        p['qty'] = 5
    save_pizzas(pizzas)

    if os.path.exists('sensitive_access_log.txt'):
        os.remove('sensitive_access_log.txt')

    return "Lab Reset Complete: Memory cleared, Stock restored, Logs deleted."

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.mkdir("uploads")
    
    if not os.path.exists(PIZZA_JSON_PATH):
        save_pizzas([])  
    
    init_db()
    app.run(debug=True)
