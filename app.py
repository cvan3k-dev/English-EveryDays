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
CORS(app, supports_credentials=True)

# ===== LOGIN =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============================================================
# KHỞI TẠO DATABASE VÀ DỮ LIỆU MẪU (TỰ ĐỘNG)
# ============================================================
with app.app_context():
    # Tạo thư mục instance
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # Tạo bảng
    db.create_all()
    print("✅ Database và các bảng đã được tạo!")
    
    # ---- TẠO ADMIN ----
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@example.com',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Đã tạo admin: admin / admin123")
    
    # ---- TẠO BÀI HỌC ----
    if Lesson.query.count() == 0:
        print("⏳ Đang tạo dữ liệu mẫu...")
        
        lessons_data = [
            # LEVEL 1
            {'level_id':1, 'name':'🔤 Bảng chữ cái ABC', 'description':'Học 26 chữ cái', 
             'content':'## 📚 LÝ THUYẾT\nBảng chữ cái tiếng Anh có 26 chữ cái...', 'xp_reward':20, 'order':1},
            {'level_id':1, 'name':'🔢 Số đếm 1-20', 'description':'Học đếm từ 1 đến 20', 
             'content':'## 📚 LÝ THUYẾT\nSố đếm từ 1 đến 20...', 'xp_reward':20, 'order':2},
            # LEVEL 2
            {'level_id':2, 'name':'👨‍👩‍👧‍👦 Gia đình', 'description':'Từ vựng về gia đình', 
             'content':'## 📚 LÝ THUYẾT\nTừ vựng về gia đình...', 'xp_reward':30, 'order':1},
            {'level_id':2, 'name':'🐱 Động vật', 'description':'Từ vựng về động vật', 
             'content':'## 📚 LÝ THUYẾT\nTừ vựng về động vật...', 'xp_reward':30, 'order':2},
            # LEVEL 3
            {'level_id':3, 'name':'⏰ Thì hiện tại đơn', 'description':'Cấu trúc và cách dùng', 
             'content':'## 📚 LÝ THUYẾT\nThì hiện tại đơn...', 'xp_reward':35, 'order':1},
            {'level_id':3, 'name':'📝 Câu phủ định & nghi vấn', 'description':'Cách đặt câu phủ định và câu hỏi', 
             'content':'## 📚 LÝ THUYẾT\nCâu phủ định và nghi vấn...', 'xp_reward':35, 'order':2},
            # LEVEL 4
            {'level_id':4, 'name':'⏳ Thì quá khứ đơn', 'description':'Cách dùng thì quá khứ đơn', 
             'content':'## 📚 LÝ THUYẾT\nThì quá khứ đơn...', 'xp_reward':45, 'order':1},
            {'level_id':4, 'name':'🔮 Thì tương lai gần', 'description':'Cấu trúc "be going to"', 
             'content':'## 📚 LÝ THUYẾT\nThì tương lai gần...', 'xp_reward':45, 'order':2},
            # LEVEL 5
            {'level_id':5, 'name':'🎯 Câu điều kiện loại 1', 'description':'Cấu trúc If + hiện tại, will + V', 
             'content':'## 📚 LÝ THUYẾT\nCâu điều kiện loại 1...', 'xp_reward':55, 'order':1},
            {'level_id':5, 'name':'📖 Câu bị động', 'description':'Cấu trúc câu bị động', 
             'content':'## 📚 LÝ THUYẾT\nCâu bị động...', 'xp_reward':55, 'order':2},
            # LEVEL 6
            {'level_id':6, 'name':'💼 Giao tiếp công sở', 'description':'Từ vựng và mẫu câu công sở', 
             'content':'## 📚 LÝ THUYẾT\nTừ vựng công sở...', 'xp_reward':70, 'order':1},
            {'level_id':6, 'name':'🌍 Du lịch & Văn hóa', 'description':'Từ vựng du lịch và giao tiếp', 
             'content':'## 📚 LÝ THUYẾT\nTừ vựng du lịch...', 'xp_reward':70, 'order':2},
        ]
        for data in lessons_data:
            db.session.add(Lesson(**data))
        db.session.commit()
        print(f"✅ Đã tạo {Lesson.query.count()} bài học")
    
    # ---- TẠO BÀI TẬP ----
    if Exercise.query.count() == 0:
        exercises = [
            # Level 1 - Bài 1
            {'lesson_id':1, 'question':'Chữ cái nào là nguyên âm?', 'option_a':'B', 'option_b':'C', 'option_c':'A', 'option_d':'D', 'correct_answer':2, 'explanation':'Nguyên âm là A, E, I, O, U'},
            {'lesson_id':1, 'question':'Phát âm chữ "B" là gì?', 'option_a':'/biː/', 'option_b':'/siː/', 'option_c':'/diː/', 'option_d':'/iː/', 'correct_answer':0, 'explanation':'B phát âm là /biː/'},
            # Level 1 - Bài 2
            {'lesson_id':2, 'question':'Số 7 trong tiếng Anh là gì?', 'option_a':'Seven', 'option_b':'Six', 'option_c':'Eight', 'option_d':'Nine', 'correct_answer':0, 'explanation':'7 = Seven'},
            {'lesson_id':2, 'question':'Số 12 trong tiếng Anh là gì?', 'option_a':'Ten', 'option_b':'Eleven', 'option_c':'Twelve', 'option_d':'Twenty', 'correct_answer':2, 'explanation':'12 = Twelve'},
            # Level 2 - Bài 1
            {'lesson_id':3, 'question':'"Mẹ" trong tiếng Anh là gì?', 'option_a':'Father', 'option_b':'Mother', 'option_c':'Brother', 'option_d':'Sister', 'correct_answer':1, 'explanation':'Mother = Mẹ'},
            {'lesson_id':3, 'question':'"Anh trai" trong tiếng Anh là gì?', 'option_a':'Sister', 'option_b':'Brother', 'option_c':'Uncle', 'option_d':'Aunt', 'correct_answer':1, 'explanation':'Brother = Anh trai'},
            # Level 2 - Bài 2
            {'lesson_id':4, 'question':'"Dog" có nghĩa là gì?', 'option_a':'Mèo', 'option_b':'Chó', 'option_c':'Chim', 'option_d':'Cá', 'correct_answer':1, 'explanation':'Dog = Chó'},
            {'lesson_id':4, 'question':'"Cat" có nghĩa là gì?', 'option_a':'Chó', 'option_b':'Mèo', 'option_c':'Chim', 'option_d':'Cá', 'correct_answer':1, 'explanation':'Cat = Mèo'},
            # Level 3 - Bài 1
            {'lesson_id':5, 'question':'Chia động từ: She (go) ____ to school.', 'option_a':'go', 'option_b':'goes', 'option_c':'going', 'option_d':'went', 'correct_answer':1, 'explanation':'She + goes'},
            {'lesson_id':5, 'question':'Chia động từ: They (play) ____ football.', 'option_a':'play', 'option_b':'plays', 'option_c':'playing', 'option_d':'played', 'correct_answer':0, 'explanation':'They + play'},
            # Level 3 - Bài 2
            {'lesson_id':6, 'question':'Phủ định: "He likes cats." → He ____ cats.', 'option_a':"don't like", 'option_b':"doesn't like", 'option_c':"not like", 'option_d':"isn't like", 'correct_answer':1, 'explanation':'He + doesn\'t + V'},
            # Level 4 - Bài 1
            {'lesson_id':7, 'question':'Quá khứ của "go" là gì?', 'option_a':'goed', 'option_b':'went', 'option_c':'gone', 'option_d':'going', 'correct_answer':1, 'explanation':'go → went'},
            {'lesson_id':7, 'question':'Quá khứ của "visit" là gì?', 'option_a':'visited', 'option_b':'visitted', 'option_c':'visit', 'option_d':'visiting', 'correct_answer':0, 'explanation':'visit → visited'},
            # Level 4 - Bài 2
            {'lesson_id':8, 'question':'"I am going to study" nghĩa là gì?', 'option_a':'Tôi đang học', 'option_b':'Tôi sẽ học', 'option_c':'Tôi đã học', 'option_d':'Tôi học', 'correct_answer':1, 'explanation':'be going to = sẽ (dự định)'},
            # Level 5 - Bài 1
            {'lesson_id':9, 'question':'Hoàn thành: If it rains, I ____ stay home.', 'option_a':'will', 'option_b':'would', 'option_c':'am', 'option_d':'was', 'correct_answer':0, 'explanation':'Câu điều kiện loại 1: will + V'},
            # Level 5 - Bài 2
            {'lesson_id':10, 'question':'Bị động: "She writes a letter" → A letter ____ by her.', 'option_a':'is written', 'option_b':'was written', 'option_c':'is writing', 'option_d':'writes', 'correct_answer':0, 'explanation':'Hiện tại đơn bị động: is/am/are + V3/ed'},
            # Level 6 - Bài 1
            {'lesson_id':11, 'question':'Từ nào có nghĩa là "cuộc họp"?', 'option_a':'Meeting', 'option_b':'Report', 'option_c':'Email', 'option_d':'Deadline', 'correct_answer':0, 'explanation':'Meeting = Cuộc họp'},
            {'lesson_id':11, 'question':'"Deadline" có nghĩa là gì?', 'option_a':'Cuộc họp', 'option_b':'Báo cáo', 'option_c':'Hạn chót', 'option_d':'Thư điện tử', 'correct_answer':2, 'explanation':'Deadline = Hạn chót'},
        ]
        for data in exercises:
            db.session.add(Exercise(**data))
        db.session.commit()
        print(f"✅ Đã tạo {Exercise.query.count()} bài tập")
    
    # ---- TẠO QUIZ ----
    if Quiz.query.count() == 0:
        quizzes = [
            {'level_id':1, 'question':'Từ nào là màu sắc?', 'option_a':'Red', 'option_b':'Table', 'option_c':'Run', 'option_d':'Happy', 'correct_answer':0, 'xp_reward':30},
            {'level_id':2, 'question':'"Cat" có nghĩa là gì?', 'option_a':'Chó', 'option_b':'Mèo', 'option_c':'Chim', 'option_d':'Cá', 'correct_answer':1, 'xp_reward':40},
            {'level_id':3, 'question':'Câu nào đúng ở thì hiện tại đơn?', 'option_a':'He eat apples.', 'option_b':'He eats apples.', 'option_c':'He eating apples.', 'option_d':'He ate apples.', 'correct_answer':1, 'xp_reward':50},
            {'level_id':4, 'question':'"Beautiful" có nghĩa là gì?', 'option_a':'Xấu xí', 'option_b':'Đẹp', 'option_c':'Cao', 'option_d':'Thấp', 'correct_answer':1, 'xp_reward':50},
            {'level_id':5, 'question':'Câu bị động của "She writes a letter" là gì?', 'option_a':'A letter is written by her.', 'option_b':'A letter was written by her.', 'option_c':'A letter is being written by her.', 'option_d':'A letter has been written by her.', 'correct_answer':0, 'xp_reward':60},
            {'level_id':6, 'question':'Từ nào là đại từ quan hệ?', 'option_a':'Who', 'option_b':'And', 'option_c':'But', 'option_d':'So', 'correct_answer':0, 'xp_reward':70},
        ]
        for data in quizzes:
            db.session.add(Quiz(**data))
        db.session.commit()
        print(f"✅ Đã tạo {Quiz.query.count()} quiz")
    
    print("🎉 Khởi tạo dữ liệu hoàn tất!")

# ============================================================
# ROUTE TẠO DỮ LIỆU THỦ CÔNG (NẾU CẦN)
# ============================================================
@app.route('/init-db')
def init_db_route():
    try:
        with app.app_context():
            if Quiz.query.count() == 0:
                # (code tạo quiz như trên)
                pass
            return f"✅ Dữ liệu hiện có: Bài học {Lesson.query.count()}, Bài tập {Exercise.query.count()}, Quiz {Quiz.query.count()}"
    except Exception as e:
        return f"❌ Lỗi: {e}"

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
        {'id':1,'name':'Egg','emoji':'🐣','desc':'Bắt đầu làm quen với bảng chữ cái!','xpRequired':0},
        {'id':2,'name':'Chick','emoji':'🐥','desc':'Tập bay với từ vựng đầu tiên!','xpRequired':150},
        {'id':3,'name':'Parrot','emoji':'🦜','desc':'Bắt chước và nói câu đơn giản!','xpRequired':350},
        {'id':4,'name':'Dolphin','emoji':'🐬','desc':'Bơi lội trong biển kiến thức!','xpRequired':600},
        {'id':5,'name':'Lion','emoji':'🦁','desc':'Gầm vang tự tin!','xpRequired':900},
        {'id':6,'name':'Eagle','emoji':'🦅','desc':'Bay cao với đôi cánh vững vàng!','xpRequired':1300}
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
