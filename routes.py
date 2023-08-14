from flask import Blueprint, render_template,request,redirect,url_for,current_app
import datetime
import uuid
# from collections import defaultdict

pages = Blueprint('habits',__name__, template_folder="templates",static_folder="static")

# habits = ["Test habit","coding", "cooking"]
# completions = defaultdict(list)

def today_at_midtime():
    today = datetime.datetime.today()
    return datetime.datetime(today.year,today.month,today.day)

@pages.context_processor
def add_calc_date_range():
    def date_range(start:datetime.datetime):
        dates = [start+datetime.timedelta(days=diff) for diff in range(-3,4)]
        return dates  
    return {"date_range":date_range}

@pages.route('/')
def index():
    date_str = request.args.get('date')
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midtime()
        
    habits_on_date = current_app.db.habits.find({"added":{'$lte':selected_date}})
        
    completions = [ 
                   habit['habit']
                   for habit in current_app.db.completions.find({'date':selected_date})
                   ]    
    
    return render_template('index.html',title='Habit Tracker - Home', habits=habits_on_date, selected_date=today_at_midtime(), completions=completions)

@pages.route('/add', methods=['GET','POST'])
def add_habit():
    today = today_at_midtime()
    
    if request.form: 
        current_app.db.habits.insert_one({
            "_id":uuid.uuid4().hex,"added":today,"name":request.form.get('habit')
        })
        
    return render_template('add_habit.html',title='Habit Tracker - Add Habit',selected_date=today)
    
@pages.post('/complete')
def complete():
    date_string = request.form.get('date')
    habit = request.form.get('habitId')
    date = datetime.datetime.fromisoformat(date_string)
    current_app.db.completions.insert_one({'date':date,'habit':habit})
    
    return redirect(url_for('.index',date = date_string))
    

