from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'hotel_management',
    'charset': 'utf8mb4',  # Keep this as utf8mb4
    'collation': 'utf8mb4_general_ci'  # Change this to a compatible collation
}

@app.route('/', methods=['GET', 'POST'])
def index():
    query_result = None
    error_message = None
    success_message = None
    column_names = None

    if request.method == 'POST':
        query = request.form['query']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        try:
            # Create a savepoint
            cursor.execute("SAVEPOINT sp1")

            # Split the query into multiple statements if needed
            statements = query.split(';')
            for stmt in statements:
                if stmt.strip():
                    cursor.execute(stmt)

            # Handle SELECT queries
            if query.strip().lower().startswith('select'):
                query_result = cursor.fetchall()
                column_names = cursor.column_names
            elif query.strip().lower().startswith('show databases'):
                query_result = cursor.fetchall()
                column_names = ['Database']
            elif query.strip().lower().startswith('show tables'):
                query_result = cursor.fetchall()
                column_names = ['Tables']
            elif query.strip().lower().startswith('desc') or query.strip().lower().startswith('describe'):
                query_result = cursor.fetchall()
                column_names = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
            else:
                success_message = "Operation executed successfully"

            connection.commit()

        except mysql.connector.Error as err:
            # Rollback to the savepoint on error
            try:
                cursor.execute("ROLLBACK TO sp1")
            except mysql.connector.Error as rollback_err:
                # Handle rollback error
                error_message = f"Rollback error: {rollback_err}"
            error_message = f"Error: {err}"

        finally:
            cursor.close()
            connection.close()

    return render_template('results.html', query_result=query_result, error_message=error_message, success_message=success_message, column_names=column_names)

if __name__ == '__main__':
    app.run(debug=True)
