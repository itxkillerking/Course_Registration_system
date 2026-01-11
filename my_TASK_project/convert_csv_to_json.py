import csv
import json

# read CSV
with open("courses_dataset.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        data.append({
            "model": "myapp.course",  # <-- replace with your actual app and model name
            "fields": {
                "title": row["title"],
                "category": row["category"],
                "level": row["level"],
                "description": row["description"],
                "duration": row["duration"],
                "instructor": row["instructor"],
                "price": row["price"],
                "language": row["language"],
                "grade": row.get("grade", "")
            }
        })

# save JSON
with open("courses_dataset.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
