from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'finn-ai-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finn_data.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        new_exp = Expense(amount=float(request.form['amount']), 
                          category=request.form['category'], 
                          user_id=current_user.id)
        db.session.add(new_exp)
        db.session.commit()

    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    total = sum(e.amount for e in expenses)
    
    # AI Logic (Finn)
    ai_advice = "I'm Finn. Add your expenses so I can help you save!"
    if total > 0:
        food = sum(e.amount for e in expenses if e.category.lower() == 'food')
        if food > (total * 0.4):
            ai_advice = "⚠️ Finn's Alert: You're spending a lot on food! Try eating home this week."
        elif total > 1000:
            ai_advice = "💡 Finn's Tip: Your spending is high. Let's look for subscriptions to cancel."
        else:
            ai_advice = "✅ Finn's Status: Looking good! You're managing your money well."

    return render_template('dashboard.html', total=total, expenses=expenses, ai_advice=ai_advice)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)