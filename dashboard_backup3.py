import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import csv
from datetime import datetime

# ============================================================
# WATCHX DASHBOARD
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "watchx_records.csv"
LOGO_FILE = BASE_DIR / "WatchX_Logo.png"

# Authorized investigators
AUTHORIZED_INVESTIGATORS = {
    "24VE1A05HC": "WatchX@2026",
    "24VE1AO5KD": "WatchX@2026",
    "24VE1AO5JH": "WatchX@2026",
    "24VE1A05HA": "WatchX@2026",
}

# Colors
BG = "#07111f"
HEADER = "#0c1b2e"
CARD = "#10243a"
CARD2 = "#142b45"
TABLE_BG = "#0b1b2e"
TABLE_ALT = "#10243a"
WHITE = "#ffffff"
TEXT = "#dce9f7"
MUTED = "#8da8c2"
GREEN = "#00f58b"
GREEN_DARK = "#00c978"
YELLOW = "#ffd43b"
RED = "#ff5b61"
BLUE = "#39a9ff"


class InvestigatorLogin:
    def __init__(self, root):
        self.root = root
        self.authenticated = False
        self.investigator_id = None

        root.title("WatchX - Investigator Login")
        root.geometry("560x650")
        root.resizable(False, False)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        self.build()

    def build(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(pady=(35, 12))

        try:
            img = Image.open(LOGO_FILE).convert("RGBA")
            img.thumbnail((125, 125))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(top, image=self.logo, bg=BG).pack()
        except Exception:
            tk.Label(
                top, text="WATCHX", font=("Arial", 30, "bold"),
                fg=GREEN, bg=BG
            ).pack()

        tk.Label(
            self.root, text="WatchX", font=("Arial", 34, "bold"),
            fg=GREEN, bg=BG
        ).pack()

        tk.Label(
            self.root, text="AI Vehicle Investigation System",
            font=("Arial", 14), fg=WHITE, bg=BG
        ).pack(pady=(0, 25))

        card = tk.Frame(self.root, bg=CARD, width=440, height=330)
        card.pack(padx=50)
        card.pack_propagate(False)

        tk.Label(
            card, text="INVESTIGATOR LOGIN",
            font=("Arial", 20, "bold"), fg=WHITE, bg=CARD
        ).pack(pady=(25, 22))

        tk.Label(
            card, text="Investigator ID", font=("Arial", 11, "bold"),
            fg=TEXT, bg=CARD
        ).pack(anchor="w", padx=45)

        self.id_entry = tk.Entry(
            card, font=("Arial", 14), bg="#f7fafc",
            fg="#111827", relief="flat"
        )
        self.id_entry.pack(fill="x", padx=45, ipady=9, pady=(5, 17))

        tk.Label(
            card, text="Password", font=("Arial", 11, "bold"),
            fg=TEXT, bg=CARD
        ).pack(anchor="w", padx=45)

        self.password_entry = tk.Entry(
            card, font=("Arial", 14), bg="#f7fafc",
            fg="#111827", show="*", relief="flat"
        )
        self.password_entry.pack(fill="x", padx=45, ipady=9, pady=(5, 20))

        tk.Button(
            card, text="ACCESS INVESTIGATION DASHBOARD",
            command=self.authenticate,
            font=("Arial", 12, "bold"),
            bg=GREEN, fg="#06111d",
            activebackground=GREEN_DARK,
            relief="flat", cursor="hand2"
        ).pack(fill="x", padx=45, ipady=10)

        self.status = tk.Label(
            card, text="Authorized investigators only",
            font=("Arial", 9), fg=MUTED, bg=CARD
        )
        self.status.pack(pady=12)

        self.password_entry.bind("<Return>", lambda e: self.authenticate())
        self.id_entry.focus()

    def authenticate(self):
        investigator_id = self.id_entry.get().strip().upper()
        password = self.password_entry.get()

        if investigator_id not in AUTHORIZED_INVESTIGATORS:
            self.status.config(
                text="ACCESS DENIED — Unauthorized Investigator ID",
                fg=RED
            )
            messagebox.showerror(
                "WatchX Security",
                "This Investigator ID is not authorized."
            )
            return

        if password != AUTHORIZED_INVESTIGATORS[investigator_id]:
            self.status.config(
                text="ACCESS DENIED — Incorrect password",
                fg=RED
            )
            messagebox.showerror(
                "WatchX Security",
                "Incorrect password."
            )
            return

        self.authenticated = True
        self.investigator_id = investigator_id
        self.status.config(text="Authentication successful", fg=GREEN)
        self.root.destroy()


class WatchXDashboard:
    def __init__(self, root, investigator_id):
        self.root = root
        self.investigator_id = investigator_id
        self.records = []
        self.last_csv_signature = None

        root.title("WatchX - AI Vehicle Investigation Dashboard")
        root.geometry("1450x900")
        root.minsize(1100, 700)
        root.configure(bg=BG)

        self.create_styles()
        self.create_interface()
        self.load_records()
        self.auto_refresh()

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------
    def create_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "WatchX.Treeview",
            background=TABLE_BG,
            foreground=TEXT,
            fieldbackground=TABLE_BG,
            rowheight=40,
            font=("Arial", 10),
            borderwidth=0
        )
        style.configure(
            "WatchX.Treeview.Heading",
            background="#173452",
            foreground=WHITE,
            font=("Arial", 10, "bold"),
            padding=11
        )
        style.map(
            "WatchX.Treeview",
            background=[("selected", "#075e43")],
            foreground=[("selected", WHITE)]
        )

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------
    def create_interface(self):
        header = tk.Frame(self.root, bg=HEADER, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            img = Image.open(LOGO_FILE).convert("RGBA")
            img.thumbnail((70, 70))
            self.dashboard_logo = ImageTk.PhotoImage(img)
            tk.Label(
                header, image=self.dashboard_logo, bg=HEADER
            ).pack(side="left", padx=(28, 15), pady=15)
        except Exception:
            pass

        title_box = tk.Frame(header, bg=HEADER)
        title_box.pack(side="left", pady=13)

        tk.Label(
            title_box, text="WatchX",
            font=("Arial", 28, "bold"), fg=GREEN, bg=HEADER
        ).pack(anchor="w")

        tk.Label(
            title_box, text="AI Vehicle Investigation Dashboard",
            font=("Arial", 13), fg=TEXT, bg=HEADER
        ).pack(anchor="w")

        investigator = tk.Frame(header, bg=HEADER)
        investigator.pack(side="right", padx=30)

        tk.Label(
            investigator, text="AUTHORIZED INVESTIGATOR",
            font=("Arial", 8, "bold"), fg=MUTED, bg=HEADER
        ).pack(anchor="e")

        tk.Label(
            investigator, text=self.investigator_id,
            font=("Arial", 13, "bold"), fg=GREEN, bg=HEADER
        ).pack(anchor="e")

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # Summary cards
        summary = tk.Frame(body, bg=BG)
        summary.pack(fill="x", padx=25, pady=20)

        self.vehicle_count = tk.StringVar(value="0")
        self.plate_count = tk.StringVar(value="0")
        self.avg_confidence = tk.StringVar(value="0%")
        self.high_confidence = tk.StringVar(value="0")

        self.create_card(
            summary, "RECORDED VEHICLE EVENTS",
            self.vehicle_count, "Total detection records"
        )
        self.create_card(
            summary, "UNIQUE NUMBER PLATES",
            self.plate_count, "Distinct OCR plates"
        )
        self.create_card(
            summary, "AVG OCR CONFIDENCE",
            self.avg_confidence, "Average recognition confidence"
        )
        self.create_card(
            summary, "HIGH CONFIDENCE RECORDS",
            self.high_confidence, "Confidence ≥ 80%"
        )

        # Search / controls
        controls = tk.Frame(body, bg=CARD)
        controls.pack(fill="x", padx=25, pady=(0, 15))

        tk.Label(
            controls, text="SEARCH",
            font=("Arial", 10, "bold"),
            fg=GREEN, bg=CARD
        ).pack(side="left", padx=(20, 10), pady=15)

        self.search_entry = tk.Entry(
            controls, font=("Arial", 12),
            bg="#f7fafc", fg="#111827", relief="flat"
        )
        self.search_entry.pack(
            side="left", fill="x", expand=True, ipady=9, pady=8
        )
        self.search_entry.bind("<KeyRelease>", self.search_records)

        tk.Button(
            controls, text="↻  REFRESH",
            command=self.load_records,
            font=("Arial", 10, "bold"),
            bg=GREEN, fg="#06111d",
            activebackground=GREEN_DARK,
            relief="flat", cursor="hand2", padx=20
        ).pack(side="right", padx=10)

        tk.Button(
            controls, text="CLEAR",
            command=self.clear_search,
            font=("Arial", 10, "bold"),
            bg=CARD2, fg=WHITE,
            activebackground="#1c3b5d",
            relief="flat", cursor="hand2", padx=15
        ).pack(side="right", padx=(0, 5))

        # Table title
        table_title = tk.Frame(body, bg=BG)
        table_title.pack(fill="x", padx=25)

        tk.Label(
            table_title, text="VEHICLE DETECTION RECORDS",
            font=("Arial", 14, "bold"), fg=WHITE, bg=BG
        ).pack(side="left")

        self.record_status = tk.Label(
            table_title, text="0 records",
            font=("Arial", 10), fg=MUTED, bg=BG
        )
        self.record_status.pack(side="right")

        # Table
        table_frame = tk.Frame(body, bg=TABLE_BG)
        table_frame.pack(
            fill="both", expand=True, padx=25, pady=(8, 10)
        )

        columns = (
            "time", "frame", "vehicle_id", "vehicle_type",
            "plate", "confidence", "votes"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="WatchX.Treeview",
            selectmode="browse"
        )

        headings = {
            "time": "TIME (SEC)",
            "frame": "FRAME",
            "vehicle_id": "VEHICLE ID",
            "vehicle_type": "VEHICLE TYPE",
            "plate": "NUMBER PLATE",
            "confidence": "OCR CONFIDENCE",
            "votes": "VOTES"
        }

        widths = {
            "time": 120,
            "frame": 110,
            "vehicle_id": 130,
            "vehicle_type": 170,
            "plate": 220,
            "confidence": 170,
            "votes": 100
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(
                col, width=widths[col],
                anchor="center", minwidth=80
            )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("even", background=TABLE_BG)
        self.tree.tag_configure("odd", background=TABLE_ALT)
        self.tree.tag_configure(
            "high", background="#0b4a38", foreground=GREEN
        )
        self.tree.tag_configure(
            "medium", background="#4b3d08", foreground=YELLOW
        )
        self.tree.tag_configure(
            "low", background="#4a2025", foreground="#ff9a9f"
        )

        self.tree.bind("<Double-1>", self.show_vehicle_details)

        # Help text
        tk.Label(
            body,
            text="Double-click any record to open the vehicle investigation.",
            font=("Arial", 9),
            fg=MUTED, bg=BG
        ).pack(pady=(0, 8))

        footer = tk.Frame(self.root, bg="#050b14", height=40)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        self.status = tk.Label(
            footer, text="Ready",
            anchor="w", font=("Arial", 9),
            fg=MUTED, bg="#050b14"
        )
        self.status.pack(side="left", padx=20)

        tk.Label(
            footer, text="WatchX • AI Vehicle Investigation",
            font=("Arial", 9), fg=MUTED, bg="#050b14"
        ).pack(side="right", padx=20)

    # --------------------------------------------------------
    # SUMMARY CARD
    # --------------------------------------------------------
    def create_card(self, parent, title, variable, description):
        frame = tk.Frame(
            parent, bg=CARD, width=280, height=110
        )
        frame.pack(
            side="left", fill="both", expand=True, padx=7
        )
        frame.pack_propagate(False)

        tk.Frame(
            frame, bg=GREEN, width=4
        ).pack(side="left", fill="y")

        content = tk.Frame(frame, bg=CARD)
        content.pack(fill="both", expand=True, padx=15)

        tk.Label(
            content, text=title,
            font=("Arial", 9, "bold"),
            fg=MUTED, bg=CARD
        ).pack(anchor="w", pady=(13, 0))

        tk.Label(
            content, textvariable=variable,
            font=("Arial", 25, "bold"),
            fg=WHITE, bg=CARD
        ).pack(anchor="w")

        tk.Label(
            content, text=description,
            font=("Arial", 8),
            fg=MUTED, bg=CARD
        ).pack(anchor="w")

    # --------------------------------------------------------
    # CSV LOADING
    # --------------------------------------------------------
    def get_csv_signature(self):
        if not CSV_FILE.exists():
            return None
        try:
            stat = CSV_FILE.stat()
            return (stat.st_mtime_ns, stat.st_size)
        except Exception:
            return None

    def load_records(self):
        if not CSV_FILE.exists():
            self.records = []
            self.display_records([])
            self.update_summary()
            self.record_status.config(text="0 records")
            self.status.config(
                text=f"Waiting for records: {CSV_FILE.name}"
            )
            self.last_csv_signature = None
            return

        try:
            new_records = []

            with open(
                CSV_FILE, "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                for row in reader:
                    if row and any(
                        str(value).strip() for value in row.values()
                    ):
                        new_records.append(row)

            self.records = new_records
            self.last_csv_signature = self.get_csv_signature()

            query = self.search_entry.get().strip()
            if query:
                self.search_records()
            else:
                self.display_records(self.records)

            self.update_summary()

            self.status.config(
                text=(
                    f"Loaded {len(self.records)} records • "
                    f"Last updated {datetime.now().strftime('%H:%M:%S')}"
                )
            )

        except PermissionError:
            self.status.config(
                text="CSV is currently being written — waiting..."
            )
        except Exception as e:
            self.status.config(text=f"CSV read error: {e}")

    # --------------------------------------------------------
    # AUTOMATIC LIVE REFRESH
    # --------------------------------------------------------
    def auto_refresh(self):
        try:
            signature = self.get_csv_signature()

            if signature != self.last_csv_signature:
                self.load_records()

        except Exception:
            pass

        # Check every 2 seconds while dashboard is open.
        self.root.after(2000, self.auto_refresh)

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------
    def display_records(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, row in enumerate(records):
            confidence_value = self.normalized_confidence(
                row.get("ocr_confidence", "")
            )

            if confidence_value >= 0.80:
                tag = "high"
            elif confidence_value >= 0.60:
                tag = "medium"
            else:
                tag = "low"

            self.tree.insert(
                "",
                "end",
                values=(
                    row.get("time_seconds", ""),
                    row.get("frame", ""),
                    row.get("vehicle_id", ""),
                    row.get("vehicle_type", ""),
                    row.get("plate", ""),
                    self.format_confidence(confidence_value),
                    row.get("votes", "")
                ),
                tags=(tag,)
            )

        self.record_status.config(
            text=f"{len(records)} records"
        )

    def normalized_confidence(self, value):
        try:
            number = float(str(value).strip())
            if number > 1:
                number /= 100
            return max(0.0, min(1.0, number))
        except Exception:
            return 0.0

    def format_confidence(self, value):
        return f"{value * 100:.1f}%"

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------
    def update_summary(self):
        if not self.records:
            self.vehicle_count.set("0")
            self.plate_count.set("0")
            self.avg_confidence.set("0%")
            self.high_confidence.set("0")
            return

        self.vehicle_count.set(str(len(self.records)))

        plates = {
            str(row.get("plate", "")).strip().upper()
            for row in self.records
            if str(row.get("plate", "")).strip()
        }
        self.plate_count.set(str(len(plates)))

        confidences = [
            self.normalized_confidence(row.get("ocr_confidence", ""))
            for row in self.records
            if str(row.get("ocr_confidence", "")).strip()
        ]

        if confidences:
            average = sum(confidences) / len(confidences)
            self.avg_confidence.set(f"{average * 100:.1f}%")
            self.high_confidence.set(
                str(sum(1 for value in confidences if value >= 0.80))
            )
        else:
            self.avg_confidence.set("0%")
            self.high_confidence.set("0")

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------
    def search_records(self, event=None):
        query = self.search_entry.get().strip().upper()

        if not query:
            self.display_records(self.records)
            self.status.config(
                text=f"Showing all {len(self.records)} records"
            )
            return

        filtered = []

        for row in self.records:
            searchable = " ".join([
                str(row.get("vehicle_id", "")),
                str(row.get("plate", "")),
                str(row.get("vehicle_type", "")),
                str(row.get("time_seconds", "")),
                str(row.get("frame", ""))
            ]).upper()

            if query in searchable:
                filtered.append(row)

        self.display_records(filtered)
        self.status.config(
            text=f"Search results: {len(filtered)} records"
        )

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.display_records(self.records)
        self.status.config(
            text=f"Showing all {len(self.records)} records"
        )

    # --------------------------------------------------------
    # VEHICLE INVESTIGATION DETAILS
    # --------------------------------------------------------
    def show_vehicle_details(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0]).get("values", [])

        if len(values) < 7:
            return

        time_seconds, frame, vehicle_id, vehicle_type, plate, confidence, votes = values

        # ----------------------------------------------------
        # FIND ALL RECORDS FOR THIS VEHICLE ID
        # ----------------------------------------------------
        vehicle_history = []

        for row in self.records:
            if str(row.get("vehicle_id", "")).strip() == str(vehicle_id).strip():
                vehicle_history.append(row)

        def get_time(row):
            try:
                return float(row.get("time_seconds", 0))
            except Exception:
                return 0.0

        vehicle_history.sort(key=get_time)

        # ----------------------------------------------------
        # INVESTIGATION STATISTICS
        # ----------------------------------------------------
        total_detections = len(vehicle_history)

        plates_seen = []

        for row in vehicle_history:
            current_plate = str(row.get("plate", "")).strip().upper()

            if current_plate and current_plate not in plates_seen:
                plates_seen.append(current_plate)

        confidence_values = [
            self.normalized_confidence(row.get("ocr_confidence", ""))
            for row in vehicle_history
        ]

        best_confidence = max(confidence_values) if confidence_values else 0.0

        first_detection = get_time(vehicle_history[0]) if vehicle_history else 0.0
        last_detection = get_time(vehicle_history[-1]) if vehicle_history else 0.0

        # ----------------------------------------------------
        # EVIDENCE DIRECTORIES
        # ----------------------------------------------------
        evidence_dir = BASE_DIR / "evidence"
        vehicle_evidence_dir = evidence_dir / "vehicles"
        plate_evidence_dir = evidence_dir / "plates"

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------
        details = tk.Toplevel(self.root)
        details.title("WatchX - Vehicle Investigation")
        details.geometry("1100x700")
        details.minsize(900, 600)
        details.resizable(True, True)
        details.state("normal")
        details.configure(bg=BG)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------
        header = tk.Frame(details, bg=HEADER, height=105)
        header.pack(fill="x")
        header.pack_propagate(False)

        try:
            img = Image.open(LOGO_FILE).convert("RGBA")
            img.thumbnail((65, 65))
            details_logo = ImageTk.PhotoImage(img)
            details.logo_ref = details_logo

            tk.Label(
                header,
                image=details_logo,
                bg=HEADER
            ).pack(side="left", padx=(25, 18), pady=18)

        except Exception:
            pass

        title_box = tk.Frame(header, bg=HEADER)
        title_box.pack(side="left", pady=15)

        tk.Label(
            title_box,
            text="VEHICLE INVESTIGATION",
            font=("Arial", 23, "bold"),
            fg=GREEN,
            bg=HEADER
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text=f"Vehicle ID {vehicle_id}  •  {vehicle_type}",
            font=("Arial", 11),
            fg=TEXT,
            bg=HEADER
        ).pack(anchor="w", pady=(3, 0))

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------
        main = tk.Frame(details, bg=BG)
        main.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # STATUS BAR
        # ----------------------------------------------------
        status_box = tk.Frame(main, bg="#083d2c")
        status_box.pack(fill="x", padx=25, pady=(18, 12))

        tk.Label(
            status_box,
            text="✓  VEHICLE RECORD UNDER INVESTIGATION",
            font=("Arial", 14, "bold"),
            fg=GREEN,
            bg="#083d2c"
        ).pack(pady=10)

        # ----------------------------------------------------
        # SUMMARY CARDS
        # ----------------------------------------------------
        summary = tk.Frame(main, bg=BG)
        summary.pack(fill="x", padx=20, pady=(0, 12))

        def create_investigation_card(parent, title, value, description):
            card = tk.Frame(parent, bg=CARD, height=85)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.pack_propagate(False)

            tk.Frame(
                card,
                bg=GREEN,
                width=4
            ).pack(side="left", fill="y")

            content = tk.Frame(card, bg=CARD)
            content.pack(fill="both", expand=True, padx=12)

            tk.Label(
                content,
                text=title,
                font=("Arial", 8, "bold"),
                fg=MUTED,
                bg=CARD
            ).pack(anchor="w", pady=(8, 0))

            tk.Label(
                content,
                text=value,
                font=("Arial", 18, "bold"),
                fg=WHITE,
                bg=CARD
            ).pack(anchor="w")

            tk.Label(
                content,
                text=description,
                font=("Arial", 7),
                fg=MUTED,
                bg=CARD
            ).pack(anchor="w")

        create_investigation_card(
            summary,
            "TOTAL DETECTIONS",
            str(total_detections),
            "Tracked appearances"
        )

        create_investigation_card(
            summary,
            "PLATES OBSERVED",
            str(len(plates_seen)),
            "OCR results detected"
        )

        create_investigation_card(
            summary,
            "BEST OCR CONFIDENCE",
            f"{best_confidence * 100:.1f}%",
            "Highest recognition confidence"
        )

        create_investigation_card(
            summary,
            "TIME SPAN",
            f"{max(0, last_detection - first_detection):.2f}s",
            "Between first and last detection"
        )

        # ----------------------------------------------------
        # VISUAL EVIDENCE
        # ----------------------------------------------------
        evidence_title = tk.Frame(main, bg=BG)
        evidence_title.pack(fill="x", padx=25)

        tk.Label(
            evidence_title,
            text="VISUAL EVIDENCE",
            font=("Arial", 13, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(side="left")

        evidence_event_label = tk.Label(
            evidence_title,
            text=f"Frame {frame}  •  {time_seconds} sec  •  {plate}",
            font=("Arial", 9),
            fg=MUTED,
            bg=BG
        )
        evidence_event_label.pack(side="right")

        evidence_section = tk.Frame(main, bg=BG)
        evidence_section.pack(fill="x", padx=25, pady=(6, 12))

        vehicle_panel = tk.Frame(
            evidence_section,
            bg=CARD,
            height=210
        )
        vehicle_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )
        vehicle_panel.pack_propagate(False)

        tk.Label(
            vehicle_panel,
            text="DETECTED VEHICLE",
            font=("Arial", 10, "bold"),
            fg=GREEN,
            bg=CARD
        ).pack(anchor="w", padx=12, pady=(8, 4))

        vehicle_image_holder = tk.Frame(
            vehicle_panel,
            bg="#07111f"
        )
        vehicle_image_holder.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        plate_panel = tk.Frame(
            evidence_section,
            bg=CARD,
            height=210
        )
        plate_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )
        plate_panel.pack_propagate(False)

        tk.Label(
            plate_panel,
            text="NUMBER PLATE",
            font=("Arial", 10, "bold"),
            fg=GREEN,
            bg=CARD
        ).pack(anchor="w", padx=12, pady=(8, 4))

        plate_image_holder = tk.Frame(
            plate_panel,
            bg="#07111f"
        )
        plate_image_holder.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        def clear_holder(holder):
            for child in holder.winfo_children():
                child.destroy()

        def show_image_or_message(holder, image_path, empty_text, max_size):
            clear_holder(holder)

            if image_path is not None and image_path.exists():
                try:
                    evidence_image = Image.open(image_path).convert("RGB")
                    evidence_image.thumbnail(max_size)

                    photo = ImageTk.PhotoImage(evidence_image)

                    if not hasattr(details, "_evidence_images"):
                        details._evidence_images = []

                    details._evidence_images.append(photo)

                    if len(details._evidence_images) > 8:
                        details._evidence_images = details._evidence_images[-8:]

                    tk.Label(
                        holder,
                        image=photo,
                        bg="#07111f"
                    ).pack(expand=True)

                    return

                except Exception:
                    pass

            tk.Label(
                holder,
                text=empty_text,
                font=("Arial", 10),
                fg=MUTED,
                bg="#07111f"
            ).pack(expand=True)

        def update_evidence(selected_time, selected_frame, selected_plate):
            selected_frame_text = str(selected_frame).strip()
            selected_plate_text = str(selected_plate).strip().upper()

            vehicle_path = (
                vehicle_evidence_dir
                / f"vehicle_{vehicle_id}_frame_{selected_frame_text}.jpg"
            )

            plate_candidates = list(
                plate_evidence_dir.glob(
                    f"plate_{vehicle_id}_frame_{selected_frame_text}_*.jpg"
                )
            )

            plate_path = None

            for candidate in plate_candidates:
                if selected_plate_text and selected_plate_text in candidate.stem.upper():
                    plate_path = candidate
                    break

            if plate_path is None and plate_candidates:
                plate_path = plate_candidates[0]

            show_image_or_message(
                vehicle_image_holder,
                vehicle_path,
                "Vehicle evidence not available",
                (500, 160)
            )

            show_image_or_message(
                plate_image_holder,
                plate_path,
                "Number-plate evidence not available",
                (500, 160)
            )

            evidence_event_label.config(
                text=(
                    f"Frame {selected_frame_text}  •  "
                    f"{selected_time} sec  •  "
                    f"{selected_plate}"
                )
            )

        # ----------------------------------------------------
        # CURRENT DETECTION INFORMATION
        # ----------------------------------------------------
        current_section = tk.Frame(main, bg=CARD)
        current_section.pack(fill="x", padx=25, pady=(0, 12))

        tk.Label(
            current_section,
            text="CURRENT DETECTION",
            font=("Arial", 11, "bold"),
            fg=GREEN,
            bg=CARD
        ).pack(anchor="w", padx=18, pady=(8, 5))

        current_grid = tk.Frame(current_section, bg=CARD)
        current_grid.pack(fill="x", padx=15, pady=(0, 8))

        current_information = [
            ("Vehicle ID", vehicle_id),
            ("Vehicle Type", vehicle_type),
            ("Number Plate", plate),
            ("OCR Confidence", confidence),
            ("Detection Votes", votes),
            ("Time Detected", f"{time_seconds} seconds"),
            ("Video Frame", frame),
            ("Investigator", self.investigator_id)
        ]

        for index, (label, value) in enumerate(current_information):
            row = index // 4
            column = index % 4

            cell = tk.Frame(current_grid, bg=CARD)
            cell.grid(
                row=row,
                column=column,
                sticky="w",
                padx=10,
                pady=4
            )

            tk.Label(
                cell,
                text=label,
                font=("Arial", 8, "bold"),
                fg=MUTED,
                bg=CARD
            ).pack(anchor="w")

            tk.Label(
                cell,
                text=str(value),
                font=("Arial", 9, "bold"),
                fg=WHITE,
                bg=CARD
            ).pack(anchor="w", pady=(1, 0))

        # ----------------------------------------------------
        # DETECTION HISTORY
        # ----------------------------------------------------
        history_title = tk.Frame(main, bg=BG)
        history_title.pack(fill="x", padx=25)

        tk.Label(
            history_title,
            text="DETECTION HISTORY",
            font=("Arial", 12, "bold"),
            fg=WHITE,
            bg=BG
        ).pack(side="left")

        tk.Label(
            history_title,
            text=f"{total_detections} events for Vehicle ID {vehicle_id}",
            font=("Arial", 9),
            fg=MUTED,
            bg=BG
        ).pack(side="right")

        history_frame = tk.Frame(main, bg=TABLE_BG, height=170)
        history_frame.pack(
            fill="x",
            padx=25,
            pady=(5, 10)
        )
        history_frame.pack_propagate(False)

        history_columns = (
            "time",
            "frame",
            "plate",
            "confidence",
            "votes"
        )

        history_tree = ttk.Treeview(
            history_frame,
            columns=history_columns,
            show="headings",
            style="WatchX.Treeview",
            selectmode="browse"
        )

        history_headings = {
            "time": "TIME (SEC)",
            "frame": "FRAME",
            "plate": "NUMBER PLATE",
            "confidence": "OCR CONFIDENCE",
            "votes": "VOTES"
        }

        history_widths = {
            "time": 140,
            "frame": 140,
            "plate": 260,
            "confidence": 220,
            "votes": 120
        }

        for col in history_columns:
            history_tree.heading(
                col,
                text=history_headings[col]
            )

            history_tree.column(
                col,
                width=history_widths[col],
                anchor="center",
                minwidth=90
            )

        history_scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=history_tree.yview
        )

        history_tree.configure(
            yscrollcommand=history_scrollbar.set
        )

        history_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        history_scrollbar.pack(
            side="right",
            fill="y"
        )

        for row in vehicle_history:
            confidence_value = self.normalized_confidence(
                row.get("ocr_confidence", "")
            )

            if confidence_value >= 0.80:
                tag = "high"
            elif confidence_value >= 0.60:
                tag = "medium"
            else:
                tag = "low"

            history_tree.insert(
                "",
                "end",
                values=(
                    row.get("time_seconds", ""),
                    row.get("frame", ""),
                    row.get("plate", ""),
                    self.format_confidence(confidence_value),
                    row.get("votes", "")
                ),
                tags=(tag,)
            )

        # ----------------------------------------------------
        # CLICK HISTORY ROW -> CHANGE VISUAL EVIDENCE
        # ----------------------------------------------------
        def on_history_select(event=None):
            selected_history = history_tree.selection()

            if not selected_history:
                return

            history_values = history_tree.item(
                selected_history[0]
            ).get("values", [])

            if len(history_values) < 3:
                return

            update_evidence(
                history_values[0],
                history_values[1],
                history_values[2]
            )

        history_tree.bind(
            "<<TreeviewSelect>>",
            on_history_select
        )

        # Show the original dashboard selection immediately.
        update_evidence(
            time_seconds,
            frame,
            plate
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------
        footer = tk.Frame(details, bg="#050b14", height=52)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text=(
                f"WatchX Investigation • "
                f"Vehicle ID {vehicle_id} • "
                f"Investigator {self.investigator_id}"
            ),
            font=("Arial", 9),
            fg=MUTED,
            bg="#050b14"
        ).pack(side="left", padx=20)

        tk.Button(
            footer,
            text="CLOSE INVESTIGATION",
            command=details.destroy,
            font=("Arial", 10, "bold"),
            bg=GREEN,
            fg="#06111d",
            activebackground=GREEN_DARK,
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=7
        ).pack(side="right", padx=20)




# ============================================================
# START WATCHX DASHBOARD
# ============================================================

if __name__ == "__main__":
    login_root = tk.Tk()
    login = InvestigatorLogin(login_root)
    login_root.mainloop()

    if login.authenticated:
        dashboard_root = tk.Tk()
        app = WatchXDashboard(
            dashboard_root,
            login.investigator_id
        )
        dashboard_root.mainloop()
