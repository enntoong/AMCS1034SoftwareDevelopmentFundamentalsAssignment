# File: room_booking/CancelledBookings.py
import tkinter as tk
from tkinter import ttk
import os, csv
from .helpers import user_in_booking

CANCELLED_FILE = os.path.join("data", "cancelled_bookings.csv")

def fetch_cancelled_bookings():
    if not os.path.exists(CANCELLED_FILE):
        return []
    with open(CANCELLED_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build_page(parent, current_user, back_callback=None):
    for w in parent.winfo_children():
        w.destroy()

    # ===== Header =====
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill="x", pady=10)

    ttk.Label(title_frame, text="❌ My Cancelled Bookings", font=("Arial", 18, "bold")).pack(side="left", padx=10)

    ttk.Button(title_frame, text="⬅ Back", width=10,
               command=(lambda: back_callback()) if back_callback else None).pack(side="right", padx=5)

    # ===== Scrollable =====
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas, padding=10)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ===== Data =====
    bookings = [b for b in fetch_cancelled_bookings() if user_in_booking(b, current_user)]

    if not bookings:
        ttk.Label(scroll_frame, text="You have no cancelled bookings.").pack(pady=20)
        return

    cards_frame = ttk.Frame(scroll_frame)
    cards_frame.pack(expand=True)

    max_per_row = 4
    for i, b in enumerate(bookings, start=1):
        card = ttk.LabelFrame(cards_frame, text=f"Cancelled Booking #{i}", padding=10)
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

    for col in range(max_per_row):
        cards_frame.grid_columnconfigure(col, weight=1)
