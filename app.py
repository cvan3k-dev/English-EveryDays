import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Lesson, Quiz, UserProgress
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

# ===== CẤU HÌNH CHO RENDER =====
# Lấy SECRET_KEY từ biến môi trường (Render sẽ tạo tự động)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Cấu hình database - dùng SQLite (có thể nâng cấp lên PostgreSQL sau)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/english_journey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# Khởi tạo Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== TẠO BẢNG VÀ DỮ LIỆU MẪU =====
with app.app_context():
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

# ===== ROUTES =====
# (Các route bạn đã có: /, /admin, /api/login, /api/register, ...)
# ... (giữ nguyên các route từ file app.py trước)

# ===== RUN =====
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
