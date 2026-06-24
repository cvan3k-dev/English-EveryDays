import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Lesson, Quiz, UserProgress
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# ==================== KHỞI TẠO APP ====================
app = Flask(__name__)

# ===== CẤU HÌNH CHO RENDER =====
# Lấy SECRET_KEY từ biến môi trường (Render sẽ tạo tự động)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ---- SỬA ĐƯỜNG DẪN DATABASE (BƯỚC 3) ----
# Lấy đường dẫn thư mục chứa file app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Tạo đường dẫn tuyệt đối đến file database trong thư mục instance
DB_PATH = os.path.join(BASE_DIR, 'instance', 'english_journey.db')
# Cấu hình database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# ===== KHỞI TẠO FLASK-LOGIN =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== TẠO BẢNG VÀ DỮ LIỆU MẪU =====
with app.app_context():
    # Tạo thư mục instance nếu chưa tồn tại (quan trọng cho Render)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    db.create_all()
    
    # Thêm dữ liệu mẫu nếu chưa có
    if Lesson.query.count() == 0:
        # Thêm levels (có thể thêm vào model nếu muốn)
        sample_lessons = [
            Lesson(level_id=1, name='Bảng chữ cái', description='Học 26 chữ cái', content='A B C D E F G...', xp_reward=15, order=1),
            Lesson(level_id=1, name='Số đếm 1-20', description='Đếm từ 1 đến 20', content='One, Two, Three...', xp_reward=15, order=2),
            Lesson(level_id=2, name='Gia đình', description='Từ vựng về gia đình', content='Father, Mother, Sister...', xp_reward=25, order=1),
            Lesson(level_id=2, name='Động vật', description='Từ vựng động vật', content='Cat, Dog, Bird...', xp_reward=25, order=2),
            Lesson(level_id=3, name='Thì hiện tại đơn', description='Cấu trúc cơ bản', content='I eat, You eat, He eats...', xp_reward=35, order=1),
            Lesson(level_id=3, name='Câu phủ định', description='Cách dùng don\'t/doesn\'t', content='I do not like...', xp_reward=35, order=2),
            Lesson(level_id=4, name='Thì quá khứ đơn', description='Động từ bất quy tắc', content='I went, You ate...', xp_reward=45, order=1),
            Lesson(level_id=4, name='Thì tương lai gần', description='Cấu trúc going to', content='I am going to...', xp_reward=45, order=2),
            Lesson(level_id=5, name='Câu điều kiện', description='If + hiện tại, will + V', content='If it rains, I will stay...', xp_reward=55, order=1),
            Lesson(level_id=5, name='Câu bị động', description='Be + V3/ed', content='The cake is eaten...', xp_reward=55, order=2),
            Lesson(level_id=6, name='Giao tiếp công sở', description='Từ vựng chuyên ngành', content='Meeting, Presentation...', xp_reward=70, order=1),
            Lesson(level_id=6, name='Thuyết trình', description='Cấu trúc bài thuyết trình', content='First, Then, Finally...', xp_reward=70, order=2),
        ]
        for l in sample_lessons:
            db.session.add(l)
        
        # Thêm Quiz mẫu
        sample_quizzes = [
            Quiz(level_id=1, question='Từ nào là màu sắc?', 
                 option_a='Red', option_b='Table', option_c='Run', option_d='Happy',
                 correct_answer=0, xp_reward=30),
            Quiz(level_id=2, question='"Cat" có nghĩa là gì?',
                 option_a='Chó', option_b='Mèo', option_c='Chim', option_d='Cá',
                 correct_answer=1, xp_reward=40),
            Quiz(level_id=3, question='Câu nào đúng ở thì hiện tại đơn?',
                 option_a='He eat apples.', option_b='He eats apples.', 
                 option_c='He eating apples.', option_d='He ate apples.',
                 correct_answer=1, xp_reward=50),
            Quiz(level_id=4, question='"Beautiful" có nghĩa là gì?',
                 option_a='Xấu xí', option_b='Đẹp', option_c='Cao', option_d='Thấp',
                 correct_answer=1, xp_reward=50),
            Quiz(level_id=5, question='Câu bị động của "She writes a letter" là gì?',
                 option_a='A letter is written by her.', 
                 option_b='A letter was written by her.',
                 option_c='A letter is being written by her.',
                 option_d='A letter has been written by her.',
                 correct_answer=0, xp_reward=60),
            Quiz(level_id=6, question='Từ nào là đại từ quan hệ?',
                 option_a='Who', option_b='And', option_c='But', option_d='So',
                 correct_answer=0, xp_reward=70),
        ]
        for q in sample_quizzes:
            db.session.add(q)
        
        # Tạo admin mặc định
        admin = User(
            username='admin', 
            password=generate_password_hash('admin123'), 
            email='admin@example.com', 
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Đã tạo dữ liệu mẫu và admin (user: admin, pass: admin123)")

# ==================== ROUTES ====================

# ===== TRANG CHỦ =====
@app.route('/')
def index():
    return render_template('index.html')

# ===== TRANG ADMIN =====
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return "Bạn không có quyền truy cập!", 403
    return render_template('admin.html')

# ===== API: ĐĂNG NHẬP/ĐĂNG KÝ =====
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

# ===== API: KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP =====
@app.route('/api/user/status')
def user_status():
    if current_user.is_authenticated:
        return jsonify({
            'logged_in': True,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        })
    return jsonify({'logged_in': False})

# ===== API: LẤY TIẾN TRÌNH USER =====
@app.route('/api/user/progress')
@login_required
def get_user_progress():
    # Lấy danh sách bài học đã hoàn thành
    progress = UserProgress.query.filter_by(user_id=current_user.id, completed=True).all()
    completed_lessons = [str(p.lesson_id) for p in progress]
    
    # Lấy danh sách quiz đã vượt qua
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
        'achievements': []  # Có thể thêm sau
    })

# ===== API: LẤY DANH SÁCH LEVEL =====
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

# ===== API: LẤY BÀI HỌC THEO LEVEL =====
@app.route('/api/lessons/<int:level_id>')
def get_lessons(level_id):
    lessons = Lesson.query.filter_by(level_id=level_id).order_by(Lesson.order).all()
    return jsonify([{
        'id': l.id,
        'name': l.name,
        'description': l.description,
        'xp_reward': l.xp_reward,
        'content': l.content
    } for l in lessons])

# ===== API: LẤY QUIZ THEO LEVEL =====
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

# ===== API: HOÀN THÀNH BÀI HỌC =====
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
        
        # Cộng XP
        lesson = Lesson.query.get(lesson_id)
        if lesson:
            current_user.xp += lesson.xp_reward
            # Kiểm tra lên level
            if current_user.xp >= 150:
                current_user.current_level = min(6, (current_user.xp // 150) + 1)
        
        db.session.commit()
        return jsonify({'message': 'Bài học đã hoàn thành!', 'xp': current_user.xp, 'xp_reward': lesson.xp_reward if lesson else 0})
    
    return jsonify({'message': 'Đã hoàn thành rồi!'})

# ===== API: HOÀN THÀNH QUIZ =====
@app.route('/api/progress/quiz', methods=['POST'])
@login_required
def pass_quiz():
    data = request.json
    level_id = data.get('level_id')
    
    # Tìm quiz của level
    quiz = Quiz.query.filter_by(level_id=level_id).first()
    if not quiz:
        return jsonify({'error': 'Không tìm thấy quiz!'}), 404
    
    # Cập nhật progress
    lessons = Lesson.query.filter_by(level_id=level_id).all()
    for lesson in lessons:
        progress = UserProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
        if progress:
            progress.quiz_passed = True
    
    # Cộng XP
    current_user.xp += quiz.xp_reward
    if current_user.xp >= 150:
        current_user.current_level = min(6, (current_user.xp // 150) + 1)
    
    db.session.commit()
    return jsonify({'message': 'Quiz hoàn thành!', 'xp': current_user.xp})

# ===== API ADMIN: THỐNG KÊ =====
@app.route('/api/admin/stats')
@login_required
def admin_stats():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_users = User.query.count()
    total_lessons = Lesson.query.count()
    total_quizzes = Quiz.query.count()
    total_xp = db.session.query(db.func.sum(User.xp)).scalar() or 0
    
    return jsonify({
        'totalUsers': total_users,
        'totalLessons': total_lessons,
        'totalQuizzes': total_quizzes,
        'totalXP': total_xp
    })

# ===== API ADMIN: DANH SÁCH USER =====
@app.route('/api/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'xp': u.xp,
        'current_level': u.current_level,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])

# ===== API ADMIN: QUẢN LÝ BÀI HỌC =====
@app.route('/api/admin/lessons', methods=['GET', 'POST'])
@login_required
def admin_lessons():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        lessons = Lesson.query.all()
        return jsonify([{
            'id': l.id,
            'level_id': l.level_id,
            'name': l.name,
            'description': l.description,
            'content': l.content,
            'xp_reward': l.xp_reward,
            'order': l.order
        } for l in lessons])
    
    if request.method == 'POST':
        data = request.json
        lesson = Lesson(
            level_id=data.get('level_id', 1),
            name=data.get('name'),
            description=data.get('description', ''),
            content=data.get('content', ''),
            xp_reward=data.get('xp_reward', 20),
            order=data.get('order', 0)
        )
        db.session.add(lesson)
        db.session.commit()
        return jsonify({'message': 'Đã thêm bài học!'}), 201

# ===== API ADMIN: SỬA/XÓA BÀI HỌC =====
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
        lesson.name = data.get('name', lesson.name)
        lesson.description = data.get('description', lesson.description)
        lesson.content = data.get('content', lesson.content)
        lesson.xp_reward = data.get('xp_reward', lesson.xp_reward)
        lesson.level_id = data.get('level_id', lesson.level_id)
        lesson.order = data.get('order', lesson.order)
        db.session.commit()
        return jsonify({'message': 'Đã cập nhật bài học!'})
    
    if request.method == 'DELETE':
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({'message': 'Đã xóa bài học!'})

# ===== API ADMIN: QUẢN LÝ QUIZ =====
@app.route('/api/admin/quizzes')
@login_required
def admin_quizzes():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quizzes = Quiz.query.all()
    return jsonify([{
        'id': q.id,
        'level_id': q.level_id,
        'question': q.question,
        'option_a': q.option_a,
        'option_b': q.option_b,
        'option_c': q.option_c,
        'option_d': q.option_d,
        'correct_answer': q.correct_answer,
        'xp_reward': q.xp_reward
    } for q in quizzes])

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
