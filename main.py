import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from uuid import uuid4

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, g, abort, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- CONFIGURATION ---

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
# --- LANGUAGES / I18N ---

LANGUAGES = {
    "en": {"label": "English"},
    "uz": {"label": "O'zbekcha"},
    "ru": {"label": "Русский"},
}

translations = {
    "en": {
        "app_name": "PortfoHub",
        "nav_home": "Home",
        "nav_my_profile": "My profile",
        "nav_create": "Create portfolio",
        "nav_settings": "Settings",
        "nav_login": "Login",
        "nav_register": "Register",
        "nav_logout": "Logout",

        "hero_kicker": "Portfolio social network",
        "hero_title": "Show your best work",
        "hero_subtitle": "Create a profile, upload your projects, and share a clean, professional portfolio – all in one simple, responsive web app.",
        "hero_cta_main_logged_out": "Get started – it’s free",
        "hero_cta_secondary_logged_out": "I already have an account",
        "hero_cta_main_logged_in": "+ New portfolio item",
        "hero_cta_secondary_logged_in": "Go to my profile",

        "section_public_feed_title": "Public feed",
        "section_public_feed_subtitle": "Browse portfolios from all users",
        "search_placeholder": "Search by name, username, title, or tags...",
        "filter_all_categories": "All categories",
        "btn_filter": "Filter",
        "btn_view_profile": "View profile",
        "text_no_portfolios": "No public portfolios found yet.",
        "text_create_account_cta": "Create your account",

        "auth_register_title": "Create your account",
        "auth_login_title": "Log in",
        "auth_register_button": "Register",
        "auth_login_button": "Login",
        "label_full_name": "Full name",
        "label_username": "Username",
        "label_email": "Email address",
        "label_password": "Password",
        "label_confirm_password": "Confirm password",
        "label_username_or_email": "Username or email",
        "label_remember_me": "Remember me",
        "auth_already_account": "Already have an account?",
        "auth_login_here": "Log in",
        "auth_new_here": "New here?",
        "auth_create_here": "Create an account",

        "settings_title": "Profile settings",
        "label_profession": "Profession / specialization",
        "label_location": "Location",
        "label_bio": "Short bio",
        "label_website": "Website",
        "label_linkedin": "LinkedIn",
        "label_github": "GitHub",
        "label_avatar": "Profile photo (avatar)",
        "btn_save_changes": "Save changes",
        "settings_privacy_note": "Privacy note: only your public portfolio items are visible on the homepage and to other users. Private items are visible only to you.",

        "profile_about_section_label": "About me",
        "profile_about_section_title": "Personal profile",
        "profile_portfolio_section_label": "Portfolio",
        "profile_portfolio_section_title": "My work",
        "profile_stats_items": "Portfolio items",
        "profile_stats_focus": "Professional focus",
        "profile_no_items": "You have no portfolio items yet.",
        "profile_create_first": "Create your first one.",
        "btn_edit_profile": "Edit profile",
        "btn_public_view": "View public profile",
        "btn_new_portfolio": "+ New portfolio",
        "btn_view_link": "View link",
        "btn_edit": "Edit",
        "btn_delete": "Delete",

        "public_about_label": "About",
        "public_about_title": "Professional profile",
        "public_portfolio_label": "Portfolio",
        "public_portfolio_title": "Selected work",
        "public_no_items": "No public portfolio items yet.",
    },

    "uz": {
        "app_name": "PortfoHub",
        "nav_home": "Bosh sahifa",
        "nav_my_profile": "Profilim",
        "nav_create": "Portfolio qo‘shish",
        "nav_settings": "Sozlamalar",
        "nav_login": "Kirish",
        "nav_register": "Ro‘yxatdan o‘tish",
        "nav_logout": "Chiqish",

        "hero_kicker": "Portfolio tarmog‘i",
        "hero_title": "Eng yaxshi ishlaringizni ko‘rsating",
        "hero_subtitle": "Profil yarating, loyihalaringizni yuklang va zamonaviy, qulay portfolio bilan bo‘lishing.",
        "hero_cta_main_logged_out": "Boshlash – bepul",
        "hero_cta_secondary_logged_out": "Menda allaqachon akkaunt bor",
        "hero_cta_main_logged_in": "Yangi portfolio qo‘shish",
        "hero_cta_secondary_logged_in": "Profilimga o‘tish",

        "section_public_feed_title": "Ochiq feed",
        "section_public_feed_subtitle": "Barcha foydalanuvchilar portfoliolarini ko‘ring",
        "search_placeholder": "Ism, username, sarlavha yoki teglar bo‘yicha qidirish...",
        "filter_all_categories": "Barcha kategoriyalar",
        "btn_filter": "Filtrlash",
        "btn_view_profile": "Profilni ko‘rish",
        "text_no_portfolios": "Hozircha ochiq portfoliolar topilmadi.",
        "text_create_account_cta": "Akkaunt yarating",

        "auth_register_title": "Akkaunt yaratish",
        "auth_login_title": "Tizimga kirish",
        "auth_register_button": "Ro‘yxatdan o‘tish",
        "auth_login_button": "Kirish",
        "label_full_name": "To‘liq ism",
        "label_username": "Foydalanuvchi nomi",
        "label_email": "Email manzil",
        "label_password": "Parol",
        "label_confirm_password": "Parolni tasdiqlash",
        "label_username_or_email": "Foydalanuvchi nomi yoki email",
        "label_remember_me": "Eslab qolish",
        "auth_already_account": "Akkauntingiz bormi?",
        "auth_login_here": "Bu yerda kiring",
        "auth_new_here": "Yangi foydalanuvchimisiz?",
        "auth_create_here": "Akkaunt yarating",

        "settings_title": "Profil sozlamalari",
        "label_profession": "Kasb / mutaxassislik",
        "label_location": "Joylashuv",
        "label_bio": "Qisqa bio",
        "label_website": "Veb-sayt",
        "label_linkedin": "LinkedIn",
        "label_github": "GitHub",
        "label_avatar": "Profil rasmi (avatar)",
        "btn_save_changes": "O‘zgarishlarni saqlash",
        "settings_privacy_note": "Maxfiylik: faqat public bo‘lgan portfoliolar bosh sahifada ko‘rinadi. Private portfoliolarni faqat siz ko‘rasiz.",

        "profile_about_section_label": "Men haqimda",
        "profile_about_section_title": "Shaxsiy profil",
        "profile_portfolio_section_label": "Portfolio",
        "profile_portfolio_section_title": "Mening ishlarim",
        "profile_stats_items": "Portfolio elementlari",
        "profile_stats_focus": "Kasbiy yo‘nalish",
        "profile_no_items": "Hozircha portfoliolar kiritilmagan.",
        "profile_create_first": "Birinchi portfolioingizni yarating.",
        "btn_edit_profile": "Profilni tahrirlash",
        "btn_public_view": "Ommaviy ko‘rinish",
        "btn_new_portfolio": "Yangi portfolio",
        "btn_view_link": "Havolani ochish",
        "btn_edit": "Tahrirlash",
        "btn_delete": "O‘chirish",

        "public_about_label": "Haqida",
        "public_about_title": "Kasbiy profil",
        "public_portfolio_label": "Portfolio",
        "public_portfolio_title": "Tanlangan ishlar",
        "public_no_items": "Ommaviy portfoliolar yo‘q.",
    },

    "ru": {
        "app_name": "PortfoHub",
        "nav_home": "Главная",
        "nav_my_profile": "Мой профиль",
        "nav_create": "Добавить портфолио",
        "nav_settings": "Настройки",
        "nav_login": "Войти",
        "nav_register": "Регистрация",
        "nav_logout": "Выйти",

        "hero_kicker": "Социальная сеть портфолио",
        "hero_title": "Покажите свои лучшие работы",
        "hero_subtitle": "Создайте профиль, загрузите проекты и делитесь аккуратным профессиональным портфолио в одном простом приложении.",
        "hero_cta_main_logged_out": "Начать — это бесплатно",
        "hero_cta_secondary_logged_out": "У меня уже есть аккаунт",
        "hero_cta_main_logged_in": "Новое портфолио",
        "hero_cta_secondary_logged_in": "Перейти в профиль",

        "section_public_feed_title": "Лента",
        "section_public_feed_subtitle": "Просматривайте портфолио всех пользователей",
        "search_placeholder": "Поиск по имени, нику, заголовку или тегам...",
        "filter_all_categories": "Все категории",
        "btn_filter": "Фильтр",
        "btn_view_profile": "Открыть профиль",
        "text_no_portfolios": "Публичные портфолио пока не найдены.",
        "text_create_account_cta": "Создать аккаунт",

        "auth_register_title": "Создание аккаунта",
        "auth_login_title": "Вход",
        "auth_register_button": "Зарегистрироваться",
        "auth_login_button": "Войти",
        "label_full_name": "Полное имя",
        "label_username": "Имя пользователя",
        "label_email": "E-mail",
        "label_password": "Пароль",
        "label_confirm_password": "Подтверждение пароля",
        "label_username_or_email": "Логин или e-mail",
        "label_remember_me": "Запомнить меня",
        "auth_already_account": "Уже есть аккаунт?",
        "auth_login_here": "Войти",
        "auth_new_here": "Впервые здесь?",
        "auth_create_here": "Создать аккаунт",

        "settings_title": "Настройки профиля",
        "label_profession": "Профессия / специализация",
        "label_location": "Местоположение",
        "label_bio": "Краткая биография",
        "label_website": "Веб-сайт",
        "label_linkedin": "LinkedIn",
        "label_github": "GitHub",
        "label_avatar": "Фото профиля (аватар)",
        "btn_save_changes": "Сохранить изменения",
        "settings_privacy_note": "Конфиденциальность: только публичные портфолио видны на главной странице. Приватные портфолио видите только вы.",

        "profile_about_section_label": "Обо мне",
        "profile_about_section_title": "Личный профиль",
        "profile_portfolio_section_label": "Портфолио",
        "profile_portfolio_section_title": "Мои работы",
        "profile_stats_items": "Элементов портфолио",
        "profile_stats_focus": "Профессиональный фокус",
        "profile_no_items": "У вас пока нет портфолио.",
        "profile_create_first": "Создайте свою первую работу.",
        "btn_edit_profile": "Редактировать профиль",
        "btn_public_view": "Публичный вид",
        "btn_new_portfolio": "Новое портфолио",
        "btn_view_link": "Открыть ссылку",
        "btn_edit": "Редактировать",
        "btn_delete": "Удалить",

        "public_about_label": "О пользователе",
        "public_about_title": "Профессиональный профиль",
        "public_portfolio_label": "Портфолио",
        "public_portfolio_title": "Выбранные работы",
        "public_no_items": "Публичных работ пока нет.",
    },
}


def get_locale():
    code = session.get("lang", "en")
    if code not in LANGUAGES:
        code = "en"
    return code


def t(key: str) -> str:
    lang = get_locale()
    return translations.get(lang, {}).get(key, translations["en"].get(key, key))

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB
app.permanent_session_lifetime = timedelta(days=30)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# --- DATABASE HELPERS ---

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    # Users table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            bio TEXT,
            location TEXT,
            website TEXT,
            linkedin TEXT,
            github TEXT,
            profession TEXT,
            avatar_filename TEXT,
            created_at TEXT NOT NULL
        );
        """
    )

    # Portfolio items table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            tags TEXT,
            external_link TEXT,
            image_filename TEXT,
            visibility TEXT NOT NULL DEFAULT 'public',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    db.commit()


# ❗ MUHIM: Flask 3 da before_first_request yo‘q, shuning uchun
# app kontekstida init_db() ni modul yuklanganda bir marta chaqiramiz.
with app.app_context():
    init_db()


# --- CSRF PROTECTION ---

def generate_csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = uuid4().hex
        session["csrf_token"] = token
    return token


@app.before_request
def csrf_protect():
    # Only check for POST
    if request.method == "POST":
        token = session.get("csrf_token", None)
        form_token = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
        if not token or not form_token or token != form_token:
            abort(400, description="Invalid CSRF token")


@app.route("/set-lang/<lang_code>")
def set_language(lang_code):
    if lang_code not in LANGUAGES:
        lang_code = "en"
    session["lang"] = lang_code
    next_url = request.referrer or url_for("index")
    return redirect(next_url)


@app.context_processor
def inject_globals():
    return {
        "current_user": get_current_user(),
        "csrf_token": generate_csrf_token,
        "t": t,
        "current_lang": get_locale(),
        "languages": LANGUAGES,
    }


# --- UTILS ---

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage):
    """Save uploaded image to uploads folder and return filename or None."""
    if not file_storage:
        return None
    if file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    # Make filename unique
    name, ext = os.path.splitext(filename)
    unique_name = f"{name}_{uuid4().hex}{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(filepath)
    return unique_name


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(**kwargs)

    return wrapped_view


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return user


# --- ROUTES ---

@app.route("/")
def index():
    db = get_db()
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 9
    offset = (page - 1) * per_page

    sql = """
        SELECT p.*, u.username, u.full_name, u.avatar_filename
        FROM portfolio_items p
        JOIN users u ON p.user_id = u.id
        WHERE p.visibility = 'public'
    """
    params = []

    if q:
        sql += """
        AND (
            LOWER(u.username) LIKE ?
            OR LOWER(u.full_name) LIKE ?
            OR LOWER(p.title) LIKE ?
            OR LOWER(p.tags) LIKE ?
        )
        """
        like = f"%{q.lower()}%"
        params.extend([like, like, like, like])

    if category:
        sql += " AND p.category = ?"
        params.append(category)

    sql += " ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page + 1, offset])  # Fetch one extra to see if there's next page

    rows = db.execute(sql, params).fetchall()
    has_next = len(rows) > per_page
    portfolios = rows[:per_page]

    # Distinct categories for filter
    categories = db.execute(
        "SELECT DISTINCT category FROM portfolio_items WHERE visibility='public' AND category IS NOT NULL AND category != '' ORDER BY category"
    ).fetchall()

    return render_template(
        "index.html",
        portfolios=portfolios,
        q=q,
        category=category,
        categories=categories,
        page=page,
        has_next=has_next,
    )


# --- AUTH ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []

        if not full_name:
            errors.append("Full name is required.")
        if not username:
            errors.append("Username is required.")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email:
            errors.append("Email is required.")
        if not password or not confirm_password:
            errors.append("Password and confirmation are required.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        db = get_db()
        if username:
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,),
            ).fetchone()
            if existing:
                errors.append("This username is already taken.")
        if email:
            existing = db.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            if existing:
                errors.append("This email is already registered.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        created_at = datetime.utcnow().isoformat()

        db.execute(
            """
            INSERT INTO users (full_name, username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, username, email, password_hash, created_at),
        )
        db.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email),
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = remember
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("index"))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# --- PROFILE & SETTINGS ---

@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    db = get_db()
    portfolios = db.execute(
        """
        SELECT * FROM portfolio_items
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user["id"],),
    ).fetchall()
    return render_template("profile.html", user=user, portfolios=portfolios)


@app.route("/u/<username>")
def public_profile(username):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username.lower(),),
    ).fetchone()
    if not user:
        abort(404)

    portfolios = db.execute(
        """
        SELECT * FROM portfolio_items
        WHERE user_id = ? AND visibility = 'public'
        ORDER BY created_at DESC
        """,
        (user["id"],),
    ).fetchall()

    return render_template("public_profile.html", user=user, portfolios=portfolios)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = get_current_user()
    db = get_db()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        bio = request.form.get("bio", "").strip()
        location = request.form.get("location", "").strip()
        website = request.form.get("website", "").strip()
        linkedin = request.form.get("linkedin", "").strip()
        github = request.form.get("github", "").strip()
        profession = request.form.get("profession", "").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("settings.html", user=user)

        avatar_file = request.files.get("avatar")
        avatar_filename = user["avatar_filename"]
        if avatar_file and avatar_file.filename:
            if not allowed_file(avatar_file.filename):
                flash("Avatar must be an image file (jpg, jpeg, png, gif).", "danger")
                return render_template("settings.html", user=user)
            avatar_filename = save_uploaded_file(avatar_file)

        db.execute(
            """
            UPDATE users
            SET full_name = ?, bio = ?, location = ?, website = ?, linkedin = ?,
                github = ?, profession = ?, avatar_filename = ?
            WHERE id = ?
            """,
            (
                full_name,
                bio,
                location,
                website,
                linkedin,
                github,
                profession,
                avatar_filename,
                user["id"],
            ),
        )
        db.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", user=user)


# --- PORTFOLIO CRUD ---

@app.route("/portfolio/new", methods=["GET", "POST"])
@login_required
def create_portfolio():
    user = get_current_user()
    db = get_db()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        tags = request.form.get("tags", "").strip()
        external_link = request.form.get("external_link", "").strip()
        visibility = request.form.get("visibility", "public")

        if visibility not in ("public", "private"):
            visibility = "public"

        if not title:
            flash("Title is required.", "danger")
            return render_template("create_portfolio.html", portfolio=None)

        image_file = request.files.get("image")
        image_filename = None
        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash("Portfolio image must be an image file (jpg, jpeg, png, gif).", "danger")
                return render_template("create_portfolio.html", portfolio=None)
            image_filename = save_uploaded_file(image_file)

        now = datetime.utcnow().isoformat()

        db.execute(
            """
            INSERT INTO portfolio_items
            (user_id, title, description, category, tags, external_link,
             image_filename, visibility, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                title,
                description,
                category,
                tags,
                external_link,
                image_filename,
                visibility,
                now,
                now,
            ),
        )
        db.commit()
        flash("Portfolio item created.", "success")
        return redirect(url_for("profile"))

    return render_template("create_portfolio.html", portfolio=None)


@app.route("/portfolio/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_portfolio(item_id):
    user = get_current_user()
    db = get_db()

    portfolio = db.execute(
        "SELECT * FROM portfolio_items WHERE id = ? AND user_id = ?",
        (item_id, user["id"]),
    ).fetchone()

    if not portfolio:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        tags = request.form.get("tags", "").strip()
        external_link = request.form.get("external_link", "").strip()
        visibility = request.form.get("visibility", "public")

        if visibility not in ("public", "private"):
            visibility = "public"

        if not title:
            flash("Title is required.", "danger")
            return render_template("create_portfolio.html", portfolio=portfolio)

        image_file = request.files.get("image")
        image_filename = portfolio["image_filename"]
        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash("Portfolio image must be an image file (jpg, jpeg, png, gif).", "danger")
                return render_template("create_portfolio.html", portfolio=portfolio)
            image_filename = save_uploaded_file(image_file)

        now = datetime.utcnow().isoformat()

        db.execute(
            """
            UPDATE portfolio_items
            SET title = ?, description = ?, category = ?, tags = ?, external_link = ?,
                image_filename = ?, visibility = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                title,
                description,
                category,
                tags,
                external_link,
                image_filename,
                visibility,
                now,
                item_id,
                user["id"],
            ),
        )
        db.commit()
        flash("Portfolio item updated.", "success")
        return redirect(url_for("profile"))

    return render_template("create_portfolio.html", portfolio=portfolio)


@app.route("/portfolio/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_portfolio(item_id):
    user = get_current_user()
    db = get_db()

    portfolio = db.execute(
        "SELECT * FROM portfolio_items WHERE id = ? AND user_id = ?",
        (item_id, user["id"]),
    ).fetchone()

    if not portfolio:
        abort(404)

    db.execute(
        "DELETE FROM portfolio_items WHERE id = ? AND user_id = ?",
        (item_id, user["id"]),
    )
    db.commit()
    flash("Portfolio item deleted.", "info")
    return redirect(url_for("profile"))


# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


@app.errorhandler(400)
def bad_request(e):
    # Mostly CSRF errors here
    flash("Bad request. Please try again.", "danger")
    return redirect(url_for("index"))


# --- STATIC UPLOADS ---

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
