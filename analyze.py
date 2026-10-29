import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
import math


def load_study_data(filename):
    """Read the study data from a CSV file."""
    study_data = []

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            session = {
                "date": row["date"],
                "course": row["course"],
                "hours": float(row["hours"]),
            }
            study_data.append(session)

    return study_data

def calculate_total_hours(study_data):
    """Calculate the total study hours from the study data."""
    total_hours = sum(session["hours"] for session in study_data)
    return total_hours

def hours_per_course(study_data):
    """Calculate the total study hours per course."""
    course_hours = {}

    for session in study_data:
        course = session["course"]
        hours = session["hours"]

        if course in course_hours:
            course_hours[course] += hours
        else:
            course_hours[course] = hours

    return course_hours

def most_studied_course(course_hours):
    """Identify the course with the most study hours."""
    if not course_hours:
        return None, 0

    most_studied = max(course_hours.items(), key=lambda item: item[1])
    return most_studied

def average_daily_hours(study_data):
    """Calculate the average daily study hours."""
    if not study_data:
        return 0

    unique_dates = {session["date"] for session in study_data}
    total_hours = calculate_total_hours(study_data)
    average_hours = total_hours / len(unique_dates)

    return average_hours

def plot_hours_per_course(study_data, output_dir):
    """Plot a bar chart of study hours per course."""
    course_hours = hours_per_course(study_data)

    if not course_hours:
        return

    courses = list(course_hours.keys())
    hours = list(course_hours.values())

    plt.figure(figsize=(8, 5))

    plt.bar(courses, hours)

    plt.xlabel("Course")
    plt.ylabel("Study Hours")
    plt.title("Study Hours by Course")

    plt.tight_layout()
    plt.savefig(output_dir / "hours_by_course.png")
    plt.close()

def plot_daily_hours(study_data, output_dir):
    """Create a line graph of daily study hours."""
    daily_hours = {}

    for session in study_data:
        date = session["date"]
        hours = session["hours"]

        if date not in daily_hours:
            daily_hours[date] = 0

        daily_hours[date] += hours

    if not daily_hours:
        return

    dates = sorted(daily_hours.keys())
    hours = [daily_hours[date] for date in dates]

    plt.figure(figsize=(10, 5))

    plt.plot(dates, hours, marker="o")

    plt.xlabel("Date")
    plt.ylabel("Study Hours")
    plt.title("Daily Study Hours")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_dir / "daily_study_hours.png")
    plt.close()

def hours_per_week(study_data):
    """Group hours by Monday-Sunday calendar weeks."""
    weekly_hours = {}

    for session in study_data:
        session_date = date.fromisoformat(session["date"])
        monday = session_date - timedelta(days=session_date.weekday())

        if monday not in weekly_hours:
            weekly_hours[monday] = 0

        weekly_hours[monday] += session["hours"]

    if not weekly_hours:
        return {}

    result = {}
    monday = min(weekly_hours)
    last_week = max(weekly_hours)

    while monday <= last_week:
        result[monday] = weekly_hours.get(monday, 0)
        monday += timedelta(weeks=1)

    return result


def weekly_goal_progress(study_data, weekly_goal=20):
    """Calculate progress towards a positive weekly study goal."""
    if not math.isfinite(weekly_goal) or weekly_goal <= 0:
        raise ValueError("Weekly goal must be a finite positive number.")

    progress = []

    for monday, hours in hours_per_week(study_data).items():
        progress.append({
            "week_start": monday,
            "hours": hours,
            "week_end": monday + timedelta(days=6),
            "percentage": hours / weekly_goal * 100,
            "remaining_hours": max(0, weekly_goal - hours),
            "goal_met": hours >= weekly_goal,
        })

    return progress

def print_weekly_summary(study_data, weekly_goal=20):
    """Print a summary of weekly study hours and progress towards the goal."""
    progress = weekly_goal_progress(study_data, weekly_goal)

    if not progress:
        print("No study data available.")
        return

    print(f"{'Week Start':<12} {'Week End':<12} {'Hours':<6} {'% of Goal':<10} {'Remaining Hours':<16} {'Goal Met'}")
    print("-" * 70)

    for week in progress:
        week_start = week["week_start"].strftime("%Y-%m-%d")
        week_end = week["week_end"].strftime("%Y-%m-%d")
        hours = week["hours"]
        percentage = week["percentage"]
        remaining_hours = week["remaining_hours"]
        goal_met = "Yes" if week["goal_met"] else "No"

        print(f"{week_start:<12} {week_end:<12} {hours:<6.2f} {percentage:<10.2f} {remaining_hours:<16.2f} {goal_met}")


def plot_weekly_progress(study_data, output_dir, weekly_goal=20):
    """Create a weekly study chart with a goal line."""
    progress = weekly_goal_progress(study_data, weekly_goal)

    if not progress:
        return

    weeks = [str(week["week_start"]) for week in progress]
    hours = [week["hours"] for week in progress]
    colors = [
        "seagreen" if week["goal_met"] else "salmon" for week in progress
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(weeks, hours, color=colors)

    plt.axhline(y=weekly_goal, color="blue", linestyle="--", label=f"Weekly Goal: {weekly_goal} hours")

    plt.xlabel("Week Starting Monday")
    plt.ylabel("Study Hours")
    plt.title("Weekly Study Goal Progress")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_dir / "weekly_study_progress.png")
    plt.close()

def save_study_session(filename, session):
    """Append a session without overwriting existing records."""
    filename = Path(filename)
    needs_header = not filename.exists() or filename.stat().st_size == 0

    # Ensure the new record starts on its own line.
    needs_newline = False
    if not needs_header:
        with open(filename, "rb") as file:
            file.seek(-1, 2)
            needs_newline = file.read(1) not in (b"\n", b"\r")

    with open(filename, "a", newline="", encoding="utf-8") as file:
        if needs_newline:
            file.write("\n")

        writer = csv.DictWriter(file, fieldnames=["date", "course", "hours"])

        if needs_header:
            writer.writeheader()

        writer.writerow(session)


def add_study_session(filename):
    """Ask for a study session, validate it, and save it."""
    while True:
        date_input = input(
            "Date (YYYY-MM-DD, Enter for today): "
        ).strip()

        if not date_input:
            session_date = date.today().isoformat()
            break

        try:
            parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()

            if parsed_date.isoformat() != date_input:
                raise ValueError

            session_date = parsed_date.isoformat()
            break
        except ValueError:
            print("Enter a valid date using YYYY-MM-DD.")

    while True:
        course = input("Course: ").strip()

        if course:
            break

        print("Course cannot be blank.")

    while True:
        try:
            hours = float(input("Hours studied: ").strip())

            if not math.isfinite(hours) or hours <= 0:
                raise ValueError

            break
        except ValueError:
            print("Enter a positive number, such as 1.5.")

    session = {
        "date": session_date,
        "course": course,
        "hours": hours,
    }

    try:
        save_study_session(filename, session)
    except OSError as error:
        print(f"Could not save session: {error}")
        return

    print(f"\nSession saved: {session_date}, {course}, {hours:g} hours")


def show_analytics(filename, chart_dir, weekly_goal=20):
    """Read the latest CSV data and display analytics and charts."""
    try:
        study_data = load_study_data(filename)
    except FileNotFoundError:
        print("\nNo study data found. Add your first session!")
        return

    if not study_data:
        print("\nNo study sessions recorded. Add your first session!")
        return

    total_hours = calculate_total_hours(study_data)
    print(f"\nTotal study hours: {total_hours:.2f}")

    course_hours = hours_per_course(study_data)
    print("\nStudy hours per course:")

    for course, hours in course_hours.items():
        print(f"{course}: {hours:g} hours")

    most_studied, hours = most_studied_course(course_hours)

    if most_studied:
        print(f"\nMost studied course: {most_studied} with {hours:g} hours")

    average_hours = average_daily_hours(study_data)
    print(f"Average daily study hours: {average_hours:.2f}")

    print_weekly_summary(study_data, weekly_goal)

    chart_dir.mkdir(exist_ok=True)

    plot_hours_per_course(study_data, chart_dir)
    plot_daily_hours(study_data, chart_dir)
    plot_weekly_progress(study_data, chart_dir, weekly_goal)

    print(f"\nCharts saved in: {chart_dir}")

def print_study_sessions(study_data):
    """Display saved sessions with numbers starting at 1."""
    print(f"\n{'ID':<5} {'Date':<12} {'Course':<16} {'Hours'}")
    print("-" * 45)

    for session_id, session in enumerate(study_data, start=1):
        print(
            f"{session_id:<5} "
            f"{session['date']:<12} "
            f"{session['course']:<16} "
            f"{session['hours']:g}"
        )


def view_study_sessions(filename):
    """Read and display all saved sessions."""
    try:
        study_data = load_study_data(filename)
    except FileNotFoundError:
        print("\nNo study data found. Add your first session!")
        return

    if not study_data:
        print("\nNo study sessions recorded.")
        return

    print_study_sessions(study_data)


def delete_study_session(filename):
    """Delete a selected session after confirmation."""
    try:
        study_data = load_study_data(filename)
    except FileNotFoundError:
        print("\nNo study data found.")
        return False

    if not study_data:
        print("\nNo study sessions to delete.")
        return False

    print_study_sessions(study_data)

    while True:
        choice = input(
            "\nSession ID to delete (Enter to cancel): "
        ).strip()

        if not choice:
            print("Deletion cancelled.")
            return False

        try:
            session_id = int(choice)

            if not 1 <= session_id <= len(study_data):
                raise ValueError

            break
        except ValueError:
            print(f"Enter a number from 1 to {len(study_data)}.")

    selected = study_data[session_id - 1]

    print(
        f"\nSelected: {selected['date']} | "
        f"{selected['course']} | {selected['hours']:g} hours"
    )

    confirmation = input("Delete this session? (yes/no): ").strip().lower()

    if confirmation != "yes":
        print("Deletion cancelled.")
        return False

    remaining_sessions = [
        session
        for index, session in enumerate(study_data)
        if index != session_id - 1
    ]

    # Write a temporary file first, then replace the CSV only after
    # the complete updated data has been written successfully.
    import os
    import tempfile

    filename = Path(filename)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=filename.parent,
            prefix="study_sessions_",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)

            writer = csv.DictWriter(
                file,
                fieldnames=["date", "course", "hours"],
            )
            writer.writeheader()
            writer.writerows(remaining_sessions)

        os.replace(temporary_path, filename)

    except OSError as error:
        print(f"Could not delete session: {error}")
        return False

    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    print("\nSession deleted successfully!")
    return True

if __name__ == "__main__":
    project_dir = Path(__file__).resolve().parent
    filename = project_dir / "study_data.csv"
    chart_dir = project_dir / "charts"
    weekly_goal = 20

    try:
        while True:
            print("\n===== STUDY ANALYZER =====")
            print("1. View analytics and charts")
            print("2. Add a study session")
            print("3. View saved sessions")
            print("4. Delete a study session")
            print("5. Exit")

            choice = input("\nChoose an option: ").strip()

            if choice == "1":
                show_analytics(filename, chart_dir, weekly_goal)

            elif choice == "2":
                add_study_session(filename)
                show_analytics(filename, chart_dir, weekly_goal)

            elif choice == "3":
                view_study_sessions(filename)

            elif choice == "4":
                if delete_study_session(filename):
                    # Remove old charts so deleting the final session
                    # cannot leave charts showing outdated data.
                    for chart_name in (
                        "hours_by_course.png",
                        "daily_study_hours.png",
                        "weekly_study_progress.png",
                    ):
                        (chart_dir / chart_name).unlink(missing_ok=True)

                    show_analytics(filename, chart_dir, weekly_goal)

            elif choice == "5":
                print("Goodbye!")
                break

            else:
                print("Please choose 1, 2, 3, 4, or 5.")

    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
