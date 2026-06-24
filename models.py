from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Bảng người dùng
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True)
    xp = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    progress = db.relationship('UserProgress', backref='user', lazy=True)

# Bảng bài học (có nội dung chi tiết)
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Nội dung lý thuyết (hỗ trợ markdown)
    xp_reward = db.Column(db.Integer, default=20)
    order = db.Column(db.Integer, default=0)
    
    exercises = db.relationship('Exercise', backref='lesson', lazy=True)

# Bảng bài tập (đa dạng loại)
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.Integer)  # 0=A, 1=B, 2=C, 3=D
    exercise_type = db.Column(db.String(50), default='multiple_choice')  # multiple_choice, fill_blank
    explanation = db.Column(db.Text)  # Giải thích đáp án

# Bảng Quiz (cuối mỗi level)
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.Integer)
    xp_reward = db.Column(db.Integer, default=30)

# Bảng tiến trình học
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    quiz_passed = db.Column(db.Boolean, default=False)
    quiz_score = db.Column(db.Integer, default=0)
    exercise_completed = db.Column(db.Boolean, default=False)  # Thêm để theo dõi bài tập
