import tkinter as tk              # Import tkinter for GUI components
from tkinter import ttk, messagebox  # Import ttk for themed widgets, messagebox for popups
import winsound                   # Import winsound for playing beep sounds on Windows
import time                       # Import time module for formatting current time
from datetime import datetime, timedelta  # Import datetime and timedelta for date/time handling
import csv                        # Import csv module to read and write CSV files
import os                         # Import os module for file and directory handling

# ---------------- CSV File Operations ----------------
DATA_DIR = "data"                 # Define the directory to store reminder CSV files
os.makedirs(DATA_DIR, exist_ok=True)  # Create the "data" directory if it does not already exist


def reminder_file(user):
    """Return the file path for a user's reminder CSV file"""
    return os.path.join(DATA_DIR, f"{user}_reminder.csv")  # Combine directory and filename with user ID


def load_reminders(user):
    """Load reminders from CSV for a given user"""
    events = []                   # Initialize an empty list to store reminders
    file = reminder_file(user)     # Get the CSV file path for the user
    if os.path.exists(file):       # Check if the file exists
        with open(file, newline="", encoding="utf-8") as f:  # Open the file in read mode
            reader = csv.DictReader(f)  # Create a CSV reader that reads rows as dictionaries
            for row in reader:          # Loop through each row in the CSV file
                events.append({         # Append each reminder as a dictionary into events list
                    "id": int(row.get("id", len(events))),  # Use ID from file, or generate one if missing
                    "task": row["task"],                    # Task description
                    "datetime": row["datetime"],            # Date and time string
                    "status": row["status"],                # Status (Pending, Ringing, Rang)
                    "repeat": row.get("repeat", "None")     # Repeat type (None, Daily, Weekly)
                })
    return events  # Return the list of reminders


def save_reminders(user, events):
    """Save all reminders back to the CSV file"""
    file = reminder_file(user)     # Get the file path for the user
    with open(file, "w", newline="", encoding="utf-8") as f:  # Open the file in write mode
        writer = csv.DictWriter(f, fieldnames=["id", "task", "datetime", "status", "repeat"])  
        # Create a CSV writer with fixed field names
        writer.writeheader()       # Write the header row (column names)
        for i, e in enumerate(events):  # Loop through all reminders
            writer.writerow({      # Write each reminder as a row in the CSV file
                "id": e.get("id", i),          # ID of the reminder (use existing or index as fallback)
                "task": e["task"],             # Task description
                "datetime": e["datetime"],     # Date and time string
                "status": e["status"],         # Status of reminder
                "repeat": e.get("repeat", "None")  # Repeat value, default to "None"
            })


def add_reminder_to_csv(user, task, dt_str, repeat="None"):
    """Add a new reminder to the CSV"""
    events = load_reminders(user)  # Load all reminders for the user
    next_id = max([e["id"] for e in events], default=-1) + 1  # Generate the next ID (increment by 1)
    events.append({                # Append a new reminder dictionary
        "id": next_id,             # Unique reminder ID
        "task": task,              # Task description
        "datetime": dt_str,        # Reminder date/time string
        "status": "Pending",       # Initial status is "Pending"
        "repeat": repeat           # Repeat option
    })
    save_reminders(user, events)   # Save the updated reminder list back to CSV


def update_reminder_status(user, reminder_id, new_status):
    """Update the status of a reminder by ID"""
    events = load_reminders(user)  # Load all reminders for the user
    for e in events:               # Loop through all reminders
        if e["id"] == reminder_id: # Find the reminder with matching ID
            e["status"] = new_status  # Update its status
            break                  # Exit the loop after updating
    save_reminders(user, events)   # Save the updated reminders back to CSV


# ---------------- Reminder GUI ----------------
class ReminderApp:
    def __init__(self, root, current_user):
        self.root = root                      # Reference to the Tkinter root window
        self.current_user = current_user      # Store the current logged-in user

        self.root.title("Simple Reminder")    # Set the window title
        self.root.geometry("750x650")         # Set the window size
        self.root.configure(bg="#E0FFFF")     # Set the background color (light cyan)

        # ---------------- Clock ----------------
        self.clock_label = tk.Label(self.root, font=('Arial', 22, "bold"), bg="#E0FFFF")
        # Create a label to display current time
        self.clock_label.pack(pady=(10, 20))  # Place the clock label with padding

        # ---------------- Reminder List Section ----------------
        list_frame = tk.LabelFrame(self.root, text="Reminder Events", bg="#E0FFFF", font=("Arial", 12, "bold"))
        # Create a labeled frame for reminder list
        list_frame.pack(pady=10, padx=20, fill="x")  # Pack it with padding and horizontal fill

        self.listbox = tk.Listbox(
            list_frame, width=100, height=12, font=("Courier New", 10),
            bg="white", relief="solid", bd=1
        )  # Create a listbox to show reminders
        self.listbox.pack(pady=5, padx=10)  # Pack the listbox inside the frame

        # ---------------- Buttons Section ----------------
        btn_frame = tk.Frame(self.root, bg="#E0FFFF")  # Create a frame to hold buttons
        btn_frame.pack(pady=10)                       # Pack it with padding

        tk.Button(btn_frame, text="Refresh", bg="yellow", width=15,
                  command=self.refresh_list).pack(side=tk.LEFT, padx=8)  
        # Button to refresh the reminder list

        tk.Button(btn_frame, text="Clear All History", bg="red", fg="white", width=15,
                  command=self.clear_history).pack(side=tk.LEFT, padx=8)  
        # Button to clear all completed reminders

        tk.Button(btn_frame, text="Cancel Repeat", bg="orange", width=15,
                  command=self.cancel_repeat).pack(side=tk.LEFT, padx=8)  
        # Button to cancel repeat reminders

        tk.Button(btn_frame, text="Delete Reminder", bg="pink", width=15,
                  command=self.delete_reminder).pack(side=tk.LEFT, padx=8)  
        # Button to delete a selected reminder


               # ---------------- Form Section (Add Reminder) ----------------
        form_frame = tk.LabelFrame(self.root, text="Add New Reminder", bg="#E0FFFF", font=("Arial", 12, "bold"))
        # Create a labeled frame for adding new reminders
        form_frame.pack(pady=15, padx=20, fill="x")  # Pack it with padding and allow horizontal fill

        # Task input
        tk.Label(form_frame, text="Task:", bg="#E0FFFF", anchor="e", width=10).grid(row=0, column=0, padx=5, pady=5)
        # Label for task input
        self.task_entry = tk.Entry(form_frame, width=40)  # Entry box for entering task description
        self.task_entry.grid(row=0, column=1, columnspan=3, pady=5, sticky="w")

        # Date selection
        tk.Label(form_frame, text="Date:", bg="#E0FFFF", anchor="e", width=10).grid(row=1, column=0, padx=5, pady=5)
        # Label for date selection
        date_frame = tk.Frame(form_frame, bg="#E0FFFF")  # Frame to hold year, month, day selection
        date_frame.grid(row=1, column=1, columnspan=3, sticky="w")

        current_year = datetime.now().year  # Get the current year
        self.year_var, self.month_var, self.day_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        # Variables to store selected year, month, day

        ttk.Combobox(date_frame, textvariable=self.year_var, values=[str(y) for y in range(current_year, current_year + 3)],
                     width=6, state="readonly").grid(row=0, column=0, padx=2)
        # Year selection box (3 years: current year + next 2 years)

        ttk.Combobox(date_frame, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1, 13)],
                     width=4, state="readonly").grid(row=0, column=1, padx=2)
        # Month selection box (01–12)

        ttk.Combobox(date_frame, textvariable=self.day_var, values=[f"{d:02d}" for d in range(1, 32)],
                     width=4, state="readonly").grid(row=0, column=2, padx=2)
        # Day selection box (01–31)

        now = datetime.now()                     # Get the current date and time
        self.year_var.set(str(now.year))         # Set default year to current year
        self.month_var.set(now.strftime("%m"))   # Set default month
        self.day_var.set(now.strftime("%d"))     # Set default day

        # Time selection
        tk.Label(form_frame, text="Time:", bg="#E0FFFF", anchor="e", width=10).grid(row=2, column=0, padx=5, pady=5)
        # Label for time selection
        time_frame = tk.Frame(form_frame, bg="#E0FFFF")  # Frame to hold hour, minute, AM/PM
        time_frame.grid(row=2, column=1, columnspan=3, sticky="w")

        self.hour_var, self.minute_var, self.ampm_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        # Variables for hour, minute, and AM/PM

        ttk.Combobox(time_frame, textvariable=self.hour_var, values=[f"{h:02d}" for h in range(1, 13)],
                     width=4, state="readonly").grid(row=0, column=0, padx=2)
        # Hour selection box (01–12)

        ttk.Combobox(time_frame, textvariable=self.minute_var, values=[f"{m:02d}" for m in range(0, 60)],
                     width=4, state="readonly").grid(row=0, column=1, padx=2)
        # Minute selection box (00–59)

        ttk.Combobox(time_frame, textvariable=self.ampm_var, values=["AM", "PM"],
                     width=4, state="readonly").grid(row=0, column=2, padx=2)
        # AM/PM selection box

        self.hour_var.set(now.strftime("%I"))  # Set default hour to current hour
        self.minute_var.set(now.strftime("%M"))  # Set default minute to current minute
        self.ampm_var.set(now.strftime("%p"))  # Set default AM/PM

        # Repeat selection
        tk.Label(form_frame, text="Repeat:", bg="#E0FFFF", anchor="e", width=10).grid(row=3, column=0, padx=5, pady=5)
        # Label for repeat selection
        self.repeat_var = tk.StringVar()  # Variable to store repeat option
        ttk.Combobox(form_frame, textvariable=self.repeat_var, values=["None", "Daily", "Weekly"],
                     width=10, state="readonly").grid(row=3, column=1, pady=5, sticky="w")
        # Dropdown for repeat options
        self.repeat_var.set("None")  # Default value is "None"

        # Add button
        tk.Button(form_frame, text="Add Reminder", bg="lightgreen", width=20, command=self.add_reminder)\
            .grid(row=4, column=0, columnspan=4, pady=10)
        # Button to add the reminder with entered details

        # Start clock + reminders check
        self.update_clock()       # Start updating clock
        self.check_reminders()    # Start checking reminders
        self.refresh_list()       # Load reminders into the list


     # ---------------- Refresh List ----------------
    def refresh_list(self):
        """Reload and display all reminders in the listbox"""
        self.listbox.delete(0, tk.END)          # Clear the listbox before reloading
        events = load_reminders(self.current_user)  # Load all reminders for current user
        if not events:                          # If no reminders exist
            self.listbox.insert(tk.END, "No reminder events.")  # Show placeholder text
        else:
            self.listbox.insert(
                tk.END,
                f"{'Date':<15} | {'Time':<10} | {'Task':<40} | {'Repeat':<10} | {'Status':<10}"
            )  # Insert header row
            self.listbox.insert(tk.END, "-" * 100)  # Insert a separator line
            for e in events:                        # Loop through all reminders
                date, time_part = e['datetime'].split(" ", 1)  # Split into date and time parts
                self.listbox.insert(
                    tk.END,
                    f"{date:<15} | {time_part:<10} | {e['task']:<40} | {e.get('repeat','None'):<10} | {e['status']:<10}"
                )  # Insert formatted reminder row


    # ---------------- Add Reminder ----------------
    def add_reminder(self):
        """Add a new reminder based on user input"""
        task = self.task_entry.get().strip()     # Get the task description
        year = self.year_var.get()               # Get selected year
        month = self.month_var.get()             # Get selected month
        day = self.day_var.get()                 # Get selected day
        hour = self.hour_var.get()               # Get selected hour
        minute = self.minute_var.get()           # Get selected minute
        ampm = self.ampm_var.get()               # Get selected AM/PM
        repeat = self.repeat_var.get()           # Get selected repeat option

        if not all([task, year, month, day, hour, minute, ampm]):
            messagebox.showerror("Error", "All fields are required!")  # Error if any field is missing
            return

        try:
            dt_str_input = f"{year}-{month}-{day} {hour}:{minute} {ampm}"  
            # Build full datetime string from inputs
            dt_obj = datetime.strptime(dt_str_input, "%Y-%m-%d %I:%M %p")  
            # Convert string to datetime object for validation
            dt_str = dt_obj.strftime("%Y-%m-%d %I:%M %p")  
            # Re-format datetime string
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time format!")  # Show error if invalid input
            return

        now_min = datetime.now().replace(second=0, microsecond=0)  
        # Get current time rounded to minutes

        if dt_obj <= now_min:  
            # Prevent adding reminders in the past
            messagebox.showerror("Error", "You cannot select a past date or time!")
            return

        add_reminder_to_csv(self.current_user, task, dt_str, repeat)  
        # Save new reminder to CSV
        messagebox.showinfo("Success", f"Reminder added for {dt_str}")  
        # Show success popup
        self.refresh_list()  
        # Refresh reminder list display


    # ---------------- Clock Update ----------------
    def update_clock(self):
        """Update the on-screen clock every second"""
        now = time.strftime("%I:%M:%S %p")   # Get current time in HH:MM:SS AM/PM format
        self.clock_label.config(text=f"{now}")  # Update clock label text
        if self.root.winfo_exists():  # Check if window still exists
            self.root.after(1000, self.update_clock)  
            # Call this function again after 1 second


    # ---------------- Check Reminders ----------------
    def check_reminders(self):
        """Check reminders every second (trigger normal + catch-up alarms)"""
        now_dt = datetime.now()  
        # Get current datetime
        now_str = now_dt.strftime("%Y-%m-%d %I:%M %p")  
        # Format current time to match reminder format
        events = load_reminders(self.current_user)  
        # Load all reminders

        for e in events:  
            # Loop through each reminder
            event_dt = datetime.strptime(e["datetime"], "%Y-%m-%d %I:%M %p")  
            # Convert reminder datetime string to datetime object

            # Normal on-time reminder
            if e["datetime"] == now_str and e["status"] == "Pending":
                update_reminder_status(self.current_user, e["id"], "Ringing")  
                # Mark status as "Ringing"
                self.root.after(0, lambda t=e["task"], rid=e["id"], r=e.get("repeat"), dt=e["datetime"]:
                                self.alert(t, rid, r, dt))  
                # Call alert popup immediately

            # Catch-up reminder (missed but still Pending)
            elif event_dt < now_dt and e["status"] == "Pending":
                update_reminder_status(self.current_user, e["id"], "Ringing")  
                # Mark status as "Ringing"
                self.root.after(500, lambda t=e["task"], rid=e["id"], r=e.get("repeat"), dt=e["datetime"]:
                                self.alert(t, rid, r, dt))  
                # Call alert popup slightly delayed (0.5s)

        if self.root.winfo_exists():  
            # Check again after 1 second if window is still open
            self.root.after(1000, self.check_reminders)


    # ---------------- Alarm Sound ----------------
    def play_alarm_sequence(self, times_left):
        """Play beep sound multiple times"""
        if times_left <= 0 or not self.root.winfo_exists():  
            # Stop if no times left or window closed
            return
        winsound.Beep(1000, 700)  
        # Play beep sound (1000 Hz, 0.7s)
        self.root.after(1000, lambda: self.play_alarm_sequence(times_left - 1))  
        # Call again after 1 second until times_left is 0


    # ---------------- Show Reminder Alert ----------------
    def alert(self, title, reminder_id, repeat, old_dt_str):
        """Show popup + play alarm when reminder time is reached"""
        self.play_alarm_sequence(3)  
        # Play alarm sound 3 times
        messagebox.showinfo("Reminder", f"{self.current_user}, time for: {title}")  
        # Show popup reminder
        update_reminder_status(self.current_user, reminder_id, "Rang")  
        # Mark reminder as already "Rang"

        reminders = load_reminders(self.current_user)  
        # Reload reminders
        latest = next((r for r in reminders if r["id"] == reminder_id), None)  
        # Find the latest reminder with this ID

        if latest is None or latest["repeat"] != repeat:  
            # If no reminder found or repeat is changed, do nothing
            return

        # Create next repeat reminder
        if repeat == "Daily":
            new_dt = datetime.now() + timedelta(days=1)  
            # Add 1 day
            add_reminder_to_csv(self.current_user, title, new_dt.strftime("%Y-%m-%d %I:%M %p"), repeat)  
            # Save new reminder for tomorrow
        elif repeat == "Weekly":
            new_dt = datetime.strptime(old_dt_str, "%Y-%m-%d %I:%M %p") + timedelta(weeks=1)  
            # Add 1 week to old reminder date
            add_reminder_to_csv(self.current_user, title, new_dt.strftime("%Y-%m-%d %I:%M %p"), repeat)  
            # Save new reminder for next week

      # ---------------- Clear History ----------------
    def clear_history(self):
        """Delete all reminders that have already rung"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all completed reminders?"):
            # Ask the user for confirmation before clearing
            clear_rang_reminders(self.current_user)  
            # Remove reminders with status = "Rang"
            self.refresh_list()  
            # Refresh the listbox to show updated reminders


    # ---------------- Cancel Repeat ----------------
    def cancel_repeat(self):
        """Cancel repeat for the selected reminder"""
        selection = self.listbox.curselection()  
        # Get the selected row index from the listbox
        if not selection:
            messagebox.showwarning("No Selection", "Please select a reminder to cancel repeat.")
            # Show warning if nothing is selected
            return
        index = selection[0]  
        # Get index of selected item
        if index <= 1:  
            # Prevent canceling header/separator rows
            messagebox.showwarning("Invalid Selection", "Please select a valid reminder row.")
            return

        line = self.listbox.get(index)  
        # Get the selected reminder text line
        parts = line.split("|")  
        # Split the line into parts (Date, Time, Task, Repeat, Status)
        if len(parts) < 5:
            messagebox.showerror("Error", "Invalid reminder format.")  
            # Error if format is not valid
            return

        date = parts[0].strip()       # Extract date
        time_part = parts[1].strip()  # Extract time
        task = parts[2].strip()       # Extract task
        dt_str = f"{date} {time_part}"  
        # Combine date and time into datetime string

        reminders = load_reminders(self.current_user)  
        # Load reminders from CSV
        for r in reminders:  
            if r["datetime"] == dt_str and r["task"] == task:
                r["repeat"] = "None"  
                # Cancel repeat by setting it to "None"

        now = datetime.now()
        reminders = [
            r for r in reminders
            if not (
                r["task"] == task and
                r["repeat"] == "Daily" and
                datetime.strptime(r["datetime"], "%Y-%m-%d %I:%M %p") > now
            )
        ]
        # Remove any future daily repeat reminders for this task

        save_reminders(self.current_user, reminders)  
        # Save updated reminders back to CSV
        self.refresh_list()  
        # Refresh the reminder list
        messagebox.showinfo("Cancelled", "Next Repeat Cancelled.")  
        # Show confirmation popup


    # ---------------- Delete Reminder ----------------
    def delete_reminder(self):
        """Delete the selected reminder"""
        selection = self.listbox.curselection()  
        # Get the selected row index from listbox
        if not selection:
            messagebox.showwarning("No Selection", "Please select a reminder to delete.")
            # Warn if nothing is selected
            return
        index = selection[0]  
        # Get index of selected item
        if index <= 1:
            # Prevent deleting header/separator rows
            messagebox.showwarning("Invalid Selection", "Please select a valid reminder row.")
            return

        line = self.listbox.get(index)  
        # Get the selected reminder line
        parts = line.split("|")  
        # Split into parts
        if len(parts) < 5:
            messagebox.showerror("Error", "Invalid reminder format.")  
            # Error if format is invalid
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete and stop repeat this reminder now?")
        # Ask user confirmation before deleting
        if not confirm:  
            # Do nothing if user cancels
            return

        date = parts[0].strip()       # Extract date
        time_part = parts[1].strip()  # Extract time
        task = parts[2].strip()       # Extract task
        dt_str = f"{date} {time_part}"  
        # Build datetime string

        reminders = load_reminders(self.current_user)  
        # Load all reminders
        reminders = [r for r in reminders if not (r["datetime"] == dt_str and r["task"] == task)]
        # Filter out the selected reminder (delete it)
        save_reminders(self.current_user, reminders)  
        # Save updated reminders
        self.refresh_list()  
        # Refresh the listbox
        messagebox.showinfo("Deleted", "Reminder deleted successfully.")  
        # Show success popup


# ---------------- Utility Functions ----------------
def clear_rang_reminders(user):
    """Remove all reminders with status 'Rang'"""
    events = load_reminders(user)  
    # Load reminders
    filtered = [e for e in events if e["status"] != "Rang"]  
    # Keep only those that are not 'Rang'
    save_reminders(user, filtered)  
    # Save updated list


# ---------------- External Interface ----------------
def open_reminder(parent, current_user):
    """Open reminder window for a user"""
    reminder_window = tk.Toplevel(parent)  
    # Create a new top-level window inside the parent
    ReminderApp(reminder_window, current_user)  
    # Initialize ReminderApp in that window


# ---------------- Standalone Test ----------------
if __name__ == "_main_":
    root = tk.Tk()  
    # Create main Tkinter window
    ReminderApp(root, "testuser")  
    # Start ReminderApp for user "testuser"
    root.mainloop()  
    # Run Tkinter event loop

