import csv
import math
import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import analyze

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "study_data.csv"
BG = "#101827"
PANEL = "#1c293c"
TEXT = "#edf3fc"
MUTED = "#a4b5ce"
ACCENT = "#67d4bc"


def load_sessions(filename):
    """Validate stored records before allowing edits."""
    if not filename.exists():
        return []
    with filename.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["date", "course", "hours"]:
            raise ValueError("CSV header must be date,course,hours (in that order).")
        sessions = []
        for line, row in enumerate(reader, 2):
            try:
                day = date.fromisoformat(row["date"])
                hours = float(row["hours"])
                course = row["course"].strip()
                if not course or not math.isfinite(hours) or hours < 0:
                    raise ValueError
                sessions.append({"date": day.isoformat(), "course": course, "hours": hours})
            except (ValueError, TypeError, KeyError, AttributeError) as error:
                raise ValueError(f"Invalid study session on CSV line {line}.") from error
        return sessions


def save_sessions(filename, sessions):
    """Replace the CSV only after its new contents have been written."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8",
                                         dir=filename.parent, delete=False) as file:
            temporary = Path(file.name)
            writer = csv.DictWriter(file, fieldnames=["date", "course", "hours"])
            writer.writeheader()
            writer.writerows(sessions)
        os.replace(temporary, filename)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def week_start(day):
    return day - timedelta(days=day.weekday())


class StudyDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Study Analyzer")
        self.geometry("1180x850")
        self.minsize(980, 760)
        self.configure(bg=BG)
        self.sessions = []
        self.week_map = {}
        self.configure_styles()
        self.build_interface()
        self.refresh()

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Arial", 11))
        style.configure("Title.TLabel", font=("Arial", 26, "bold"))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("TButton", font=("Arial", 11), padding=9,
                        background=PANEL, foreground=TEXT)
        style.map("TButton", background=[("active", "#304660")])
        style.configure("Accent.TButton", background=ACCENT, foreground=BG)
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=29, borderwidth=0, font=("Arial", 11))
        style.configure("Treeview.Heading", background="#293b53", foreground=TEXT,
                        font=("Arial", 11, "bold"))
        style.map("Treeview", background=[("selected", "#365b78")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 9), background=PANEL, foreground=TEXT)
        style.map("TNotebook.Tab", background=[("selected", "#365b78")])

    def build_interface(self):
        outer = ttk.Frame(self, padding=24)
        outer.pack(fill="both", expand=True)
        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="Study Analyzer", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Refresh", command=self.refresh).pack(side="right")
        ttk.Label(outer, text="Build your routine. See your progress.",
                  style="Muted.TLabel").pack(anchor="w", pady=(4, 18))

        filters = ttk.Frame(outer)
        filters.pack(fill="x", pady=(0, 16))
        ttk.Label(filters, text="Report period").pack(side="left", padx=(0, 10))
        self.period = tk.StringVar(value="All time")
        self.period_box = ttk.Combobox(filters, textvariable=self.period,
                                      state="readonly", width=33)
        self.period_box.pack(side="left")
        self.period_box.bind("<<ComboboxSelected>>", lambda event: self.render())
        ttk.Label(filters, text="Weekly goal (hours)").pack(side="left", padx=(24, 8))
        self.goal = tk.StringVar(value="20")
        ttk.Entry(filters, textvariable=self.goal, width=7).pack(side="left")
        ttk.Button(filters, text="Apply", command=self.render).pack(side="left", padx=8)

        cards = ttk.Frame(outer)
        cards.pack(fill="x")
        self.metrics = []
        for index, label in enumerate(("STUDY HOURS", "SESSIONS", "TOP COURSE", "HOURS / STUDY DAY")):
            cards.columnconfigure(index, weight=1, uniform="card")
            card = tk.Frame(cards, bg=PANEL, padx=16, pady=14)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10 if index < 3 else 0))
            tk.Label(card, text=label, bg=PANEL, fg=MUTED,
                     font=("Arial", 9, "bold")).pack(anchor="w")
            value = tk.Label(card, text="—", bg=PANEL, fg=TEXT, font=("Arial", 22, "bold"))
            value.pack(anchor="w", pady=(8, 0))
            self.metrics.append(value)

        self.progress_text = ttk.Label(outer, style="Muted.TLabel")
        self.progress_text.pack(anchor="w", pady=(15, 5))
        self.progress = ttk.Progressbar(outer, maximum=100)
        self.progress.pack(fill="x", pady=(0, 15))

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        chart_tab = ttk.Frame(notebook)
        session_tab = ttk.Frame(notebook, padding=12)
        notebook.add(chart_tab, text="Overview & charts")
        notebook.add(session_tab, text="Study sessions")
        self.figure = Figure(figsize=(10, 4), dpi=100, facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_tab)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        table_frame = ttk.Frame(session_tab)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=("date", "course", "hours"),
                                  show="headings", selectmode="browse")
        for key, title in (("date", "Date"), ("course", "Course"), ("hours", "Hours")):
            self.table.heading(key, text=title)
            self.table.column(key, width=180, anchor="w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        ttk.Button(session_tab, text="Delete selected session", command=self.delete_session).pack(anchor="e", pady=(10, 0))

        form = ttk.Frame(outer)
        form.pack(fill="x", pady=(18, 0))
        self.day = tk.StringVar(value=date.today().isoformat())
        self.course = tk.StringVar()
        self.hours = tk.StringVar()
        for col, (label, variable, width) in enumerate((("Date · YYYY-MM-DD", self.day, 18),
                                                        ("Course", self.course, 22),
                                                        ("Hours", self.hours, 10))):
            field = ttk.Frame(form)
            field.grid(row=0, column=col, padx=(0, 14), sticky="w")
            ttk.Label(field, text=label).pack(anchor="w", pady=(0, 5))
            ttk.Entry(field, textvariable=variable, width=width).pack()
        ttk.Button(form, text="+ Add session", style="Accent.TButton",
                   command=self.add_session).grid(row=0, column=3, sticky="s")
        self.status = ttk.Label(outer, text=f"Data: {DATA_FILE}", style="Muted.TLabel")
        self.status.pack(anchor="w", pady=(12, 0))

    def refresh(self):
        try:
            sessions = load_sessions(DATA_FILE)
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not load data", str(error))
            return
        self.sessions = sessions
        starts = sorted({week_start(date.fromisoformat(s["date"])) for s in sessions}, reverse=True)
        self.week_map = {f"{start} → {start + timedelta(days=6)}": start for start in starts}
        self.period_box["values"] = ["All time", *self.week_map]
        if self.period.get() not in ["All time", *self.week_map]:
            self.period.set("All time")
        self.render()

    def filtered_sessions(self):
        monday = self.week_map.get(self.period.get())
        return [(index, s) for index, s in enumerate(self.sessions)
                if monday is None or week_start(date.fromisoformat(s["date"])) == monday]

    def render(self):
        try:
            goal = float(self.goal.get())
            if not math.isfinite(goal) or goal <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid goal", "Enter a finite weekly goal greater than zero.")
            return
        indexed = self.filtered_sessions()
        data = [s for _, s in indexed]
        course_hours = analyze.hours_per_course(data)
        top, _ = analyze.most_studied_course(course_hours)
        values = (f"{analyze.calculate_total_hours(data):.1f}", str(len(data)),
                  top or "—", f"{analyze.average_daily_hours(data):.2f}")
        for label, value in zip(self.metrics, values):
            label.config(text=value)
        monday = self.week_map.get(self.period.get(), week_start(date.today()))
        total = sum(s["hours"] for s in data if week_start(date.fromisoformat(s["date"])) == monday)
        percent = total / goal * 100
        prefix = "Current week" if self.period.get() == "All time" else "Selected week"
        self.progress_text.config(text=f"{prefix}: {total:g} / {goal:g} hours · {percent:.0f}% · "
                                  + ("Goal reached!" if total >= goal else f"{goal-total:g} hours remaining"))
        self.progress["value"] = min(percent, 100)
        self.table.delete(*self.table.get_children())
        for index, s in sorted(indexed, key=lambda item: item[1]["date"], reverse=True):
            self.table.insert("", "end", iid=str(index), values=(s["date"], s["course"], f'{s["hours"]:g}'))
        self.draw_charts(data, course_hours, goal)

    def draw_charts(self, data, course_hours, goal):
        self.figure.clear()
        if not data:
            self.figure.text(.5, .5, "Your next study session starts here.\nAdd one below to see your progress.",
                             ha="center", va="center", color=MUTED, fontsize=15)
            self.canvas.draw_idle()
            return
        left, right = self.figure.subplots(1, 2)
        for ax in (left, right):
            ax.set_facecolor(BG)
            ax.tick_params(colors=MUTED, labelsize=9)
            ax.spines[["top", "right"]].set_visible(False)
            for spine in ax.spines.values():
                spine.set_color("#3a4b61")
            ax.set_axisbelow(True)
            ax.grid(axis="y", color=PANEL)
        left.bar(list(course_hours), list(course_hours.values()), color=ACCENT, width=.6)
        left.set_title("Hours by course", color=TEXT, loc="left", pad=18)
        left.tick_params(axis="x", rotation=30)
        if self.period.get() == "All time":
            weekly = analyze.hours_per_week(data)
            labels = [str(day) for day in weekly]
            totals = list(weekly.values())
            right.bar(range(len(labels)), totals,
                      color=[ACCENT if h >= goal else "#7ca9ef" for h in totals])
            step = max(1, math.ceil(len(labels) / 6))
            right.set_xticks(list(range(0, len(labels), step)), labels[::step], rotation=30, ha="right")
            right.axhline(goal, color="#f2bb72", linestyle="--", label=f"Goal: {goal:g}h")
            right.legend(facecolor=PANEL, labelcolor=TEXT)
            right.set_title("Weekly progress · Monday start", color=TEXT, loc="left", pad=18)
        else:
            monday = self.week_map[self.period.get()]
            days = [monday + timedelta(days=i) for i in range(7)]
            totals = [sum(s["hours"] for s in data if s["date"] == day.isoformat()) for day in days]
            right.plot([d.strftime("%a") for d in days], totals, color="#7ca9ef", marker="o", linewidth=2.5)
            right.set_ylim(bottom=0)
            right.set_title("Daily hours · selected week", color=TEXT, loc="left", pad=18)
        self.figure.tight_layout(pad=2.5)
        self.canvas.draw_idle()

    def add_session(self):
        try:
            raw_day = self.day.get().strip()
            day = date.fromisoformat(raw_day)
            if day.isoformat() != raw_day:
                raise ValueError("Use YYYY-MM-DD for the date.")
            course = self.course.get().strip()
            hours = float(self.hours.get())
            if not course or not math.isfinite(hours) or hours <= 0:
                raise ValueError("Enter a course and positive, finite study hours.")
            # Reload before editing so externally added records are preserved.
            sessions = load_sessions(DATA_FILE)
            sessions.append({"date": day.isoformat(), "course": course, "hours": hours})
            save_sessions(DATA_FILE, sessions)
        except (ValueError, OSError) as error:
            messagebox.showerror("Could not add session", str(error))
            return
        self.course.set("")
        self.hours.set("")
        self.refresh()
        # Reveal the new session even when another week was selected.
        monday = week_start(day)
        self.period.set(next(label for label, start in self.week_map.items() if start == monday))
        self.render()
        self.status.config(text=f"Saved {course} · {hours:g} hours · {day}")

    def delete_session(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a session", "Select a row in Study sessions first.")
            return
        index = int(selected[0])
        session = self.sessions[index]
        if not messagebox.askyesno("Delete session?", f"Delete {session['course']} on {session['date']} ({session['hours']:g} hours)?"):
            return
        try:
            current = load_sessions(DATA_FILE)
            if current != self.sessions:
                self.refresh()
                messagebox.showinfo("Data changed", "Your CSV changed. Select the session again.")
                return
            del current[index]
            save_sessions(DATA_FILE, current)
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not delete session", str(error))
            return
        self.refresh()
        self.status.config(text="Session deleted. Dashboard updated.")


if __name__ == "__main__":
    StudyDashboard().mainloop()
