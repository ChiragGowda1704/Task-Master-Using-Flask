from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid warnings

# Initialize Database
db = SQLAlchemy(app)

# Define Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id}>"

# Create Database Tables
with app.app_context():
    db.create_all()

# Route for Home Page
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form.get("content")

        if not task_content.strip():
            return "Task content cannot be empty!", 400  # Return error response

        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Database error: {e}", 500  # Specific error message

    tasks = Todo.query.order_by(Todo.date_created.desc()).all()
    return render_template("index.html", tasks=tasks)

# Delete Task
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"There was a problem deleting the task: {e}", 500

# Update Task
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an issue updating the task: {e}", 500
    else:
        return render_template('update.html', task=task)

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
