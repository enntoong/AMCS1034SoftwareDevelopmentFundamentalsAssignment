import tkinter as tk  # Import tkinter GUI library
from tkinter import ttk, messagebox  # Import themed widgets and message boxes
import os  # Import OS module for file operations
import csv  # Import CSV module to read/write CSV files
from datetime import datetime  # Import datetime module for date and time handling
from PIL import Image, ImageTk  # Import Pillow for image handling
from simple_reminder import open_reminder  # Import function to open reminder window
DATA_DIR = "data"  # Define directory to store user data
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist

# =========================================================

# =========================================================
def get_user_events_file(username):
    return os.path.join("data", f"{username}_events.csv")  # Return file path for user's events CSV

def load_events(user, date=None):
    """load event"""
    events = []  # Initialize empty list of events
    file = get_user_events_file(user)  # Get CSV file path for the user
    if not os.path.exists(file):  # If file doesn't exist
        return events  # Return empty list

    with open(file, "r", encoding="utf-8") as f:  # Open CSV file in read mode
        reader = csv.DictReader(f)  # Read rows as dictionaries
        for row in reader:  # Loop through each row
            start_time_str = row["start_time"]  # Get start time string

            
            if ":" in start_time_str:  # If format is HH:MM
                start = start_time_str  # Keep as is
            elif "," in start_time_str:  # If format is H,M
                h, m = start_time_str.split(",")  # Split by comma
                start = f"{int(h):02d}:{int(m):02d}"  # Convert to HH:MM
            else:
                continue  # Skip invalid format

            events.append({  # Append event to list
                "id": int(row["id"]),  # Event ID
                "date": row["date"],  # Event date
                "start_time": start,  # Start time in HH:MM
                "end_time": row["end_time"],  # End time
                "title": row["title"],  # Event title
                "reminder": row.get("reminder", "0"),  # Reminder flag
                "category": row.get("category", "event"),  # Event category
                "description": row.get("description", "")  # Event description
            })

    if date:  # If date filter is provided
        events = [e for e in events if e["date"] == date]  # Filter events by date
    return events  # Return list of events

def save_events(username, events):
    """保存某用户的所有事件"""
    file = get_user_events_file(username)  # Get CSV file path
    with open(file, "w", newline="", encoding="utf-8") as f:  # Open file in write mode
        writer = csv.writer(f)  # Create CSV writer
        writer.writerow(["id", "date", "start_time", "end_time", "title", "reminder", "category","description"])  # Write header
        for e in events:  # Loop through events
            writer.writerow([  # Write event data
                e["id"], e["date"], e["start_time"], e["end_time"],
                e["title"], e["reminder"], e["category"],e.get("description","")
            ])

def add_event_txt(username, date, start, end, title, category="event",description=""):
    events = load_events(username)  # Load existing events
    eid = max([e["id"] for e in events], default=0) + 1  # Generate new event ID
    events.append({  # Append new event
        "id": eid,
        "date": date,
        "start_time": start,
        "end_time": end,
        "title": title,
        "reminder": "0",  # Default reminder off
        "category": category,
        "description" : description
    })
    save_events(username, events)  # Save updated events

def update_event_txt(username, eid, title, start, end, category,description):
    events = load_events(username)  # Load existing events
    for e in events:  # Find the event by ID
        if e["id"] == eid:
            e["title"] = title  # Update title
            e["start_time"] = start  # Update start time
            e["end_time"] = end  # Update end time
            e["category"] = category  # Update category
            e["description"] = description  # Update description
            break
    save_events(username, events)  # Save updated events

def delete_event_txt(username, eid):
    events = load_events(username)  # Load existing events
    events = [e for e in events if e["id"] != eid]  # Remove event by ID
    save_events(username, events)  # Save updated events

# =========================================================
# Appointment Delete (check delete of two person)
# =========================================================
def delete_appointment(current_user, event):
    title = event["title"]  # Get event title
    date = event["date"]  # Get event date
    start = event["start_time"]  # Get start time
    end = event["end_time"]  # Get end time

    delete_event_txt(current_user, event["id"])  # Delete current user's event

    if title.startswith("Appointment with "):  # Check if it is an appointment
        other_user = title.replace("Appointment with ", "").strip()  # Extract other user
        other_events = load_events(other_user)  # Load other user's events
        for ev in other_events:  # Loop through other user's events
            expected_title = f"Appointment with {current_user}"  # Expected reciprocal title
            if (
                ev["date"] == date
                and ev["start_time"] == start
                and ev["end_time"] == end
                and ev["title"] == expected_title
            ):
                delete_event_txt(other_user, ev["id"])  # Delete reciprocal event
                break

# =========================================================
# Reminder 
# =========================================================
# =========================================================
# Reminder CSV
# =========================================================
def get_user_reminders_file(username):
    return os.path.join(DATA_DIR, f"{username}_reminder.csv")  # Return path to user's reminder CSV

def load_reminders(username):
    reminders = []  # Initialize empty list
    file = get_user_reminders_file(username)  # Get file path
    if not os.path.exists(file):  # If file does not exist
        return reminders  # Return empty list

    with open(file, "r", encoding="utf-8-sig") as f:  # Open CSV with BOM-safe encoding
        reader = csv.DictReader(f)  # Read rows as dicts
        for i, row in enumerate(reader, start=1):  # Loop with default index
            if not row:  # Skip empty rows
                continue
            reminders.append({  # Append reminder
                "id": int(row.get("id", i)),  # Use CSV ID or default index
                "task": row.get("task", ""),  # Reminder task
                "datetime": row.get("datetime", ""),  # Date and time string
                "status": row.get("status", "Pending")  # Status
            })
    return reminders  # Return reminders list

def save_reminders(username, reminders):
    file = get_user_reminders_file(username)  # Get file path
    with open(file, "w", newline="", encoding="utf-8") as f:  # Open file to write
        writer = csv.writer(f)  # CSV writer
        writer.writerow(["id", "task", "datetime", "status"])  # Write header
        for r in reminders:  # Loop through reminders
            writer.writerow([r["id"], r["task"], r["datetime"], r["status"]])  # Write row

def add_reminder(username, task, dt_str):
    reminders = load_reminders(username)  # Load existing reminders
    rid = max([r["id"] for r in reminders], default=0) + 1  # Generate new reminder ID
    reminders.append({  # Append new reminder
        "id": rid,
        "task": task,
        "datetime": dt_str,
        "status": "Pending"  # Default status
    })
    save_reminders(username, reminders)  # Save reminders

def update_reminder_status(username, rid, status):
    reminders = load_reminders(username)  # Load existing reminders
    for r in reminders:  # Find reminder by ID
        if r["id"] == rid:
            r["status"] = status  # Update status
            break
    save_reminders(username, reminders)  # Save changes

def toggle_reminder(username, event, all_events):
    # click the reminder
    reminders = load_reminders(username)  # Load reminders
    dt_str = datetime.strptime(
        f"{event['date']} {event['start_time']}", "%Y-%m-%d %H:%M"
    ).strftime("%Y-%m-%d %I:%M %p")  # Convert to 12-hour format
    task = event["title"]  # Get task title

    # Check got or not
    existing = next((r for r in reminders if r["task"] == task and r["datetime"] == dt_str), None)  # Check if reminder exists

    if event["reminder"] == "0" and not existing:  # If reminder not set
        # add to reminders.csv
        add_reminder(username, task, dt_str)  # Add reminder
        event["reminder"] = "1"  # Update event flag
    elif event["reminder"] == "1" and existing:  # If reminder exists
        # delete reminder
        reminders = [r for r in reminders if not (r["task"] == task and r["datetime"] == dt_str)]  # Remove reminder
        save_reminders(username, reminders)  # Save
        event["reminder"] = "0"  # Update event flag

    # save title CSV
    save_events(username, all_events)  # Save events

# =========================================================
# Time
# =========================================================
def to_24h(hour, minute, ampm):
    hour = int(hour)  # Convert hour to int
    minute = int(minute)  # Convert minute to int
    if ampm == "PM" and hour != 12:  # Convert PM hour
        hour += 12
    if ampm == "AM" and hour == 12:  # Convert midnight
        hour = 0
    return f"{hour:02d}:{minute:02d}"  # Return HH:MM string

def to_12h(hhmm):
    hour, minute = map(int, hhmm.split(":"))  # Split HH:MM
    ampm = "AM"  # Default AM
    if hour >= 12:  # Convert PM
        ampm = "PM"
        if hour > 12:
            hour -= 12
    if hour == 0:  # Convert midnight
        hour = 12
    return hour, minute, ampm  # Return hour, minute, AM/PM

def to_12h_str(hhmm):
    h, m, ampm = to_12h(hhmm)  # Convert to 12h
    return f"{h}:{m:02d} {ampm}"  # Return formatted string





# =========================================================
# Timetable Homepage
# =========================================================
class TimetableApp:
    def __init__(self, root, current_user):
        self.root = root  # store the main Tk window
        self.current_user = current_user  # store the current username
        self.root.title("Student Timetable")  # set window title
        self.root.geometry("1400x900")  # set default window size
        edit_img = Image.open(os.path.join("assets","edit-246.png")).resize((16,16))  # load and resize edit icon
        delete_img = Image.open(os.path.join("assets", "delete.png")).resize((16,16))  # load and resize delete icon
        self.delete_icon = ImageTk.PhotoImage(delete_img)  # convert delete image to Tkinter PhotoImage
        self.edit_icon = ImageTk.PhotoImage(edit_img)  # convert edit image to Tkinter PhotoImage

        # allow window resizing
        self.root.rowconfigure(0, weight=1)  # make row 0 expandable
        self.root.columnconfigure(0, weight=1)  # make column 0 expandable
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))  # store selected date

        # control frame for filters and buttons
        control_frame = tk.Frame(root)  # create a frame for controls
        control_frame.pack(pady=10)  # pack frame with padding

        # category filter combobox
        self.category_filter = tk.StringVar(value="all")  # variable to store selected category
        filter_box = ttk.Combobox(
            control_frame,
            textvariable=self.category_filter,  # bind variable
            values=["all", "event", "class", "appointment", "meeting"],  # combobox options
            state="readonly",  # prevent manual entry
            width=12
        )
        filter_box.pack(side="left", padx=5)  # place combobox on left with padding
        filter_box.bind("<<ComboboxSelected>>", lambda e: self.redraw())  # redraw table on selection

        # date pickers for year/month/day
        years = [str(y) for y in range(2020, 2031)]  # list of years
        months = [f"{m:02d}" for m in range(1, 13)]  # list of months
        days = [f"{d:02d}" for d in range(1, 32)]  # list of days

        self.year_var = tk.StringVar(value=datetime.now().strftime("%Y"))  # current year
        self.month_var = tk.StringVar(value=datetime.now().strftime("%m"))  # current month
        self.day_var = tk.StringVar(value=datetime.now().strftime("%d"))  # current day

        ttk.Combobox(control_frame, textvariable=self.year_var, values=years, width=6, state="readonly").pack(side="left", padx=2)  # year picker
        ttk.Combobox(control_frame, textvariable=self.month_var, values=months, width=4, state="readonly").pack(side="left", padx=2)  # month picker
        ttk.Combobox(control_frame, textvariable=self.day_var, values=days, width=4, state="readonly").pack(side="left", padx=2)  # day picker

        style = ttk.Style()  # create style object
        style.configure("TButton", padding=6, font=("Segoe UI", 10))  # configure button style

        btn_width = 12  # standard button width

        ttk.Button(control_frame, text="Load Date", width=btn_width, command=self.load_date_from_picker).pack(side="left", padx=5, pady=2)  # button to load selected date
        ttk.Button(control_frame, text="Add Event", width=btn_width, command=self.add_event_popup).pack(side="left", padx=5, pady=2)  # button to add event

        self.table_frame = tk.Frame(root)  # frame to hold event table
        self.table_frame.pack(padx=10, pady=10)  # pack table frame with padding

        self.redraw()  # draw the table for the first time

    def load_date_from_picker(self):
        date_str = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"  # construct date string
        self.date_var.set(date_str)  # update date_var
        self.redraw()  # refresh table

    def redraw(self):
        for w in self.table_frame.winfo_children():
            w.destroy()  # clear old table content

        card = tk.Frame(self.table_frame, bg="#f9f9f9", bd=1, relief="solid")  # create background card frame
        card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)  # place card in grid

        table = tk.Frame(card, bg="white")  # create table frame inside card
        table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)  # place table

        # configure column widths
        table.grid_columnconfigure(0, minsize=180)  # time column
        table.grid_columnconfigure(1, minsize=420)  # event column
        table.grid_columnconfigure(2, minsize=240)  # action column

        headers = ["⏰ Time", "📌 Event", "⚙ Action"]  # table headers
        for col, text in enumerate(headers):
            tk.Label(
                table, text=text, bg="#2c3e50", fg="white",
                font=("Segoe UI", 11, "bold"), pady=6
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)  # create header labels

        date = self.date_var.get()  # get selected date
        events = load_events(self.current_user, date)  # load events for user and date

        if not events:
            tk.Label(
                table, text="No events for this date.", fg="gray",
                font=("Segoe UI", 11), pady=10
            ).grid(row=1, column=0, columnspan=3)  # show message if no events
            return

        events.sort(key=lambda e: e["start_time"])  # sort events by start time

        for i, e in enumerate(events, start=1):
            bg_color = "#ffffff" if i % 2 == 1 else "#f4f6f7"  # alternate row color

            s_h, s_m, s_ampm = to_12h(e["start_time"])  # convert start time to 12h
            e_h, e_m, e_ampm = to_12h(e["end_time"])  # convert end time to 12h
            time_str = f"{s_h}:{s_m:02d} {s_ampm} - {e_h}:{e_m:02d} {e_ampm}"  # formatted time string

            tk.Label(
                table, text=time_str, bg=bg_color, anchor="w", font=("Segoe UI", 10)
            ).grid(row=i, column=0, sticky="nsew", padx=2, pady=2)  # display time

            lbl = tk.Label(
                table, text=f"[{e['category']}] {e['title']}",
                bg=bg_color, anchor="w", font=("Segoe UI", 10)
            )
            lbl.grid(row=i, column=1, sticky="nsew", padx=2, pady=2)  # display event title
            lbl.bind("<Button-1>", lambda _ev=None, ev=e: self.show_event_detail(ev))  # bind click to show details

            action_frame = tk.Frame(table, bg=bg_color)  # frame for buttons
            action_frame.grid(row=i, column=2, sticky="nsew", padx=2, pady=2)  # place frame

            action_frame.grid_columnconfigure(0, minsize=70)  # edit button column
            action_frame.grid_columnconfigure(1, minsize=90)  # delete button column
            action_frame.grid_columnconfigure(2, weight=1)  # spacer column
            action_frame.grid_columnconfigure(3, minsize=120)  # reminder column

            if e.get("category") == "appointment":
                tk.Label(
                    action_frame, text="(Locked)", fg="gray",
                    bg=bg_color, font=("Segoe UI", 10, "italic")
                ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5)  # display locked if appointment
            else:
                tk.Button(
                    action_frame, text="✏ Edit", width=8,
                    fg="white", bg="#3498db", relief="flat",
                    command=lambda eid=e["id"]: self.edit_event_popup(eid)
                ).grid(row=0, column=0, sticky="w", padx=5)  # edit button

                tk.Button(
                    action_frame, text="🗑 Delete", width=8,
                    fg="white", bg="#e74c3c", relief="flat",
                    command=lambda ev=e: self.delete_and_refresh(ev)
                ).grid(row=0, column=1, sticky="e", padx=5)  # delete button

            var = tk.IntVar(value=int(e.get("reminder", "0")))  # variable for reminder checkbox
            e["_rem_var"] = var  # store in event dict
            cb = tk.Checkbutton(
                action_frame, text="🔔 Reminder",
                variable=var, bg=bg_color,
                command=lambda ev=e, v=var: (
                    toggle_reminder(self.current_user, ev, events),
                    self.redraw()
                )
            )
            cb.grid(row=0, column=3, sticky="w", padx=5)  # reminder checkbox

         




    

    def add_event_popup(self):
        self.event_popup()

    def edit_event_popup(self, eid):
        events = load_events(self.current_user, self.date_var.get())
        event = next((ev for ev in events if ev["id"] == eid), None)
        if event:
            self.event_popup(event)

    def event_popup(self, event=None):
        popup = tk.Toplevel(self.root)
        popup.title("Event Editor")
        popup.geometry("600x500")
        popup.configure(bg="#e9ecf1")   # background

        card = tk.Frame(
            popup,
            bg="white",
            highlightbackground="#d0d4db",
            highlightthickness=1,
            padx=20, pady=15
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # === Title ===
        tk.Label(
            card,
            text="✏ Edit Event" if event else "➕ Add Event",
            font=("Segoe UI", 14, "bold"),
            fg="#2c3e50", bg="white"
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        # === Event Title ===
        tk.Label(card, text="Title:", font=("Segoe UI", 11), bg="white").grid(row=1, column=0, sticky="e", pady=5)
        title_var = tk.StringVar(value=event["title"] if event else "")
        tk.Entry(card, textvariable=title_var, font=("Segoe UI", 10), width=30, relief="solid", bd=1).grid(row=1, column=1, columnspan=3, pady=5, sticky="w")

        # === Category ===
        tk.Label(card, text="Category:", font=("Segoe UI", 11), bg="white").grid(row=2, column=0, sticky="e", pady=5)
        category_var = tk.StringVar(value=event["category"] if event else "event")
        category_box = ttk.Combobox(card, textvariable=category_var,
                                    values=["event", "class", "meeting"], state="readonly", width=27)
        category_box.grid(row=2, column=1, columnspan=3, pady=5, sticky="w")

        # === Start / End Time ===
        tk.Label(card, text="Start:", font=("Segoe UI", 11), bg="white").grid(row=3, column=0, sticky="e", pady=5)
        tk.Label(card, text="End:", font=("Segoe UI", 11), bg="white").grid(row=4, column=0, sticky="e", pady=5)

        s_hour, s_min, s_ampm = tk.StringVar(), tk.StringVar(), tk.StringVar(value="AM")
        e_hour, e_min, e_ampm = tk.StringVar(), tk.StringVar(), tk.StringVar(value="AM")

        hours = [str(i) for i in range(1, 13)]
        minutes = [f"{i:02d}" for i in range(60)]
        ampm = ["AM", "PM"]

        if event:
            s_h, s_m, s_amp = to_12h(event["start_time"])
            e_h, e_m, e_amp = to_12h(event["end_time"])
            s_hour.set(s_h)
            s_min.set(f"{s_m:02d}")
            s_ampm.set(s_amp)
            e_hour.set(e_h)
            e_min.set(f"{e_m:02d}")
            e_ampm.set(e_amp)

        ttk.Combobox(card, textvariable=s_hour, values=hours, width=3, state="readonly").grid(row=3, column=1)
        ttk.Combobox(card, textvariable=s_min, values=minutes, width=3, state="readonly").grid(row=3, column=2)
        ttk.Combobox(card, textvariable=s_ampm, values=ampm, width=3, state="readonly").grid(row=3, column=3)

        ttk.Combobox(card, textvariable=e_hour, values=hours, width=3, state="readonly").grid(row=4, column=1)
        ttk.Combobox(card, textvariable=e_min, values=minutes, width=3, state="readonly").grid(row=4, column=2)
        ttk.Combobox(card, textvariable=e_ampm, values=ampm, width=3, state="readonly").grid(row=4, column=3)

        # === Description ===
        tk.Label(card, text="Description:", font=("Segoe UI", 11), bg="white").grid(row=5, column=0, sticky="ne", pady=5)
        desc_text = tk.Text(card, width=35, height=4, font=("Segoe UI", 10), relief="solid", bd=1)
        desc_text.grid(row=5, column=1, columnspan=3, pady=5, sticky="w")
        if event:
            desc_text.insert("1.0", event.get("description", ""))

        # === Save ===
        def save():
            if not title_var.get().strip():
                messagebox.showerror("Error", "Title cannot be empty")
                return

            if not s_hour.get() or not s_min.get() or not s_ampm.get() \
            or not e_hour.get() or not e_min.get() or not e_ampm.get():
                messagebox.showerror("Error", "Please select full start/end time.")
                return

            start = to_24h(s_hour.get(), s_min.get(), s_ampm.get())
            end   = to_24h(e_hour.get(), e_min.get(), e_ampm.get())

            if start >= end:
                messagebox.showerror("Error", "Start time must be before end time.")
                return

            events = load_events(self.current_user, self.date_var.get())
            for ev in events:
                if event and ev["id"] == event["id"]:
                    continue  

                ev_start = ev["start_time"]
                ev_end   = ev["end_time"]

                # Check if time tumplica
                if not (end <= ev_start or start >= ev_end):
                    messagebox.showerror(
                        "Error",
                        f"Time conflict with existing event:\n{ev['title']} ({ev_start} - {ev_end})"
                    )
                    return
                    
            title = title_var.get().strip()
            category = category_var.get().strip()
            description = desc_text.get("1.0", "end").strip()

            if event:
                update_event_txt(self.current_user, event["id"], title, start, end, category, description)
            else:
                add_event_txt(self.current_user, self.date_var.get(), start, end, title, category, description)

            popup.destroy()
            self.redraw()

        # === button ===
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.grid(row=6, column=0, columnspan=4, pady=15)

        tk.Button(btn_frame, text="💾 Save", command=save,
                bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"),
                relief="flat", width=10).pack(side="left", padx=10)

        tk.Button(btn_frame, text="✖ Cancel", command=popup.destroy,
                bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                relief="flat", width=10).pack(side="left", padx=10)


    def show_event_detail(self, ev):
        # === popup ===
        win = tk.Toplevel(self.root)
        win.title("Event Detail")
        win.configure(bg="#e9ecf1")             # bsckground
        win.geometry("420x320")
        win.resizable(False, False)

       
        style = ttk.Style()
        style.theme_use("clam")

    
        card = tk.Frame(
            win,
            bg="white",
            highlightbackground="#d0d4db",      
            highlightthickness=1,
            bd=0,
            padx=25, pady=20
        )
        card.pack(padx=25, pady=25, fill="both", expand=True)

        # === title ===
        tk.Label(
            card,
            text=ev['title'],
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 15))

        # === time and category ===
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(anchor="w", fill="x", pady=(0, 15))

        tk.Label(
            info_frame,
            text=f"🕒  {ev['start_time']}  –  {ev['end_time']}",
            font=("Segoe UI", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=f"📂  {ev['category'].title()}",
            font=("Segoe UI", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor="w", pady=(5, 0))

        # === Description ===
        desc = ev.get("description", "").strip() or "No description provided."
        desc_box = tk.Label(
            card,
            text=desc,
            font=("Segoe UI", 11),
            wraplength=350,
            justify="left",
            bg="#f7f9fb",
            fg="#2f3640",
            anchor="nw",
            relief="groove",
            padx=10,
            pady=10
        )
        desc_box.pack(fill="x", pady=(0, 15))

        # === button ===
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill="x", pady=(10, 0))

        close_btn = ttk.Button(
            btn_frame,
            text="Close",
            command=win.destroy
        )
        close_btn.pack(anchor="e")



    
    def delete_and_refresh(self, event):
        delete_appointment(self.current_user, event)
        self.redraw()

# =========================================================

# =========================================================
def open_timetable(parent, current_user):
    timetable_window = tk.Toplevel(parent)
    TimetableApp(timetable_window, current_user)

if __name__ == "_main_":
    current_user = "testuser"
    root = tk.Tk()
    root.title("Student Timetable")
    root.geometry("900x600")  # size

    # zoom page
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    TimetableApp(root, current_user)
    root.mainloop()
