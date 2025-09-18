# File: homepage.py
import tkinter as tk                    # Import tkinter for GUI components
from PIL import Image, ImageTk          # Import Pillow for image handling
import os                               # Import os for file and path handling
from simple_reminder import ReminderApp # Import ReminderApp for reminder feature
from student_timetable import open_timetable   # Import timetable window function
from make_appointment import open_appointment # Import appointment window function
from notes_organizer_app import NotesOrganizerApp # Import Notes Organizer feature
from room_booking.main import MainApp   # Import MainApp for discussion room booking

# =========================================================
# Main Homepage Function
# =========================================================
def open_main_app(login_window, current_user):
    """Open the main homepage after login"""

    # Keep references to sub-windows to avoid duplicate openings
    reminder_window = None
    booking_window = None
    notes_window = None

    # ---------------- Reminder App ----------------
    def open_reminder():
        nonlocal reminder_window                # Use outer variable
        if reminder_window is not None and reminder_window.winfo_exists():
            reminder_window.lift()              # If window exists, bring it to front
            return
        reminder_window = tk.Toplevel(root)     # Create new window
        ReminderApp(reminder_window, current_user)  # Start ReminderApp

    # ---------------- Notes Organizer ----------------
    def open_notes_organizer():
        nonlocal notes_window
        if notes_window is not None and notes_window.winfo_exists():
            notes_window.lift()                 # If already open, bring to front
            return
        notes_window = tk.Toplevel(root)        # Create new window
        NotesOrganizerApp(notes_window, current_user)  # Start NotesOrganizerApp

    # ---------------- Room Booking ----------------
    def open_booking():
        nonlocal booking_window
        if booking_window is not None and booking_window.winfo_exists():
            booking_window.lift()               # If already open, bring to front
            return
        booking_window = MainApp(root, current_user)  # Start MainApp for booking
        root.withdraw()                         # Hide homepage while booking is open

    # ---------------- Logout ----------------
    def logout():
        root.destroy()          # Close homepage window
        login_window.deiconify()  # Show login window again

    # ---------------- Root Window ----------------
    root = tk.Toplevel(login_window)     # Create homepage as a child of login
    root.geometry("500x500")             # Set size
    root.configure(bg="#fdf6e3")         # Set background color (cream)
    root.title("TAR UMT Student Assistant App")  # Set window title

    # ---------------- Title Section ----------------
    title_frame = tk.Frame(root, bg="#fdf6e3")   # Frame for title
    title_frame.pack(pady=20)

    if os.path.exists("lightbulb.png"):          # Check if icon exists
        img = Image.open(os.path.join("assets", "lightbulb.png")).resize((50, 50))
        # Open and resize icon image
        photo = ImageTk.PhotoImage(img)          # Convert to Tkinter-compatible format
        icon = tk.Label(title_frame, image=photo, bg="#fdf6e3")
        icon.image = photo                       # Keep a reference to avoid garbage collection
        icon.pack(side="right", padx=5)          # Place on right side of title bar

    title_label = tk.Label(
        title_frame,
        text="SMART ASSISTANT",                 # Title text
        font=("Arial", 18, "bold"),
        bg="#fdf6e3",
        fg="#333"
    )
    title_label.pack(side="left")               # Place text on left side

    # ---------------- Logout Button ----------------
    logout_btn = tk.Button(
        root, text="Logout",
        font=("Arial", 10, "bold"),
        bg="#f08080", fg="white",
        relief="raised", command=logout
    )
    logout_btn.place(relx=1.0, x=-10, y=10, anchor="ne")
    # Place button at top-right corner

    # ---------------- Buttons Section ----------------
    btn_frame = tk.Frame(root, bg="#fdf6e3")     # Frame to hold buttons
    btn_frame.pack(expand=True)

    def make_button(text, color, command):
        """Helper to create buttons with consistent style"""
        return tk.Button(
            btn_frame, text=text,
            font=("Arial", 12, "bold"),
            bg=color, fg="black",
            relief="raised", width=25, height=2,
            command=command
        )

    # Create feature buttons
    make_button("🕒 Simple Reminder App", "#FFD700", open_reminder).pack(pady=10)
    make_button("📅 Student Timetable", "#90EE90", lambda: open_timetable(root, current_user)).pack(pady=10)
    make_button("📌 Make Appointment", "#ADD8E6", lambda: open_appointment(root, current_user)).pack(pady=10)
    make_button("🏠 Discussion Room Booking", "#FFA07A", open_booking).pack(pady=10)
    make_button("📒 Notes Organizer", "#3498db", open_notes_organizer).pack(pady=10) 

    # Handle window close (X button) as logout
    root.protocol("WM_DELETE_WINDOW", logout)


# =========================================================
# For standalone testing
# =========================================================
if __name__ == "__main__":
    root = tk.Tk()                # Create root window
    root.withdraw()               # Hide it
    open_main_app(root, "testuser")  # Open homepage with dummy user
    root.mainloop()               # Run Tkinter loop
