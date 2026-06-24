import os
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Lesson, Exercise, Quiz, UserProgress
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import markdown  # Thư viện chuyển markdown sang HTML

app = Flask(__name__)

# ===== CẤU HÌNH =====
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Đường dẫn database tuyệt đối
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

# ===== TẠO BẢNG VÀ DỮ LIỆU MẪU (CÓ NỘI DUNG HỌC PHONG PHÚ) =====
with app.app_context():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db.create_all()
    
    if Lesson.query.count() == 0:
        # ===== LEVEL 1: EGG =====
        lessons_data = [
            # Level 1 - Bài 1
            {
                'level_id': 1,
                'name': '🔤 Bảng chữ cái ABC',
                'description': 'Học 26 chữ cái tiếng Anh qua hình ảnh và âm thanh',
                'content': '''
## 📚 Lý thuyết
Bảng chữ cái tiếng Anh có 26 chữ cái, chia thành:
- **Nguyên âm (Vowels):** A, E, I, O, U (5 chữ)
- **Phụ âm (Consonants):** 21 chữ còn lại

## 🔊 Cách phát âm
| Chữ | Phiên âm | Ví dụ |
|-----|----------|-------|
| A | /eɪ/ | **A**pple |
| B | /biː/ | **B**all |
| C | /siː/ | **C**at |
| D | /diː/ | **D**og |
| E | /iː/ | **E**lephant |

## 🎯 Ví dụ
- **A** → **A**pple (quả táo)
- **B** → **B**all (quả bóng)
- **C** → **C**at (con mèo)

## 📝 Bài tập
1. Chữ cái nào là nguyên âm?
2. Phát âm chữ "A" trong tiếng Anh là gì?
''',
                'xp_reward': 20,
                'order': 1
            },
            # Level 1 - Bài 2
            {
                'level_id': 1,
                'name': '🔢 Số đếm 1-20',
                'description': 'Học đếm từ 1 đến 20',
                'content': '''
## 📚 Lý thuyết
Số đếm từ 1 đến 20:
- **1-10:** One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten
- **11-20:** Eleven, Twelve, Thirteen, Fourteen, Fifteen, Sixteen, Seventeen, Eighteen, Nineteen, Twenty

## 🎯 Ví dụ
- **One** apple = 1 quả táo
- **Five** dogs = 5 con chó
- **Twenty** students = 20 học sinh

## 📝 Bài tập
Điền số thích hợp:
1. There are ____ (7) days in a week.
2. I have ____ (3) brothers.
''',
                'xp_reward': 20,
                'order': 2
            },
            # Level 2 - Bài 1
            {
                'level_id': 2,
                'name': '👨‍👩‍👧‍👦 Gia đình (Family)',
                'description': 'Từ vựng về các thành viên trong gia đình',
                'content': '''
## 📚 Lý thuyết
Từ vựng về gia đình:
- **Father (Dad)** - Bố
- **Mother (Mom)** - Mẹ
- **Brother** - Anh/Em trai
- **Sister** - Chị/Em gái
- **Grandfather (Grandpa)** - Ông
- **Grandmother (Grandma)** - Bà

## 📝 Cấu trúc câu
- "This is my mother." (Đây là mẹ tôi.)
- "I have one brother." (Tôi có một anh trai.)

## 🎯 Ví dụ
My **father** is a doctor. (Bố tôi là bác sĩ.)
Her **sister** is a teacher. (Chị gái cô ấy là giáo viên.)

## 📝 Bài tập
1. "Mẹ" trong tiếng Anh là gì?
2. Dịch: "Tôi có một em gái."
''',
                'xp_reward': 30,
                'order': 1
            },
            # Level 3 - Bài 1 (Thì hiện tại đơn)
            {
                'level_id': 3,
                'name': '⏰ Thì hiện tại đơn',
                'description': 'Cấu trúc và cách dùng thì hiện tại đơn',
                'content': '''
## 📚 Lý thuyết
Thì hiện tại đơn diễn tả:
- **Hành động thường xuyên xảy ra** (I eat breakfast every day.)
- **Sự thật hiển nhiên** (The sun rises in the east.)
- **Sở thích, thói quen** (She likes music.)

## 🔧 Cấu trúc
**Khẳng định:** S + V(s/es) + O
- I/You/We/They + V (nguyên mẫu)
- He/She/It + V(s/es)

**Phủ định:** S + do/does + not + V
- I/You/We/They + do not (don't) + V
- He/She/It + does not (doesn't) + V

**Nghi vấn:** Do/Does + S + V?

## 🎯 Ví dụ
- **I eat** breakfast at 7 AM.
- **She eats** lunch at noon.
- **They do not (don't) play** football.

## 📝 Bài tập
Chia động từ trong ngoặc:
1. She (go) ____ to school every day.
2. They (not/watch) ____ TV in the morning.
''',
                'xp_reward': 35,
                'order': 1
            },
            # Thêm các bài học khác tương tự cho level 4,5,6
            # (Bạn có thể tự thêm hoặc yêu cầu tôi viết thêm)
        ]
        
        for data in lessons_data:
            lesson = Lesson(
                level_id=data['level_id'],
                name=data['name'],
                description=data['description'],
                content=data['content'],
                xp_reward=data['xp_reward'],
                order=data['order']
            )
            db.session.add(lesson)
        
        # ===== THÊM BÀI TẬP =====
        exercises_data = [
            # Bài tập cho Level 1 - Bài 1 (Bảng chữ cái)
            {
                'lesson_id': 1,  # Giả sử bài học đầu tiên có id=1
                'question': 'Chữ cái nào sau đây là nguyên âm?',
                'option_a': 'B',
                'option_b': 'C',
                'option_c': 'A',
                'option_d': 'D',
                'correct_answer': 2,  # C
                'exercise_type': 'multiple_choice',
                'explanation': 'Nguyên âm là A, E, I, O, U'
            },
            {
                'lesson_id': 1,
                'question': 'Phát âm đúng của chữ "B" là gì?',
                'option_a': '/biː/',
                'option_b': '/siː/',
                'option_c': '/diː/',
                'option_d': '/iː/',
                'correct_answer': 0,
                'exercise_type': 'multiple_choice',
                'explanation': 'B phát âm là /biː/'
            },
            # Bài tập cho Level 1 - Bài 2 (Số đếm)
            {
                'lesson_id': 2,
                'question': 'Số 7 trong tiếng Anh là gì?',
                'option_a': 'Seven',
                'option_b': 'Six',
                'option_c': 'Eight',
                'option_d': 'Nine',
                'correct_answer': 0,
                'exercise_type': 'multiple_choice',
                'explanation': '7 = Seven'
            },
            # Bài tập cho Level 2 - Bài 1 (Gia đình)
            {
                'lesson_id': 3,
                'question': '"Mẹ" trong tiếng Anh là gì?',
                'option_a': 'Father',
                'option_b': 'Mother',
                'option_c': 'Brother',
                'option_d': 'Sister',
                'correct_answer': 1,
                'exercise_type': 'multiple_choice',
                'explanation': 'Mother = Mẹ'
            },
            # Bài tập cho Level 3 - Bài 1 (Hiện tại đơn)
            {
                'lesson_id': 4,
                'question': 'Chia động từ: She (go) ____ to school every day.',
                'option_a': 'go',
                'option_b': 'goes',
                'option_c': 'going',
                'option_d': 'went',
                'correct_answer': 1,
                'exercise_type': 'multiple_choice',
                'explanation': 'Chủ ngữ She + V(s/es) → goes'
            },
        ]
        
        for data in exercises_data:
            exercise = Exercise(
                lesson_id=data['lesson_id'],
                question=data['question'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                correct_answer=data['correct_answer'],
                exercise_type=data.get('exercise_type', 'multiple_choice'),
                explanation=data.get('explanation', '')
            )
            db.session.add(exercise)
        
        # ===== THÊM QUIZ =====
        quizzes_data = [
            {
                'level_id': 1,
                'question': 'Từ nào là màu sắc?',
                'option_a': 'Red',
                'option_b': 'Table',
                'option_c': 'Run',
                'option_d': 'Happy',
                'correct_answer': 0,
                'xp_reward': 30
            },
            {
                'level_id': 2,
                'question': '"Cat" có nghĩa là gì?',
                'option_a': 'Chó',
                'option_b': 'Mèo',
                'option_c': 'Chim',
                'option_d': 'Cá',
                'correct_answer': 1,
                'xp_reward': 40
            },
            {
                'level_id': 3,
                'question': 'Câu nào đúng ở thì hiện tại đơn?',
                'option_a': 'He eat apples.',
                'option_b': 'He eats apples.',
                'option_c': 'He eating apples.',
                'option_d': 'He ate apples.',
                'correct_answer': 1,
                'xp_reward': 50
            },
        ]
        
        for data in quizzes_data:
            quiz = Quiz(
                level_id=data['level_id'],
                question=data['question'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                correct_answer=data['correct_answer'],
                xp_reward=data['xp_reward']
            )
            db.session.add(quiz)
        
        # Tạo admin
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@example.com',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Đã tạo dữ liệu mẫu (bài học, bài tập, quiz) và admin!")

# ===== API =====

# ---- Lấy chi tiết bài học (có nội dung markdown) ----
@app.route('/api/lessons/detail/<int:lesson_id>')
def get_lesson_detail(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Không tìm thấy bài học!'}), 404
    
    # Chuyển markdown sang HTML
    html_content = markdown.markdown(lesson.content)
    
    return jsonify({
        'id': lesson.id,
        'name': lesson.name,
        'description': lesson.description,
        'content': html_content,
        'xp_reward': lesson.xp_reward
    })

# ---- Lấy danh sách bài tập của một bài học ----
@app.route('/api/exercises/<int:lesson_id>')
def get_exercises(lesson_id):
    exercises = Exercise.query.filter_by(lesson_id=lesson_id).all()
    return jsonify([{
        'id': e.id,
        'question': e.question,
        'options': [e.option_a, e.option_b, e.option_c, e.option_d],
        'correct_answer': e.correct_answer,
        'type': e.exercise_type,
        'explanation': e.explanation
    } for e in exercises])

# ---- Lấy danh sách Level ----
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

# ---- Lấy bài học theo Level ----
@app.route('/api/lessons/<int:level_id>')
def get_lessons(level_id):
    lessons = Lesson.query.filter_by(level_id=level_id).order_by(Lesson.order).all()
    return jsonify([{
        'id': l.id,
        'name': l.name,
        'description': l.description,
        'xp_reward': l.xp_reward
    } for l in lessons])

# ---- Lấy Quiz theo Level ----
@app.route('/api/quiz/<int:level_id>')
def get_quiz(level_id):
    quiz = Quiz.query.filter_by(level_id=level_id).first()
    if quiz:
        return jsonify({
            'id': quiz.id,
            'question': quiz.question,
            'options': [quiz.option_a, quiz.option_b, quiz.option_c, quiz.option_d],
            'correct_answer': quiz.correct_answer,
            'xp_reward': quiz.xp_reward
        })
    return jsonify({'error': 'Chưa có quiz!'}), 404

# ---- Hoàn thành bài tập ----
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
    
    # Cập nhật tiến trình
    progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if progress and is_correct:
        progress.exercise_completed = True
        db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'explanation': exercise.explanation
    })

# ---- Các API khác (giữ nguyên) ----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Bạn không có quyền truy cập!", 403
    return "Trang Admin (đang phát triển)"

# ===== LOGIN/REGISTER =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Tên đăng nhập đã tồn tại!'}), 400
    
    hashed = generate_password_hash(password)
    user = User(username=username, password=hashed, email=email)
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
        return jsonify({
            'logged_in': True,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        })
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

# ===== RUN =====
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
