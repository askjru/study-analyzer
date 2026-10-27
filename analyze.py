import csv

hours_by_course = {}

with open("study_data.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        course = row["course"]
        hours = float(row["hours"])

        if course not in hours_by_course:
            hours_by_course[course] = 0

        hours_by_course[course] += hours

for course, hours in hours_by_course.items():
    print(f"{course}: {hours} hours")
