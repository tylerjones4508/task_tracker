import datetime
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app


pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")
# habits = []
# completions = defaultdict(list)




@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = datetime.datetime.today()

    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    print(habits_on_date)
    completions = [habit["habit"] for habit in current_app.db.completions.find({"date": selected_date})]
    print(completions)


    return render_template(
        "index.html",
        habits=habits_on_date,
        selected_date=selected_date,
        completions=completions,
        title="Task Tracker - Home",
    )


@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = datetime.datetime.fromisoformat(date_string)
    habit = request.form.get("habitId")
    # completions[date].append(habit)
    current_app.db.completions.insert_one({"date": date, "habit": habit})

    return redirect(url_for("habits.index", date=date_string))


@pages.route("/delete", methods=['POST'])
def delete():
    date_string = request.form.get("date")
    date = datetime.datetime.fromisoformat(date_string)
    if request.form:
        print(request.form.get('habitId'))
        current_app.db.habits.delete_one({
            "_id": request.form.get('habitId')
        })
        current_app.db.completions.delete_one({
            "habit": request.form.get('habitId')
        })

    return redirect(url_for("habits.index", date=date_string))


@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    if request.form:
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )
        return redirect(url_for("habits.index"))

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=today,
    )