# Study Analyzer

**Build your routine. See your progress.**

A local Python study tracker with a desktop dashboard and an interactive terminal interface. Log study sessions, compare time spent across courses, and track progress toward a weekly study goal. Sessions are stored in CSV files on your computer.

## Features

| Capability | Desktop dashboard (`app.py`) | Terminal interface (`analyze.py`) |
| --- | --- | --- |
| Add and view sessions | Form and date-sorted table | Interactive prompts and numbered list |
| Delete sessions | Select a row and confirm | Choose a session ID and confirm |
| Profiles | Create, switch, and permanently delete local profiles | One shared project-level CSV |
| Analytics | Total hours, session count, top course, hours per study day | Total hours, hours by course, top course, hours per study day |
| Reporting periods | All time or a recorded calendar week | Overall analytics or a selected recorded week |
| Weekly goals | Adjustable goal and progress bar | Goal summary and chart; configured in source |
| Charts | Embedded course and weekly/daily charts | Three PNG charts per report |

The GUI reuses the analytics functions in `analyze.py`, so keep both Python files in the same directory.

## Requirements

- Python 3.8 or newer is required by the source's use of `Path.unlink(missing_ok=True)`. Use a Python version supported by your installed Matplotlib release.
- **Matplotlib**, the only third-party Python dependency.
- **Tkinter with Tcl/Tk** and a graphical desktop session for the GUI. Tkinter is part of Python's standard library, but some Python installations package it separately.
- Write access to the project folder for CSV data, profile folders, and exported charts.

No database or account service is required. Profiles are local data folders, not password-protected accounts.

## Installation

1. Download the project and place `app.py` and `analyze.py` together in a folder.
2. Open a terminal in that folder and create a virtual environment:

   ```sh
   python -m venv .venv
   ```

3. Activate the environment:

   **macOS / Linux**

   ```sh
   source .venv/bin/activate
   ```

   **Windows PowerShell**

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Install Matplotlib:

   ```sh
   python -m pip install matplotlib
   ```

If your system uses `python3` instead of `python`, use `python3` to create the environment. The supplied source does not include a dependency lockfile or pinned package versions.

To check that Tkinter is available, run:

```sh
python -m tkinter
```

A small demonstration window should open. If Tkinter is missing, install Tcl/Tk support for your Python distribution; installing Matplotlib alone does not provide it.

## Run the desktop dashboard

```sh
python app.py
```

1. Click **+ New profile**, enter a name, or select an existing profile from **Your profile**.
2. Enter a date in `YYYY-MM-DD` format, a course, and hours studied, then click **+ Add session**. The date starts at today; hours may be fractional, such as `1.5`.
3. Use **Report period** to switch between **All time** and a recorded Monday–Sunday week.
4. Set **Weekly goal (hours)** and click **Apply**.
5. Open **Study sessions** to review records. Select a row and click **Delete selected session** to remove it after confirmation.

Changes to sessions are saved automatically. Adding a session selects its week so the new entry is visible. **Refresh** reloads the active profile's CSV after an external edit.

Profile names must contain 1–60 characters after trimming whitespace and cannot contain control characters. Names are case-insensitive for directory identity, so `Alex` and `alex` cannot be separate profiles.

**Delete profile** permanently removes that profile and all of its sessions after confirmation. Back up its folder first if you may need the data later.

### Dashboard charts

- **All time:** hours by course and weekly totals with a dashed goal line. The metric cards cover all sessions, while the progress bar refers to the **current calendar week**.
- **Selected week:** hours by course and a daily line chart for all seven days, including days with zero hours. Both the cards and progress bar refer to the selected week.
- Goal percentages can exceed 100%; the progress bar stops at 100%.

The dashboard displays charts inside the window. It does not export PNGs or provide an import/export dialog.

## Run the terminal interface

```sh
python analyze.py
```

Choose an option from the interactive menu:

```text
1. View analytics and charts
2. Add a study session
3. View saved sessions
4. Delete a study session
5. View a weekly report
6. Exit
```

- **Add:** press Enter at the date prompt to use today. Enter a nonblank course and positive, finite hours. Analytics and charts refresh after saving.
- **Delete:** use an ID from the full saved-session list, then type `yes` to confirm. Press Enter at the ID prompt to cancel. IDs are row positions, not permanent identifiers.
- **Weekly report:** select a week containing sessions to see its records, course totals, session count, averages, and goal progress. Press Enter at the week-selection prompt to return to the main menu.
- **Exit:** choose `6`; Ctrl+C or end-of-input also exits cleanly.

No CSV is needed to start: adding the first terminal session creates `study_data.csv` with its header. Viewing analytics before data exists displays a message asking you to add a session.

The terminal uses Matplotlib's `Agg` backend: it saves charts as PNG files instead of opening chart windows.

## Data storage: profiles versus terminal data

**The two interfaces do not automatically share sessions.** Both use the same CSV schema, but their default file locations differ:

| Interface | Data location relative to the Python files |
| --- | --- |
| Terminal | `study_data.csv` |
| Desktop profile | `profiles/<profile-hash>/study_data.csv` |
| Profile display name | `profiles/<profile-hash>/profile.json` |

Paths are resolved relative to the script directory, not the terminal's current working directory. Each profile folder is named using the SHA-256 hash of the case-folded profile name; read `profile.json` to identify its display name.

To transfer data manually, close the GUI, back up the destination CSV, and copy the desired CSV to that destination. Create the destination profile through the GUI first if needed. Copying replaces its data; there is no automatic merge or synchronization. Reopen the GUI afterward. To analyze a profile through the terminal, copy its CSV to the project-level `study_data.csv` first.

## CSV format

Use this exact header and column order:

```csv
date,course,hours
2026-10-19,Mathematics,1.5
2026-10-19,Computer Science,2
2026-10-21,Physics,0.75
2026-10-26,Mathematics,2.5
```

| Column | Format | Example |
| --- | --- | --- |
| `date` | Calendar date in `YYYY-MM-DD` format | `2026-10-19` |
| `course` | Nonblank course name; consistent spelling keeps totals grouped | `Mathematics` |
| `hours` | Positive, finite decimal hours | `1.5` means 1 hour 30 minutes |

Multiple sessions on the same date are supported and contribute to that day's total. Course names are case-sensitive in analytics, so `Physics` and `physics` form separate groups. Quote CSV fields containing commas, for example `"History, Modern"`.

Both interfaces require positive hours when adding a session. The GUI's file loader also accepts zero-hour records already present in a CSV, but rejects negative or non-finite values, blank courses, invalid dates, and an incorrect header. The terminal loader performs less validation; malformed imported records may stop a report. Use valid, consistently formatted records in either interface.

## Weekly goals and averages

- A week runs **Monday through Sunday** and is labeled by its Monday start date.
- The default goal is **20 hours per week**.
- Goal progress is `weekly hours / weekly goal × 100`. Remaining hours never fall below zero, and a goal is met when weekly hours are at least the goal.
- Weekly totals include zero-hour weeks between the earliest and latest recorded weeks. The week-selection menus list only weeks with sessions.
- **Hours per study day** is total hours divided by the number of distinct recorded dates. Days without records are excluded. A pre-existing zero-hour row still makes its date a recorded day.
- The terminal's selected-week report also shows **hours per calendar day**, calculated as that week's total divided by seven.

In the GUI, change the goal field and click **Apply**. This setting is not saved: it returns to 20 when switching profiles or restarting the app. In the terminal, change `weekly_goal = 20` in the `if __name__ == "__main__":` block of `analyze.py`. There is no command-line goal flag or goal-setting menu.

## Exported terminal charts

Overall analytics writes these files to `charts/`:

| File | Contents |
| --- | --- |
| `hours_by_course.png` | Total hours per course |
| `daily_study_hours.png` | Daily totals for recorded dates, sorted by date |
| `weekly_study_progress.png` | Weekly totals, goal line, and goal-met colors |

Weekly reports save the same three filenames under `charts/weekly_reports/YYYY-MM-DD/`, where the folder date is the week's Monday. The weekly progress chart uses green for goals met and salmon for goals not yet met.

Generating a report replaces charts with the same filenames. Different weekly folders preserve separate reports. The terminal daily chart includes recorded dates only; it does not insert missing days. Charts are snapshots: regenerate a report after changing data. Successful terminal deletion clears the three overall PNGs and regenerates them if sessions remain, but older weekly-report images are not automatically removed or updated.

## File structure

```text
study-analyzer/
├── app.py                         # Tkinter dashboard and profile management
├── analyze.py                     # Analytics, CSV operations, and terminal menu
├── README.md
├── study_data.csv                 # Terminal data; created when first saved
├── profiles/                      # Created when adding a GUI profile
│   └── <profile-hash>/
│       ├── profile.json           # Profile display name
│       └── study_data.csv         # Sessions belonging to this profile
└── charts/                        # Created when terminal reports are generated
    ├── hours_by_course.png
    ├── daily_study_hours.png
    ├── weekly_study_progress.png
    └── weekly_reports/
        └── YYYY-MM-DD/
            ├── hours_by_course.png
            ├── daily_study_hours.png
            └── weekly_study_progress.png
```

Generated data and chart folders do not need to exist before the first run.

## Tips and troubleshooting

- **Start with a short session:** create a profile, add `1.5` hours for one course, and check its selected-week chart before entering your history.
- **Use hours, not minutes:** enter `0.5` for 30 minutes. Use a decimal point rather than a decimal comma.
- **Missing sessions between interfaces:** check whether you are using a GUI profile CSV or the terminal's project-level CSV.
- **`No module named matplotlib`:** activate the intended environment and run `python -m pip install matplotlib` with the same Python used to launch the app.
- **Tkinter import or display errors:** verify `python -m tkinter` works in a graphical session. The terminal interface can generate PNG charts without a display.
- **CSV errors:** check the exact header, dates, course names, and numeric hours. Back up files before editing them by hand.
- **Unexpected weekly progress:** All time in the GUI shows the current week's progress bar; choose a specific week to inspect historical progress.
- **External edits:** click Refresh after changing a profile CSV. The GUI reloads data before adding and checks for changed data before deleting; avoid simultaneous edits from multiple running copies.
- **Backups and Git:** preserve `profiles/` and `study_data.csv` when backing up your study history. Consider excluding `.venv/`, `__pycache__/`, personal CSV data, `profiles/`, and generated `charts/` from a public repository.

Sessions cannot be edited directly in either interface. To correct one, delete it and add a replacement, or carefully edit a backed-up CSV while the application is closed.
