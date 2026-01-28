import sqlite3

DATABASE = 'users.db'

def view_users():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if users:
            print("\n=== Users Table ===")
            print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Password':<30}")
            print("-" * 75)
            for user in users:
                print(f"{user['id']:<5} {user['username']:<15} {user['email']:<25} {user['password'][:20]:<30}")
        else:
            print("No users found in database")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    view_users()
