import streamlit as st
import sqlite3
from datetime import datetime

# Настройка страницы для мобильных устройств
st.set_page_config(
    page_title="Финансовый питомец Москвы",
    page_icon="🐾",
    layout="centered"
)

# --- БАЗА ДАННЫХ ДЛЯ СОХРАНЕНИЯ ПРОГРЕССА ---
def init_db():
    conn = sqlite3.connect("milli_game.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            username TEXT,
            pet_chosen TEXT,
            coins INTEGER,
            fullness INTEGER,
            pet_level INTEGER,
            missions_completed TEXT,
            last_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_profile():
    conn = sqlite3.connect("milli_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "username": row[1],
            "pet_chosen": row[2],
            "coins": row[3],
            "fullness": row[4],
            "pet_level": row[5],
            "missions_completed": row[6].split(",") if row[6] else [],
            "last_time": row[7]
        }
    return None

def save_profile(profile):
    conn = sqlite3.connect("milli_game.db")
    cursor = conn.cursor()
    missions_str = ",".join(profile["missions_completed"])
    cursor.execute("""
        INSERT OR REPLACE INTO user_profile (id, username, pet_chosen, coins, fullness, pet_level, missions_completed, last_time)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile["username"],
        profile["pet_chosen"],
        profile["coins"],
        profile["fullness"],
        profile["pet_level"],
        missions_str,
        profile["last_time"]
    ))
    conn.commit()
    conn.close()

# Запуск базы данных
init_db()

# Загрузка данных в сессию
if "game_data" not in st.session_state:
    saved = load_profile()
    if saved:
        st.session_state.game_data = saved
    else:
        st.session_state.game_data = {
            "username": "Гость",
            "pet_chosen": None,
            "coins": 100,
            "fullness": 70,
            "pet_level": 1,
            "missions_completed": [],
            "last_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

data = st.session_state.game_data

# --- ЭФФЕКТ УМЕНЬШЕНИЯ ЭНЕРГИИ ---
current_time = datetime.now()
last_time_obj = datetime.strptime(data["last_time"], "%Y-%m-%d %H:%M:%S")
time_passed = (current_time - last_time_obj).total_seconds()

if time_passed >= 120 and data["pet_chosen"]:
    intervals = int(time_passed // 120)
    data["fullness"] = max(10, data["fullness"] - intervals * 5)
    data["last_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
    save_profile(data)

# --- БАЗА ССЫЛОК НА КАРТИНКИ ПИТОМЦЕВ ---
PET_GRAPHICS = {
    "Енот Милли 🦝": {
        "desc": "Любознательный и шустрый. Обожает собирать монеты и раскладывать их по копилкам.",
        "happy": "https://icons8.com",
        "sad": "https://icons8.com"
    },
    "Лис Финник 🦊": {
        "desc": "Умный и сообразительный. Знает всё про кэшбэк и финансовую безопасность.",
        "happy": "https://icons8.com",
        "sad": "https://icons8.com"
    },
    "Панда Копич 🐼": {
        "desc": "Спокойный и мудрый. Помогает грамотно планировать бюджет и копить на крупные покупки.",
        "happy": "https://icons8.com",
        "sad": "https://icons8.com"
    }
}

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# ШАГ 1: ЛИЧНЫЙ КАБИНЕТ – ВЫБОР ПИТОМЦА
if not data["pet_chosen"]:
    st.title("🏙️ Финансовый питомец Москвы")
    st.subheader("Создай своего цифрового помощника")
    st.write("Добро пожаловать! Введите своё имя и выберите питомца:")
    
    # Поле ввода имени игрока вместо жестко прописанного
    user_name_input = st.text_input("Ваше имя:", value="Настя")
    
    chosen = st.radio("Доступные питомцы:", list(PET_GRAPHICS.keys()))
    st.info(PET_GRAPHICS[chosen]["desc"])
    st.image(PET_GRAPHICS[chosen]["happy"], width=150)
    
    if st.button("Создать личный кабинет и питомца ✨"):
        data["username"] = user_name_input if user_name_input else "Игрок"
        data["pet_chosen"] = chosen
        data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(data)
        st.rerun()

# ШАГ 2: ИГРОВОЙ ЭКРАН
else:
    st.title(f"🐾 Личный кабинет участника ЛЦТ")
    
    with st.container(border=True):
        st.subheader("📋 Мой профиль")
        col_user, col_stats = st.columns(2)
        
        with col_user:
            st.write(f"👤 **Игрок:** {data['username']}")
            st.write(f"🌟 **Уровень:** {data['pet_level']}")
            
        with col_stats:
            rank = "Новичок" if data["pet_level"] < 3 else "Знаток"
            st.write(f"🏆 **Статус:** {rank}")
            st.write(f"✅ **Миссии:** {len(data['missions_completed'])} из 2")
            
    st.markdown("---")
    
    st.subheader(f"🏡 Домик: {data['pet_chosen']}")
    
    pet_name = data["pet_chosen"]
    if data["fullness"] > 40:
        st.image(PET_GRAPHICS[pet_name]["happy"], width=150)
        st.success(f"✨ {pet_name} счастлив и готов учиться!")
    else:
        st.image(PET_GRAPHICS[pet_name]["sad"], width=150)
        st.warning(f"⚠️ {pet_name} проголодался! Покормите его.")
        
    col_c, col_f = st.columns(2)
    col_c.metric("Монеты в кошельке", f"{data['coins']} 🪙")
    col_f.metric("Сытость питомца", f"{data['fullness']}/100")
    
    st.progress(data["fullness"] / 100)
    
    # Механика кормления
    if st.button("🍎 Покормить питомца — 20 монет"):
        if data["coins"] >= 20:
            if data["fullness"] < 100:
                data["coins"] -= 20
                data["fullness"] = min(100, data["fullness"] + 20)
                if data["fullness"] == 100:
                    data["pet_level"] += 1
                data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_profile(data)
                st.rerun()
            else:
                st.warning("Питомец уже сыт!")
        else:
            st.error("Не хватает монет на еду!")
            
    st.markdown("---")
    st.header("🎯 Финансовые миссии Департамента")
    
    any_mission_available = False
    
    # Миссия 1
    if "m1" not in data["missions_completed"]:
        any_mission_available = True
        with st.container(border=True):
            st.subheader("🛡️ Безопасность в сети")
            st.write("Вам пришло сообщение: 'Вы выиграли 5000 рублей! Срочно пришлите код из СМС, чтобы забрать'. Что сделаете?")
            
            m1_options = [
                "Быстро отправить пароль, пока деньги не отдали",
                "Остановиться и рассказать родителям / в поддержку, это мошенники",
                "Переслать сообщение всем друзьям",
                "Придумать и отправить неверный код ради шутки"
            ]
            ans1 = st.radio("Выберите правильный ответ:", m1_options, key="m1_ans")
            
            if st.button("Проверить ответ 🐾", key="m1_btn"):
                if ans1 == "Остановиться и рассказать родителям / в поддержку, это мошенники":
                    data["coins"] += 5000
                    data["missions_completed"].append("m1")
                    data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_profile(data)
                    st.success("Идеально! Настоящий эксперт по безопасности. Получено 5000 монет! 🪙")
                    st.rerun()
                else:
                    st.error("Неверно. Никому и никогда нельзя передавать коды из СМС!")
                    
    # Миссия 2
    if "m2" not in data["missions_completed"]:
        any_mission_available = True
        with st.container(border=True):
            st.subheader("📊 Приоритезация расходов")
            st.write("Ваш баланс монет на исходе, а питомец голоден. Куда потратите последние сбережения?")
            
            m2_options = [
                "Купить красивые новые обои для домика",
                "Купить полезную еду (яблоко или кашу)",
                "Потратить всё на лотерейный билет"
            ]
            ans2 = st.radio("Выберите правильный ответ:", m2_options, key="m2_ans")
            
            if st.button("Проверить ответ 🐾", key="m2_btn"):
                if ans2 == "Купить полезную еду (яблоко или кашу)":
                    data["coins"] += 60
                    data["missions_completed"].append("m2")
                    data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_profile(data)
                    st.success("Отлично! Сначала закрываем важные потребности, а потом развлечения. Получено 60 монет! 🪙")
                    st.rerun()
                else:
                    st.error("Ошибка. Приоритет должен быть на здоровье и еде питомца!")
                    
    if not any_mission_available:
        st.success("🏆 Все доступные миссии успешно выполнены!")
        
    st.markdown(" ")
    if st.button("🔄 Сбросить профиль (Начать заново)"):
        data["username"] = "Гость"
        data["pet_chosen"] = None
        data["coins"] = 100
        data["fullness"] = 70
        data["pet_level"] = 1
        data["missions_completed"] = []
        data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(data)
        st.rerun()
