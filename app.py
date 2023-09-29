import datetime
import uuid
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://arnab:%23Shiprarani1A@microblog-application.wzqdufe.mongodb.net/test")
app.db = client.habit_tracker

habits = ["Test habit"]
completion = defaultdict(list)

@app.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start+datetime.timedelta(days=i) for i in range(-3,4)]
        return dates
    return {"date_range":date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

@app.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()
    
    habit_at_that_date = app.db.entries.find({"added":{"$lte":selected_date}})
    completion = [
            entry["habit"]
            for entry in app.db.entries.find({"date":selected_date})
    ]
    return render_template("index.html", habits=habit_at_that_date, title="Habit Tracker - Home", 
                           selected_date=selected_date, completion= completion)

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    if request.form:
        app.db.entries.insert_one({"_id":uuid.uuid4().hex, "added":today, "name":request.form.get("habit")})
    return render_template("add_habit.html", title="Habit Tracker - Add Habit", selected_date=today)

@app.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)
    app.db.entries.insert_one({"date":date, "habit":habit})
    completion[date].append(habit)
    return redirect(url_for("index", date=date_string))

if __name__ == "__main__":
    app = app.run(debug=True)
