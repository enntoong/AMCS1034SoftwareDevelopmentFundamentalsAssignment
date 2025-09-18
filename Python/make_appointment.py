# File: make_appointment.py
import tkinter as tk  # import tkinter for GUI
from tkinter import ttk, messagebox  # import ttk for styled widgets, messagebox for dialogs
from datetime import datetime  # import datetime for date and time handling
import os  # import os for file path operations
from student_timetable import (  # import timetable functions
    load_events,  # command: load events from file
    add_event_txt,  # command: add an event to file
    delete_event_txt  # command: delete an event from file
)


USERS_FILE = os.path.join("data", "users.txt")  # command: set the file path for users


def to_minutes(hhmm: str) -> int:  # command: convert HH:MM to total minutes
    h, m = map(int, hhmm.split(":"))  # command: split hour and minute
    return h * 60 + m  # command: return total minutes


def to_12h_str(hhmm: str) -> str:  # command: convert 24h HH:MM to 12h string
    hour, minute = map(int, hhmm.split(":"))  # command: split hour and minute
    suffix = "AM"  # command: default suffix
    if hour == 0:  # command: midnight check
        hour = 12
    elif hour == 12:  # command: noon check
        suffix = "PM"
    elif hour > 12:  # command: afternoon adjustment
        hour -= 12
        suffix = "PM"
    return f"{hour}:{minute:02d} {suffix}"  # command: return formatted string


class AppointmentApp:  # command: main appointment GUI class
    def __init__(self, root, current_user):  # command: initialize the GUI
        self.root = root  # command: store root window
        self.current_user = current_user  # command: store current user
        self.root.title("Make Appointment")  # command: set window title
        self.root.geometry("600x400")  # command: set window size
        self.root.configure(bg="lightcyan")  # command: set background color

        tk.Label(root, text="Select User to Appointment:", bg="lightcyan").place(x=20, y=20)  # command: add user selection label
        self.user_var = tk.StringVar()  # command: variable for selected user
        self.user_combobox = ttk.Combobox(root, textvariable=self.user_var, width=25, state="readonly")  # command: create user dropdown
        self.user_combobox.place(x=250, y=20)  # command: place user dropdown
        self.load_users()  # command: load users into dropdown

        tk.Label(root, text="Date (YYYY-MM-DD):", bg="lightcyan").place(x=20, y=60)  # command: add date label

        years = [str(y) for y in range(datetime.now().year, datetime.now().year + 6)]  # command: generate years
        months = [f"{m:02d}" for m in range(1, 13)]  # command: generate months
        days = [f"{d:02d}" for d in range(1, 32)]  # command: generate days

        self.year_var = tk.StringVar(value=datetime.now().strftime("%Y"))  # command: default year
        self.month_var = tk.StringVar(value=datetime.now().strftime("%m"))  # command: default month
        self.day_var = tk.StringVar(value=datetime.now().strftime("%d"))  # command: default day

        ttk.Combobox(root, textvariable=self.year_var,  values=years,  width=6, state="readonly").place(x=250, y=60)  # command: year dropdown
        ttk.Combobox(root, textvariable=self.month_var, values=months, width=4, state="readonly").place(x=320, y=60)  # command: month dropdown
        ttk.Combobox(root, textvariable=self.day_var,   values=days,   width=4, state="readonly").place(x=370, y=60)  # command: day dropdown

        time_options = self.generate_time_options()  # command: generate time options list

        tk.Label(root, text="Start Time:", bg="lightcyan").place(x=20, y=100)  # command: add start time label

        self.start_hour = tk.StringVar(value="09")  # command: default start hour
        self.start_min  = tk.StringVar(value="00")  # command: default start minute
        self.start_ampm = tk.StringVar(value="AM")  # command: default start AM/PM

        hours = [f"{h:02d}" for h in range(1, 13)]  # command: hour options
        minutes = [f"{m:02d}" for m in range(60)]  # command: minute options
        ampm = ["AM", "PM"]  # command: AM/PM options

        ttk.Combobox(root, textvariable=self.start_hour, values=hours, width=4, state="readonly").place(x=250, y=100)  # command: start hour dropdown
        ttk.Combobox(root, textvariable=self.start_min,  values=minutes, width=4, state="readonly").place(x=300, y=100)  # command: start minute dropdown
        ttk.Combobox(root, textvariable=self.start_ampm, values=ampm,   width=4, state="readonly").place(x=350, y=100)  # command: start AM/PM dropdown

        tk.Label(root, text="End Time:", bg="lightcyan").place(x=20, y=140)  # command: add end time label

        self.end_hour = tk.StringVar(value="10")  # command: default end hour
        self.end_min  = tk.StringVar(value="00")  # command: default end minute
        self.end_ampm = tk.StringVar(value="AM")  # command: default end AM/PM

        ttk.Combobox(root, textvariable=self.end_hour, values=hours, width=4, state="readonly").place(x=250, y=140)  # command: end hour dropdown
        ttk.Combobox(root, textvariable=self.end_min,  values=minutes, width=4, state="readonly").place(x=300, y=140)  # command: end minute dropdown
        ttk.Combobox(root, textvariable=self.end_ampm, values=ampm,   width=4, state="readonly").place(x=350, y=140)  # command: end AM/PM dropdown

        tk.Button(root, text="Make Appointment", bg="lightgreen", command=self.make_appointment).place(x=100, y=180)  # command: button to create appointment
        tk.Button(root, text="Cancel Selected", bg="lightcoral", command=self.cancel_appointment).place(x=400, y=180)  # command: button to cancel selected appointment

        tk.Label(root, text="Your Appointment History:", bg="lightcyan").place(x=20, y=230)  # command: label for history
        self.history_listbox = tk.Listbox(root, width=70, height=8)  # command: listbox to show appointment history
        self.history_listbox.place(x=20, y=260)  # command: place listbox

        self.refresh_history()  # command: refresh the listbox with current appointments

    def generate_time_options(self):  # command: generate times for dropdown
        options = []
        for h in range(0, 24):
            for m in (0, 30):
                t = datetime(2000, 1, 1, h, m)  # command: create datetime object
                options.append(t.strftime("%I:%M %p"))  # command: append formatted time
        return options  # command: return time list

    def load_users(self):  # command: load users from file
        if not os.path.exists(USERS_FILE):  # command: check file exists
            messagebox.showerror("Error", f"{USERS_FILE} not found.")  # command: error if missing
            return

        users = []
        with open(USERS_FILE, "r", encoding="utf-8") as f:  # command: open file
            for line in f:
                parts = line.strip().split(",")  # command: split line
                if len(parts) == 2:  # command: format username,password
                    username, _ = parts
                    if username != self.current_user:
                        users.append(username)  # command: add user
                elif len(parts) == 3:  # command: format id,username,password
                    student_id, username, _ = parts
                    if username != self.current_user:
                        users.append(username)  # command: add user

        self.user_combobox["values"] = users  # command: update dropdown
        if users:
            self.user_var.set(users[0])  # command: default selection

    def has_conflict(self, events, start, end):  # command: check for conflicts
        for e in events:
            e_start = to_minutes(e['start_time'])  # command: event start minutes
            e_end = to_minutes(e['end_time'])  # command: event end minutes
            if start < e_end and end > e_start:  # command: check overlap
                return True  # command: conflict found
        return False  # command: no conflict

    def make_appointment(self):  # command: create appointment
        other_user = self.user_var.get().strip()  # command: get selected user
        date = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"  # command: get date
        start_str = f"{self.start_hour.get()}:{self.start_min.get()} {self.start_ampm.get()}"  # command: get start time
        end_str   = f"{self.end_hour.get()}:{self.end_min.get()} {self.end_ampm.get()}"  # command: get end time

        if not other_user or not date or not start_str or not end_str:  # command: check blanks
            messagebox.showerror("Error", "All fields are required!")  # command: show error
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")  # command: validate date
            start_24 = datetime.strptime(start_str, "%I:%M %p").strftime("%H:%M")  # command: convert start to 24h
            end_24 = datetime.strptime(end_str, "%I:%M %p").strftime("%H:%M")  # command: convert end to 24h
            if to_minutes(start_24) >= to_minutes(end_24):  # command: check start < end
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid date or time!")  # command: show error
            return

        user_events = load_events(self.current_user, date)  # command: load current user events
        if self.has_conflict(user_events, to_minutes(start_24), to_minutes(end_24)):  # command: check conflict
            messagebox.showerror("Error", "Conflict with your timetable!")  # command: show conflict
            return
        other_events = load_events(other_user, date)  # command: load other user events
        if self.has_conflict(other_events, to_minutes(start_24), to_minutes(end_24)):  # command: check conflict
            messagebox.showerror("Error", "Conflict with other user's timetable!")  # command: show conflict
            return

        title_current = f"Appointment with {other_user}"  # command: set current user title
        add_event_txt(self.current_user, date, start_24, end_24, title_current, category="appointment")  # command: add event

        title_other = f"Appointment with {self.current_user}"  # command: set other user title
        add_event_txt(other_user, date, start_24, end_24, title_other, category="appointment")  # command: add event

        messagebox.showinfo("Success", "Appointment created!")  # command: show success
        self.refresh_history()  # command: refresh history

    def cancel_appointment(self):  # command: cancel appointment
        selection = self.history_listbox.curselection()  # command: get selected index
        if not selection:
            messagebox.showerror("Error", "No appointment selected!")  # command: show error
            return
        idx = selection[0]  # command: get index
        line = self.history_listbox.get(idx)  # command: get line text
        date, time_str, title = line.split(" | ", 2)  # command: split line
        start_str, end_str = time_str.split(" - ")  # command: split time

        start_24 = datetime.strptime(start_str.strip(), "%I:%M %p").strftime("%H:%M")  # command: convert start
        end_24 = datetime.strptime(end_str.strip(), "%I:%M %p").strftime("%H:%M")  # command: convert end

        user_events = load_events(self.current_user, date)  # command: load user events
        to_delete = None  # command: init
        for e in user_events:
            if e['title'] == title and e['start_time'] == start_24 and e['end_time'] == end_24:  # command: match event
                to_delete = e
                break

        if not to_delete:
            messagebox.showerror("Error", "Appointment not found in your records.")  # command: show error
            return

        delete_event_txt(self.current_user, to_delete['id'])  # command: delete event

        if title.startswith("Appointment with "):  # command: remove from other user
            other_user = title.replace("Appointment with ", "").strip()
            other_events = load_events(other_user, date)
            for ev in other_events:
                if ev['title'] == f"Appointment with {self.current_user}" and ev['start_time'] == start_24 and ev['end_time'] == end_24:
                    delete_event_txt(other_user, ev['id'])
                    break

        messagebox.showinfo("Success", "Appointment cancelled.")  # command: show success
        self.refresh_history()  # command: refresh history

    def refresh_history(self):  # command: update history listbox
        self.history_listbox.delete(0, tk.END)  # command: clear listbox
        events = load_events(self.current_user)  # command: load events
        appointments = [e for e in events if e['title'].startswith("Appointment with ")]  # command: filter appointments
        for e in sorted(appointments, key=lambda x: (x['date'], x['start_time'])):  # command: sort
            line = f"{e['date']} | {to_12h_str(e['start_time'])} - {to_12h_str(e['end_time'])} | {e['title']}"  # command: format line
            self.history_listbox.insert(tk.END, line)  # command: insert line

def open_appointment(parent, current_user):  # command: open appointment window
    app_window = tk.Toplevel(parent)  # command: create new window
    AppointmentApp(app_window, current_user)  # command: create appointment app in new window

if __name__ == "__main__":  # command: run standalone
    current_user = "testuser"  # command: default user
    root = tk.Tk()  # command: create main window
    AppointmentApp(root, current_user)  # command: initialize app
    root.mainloop()  # command: run main loop
