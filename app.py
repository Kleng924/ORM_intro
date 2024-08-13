from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mcleanne1624$@localhost/fitness_center'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Member {self.name}>"

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes

    member = db.relationship('Member', backref=db.backref('workouts', lazy=True))

    def __repr__(self):
        return f"<WorkoutSession {self.date} - {self.duration} mins>"

if __name__ == '__main__':
    db.create_all()  # Create tables
    app.run(debug=True)

from flask import request, jsonify

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], email=data['email'])
    try:
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'Member added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'email': m.email} for m in members])

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify({'id': member.id, 'name': member.name, 'email': member.email})

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.get_json()
    member = Member.query.get_or_404(member_id)
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    try:
        db.session.commit()
        return jsonify({'message': 'Member updated successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/workouts', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_session = WorkoutSession(
        member_id=data['member_id'],
        date=data['date'],
        duration=data['duration']
    )
    try:
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'message': 'Workout session scheduled successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/workouts', methods=['GET'])
def get_workout_sessions():
    sessions = WorkoutSession.query.all()
    return jsonify([{
        'id': s.id,
        'member_id': s.member_id,
        'date': s.date.strftime('%Y-%m-%d'),
        'duration': s.duration
    } for s in sessions])

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{
        'id': s.id,
        'date': s.date.strftime('%Y-%m-%d'),
        'duration': s.duration
    } for s in sessions])