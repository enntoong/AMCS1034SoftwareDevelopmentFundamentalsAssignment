# File: room_booking/main.py

import tkinter as tk
from tkinter import ttk

from . import BookRoom
from . import UpcomingBookings
from . import CancelledBookings
from . import PastBookings
from . import ViewAvailability
from .rooms_data import ROOMS


class MainApp(tk.Toplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.parent = parent
        self.current_user = current_user

        self.title("Discussion Room Booking")
        self.geometry("1050x620")
        self.configure(bg="#eef2f7")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.content = ttk.Frame(self, padding=30)
        self.content.grid(row=0, column=0, sticky="nsew")

        # Custom style
        style = ttk.Style()
        style.configure(
            "Card.TFrame",
            background="white",
            relief="raised"
        )
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 26, "bold"),
            foreground="#2c3e50"
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 13, "bold"),
            padding=10
        )
        style.map(
            "TButton",
            background=[("active", "#3498db")],
            foreground=[("active", "white")]
        )

        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self.back_to_home)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ---------------- Dashboard ----------------
    def show_dashboard(self):
        self.clear_content()

        dash = ttk.Frame(self.content, padding=40)
        dash.pack(expand=True)

        ttk.Label(
            dash, text="📚 Discussion Room Booking",
            style="Title.TLabel"
        ).pack(pady=(0, 20))

        # White card container
        card = tk.Frame(
            dash, bg="white",
            bd=0, relief="flat",
            highlightbackground="#dcdde1",
            highlightthickness=1
        )
        card.pack(pady=20, ipadx=40, ipady=20)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(pady=10)

        def make_btn(text, cmd, color):
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=color,
                activebackground="#2c3e50",
                activeforeground="white",
                relief="flat",
                width=20, height=2,
                bd=0,
                highlightthickness=0,
                command=cmd
            )
            btn.pack(side="left", padx=15, pady=10)  # <-- side by side
            return btn

        make_btn("🏠 Book a Room", self.show_venues, "#3498db")
        make_btn("📅 View Availability", self.show_availability_venues, "#27ae60")
        make_btn("🗂 My Bookings", lambda: self.show_page("mybookings"), "#f39c12")

        tk.Button(
            dash, text="⬅ Back to Homepage",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#7f8c8d",
            activebackground="#2c3e50",
            activeforeground="white",
            relief="flat",
            width=25, height=2,
            command=self.back_to_home
        ).pack(pady=30)

    # ---------------- Venue selection for booking ----------------
    def show_venues(self):
        self.clear_content()
        ven = ttk.Frame(self.content, padding=30)
        ven.pack(expand=True)

        ttk.Label(
            ven, text="🏟 Select a Venue",
            font=("Segoe UI", 20, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        btn_frame = ttk.Frame(ven)
        btn_frame.pack(pady=20)

        # 🎨 自定义颜色表
        colors = {
            "Library": "#3498db",         # 蓝
            "Cyber Center": "#27ae60",    # 绿
            "Faculty Block A": "#f39c12", # 橙
            "Faculty Block B": "#8e44ad", # 紫
            "Student Hub": "#e74c3c",     # 红
            "Research Center": "#7f8c8d"  # 灰
        }

        col, row = 0, 0
        for venue in ROOMS.keys():
            color = colors.get(venue, "#34495e")
            btn = tk.Button(
                btn_frame, text=venue,
                width=20, height=2,
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=color,
                activebackground="#2c3e50",
                activeforeground="white",
                relief="flat",
                command=lambda v=venue: self.show_page("book", v)
            )
            btn.grid(row=row, column=col, padx=20, pady=15)

            col += 1
            if col > 1:
                col = 0
                row += 1

        tk.Button(
            ven, text="⬅ Back to Dashboard",
            width=20, height=2,
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#95a5a6",
            activebackground="#2c3e50",
            activeforeground="white",
            relief="flat",
            command=self.show_dashboard
        ).pack(pady=25)

    # ---------------- Venue selection for availability ----------------
    def show_availability_venues(self):
        self.clear_content()
        ven = ttk.Frame(self.content, padding=30)
        ven.pack(expand=True)

        ttk.Label(
            ven, text="📊 Select a Venue to View Availability",
            font=("Segoe UI", 20, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        btn_frame = ttk.Frame(ven)
        btn_frame.pack(pady=20)

        # 🎨 同样的颜色表
        colors = {
            "Library": "#3498db",
            "Cyber Center": "#27ae60",
            "Faculty Block A": "#f39c12",
            "Faculty Block B": "#8e44ad",
            "Student Hub": "#e74c3c",
            "Research Center": "#7f8c8d"
        }

        col, row = 0, 0
        for venue in ROOMS.keys():
            color = colors.get(venue, "#34495e")
            btn = tk.Button(
                btn_frame, text=venue,
                width=20, height=2,
                font=("Segoe UI", 12, "bold"),
                fg="white", bg=color,
                activebackground="#2c3e50",
                activeforeground="white",
                relief="flat",
                command=lambda v=venue: self.show_page("availability_table", v)
            )
            btn.grid(row=row, column=col, padx=20, pady=15)

            col += 1
            if col > 1:
                col = 0
                row += 1

        tk.Button(
            ven, text="⬅ Back to Dashboard",
            width=20, height=2,
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#95a5a6",
            activebackground="#2c3e50",
            activeforeground="white",
            relief="flat",
            command=self.show_dashboard
        ).pack(pady=25)

    # ---------------- Page dispatcher ----------------
    def show_page(self, name, venue=None):
        self.clear_content()
        page = ttk.Frame(self.content, padding=30)
        page.pack(expand=True, fill="both")

        if name == "book":
            BookRoom.build_page(
                page,
                selected_venue=venue,
                current_user=self.current_user,
                back_callback=self.show_venues
            )
        elif name == "availability_table":
            ViewAvailability.build_page(
                page,
                selected_venue=venue,
                back_callback=self.show_availability_venues
            )
        elif name == "mybookings":
            self.show_my_bookings_menu(page)

    # ---------------- My Bookings menu ----------------
    def show_my_bookings_menu(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        ttk.Label(
            parent, text="🗂 My Bookings",
            font=("Segoe UI", 20, "bold"),
            foreground="#2c3e50"
        ).pack(pady=20)

        from . import UpcomingBookings, CancelledBookings, PastBookings

        # Upcoming (蓝色)
        tk.Button(
            parent, text="⏳ Upcoming Bookings",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#3498db",
            activebackground="#2980b9",
            relief="flat", width=30, height=2,
            command=lambda: UpcomingBookings.build_page(
                parent, self.current_user,
                back_callback=lambda: self.show_my_bookings_menu(parent)
            )
        ).pack(pady=10)

        # Cancelled (红色)
        tk.Button(
            parent, text="❌ Cancelled Bookings",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#e74c3c",
            activebackground="#c0392b",
            relief="flat", width=30, height=2,
            command=lambda: CancelledBookings.build_page(
                parent, self.current_user,
                back_callback=lambda: self.show_my_bookings_menu(parent)
            )
        ).pack(pady=10)

        # Past (橙色)
        tk.Button(
            parent, text="📜 Past Bookings",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#f39c12",
            activebackground="#d35400",
            relief="flat", width=30, height=2,
            command=lambda: PastBookings.build_page(
                parent, self.current_user,
                back_callback=lambda: self.show_my_bookings_menu(parent)
            )
        ).pack(pady=10)

        # Back (灰色)
        tk.Button(
            parent, text="⬅ Back to Dashboard",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#95a5a6",
            activebackground="#7f8c8d",
            relief="flat", width=30, height=2,
            command=self.show_dashboard
        ).pack(pady=20)

    def back_to_home(self):
        self.destroy()
        self.parent.deiconify()
