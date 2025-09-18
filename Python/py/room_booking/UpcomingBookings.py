# File: room_booking/UpcomingBookings.py
import tkinter as tk
from tkinter import ttk, messagebox
import os, csv, datetime as dt
from .BookRoom import fetch_upcoming_bookings
from .helpers import user_in_booking

BOOKINGS_FILE = os.path.join("data", "bookings.csv")
CANCELLED_FILE = os.path.join("data", "cancelled_bookings.csv")


def move_to_cancelled(booking: dict):
    """Move booking to cancelled file and remove from active bookings"""
    if not os.path.exists(CANCELLED_FILE):
        with open(CANCELLED_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=booking.keys())
            writer.writeheader()

    with open(CANCELLED_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=booking.keys())
        writer.writerow(booking)

    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows = [r for r in rows if not (
            r["venue"] == booking["venue"]
            and r["room"] == booking["room"]
            and r["date"] == booking["date"]
            and r["start"] == booking["start"]
            and r["end"] == booking["end"]
            and r["owner_id"] == booking["owner_id"]
        )]
        with open(BOOKINGS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=booking.keys())
            writer.writeheader()
            writer.writerows(rows)


def build_page(parent, current_user, back_callback=None):
    for w in parent.winfo_children():
        w.destroy()

    now = dt.datetime.now()
    today = now.date()

    # ===== Header =====
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill="x", pady=10)

    ttk.Label(title_frame, text="📅 My Upcoming Bookings", font=("Arial", 18, "bold")).pack(side="left", padx=10)

    btn_frame = ttk.Frame(title_frame)
    btn_frame.pack(side="right")
    ttk.Button(btn_frame, text="🔄 Refresh", width=10,
               command=lambda: build_page(parent, current_user, back_callback)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="⬅ Back", width=10,
               command=(lambda: back_callback()) if back_callback else None).pack(side="left", padx=5)

    # ===== Scrollable area =====
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas, padding=10)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ===== Data =====
    bookings = []
    for b in fetch_upcoming_bookings():
        if not user_in_booking(b, current_user):
            continue
        b_date = dt.datetime.strptime(b["date"], "%Y-%m-%d").date()
        b_end = dt.datetime.strptime(b["end"], "%I:%M %p").time()
        if b_date > today or (b_date == today and b_end > now.time()):
            bookings.append(b)

    if not bookings:
        ttk.Label(scroll_frame, text="You have no upcoming bookings.").pack(pady=20)
        return

    cards_frame = ttk.Frame(scroll_frame)
    cards_frame.pack(expand=True)

    max_per_row = 4
    for i, b in enumerate(bookings, start=1):
        card = ttk.LabelFrame(cards_frame, text=f"My Booking #{i}", padding=10)
        row, col = divmod(i - 1, max_per_row)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="n")
        card.config(width=230)

        ttk.Label(card, text=f"📍 Venue: {b['venue']}").pack(anchor="w")
        ttk.Label(card, text=f"🏠 Room: {b['room']}").pack(anchor="w")
        ttk.Label(card, text=f"🗓 Date: {b['date']}").pack(anchor="w")
        ttk.Label(card, text=f"⏰ Time: {b['start']} – {b['end']}").pack(anchor="w")
        ttk.Label(card, text=f"👥 Pax: {b['pax']}").pack(anchor="w")
        ttk.Label(card, text=f"👤 Owner ID: {b['owner_id']}").pack(anchor="w")
        ttk.Label(card, text=f"👤 Owner Name: {b['owner_name']}").pack(anchor="w")

        members = b.get("members", "").strip()
        if members:
            ttk.Label(card, text="👥 Members:", font=("Arial", 10)).pack(anchor="w")
            for m in members.split(";"):
                sid, sep, name = m.partition("|")
                ttk.Label(card, text=f"   • {sid} | {name}" if sep else f"   • {m}").pack(anchor="w", padx=15)

        # Cancel button only if current user is owner
        if (b.get("owner_id", "").strip() == str(current_user).strip() or
            b.get("owner_name", "").strip().upper() == str(current_user).strip().upper()):
            def cancel_this_booking(b=b):
                if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel this booking?"):
                    move_to_cancelled(b)
                    messagebox.showinfo("Cancelled", "Your booking has been cancelled.")
                    build_page(parent, current_user, back_callback)

            tk.Button(card, text="❌ Cancel", font=("Segoe UI", 9, "bold"),
                      fg="white", bg="#e74c3c", activebackground="#c0392b",
                      relief="flat", width=10, command=cancel_this_booking).pack(anchor="e", pady=5)

    for col in range(max_per_row):
        cards_frame.grid_columnconfigure(col, weight=1)
