from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Function to allocate study hours based on priorities
def allocate_study_hours(week_days, hours_per_day, subjects, priorities):
    total_study_hours = sum(hours_per_day)
    priority_sum = sum(priorities)
    normalized_priorities = [p / priority_sum for p in priorities]
    
    # Calculate total hours allocated to each subject
    subject_allocation = [total_study_hours * norm_p for norm_p in normalized_priorities]
    
    # Distribute hours across the week
    daily_allocation = []
    for day in range(len(week_days)):
        day_allocation = [hours * (hours_per_day[day] / total_study_hours) for hours in subject_allocation]
        daily_allocation.append(day_allocation)
    
    return daily_allocation

# Function to generate the timetable and return as a dictionary
def generate_timetable(week_days, subjects, daily_allocation):
    timetable = {}
    for day, day_name in enumerate(week_days):
        timetable[day_name] = {}
        for subj, hours in zip(subjects, daily_allocation[day]):
            timetable[day_name][subj] = round(hours, 2)
    return timetable

# Function to create a bar plot for the timetable
def create_barplot(week_days, subjects, daily_allocation):
    # Prepare data for barplot
    day_labels = week_days
    subject_bars = {subj: [daily_allocation[day][i] for day in range(len(week_days))] for i, subj in enumerate(subjects)}
    
    # Create bar plot
    x = np.arange(len(day_labels))
    bar_width = 0.2
    offsets = np.arange(len(subjects)) * bar_width - (len(subjects) - 1) * bar_width / 2

    plt.figure(figsize=(10, 6))
    for i, subj in enumerate(subjects):
        plt.bar(x + offsets[i], subject_bars[subj], width=bar_width, label=subj)

    plt.xlabel("Days of the Week")
    plt.ylabel("Hours Allocated")
    plt.title("Study Timetable Bar Plot")
    plt.xticks(x, day_labels)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Convert plot to image for HTML embedding
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    return img_base64

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the subjects and priorities from the form
        subjects = request.form['subjects'].split(',')
        priorities = [int(request.form[f'priority_{i+1}']) for i in range(len(subjects))]
        
        # Get the available study hours for each day of the week
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours_per_day = [int(request.form[f'hours_day_{day}']) for day in week_days]

        # Allocate study hours and generate timetable
        daily_allocation = allocate_study_hours(week_days, hours_per_day, subjects, priorities)
        timetable = generate_timetable(week_days, subjects, daily_allocation)

        # Generate bar plot
        img_base64 = create_barplot(week_days, subjects, daily_allocation)

        return render_template('index.html', timetable=timetable, img_base64=img_base64)

    return render_template('index.html', timetable=None, img_base64=None)

if __name__ == '__main__':
    app.run(debug=True)
