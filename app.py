import os
import datetime
import markdown
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Lesson, Exercise, Quiz, UserProgress
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ===== CẤU HÌNH =====
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'english_journey.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# ===== LOGIN =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============================================================
# ROUTE TẠO DỮ LIỆU MẪU (GIẢI PHÁP THAY THẾ SHELL)
# ============================================================
@app.route('/init-db')
def init_database():
    """Truy cập /init-db để tạo dữ liệu mẫu tự động"""
    try:
        with app.app_context():
            # Tạo thư mục instance
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            db.create_all()
            
            # === TẠO ADMIN ===
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@example.com',
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
            
            # === TẠO BÀI HỌC MẪU ===
            if Lesson.query.count() == 0:
                lessons = [
                    Lesson(level_id=1, name='🔤 Bảng chữ cái ABC', description='Học 26 chữ cái tiếng Anh', 
                           content='## 📚 Lý thuyết\nBảng chữ cái tiếng Anh có 26 chữ cái...', xp_reward=20, order=1),
                    Lesson(level_id=1, name='🔢 Số đếm 1-20', description='Học đếm từ 1 đến 20', 
                           content='## 📚 Lý thuyết\nSố đếm từ 1 đến 20...', xp_reward=20, order=2),
                    Lesson(level_id=2, name='👨‍👩‍👧‍👦 Gia đình', description='Từ vựng về gia đình', 
                           content='## 📚 Lý thuyết\nTừ vựng về gia đình...', xp_reward=30, order=1),
                    Lesson(level_id=2, name='🐱 Động vật', description='Từ vựng về động vật', 
                           content='## 📚 Lý thuyết\nTừ vựng về động vật...', xp_reward=30, order=2),
                ]
                for l in lessons:
                    db.session.add(l)
                db.session.commit()
            
            # === TẠO BÀI TẬP ===
            if Exercise.query.count() == 0:
                exercises = [
                    Exercise(lesson_id=1, question='Chữ cái nào là nguyên âm?', 
                             option_a='B', option_b='C', option_c='A', option_d='D', 
                             correct_answer=2, explanation='Nguyên âm là A, E, I, O, U'),
                    Exercise(lesson_id=1, question='Phát âm chữ "B" là gì?', 
                             option_a='/biː/', option_b='/siː/', option_c='/diː/', option_d='/iː/', 
                             correct_answer=0, explanation='B phát âm là /biː/'),
                ]
                for e in exercises:
                    db.session.add(e)
                db.session.commit()
            
            # === TẠO QUIZ ===
            if Quiz.query.count() == 0:
                quizzes = [
                    Quiz(level_id=1, question='Từ nào là màu sắc?', 
                         option_a='Red', option_b='Table', option_c='Run', option_d='Happy', 
                         correct_answer=0, xp_reward=30),
                    Quiz(level_id=2, question='"Cat" có nghĩa là gì?', 
                         option_a='Chó', option_b='Mèo', option_c='Chim', option_d='Cá', 
                         correct_answer=1, xp_reward=40),
                ]
                for q in quizzes:
                    db.session.add(q)
                db.session.commit()
            
            return f"""
            <html>
            <head><title>Khởi tạo dữ liệu</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #27ae60;">✅ KHỞI TẠO THÀNH CÔNG!</h1>
                <ul style="list-style: none; padding: 0;">
                    <li>👤 Admin: <strong>admin</strong> / <strong>admin123</strong></li>
                    <li>📚 Bài học: <strong>{Lesson.query.count()}</strong></li>
                    <li>📝 Bài tập: <strong>{Exercise.query.count()}</strong></li>
                    <li>📊 Quiz: <strong>{Quiz.query.count()}</strong></li>
                </ul>
                <p>
                    <a href="/" style="padding: 10px 20px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px;">Về trang chủ</a>
                    <a href="/admin" style="padding: 10px 20px; background: #2d3436; color: white; text-decoration: none; border-radius: 5px;">Vào Admin</a>
                </p>
                <p style="color: #888; font-size: 14px; margin-top: 20px;">⚠️ Bạn nên xóa route /init-db sau khi chạy xong để bảo mật.</p>
            </body>
            </html>
            """
    except Exception as e:
        return f"""
        <html>
        <head><title>Lỗi</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #e74c3c;">❌ LỖI: {e}</h1>
            <p>Vui lòng kiểm tra Logs trên Render để biết chi tiết.</p>
        </body>
        </html>
        """

# ============================================================
# ROUTES CHÍNH
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Bạn không có quyền truy cập!", 403
    return render_template('admin.html')

# ===== API AUTH =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Tên đăng nhập đã tồn tại!'}), 400
    
    user = User(username=username, password=generate_password_hash(password), email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Đăng ký thành công!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'message': 'Đăng nhập thành công!', 'is_admin': user.is_admin})
    return jsonify({'error': 'Sai tên đăng nhập hoặc mật khẩu!'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Đã đăng xuất!'})

@app.route('/api/user/status')
def user_status():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username, 'is_admin': current_user.is_admin})
    return jsonify({'logged_in': False})

@app.route('/api/user/progress')
@login_required
def get_user_progress():
    progress = UserProgress.query.filter_by(user_id=current_user.id, completed=True).all()
    completed_lessons = [str(p.lesson_id) for p in progress]
    
    quiz_passed = {}
    for p in progress:
        if p.quiz_passed:
            lesson = Lesson.query.get(p.lesson_id)
            if lesson:
                quiz_passed[str(lesson.level_id)] = True
    
    return jsonify({
        'xp': current_user.xp,
        'current_level': current_user.current_level,
        'completed_lessons': completed_lessons,
        'quiz_passed': quiz_passed,
        'achievements': []
    })

# ===== API LEARNING =====
@app.route('/api/levels')
def get_levels():
    levels = [
        {'id': 1, 'name': 'Egg', 'emoji': '🐣', 'desc': 'Bắt đầu làm quen với bảng chữ cái!', 'xpRequired': 0},
        {'id': 2, 'name': 'Chick', 'emoji': '🐥', 'desc': 'Tập bay với từ vựng đầu tiên!', 'xpRequired': 150},
        {'id': 3, 'name': 'Parrot', 'emoji': '🦜', 'desc': 'Bắt chước và nói câu đơn giản!', 'xpRequired': 350},
        {'id': 4, 'name': 'Dolphin', 'emoji': '🐬', 'desc': 'Bơi lội trong biển kiến thức!', 'xpRequired': 600},
        {'id': 5, 'name': 'Lion', 'emoji': '🦁', 'desc': 'Gầm vang tự tin!', 'xpRequired': 900},
        {'id': 6, 'name': 'Eagle', 'emoji': '🦅', 'desc': 'Bay cao với đôi cánh vững vàng!', 'xpRequired': 1300}
    ]
    return jsonify(levels)

@app.route('/api/lessons/<int:level_id>')
def get_lessons(level_id):
    lessons = Lesson.query.filter_by(level_id=level_id).order_by(Lesson.order).all()
    return jsonify([{
        'id': l.id, 'name': l.name, 'description': l.description, 'xp_reward': l.xp_reward
    } for l in lessons])

@app.route('/api/lessons/detail/<int:lesson_id>')
def get_lesson_detail(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Không tìm thấy bài học!'}), 404
    return jsonify({
        'id': lesson.id,
        'name': lesson.name,
        'content': markdown.markdown(lesson.content),
        'xp_reward': lesson.xp_reward
    })

@app.route('/api/exercises/<int:lesson_id>')
def get_exercises(lesson_id):
    exercises = Exercise.query.filter_by(lesson_id=lesson_id).all()
    return jsonify([{
        'id': e.id, 'question': e.question,
        'options': [e.option_a, e.option_b, e.option_c, e.option_d],
        'correct_answer': e.correct_answer, 'explanation': e.explanation
    } for e in exercises])

@app.route('/api/quiz/<int:level_id>')
def get_quiz(level_id):
    quiz = Quiz.query.filter_by(level_id=level_id).first()
    if quiz:
        return jsonify({
            'id': quiz.id, 'question': quiz.question,
            'options': [quiz.option_a, quiz.option_b, quiz.option_c, quiz.option_d],
            'correct_answer': quiz.correct_answer, 'xp_reward': quiz.xp_reward
        })
    return jsonify({'error': 'Chưa có quiz!'}), 404

# ===== API PROGRESS =====
@app.route('/api/progress/lesson', methods=['POST'])
@login_required
def complete_lesson():
    data = request.json
    lesson_id = data.get('lesson_id')
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
    
    if not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.datetime.utcnow()
        
        lesson = Lesson.query.get(lesson_id)
        if lesson:
            current_user.xp += lesson.xp_reward
            current_user.current_level = min(6, (current_user.xp // 150) + 1)
        
        db.session.commit()
        return jsonify({'message': 'Bài học đã hoàn thành!', 'xp': current_user.xp})
    
    return jsonify({'message': 'Đã hoàn thành rồi!'})

@app.route('/api/progress/exercise', methods=['POST'])
@login_required
def complete_exercise():
    data = request.json
    exercise_id = data.get('exercise_id')
    lesson_id = data.get('lesson_id')
    user_answer = data.get('user_answer')
    
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return jsonify({'error': 'Không tìm thấy bài tập!'}), 404
    
    is_correct = (user_answer == exercise.correct_answer)
    
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if progress and is_correct:
        progress.exercise_completed = True
        db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'explanation': exercise.explanation
    })

@app.route('/api/progress/quiz', methods=['POST'])
@login_required
def pass_quiz():
    data = request.json
    level_id = data.get('level_id')
    
    quiz = Quiz.query.filter_by(level_id=level_id).first()
    if not quiz:
        return jsonify({'error': 'Không tìm thấy quiz!'}), 404
    
    lessons = Lesson.query.filter_by(level_id=level_id).all()
    for lesson in lessons:
        progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
        if progress:
            progress.quiz_passed = True
    
    current_user.xp += quiz.xp_reward
    current_user.current_level = min(6, (current_user.xp // 150) + 1)
    db.session.commit()
    return jsonify({'message': 'Quiz hoàn thành!', 'xp': current_user.xp})

# ===== API ADMIN =====
@app.route('/api/admin/stats')
@login_required
def admin_stats():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'totalUsers': User.query.count(),
        'totalLessons': Lesson.query.count(),
        'totalQuizzes': Quiz.query.count(),
        'totalXP': int(db.session.query(db.func.sum(User.xp)).scalar() or 0),
        'totalCompleted': UserProgress.query.filter_by(completed=True).count()
    })

@app.route('/api/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id, 'username': u.username, 'email': u.email,
            'xp': u.xp, 'current_level': u.current_level,
            'created_at': u.created_at.isoformat() if u.created_at else None,
            'is_admin': u.is_admin,
            'completed_lessons': UserProgress.query.filter_by(user_id=u.id, completed=True).count(),
            'quiz_passed': UserProgress.query.filter_by(user_id=u.id, quiz_passed=True).count()
        })
    return jsonify(result)

@app.route('/api/admin/user/<int:user_id>/progress')
@login_required
def admin_user_progress(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Không tìm thấy user!'}), 404
    
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    lessons = Lesson.query.all()
    lesson_map = {l.id: {'name': l.name, 'level': l.level_id} for l in lessons}
    
    completed_lessons = []
    for p in progress:
        if p.completed:
            lesson_info = lesson_map.get(p.lesson_id, {'name': 'Không xác định', 'level': 0})
            completed_lessons.append({
                'lesson_id': p.lesson_id,
                'lesson_name': lesson_info['name'],
                'level': lesson_info['level'],
                'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                'quiz_passed': p.quiz_passed
            })
    
    return jsonify({
        'user': {
            'id': user.id, 'username': user.username, 'email': user.email,
            'xp': user.xp, 'current_level': user.current_level
        },
        'completed_lessons': completed_lessons,
        'total_completed': len(completed_lessons)
    })

@app.route('/api/admin/lessons', methods=['GET', 'POST'])
@login_required
def admin_lessons():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        lessons = Lesson.query.order_by(Lesson.level_id, Lesson.order).all()
        return jsonify([{
            'id': l.id, 'level_id': l.level_id, 'name': l.name,
            'description': l.description, 'xp_reward': l.xp_reward, 'order': l.order
        } for l in lessons])
    
    if request.method == 'POST':
        data = request.json
        lesson = Lesson(**data)
        db.session.add(lesson)
        db.session.commit()
        return jsonify({'message': 'Đã thêm bài học!', 'id': lesson.id}), 201

@app.route('/api/admin/lessons/<int:lesson_id>', methods=['PUT', 'DELETE'])
@login_required
def admin_lesson_detail(lesson_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Không tìm thấy bài học!'}), 404
    
    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            setattr(lesson, key, value)
        db.session.commit()
        return jsonify({'message': 'Đã cập nhật bài học!'})
    
    if request.method == 'DELETE':
        Exercise.query.filter_by(lesson_id=lesson_id).delete()
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({'message': 'Đã xóa bài học!'})

@app.route('/api/admin/quizzes', methods=['GET', 'POST'])
@login_required
def admin_quizzes():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        quizzes = Quiz.query.all()
        return jsonify([{
            'id': q.id, 'level_id': q.level_id, 'question': q.question,
            'option_a': q.option_a, 'option_b': q.option_b,
            'option_c': q.option_c, 'option_d': q.option_d,
            'correct_answer': q.correct_answer, 'xp_reward': q.xp_reward
        } for q in quizzes])
    
    if request.method == 'POST':
        data = request.json
        quiz = Quiz(**data)
        db.session.add(quiz)
        db.session.commit()
        return jsonify({'message': 'Đã thêm quiz!', 'id': quiz.id}), 201

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['PUT', 'DELETE'])
@login_required
def admin_quiz_detail(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Không tìm thấy quiz!'}), 404
    
    if request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            setattr(quiz, key, value)
        db.session.commit()
        return jsonify({'message': 'Đã cập nhật quiz!'})
    
    if request.method == 'DELETE':
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Đã xóa quiz!'})

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
