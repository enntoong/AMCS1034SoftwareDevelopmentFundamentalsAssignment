import tkinter as tk              # Import tkinter for GUI components
from tkinter import messagebox    # Import messagebox for popup dialogs
import os                         # Import os for file and directory handling
from homepage import open_main_app  # Import function to open the main app after login

# --- Global variables for this file ---
USER_FILE = os.path.join("data", "users.txt")  # Path to user data file
current_user = ""                              # Store currently logged-in username


# =========================================================
# Utility functions
# =========================================================
def ensure_user_file():
    """Make sure the user file exists"""
    if not os.path.exists(USER_FILE):                      # Check if file does not exist
        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)  # Create "data" directory if missing
        with open(USER_FILE, "w") as f:                    # Create an empty file
            pass


def read_users():
    """Return [(student_id, username, password), ...]"""
    ensure_user_file()                         # Ensure user file exists before reading
    users = []                                 # Initialize empty list
    with open(USER_FILE, "r", encoding="utf-8") as f:   # Open user file in read mode
        for line in f:                         # Read each line
            parts = line.strip().split(",")    # Split by comma
            if len(parts) == 3:                # New format: id, username, password
                users.append((parts[0], parts[1], parts[2]))
            elif len(parts) == 2:              # Old format fallback: username, password
                users.append(("0000000", parts[0], parts[1]))  # Use default ID
    return users                               # Return list of users


def generate_student_id():
    """Generate a new unique student ID"""
    users = read_users()                       # Load all users
    ids = [int(u[0]) for u in users if u[0].isdigit()]  # Collect valid numeric IDs
    if not ids:                                # If no IDs exist
        return "1000001"                       # Start from 1000001
    return str(max(ids) + 1).zfill(7)          # Otherwise assign max+1, padded to 7 digits


def write_user(username, password):
    """Write new user with auto student_id"""
    student_id = generate_student_id()         # Generate a new ID
    with open(USER_FILE, "a", encoding="utf-8") as f:   # Open file in append mode
        f.write(f"{student_id},{username},{password}\n")  # Write user info
    return student_id                          # Return assigned ID


# =========================================================
# Register window
# =========================================================
def open_register_window(parent):
    """Open a new window for user registration"""
    reg_win = tk.Toplevel(parent)              # Create a new top-level window
    reg_win.title("Register New User")         # Set window title
    reg_win.geometry("300x200")                # Set window size
    reg_win.resizable(False, False)            # Disable resizing

    tk.Label(reg_win, text="Register", font=("Arial", 14, "bold")).pack(pady=10)
    # Title label

    tk.Label(reg_win, text="Username:").pack() # Label for username
    username_entry = tk.Entry(reg_win, width=25)   # Entry for username
    username_entry.pack(pady=5)

    tk.Label(reg_win, text="Password:").pack() # Label for password
    password_entry = tk.Entry(reg_win, show="*", width=25)  # Entry for password (masked)
    password_entry.pack(pady=5)

    def register_user():
        """Inner function to handle registration logic"""
        username = username_entry.get().strip()  # Get input username
        password = password_entry.get().strip()  # Get input password

        if not username or not password:         # Check for empty fields
            messagebox.showwarning("Warning", "Fields cannot be empty!", parent=reg_win)
            return

        users = read_users()                     # Load existing users
        if any(saved_user == username for _, saved_user, _ in users):
            # If username already exists, show error
            messagebox.showerror("Error", "Username already exists!", parent=reg_win)
            return

        student_id = write_user(username, password)  # Save new user
        messagebox.showinfo("Success", f"User '{username}' registered successfully!\nAssigned Student ID: {student_id}", parent=reg_win)
        # Show success message with assigned ID
        reg_win.destroy()                        # Close register window

    tk.Button(reg_win, text="Register", bg="lightgreen", width=15, command=register_user).pack(pady=15)
    # Button to trigger registration


# =========================================================
# Login logic
# =========================================================
def login_user():
    """Handle user login"""
    global current_user
    username = user_entry.get().strip()         # Get username input
    password = pass_entry.get().strip()         # Get password input

    users = read_users()                        # Load users
    for saved_sid, saved_user, saved_pass in users:  # Check each user
        if saved_user == username and saved_pass == password:  # Match found
            current_user = username             # Set current user
            messagebox.showinfo("Login Successful", f"Welcome, {username}!\nID: {saved_sid}", parent=login_window)
            # Show success popup with ID
            user_entry.delete(0, tk.END)        # Clear username field
            pass_entry.delete(0, tk.END)        # Clear password field
            login_window.withdraw()             # Hide login window
            open_main_app(login_window, current_user)  # Open main app
            return

    # If loop finishes without returning -> wrong login
    messagebox.showerror("Login Failed", "Wrong username or password!", parent=login_window)
    pass_entry.delete(0, tk.END)                # Clear only password field


# =========================================================
# Main login window
# =========================================================
login_window = tk.Tk()                          # Create the root window
login_window.title("Login")                     # Set title
login_window.geometry("350x250")                # Set size
login_window.resizable(False, False)            # Disable resizing

tk.Label(login_window, text="TAR UMT Assistant", font=("Arial", 16, "bold")).pack(pady=15)
# App title label

tk.Label(login_window, text="Username:").pack() # Username label
user_entry = tk.Entry(login_window, width=25)  # Username input field
user_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack() # Password label
pass_entry = tk.Entry(login_window, show="*", width=25)  # Password input field (masked)
pass_entry.pack(pady=5)

btn_frame = tk.Frame(login_window)              # Frame for buttons
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Login", bg="lightblue", width=10, command=login_user).grid(row=0, column=0, padx=10)
# Login button

tk.Button(btn_frame, text="Register", bg="lightgreen", width=10, command=lambda: open_register_window(login_window)).grid(row=0, column=1, padx=10)
# Register button (opens register window)

login_window.mainloop()                         # Start Tkinter event loop
