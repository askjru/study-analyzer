import csv
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import date, timedelta
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


if __name__ == "__main__":
    filename = "study_data.csv"
    study_data = load_study_data(filename)

    total_hours = calculate_total_hours(study_data)
    print(f"Total study hours: {total_hours}")

    course_hours = hours_per_course(study_data)
    print("Study hours per course:")
    for course, hours in course_hours.items():
        print(f"{course}: {hours} hours")

    most_studied, hours = most_studied_course(course_hours)
    if most_studied:
        print(f"Most studied course: {most_studied} with {hours} hours")
    else:
        print("No courses found.")

    average_hours = average_daily_hours(study_data)
    print(f"Average daily study hours: {average_hours:.2f}")

    weekly_goal = 20
    print_weekly_summary(study_data, weekly_goal)

    chart_dir = Path(__file__).resolve().parent / "charts"
    chart_dir.mkdir(exist_ok=True)

    plot_hours_per_course(study_data, chart_dir)
    plot_daily_hours(study_data, chart_dir)
    plot_weekly_progress(study_data, chart_dir, weekly_goal)
    print("\nCharts saved successfully!")

