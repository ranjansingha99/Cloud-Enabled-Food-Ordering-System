from flask import Flask, render_template, request, redirect, url_for, session
import pymssql

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Function to create the database connection
def get_db_connection():
    server = 'new-server-assign.database.windows.net'
    database = 'Ranjan_db_new'
    username = 'ranjan'
    password = '**********'

    conn = pymssql.connect(server=server, user=username, password=password, database=database)
    return conn

# Function to create the Orders table if it doesn't exist
def create_table():
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Check if the table exists
        cursor.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Orders'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Table does not exist, create it
            cursor.execute(
                '''
                CREATE TABLE Orders (
                    id INT PRIMARY KEY IDENTITY,
                    user_name NVARCHAR(255) NOT NULL,
                    food_name NVARCHAR(255) NOT NULL,
                    quantity INT,
                    delivered INT DEFAULT 0 CHECK (delivered IN (0, 1))
                )
                '''
            )

        connection.commit()

# Create the table when the application starts
create_table()

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == '12345':  # Replace 'your_password_here' with your actual password
            session['authenticated'] = True
            return redirect(url_for('restaurant'))
        else:
            error = "Invalid password. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('launch'))

@app.route('/')
def launch():
    return render_template('launch.html')

@app.route('/restaurant')
def restaurant():
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('login'))

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Orders")
        products = cursor.fetchall()
    return render_template('restaurant.html', products=products)

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/order_details')
def order_details():
    order_id = session.get('order_id')
    if order_id is None:
        return redirect(url_for('launch'))

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()

    return render_template('order_details.html', order=order)

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        user_name = request.form['user_name']
        food_name = request.form['food_name']
        quantity = request.form['quantity']
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Orders (user_name, food_name, quantity) VALUES (%s, %s, %s)", (user_name, food_name, quantity))
            connection.commit()

            # Retrieve the ID of the most recent order
            cursor.execute("SELECT TOP 1 id FROM Orders WHERE user_name = %s ORDER BY id DESC", (user_name,))
            order_id = cursor.fetchone()[0]

            # Store the order ID in the session
            session['order_id'] = order_id

    return redirect(url_for('order_details'))
@app.route('/update_delivery', methods=['POST'])
def update_delivery():
    if request.method == 'POST':
        product_ids = request.form.getlist('product_ids[]')  # Get list of product IDs
        with get_db_connection() as connection:
            cursor = connection.cursor()
            for product_id in product_ids:
                cursor.execute("UPDATE Orders SET delivered = 1 WHERE id = %s", (product_id,))
            connection.commit()
    return redirect(url_for('restaurant'))

if __name__ == '__main__':
    app.run(debug=True)
