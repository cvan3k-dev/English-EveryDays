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
# KHỞI TẠO DATABASE VÀ DỮ LIỆU MẪU (TỰ ĐỘNG KHI CHẠY)
# ============================================================
with app.app_context():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db.create_all()
    print("✅ Database và các bảng đã được tạo!")
    
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
        print("✅ Đã tạo admin: admin / admin123")
    
    # === TẠO DỮ LIỆU MẪU (CHỈ KHI CHƯA CÓ BÀI HỌC) ===
    if Lesson.query.count() == 0:
        print("⏳ Đang tạo dữ liệu mẫu...")
        
        # ===== BÀI HỌC (LÝ THUYẾT CHI TIẾT) =====
        lessons_data = [
            # LEVEL 1: EGG
            {
                'level_id': 1,
                'name': '🔤 Bảng chữ cái ABC',
                'description': 'Học 26 chữ cái tiếng Anh qua hình ảnh',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Bảng chữ cái tiếng Anh có **26 chữ cái**, chia thành:
- **Nguyên âm (Vowels):** A, E, I, O, U (5 chữ)
- **Phụ âm (Consonants):** 21 chữ còn lại

### 🎯 MẸO GHI NHỚ
Hát theo bài hát ABC để nhớ thứ tự các chữ cái!

### 📝 VÍ DỤ
- **A** → **A**pple (quả táo)
- **B** → **B**all (quả bóng)
- **C** → **C**at (con mèo)

### ✅ BÀI TẬP THỰC HÀNH
1. Chữ cái nào là nguyên âm? (Khoanh tròn)
2. Viết 3 từ bắt đầu bằng chữ cái "B".
                ''',
                'xp_reward': 20,
                'order': 1
            },
            {
                'level_id': 1,
                'name': '🔢 Số đếm 1-20',
                'description': 'Học đếm từ 1 đến 20',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Số đếm từ 1 đến 20:
- **1-10:** One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten
- **11-20:** Eleven, Twelve, Thirteen, Fourteen, Fifteen, Sixteen, Seventeen, Eighteen, Nineteen, Twenty

### 🎯 MẸO GHI NHỚ
- Số 13-19 đều có đuôi "**teen**"
- Số 20 là "**Twenty**"

### 📝 VÍ DỤ
- **One** apple = 1 quả táo
- **Five** dogs = 5 con chó
- **Twenty** students = 20 học sinh

### ✅ BÀI TẬP THỰC HÀNH
1. Điền số thích hợp: There are ____ (7) days in a week.
2. Viết số 15 bằng tiếng Anh.
                ''',
                'xp_reward': 20,
                'order': 2
            },
            # LEVEL 2: CHICK
            {
                'level_id': 2,
                'name': '👨‍👩‍👧‍👦 Gia đình (Family)',
                'description': 'Từ vựng về các thành viên trong gia đình',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Từ vựng về gia đình:
- **Father (Dad)** - Bố
- **Mother (Mom)** - Mẹ
- **Brother** - Anh/Em trai
- **Sister** - Chị/Em gái
- **Grandfather (Grandpa)** - Ông
- **Grandmother (Grandma)** - Bà

### 🎯 MẸO GHI NHỚ
- "**Father**" và "**Mother**" là cách nói trang trọng
- "**Dad**" và "**Mom**" là cách nói thân mật

### 📝 VÍ DỤ
- "This is my **mother**." (Đây là mẹ tôi.)
- "I have one **brother**." (Tôi có một anh trai.)

### ✅ BÀI TẬP THỰC HÀNH
1. "Mẹ" trong tiếng Anh là gì?
2. Dịch: "Tôi có một em gái."
                ''',
                'xp_reward': 30,
                'order': 1
            },
            {
                'level_id': 2,
                'name': '🐱 Động vật (Animals)',
                'description': 'Từ vựng về các con vật',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Từ vựng về động vật:
- **Cat** - Mèo
- **Dog** - Chó
- **Bird** - Chim
- **Fish** - Cá
- **Horse** - Ngựa
- **Elephant** - Voi

### 🎯 MẸO GHI NHỚ
- **Cat** và **Dog** là 2 con vật nuôi phổ biến nhất
- **Elephant** là con vật lớn nhất trên cạn

### 📝 VÍ DỤ
- I have a **cat**. (Tôi có một con mèo.)
- The **dog** is big. (Con chó to.)

### ✅ BÀI TẬP THỰC HÀNH
1. "Dog" có nghĩa là gì?
2. Dịch: "Con chim đang bay."
                ''',
                'xp_reward': 30,
                'order': 2
            },
            # LEVEL 3: PARROT
            {
                'level_id': 3,
                'name': '⏰ Thì hiện tại đơn',
                'description': 'Cấu trúc và cách dùng thì hiện tại đơn',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Thì hiện tại đơn diễn tả:
- **Hành động thường xuyên xảy ra** (I eat breakfast every day.)
- **Sự thật hiển nhiên** (The sun rises in the east.)
- **Sở thích, thói quen** (She likes music.)

### 🔧 CẤU TRÚC
**Khẳng định:** S + V(s/es) + O
- I/You/We/They + V (nguyên mẫu)
- He/She/It + V(s/es)

**Phủ định:** S + do/does + not + V
- I/You/We/They + do not (don't) + V
- He/She/It + does not (doesn't) + V

**Nghi vấn:** Do/Does + S + V?

### 📝 VÍ DỤ
- **I eat** breakfast at 7 AM.
- **She eats** lunch at noon.
- **They do not (don't) play** football.

### ✅ BÀI TẬP THỰC HÀNH
1. Chia động từ: She (go) ____ to school every day.
2. Chia động từ: They (play) ____ football.
                ''',
                'xp_reward': 35,
                'order': 1
            },
            {
                'level_id': 3,
                'name': '📝 Câu phủ định & nghi vấn',
                'description': 'Cách đặt câu phủ định và câu hỏi',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

**Câu phủ định:** Thêm "do not" (don't) hoặc "does not" (doesn't) trước động từ.
- I **don't** like coffee.
- She **doesn't** eat meat.

**Câu nghi vấn:** Đưa "do/does" lên đầu câu.
- **Do** you like music?
- **Does** she speak English?

### 🎯 MẸO GHI NHỚ
- **Don't** = do not (dùng với I/You/We/They)
- **Doesn't** = does not (dùng với He/She/It)

### ✅ BÀI TẬP THỰC HÀNH
1. Chuyển sang phủ định: "He likes cats."
2. Chuyển sang nghi vấn: "They play football."
                ''',
                'xp_reward': 35,
                'order': 2
            },
            # LEVEL 4: DOLPHIN
            {
                'level_id': 4,
                'name': '⏳ Thì quá khứ đơn',
                'description': 'Cách dùng thì quá khứ đơn',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Thì quá khứ đơn diễn tả hành động đã xảy ra và kết thúc trong quá khứ.

**Cấu trúc:** S + V(ed/ cột 2) + O
- I **walked** to school.
- She **went** to the market.

### 🎯 MẸO GHI NHỚ
- Động từ có quy tắc: thêm **-ed** (walk → walked)
- Động từ bất quy tắc: học thuộc (go → went)

### 📝 VÍ DỤ
- I **visited** my grandmother yesterday.
- They **played** football last Sunday.

### ✅ BÀI TẬP THỰC HÀNH
1. Chia động từ: I (visit) ____ my grandmother yesterday.
2. Chia động từ: They (play) ____ football last Sunday.
                ''',
                'xp_reward': 45,
                'order': 1
            },
            {
                'level_id': 4,
                'name': '🔮 Thì tương lai gần',
                'description': 'Cấu trúc "be going to"',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Thì tương lai gần diễn tả dự định hoặc kế hoạch trong tương lai.

**Cấu trúc:** S + am/is/are + going to + V
- I **am going to** study.
- She **is going to** travel.

### 🎯 MẸO GHI NHỚ
- Dùng "**going to**" cho dự định đã có kế hoạch
- Dùng "**will**" cho quyết định tại thời điểm nói

### ✅ BÀI TẬP THỰC HÀNH
1. We (visit) ____ the museum tomorrow.
2. He (buy) ____ a new car.
                ''',
                'xp_reward': 45,
                'order': 2
            },
            # LEVEL 5: LION
            {
                'level_id': 5,
                'name': '🎯 Câu điều kiện loại 1',
                'description': 'Cấu trúc If + hiện tại, will + V',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Câu điều kiện loại 1 diễn tả điều có thể xảy ra ở hiện tại hoặc tương lai.

**Cấu trúc:** If + S + V(hiện tại), S + will + V
- If it **rains**, I **will stay** home.
- If you **study** hard, you **will pass** the exam.

### 🎯 MẸO GHI NHỚ
- Vế "If" chia ở thì hiện tại đơn
- Vế chính chia ở thì tương lai đơn (will)

### ✅ BÀI TẬP THỰC HÀNH
1. If she (come) ____, I (tell) ____ her.
2. We (go) ____ out if it (not/rain) ____.
                ''',
                'xp_reward': 55,
                'order': 1
            },
            {
                'level_id': 5,
                'name': '📖 Câu bị động',
                'description': 'Cấu trúc câu bị động',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Câu bị động dùng khi chủ thể thực hiện hành động không quan trọng hoặc không rõ.

**Cấu trúc:** S + be + V3/ed + (by O)
- Active: She **writes** a letter.
- Passive: A letter **is written** by her.

### 🎯 MẸO GHI NHỚ
- **Be** chia theo thì của câu chủ động
- **V3/ed** là quá khứ phân từ của động từ

### ✅ BÀI TẬP THỰC HÀNH
1. He cleans the room. → The room ____ by him.
2. They built this house in 2000. → This house ____ in 2000.
                ''',
                'xp_reward': 55,
                'order': 2
            },
            # LEVEL 6: EAGLE
            {
                'level_id': 6,
                'name': '💼 Giao tiếp công sở',
                'description': 'Từ vựng và mẫu câu công sở',
                'content': '''
## 📚 LÝ THUYẾT CẦN NHỚ

Từ vựng công sở:
- **Meeting** - Cuộc họp
- **Presentation** - Thuyết trình
- **Report** - Báo cáo
- **Email** - Thư điện tử
- **Deadline** - Hạn chót

### 📝 MẪU CÂU
- "I'd like to schedule a meeting." (Tôi muốn lên lịch một cuộc họp.)
- "Please send me the report by Friday." (Làm ơn gửi tôi báo cáo trước thứ Sáu.)

### ✅ BÀI TẬP THỰC HÀNH
1. Dịch: "Tôi có một cuộc họp lúc 2 giờ."
2. Dịch: "Cô ấy đang viết một báo cáo."
                ''',
                'xp_reward': 70,
                'order': 1
            },
        ]
        
        for data in lessons_data:
            lesson = Lesson(**data)
            db.session.add(lesson)
        
        # ===== BÀI TẬP (EXERCISES) =====
        exercises_data = [
            # Level 1
            {'lesson_id': 1, 'question': 'Chữ cái nào là nguyên âm?', 
             'option_a': 'B', 'option_b': 'C', 'option_c': 'A', 'option_d': 'D', 
             'correct_answer': 2, 'explanation': 'Nguyên âm là A, E, I, O, U'},
            {'lesson_id': 1, 'question': 'Phát âm chữ "B" là gì?', 
             'option_a': '/biː/', 'option_b': '/siː/', 'option_c': '/diː/', 'option_d': '/iː/', 
             'correct_answer': 0, 'explanation': 'B phát âm là /biː/'},
            {'lesson_id': 2, 'question': 'Số 7 trong tiếng Anh là gì?', 
             'option_a': 'Seven', 'option_b': 'Six', 'option_c': 'Eight', 'option_d': 'Nine', 
             'correct_answer': 0, 'explanation': '7 = Seven'},
            {'lesson_id': 2, 'question': 'Số 12 trong tiếng Anh là gì?', 
             'option_a': 'Ten', 'option_b': 'Eleven', 'option_c': 'Twelve', 'option_d': 'Twenty', 
             'correct_answer': 2, 'explanation': '12 = Twelve'},
            # Level 2
            {'lesson_id': 3, 'question': '"Mẹ" trong tiếng Anh là gì?', 
             'option_a': 'Father', 'option_b': 'Mother', 'option_c': 'Brother', 'option_d': 'Sister', 
             'correct_answer': 1, 'explanation': 'Mother = Mẹ'},
            {'lesson_id': 3, 'question': '"Anh trai" trong tiếng Anh là gì?', 
             'option_a': 'Sister', 'option_b': 'Brother', 'option_c': 'Uncle', 'option_d': 'Aunt', 
             'correct_answer': 1, 'explanation': 'Brother = Anh trai'},
            {'lesson_id': 4, 'question': '"Dog" có nghĩa là gì?', 
             'option_a': 'Mèo', 'option_b': 'Chó', 'option_c': 'Chim', 'option_d': 'Cá', 
             'correct_answer': 1, 'explanation': 'Dog = Chó'},
            {'lesson_id': 4, 'question': '"Cat" có nghĩa là gì?', 
             'option_a': 'Chó', 'option_b': 'Mèo', 'option_c': 'Chim', 'option_d': 'Cá', 
             'correct_answer': 1, 'explanation': 'Cat = Mèo'},
            # Level 3
            {'lesson_id': 5, 'question': 'Chia động từ: She (go) ____ to school.', 
             'option_a': 'go', 'option_b': 'goes', 'option_c': 'going', 'option_d': 'went', 
             'correct_answer': 1, 'explanation': 'She + goes'},
            {'lesson_id': 5, 'question': 'Chia động từ: They (play) ____ football.', 
             'option_a': 'play', 'option_b': 'plays', 'option_c': 'playing', 'option_d': 'played', 
             'correct_answer': 0, 'explanation': 'They + play'},
            {'lesson_id': 6, 'question': 'Phủ định: "He likes cats." → He ____ cats.', 
             'option_a': "don't like", 'option_b': "doesn't like", 'option_c': "not like", 'option_d': "isn't like", 
             'correct_answer': 1, 'explanation': 'He + doesn\'t + V'},
            # Level 4
            {'lesson_id': 7, 'question': 'Quá khứ của "go" là gì?', 
             'option_a': 'goed', 'option_b': 'went', 'option_c': 'gone', 'option_d': 'going', 
             'correct_answer': 1, 'explanation': 'go → went'},
            {'lesson_id': 7, 'question': 'Quá khứ của "visit" là gì?', 
             'option_a': 'visited', 'option_b': 'visitted', 'option_c': 'visit', 'option_d': 'visiting', 
             'correct_answer': 0, 'explanation': 'visit → visited'},
            {'lesson_id': 8, 'question': '"I am going to study" nghĩa là gì?', 
             'option_a': 'Tôi đang học', 'option_b': 'Tôi sẽ học', 'option_c': 'Tôi đã học', 'option_d': 'Tôi học', 
             'correct_answer': 1, 'explanation': 'be going to = sẽ (dự định)'},
            # Level 5
            {'lesson_id': 9, 'question': 'Hoàn thành: If it rains, I ____ stay home.', 
             'option_a': 'will', 'option_b': 'would', 'option_c': 'am', 'option_d': 'was', 
             'correct_answer': 0, 'explanation': 'Câu điều kiện loại 1: will + V'},
            {'lesson_id': 10, 'question': 'Bị động: "She writes a letter" → A letter ____ by her.', 
             'option_a': 'is written', 'option_b': 'was written', 'option_c': 'is writing', 'option_d': 'writes', 
             'correct_answer': 0, 'explanation': 'Hiện tại đơn bị động: is/am/are + V3/ed'},
            # Level 6
            {'lesson_id': 11, 'question': 'Từ nào có nghĩa là "cuộc họp"?', 
             'option_a': 'Meeting', 'option_b': 'Report', 'option_c': 'Email', 'option_d': 'Deadline', 
             'correct_answer': 0, 'explanation': 'Meeting = Cuộc họp'},
            {'lesson_id': 11, 'question': '"Deadline" có nghĩa là gì?', 
             'option_a': 'Cuộc họp', 'option_b': 'Báo cáo', 'option_c': 'Hạn chót', 'option_d': 'Thư điện tử', 
             'correct_answer': 2, 'explanation': 'Deadline = Hạn chót'},
        ]
        
        for data in exercises_data:
            exercise = Exercise(**data)
            db.session.add(exercise)
        
        # ===== QUIZ (CHO MỖI LEVEL) =====
        quizzes_data = [
            {'level_id': 1, 'question': 'Từ nào là màu sắc?', 
             'option_a': 'Red', 'option_b': 'Table', 'option_c': 'Run', 'option_d': 'Happy', 
             'correct_answer': 0, 'xp_reward': 30},
            {'level_id': 2, 'question': '"Cat" có nghĩa là gì?', 
             'option_a': 'Chó', 'option_b': 'Mèo', 'option_c': 'Chim', 'option_d': 'Cá', 
             'correct_answer': 1, 'xp_reward': 40},
            {'level_id': 3, 'question': 'Câu nào đúng ở thì hiện tại đơn?', 
             'option_a': 'He eat apples.', 'option_b': 'He eats apples.', 
             'option_c': 'He eating apples.', 'option_d': 'He ate apples.', 
             'correct_answer': 1, 'xp_reward': 50},
            {'level_id': 4, 'question': '"Beautiful" có nghĩa là gì?', 
             'option_a': 'Xấu xí', 'option_b': 'Đẹp', 'option_c': 'Cao', 'option_d': 'Thấp', 
             'correct_answer': 1, 'xp_reward': 50},
            {'level_id': 5, 'question': 'Câu bị động của "She writes a letter" là gì?', 
             'option_a': 'A letter is written by her.', 'option_b': 'A letter was written by her.', 
             'option_c': 'A letter is being written by her.', 'option_d': 'A letter has been written by her.', 
             'correct_answer': 0, 'xp_reward': 60},
            {'level_id': 6, 'question': 'Từ nào là đại từ quan hệ?', 
             'option_a': 'Who', 'option_b': 'And', 'option_c': 'But', 'option_d': 'So', 
             'correct_answer': 0, 'xp_reward': 70},
        ]
        
        for data in quizzes_data:
            quiz = Quiz(**data)
            db.session.add(quiz)
        
        db.session.commit()
        print(f"✅ Đã tạo {Lesson.query.count()} bài học, {Exercise.query.count()} bài tập, {Quiz.query.count()} quiz")
    else:
        print(f"ℹ️ Đã có {Lesson.query.count()} bài học trong database")

# ============================================================
# ROUTE TẠO DỮ LIỆU MẪU (DÙNG KHI CẦN RESET)
# ============================================================
@app.route('/init-db')
def init_database():
    try:
        with app.app_context():
            # Tạo admin nếu chưa có
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@example.com',
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
            
            # Tạo bài học mẫu nếu chưa có
            if Lesson.query.count() == 0:
                # (phần tạo dữ liệu mẫu - copy từ above)
                pass
            
            return """
            <html>
            <head><title>Khởi tạo dữ liệu</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #27ae60;">✅ KHỞI TẠO THÀNH CÔNG!</h1>
                <ul style="list-style: none; padding: 0;">
                    <li>👤 Admin: <strong>admin</strong> / <strong>admin123</strong></li>
                    <li>📚 Bài học: <strong>{}</strong></li>
                    <li>📝 Bài tập: <strong>{}</strong></li>
                    <li>📊 Quiz: <strong>{}</strong></li>
                </ul>
                <p>
                    <a href="/" style="padding: 10px 20px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px;">Về trang chủ</a>
                    <a href="/admin" style="padding: 10px 20px; background: #2d3436; color: white; text-decoration: none; border-radius: 5px;">Vào Admin</a>
                </p>
            </body>
            </html>
            """.format(Lesson.query.count(), Exercise.query.count(), Quiz.query.count())
    except Exception as e:
        return f"<h2>❌ Lỗi: {e}</h2>"

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

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
