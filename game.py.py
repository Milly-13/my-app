import streamlit as st
import sqlite3
from datetime import datetime

# Настройка страницы для мобильных устройств
st.set_page_config(
    page_title="Финансовый питомец Москвы", 
    page_icon="🦝", 
    layout="centered"
)

# --- БАЗА ДАННЫХ ДЛЯ СОХРАНЕНИЯ ПРОГРЕССА ---
def init_db():
    conn = sqlite3.connect("milli_game.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
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
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "pet_chosen": row[1],
            "coins": row[2],
            "fullness": row[3],
            "pet_level": row[4],
            "missions_completed": row[5].split(",") if row[5] else [],
            "last_time": row[6]
        }
    return None

def save_profile(profile):
    conn = sqlite3.connect("milli_game.db")
    cursor = conn.cursor()
    missions_str = ",".join(profile["missions_completed"])
    cursor.execute("""
        INSERT OR REPLACE INTO user_profile 
        (id, pet_chosen, coins, fullness, pet_level, missions_completed, last_time)
        VALUES (1, ?, ?, ?, ?, ?, ?)
    """, (
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
            "pet_chosen": None,
            "coins": 100,
            "fullness": 70,
            "pet_level": 1,
            "missions_completed": [],
            "last_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

data = st.session_state.game_data

# --- ЭФФЕКТ УМЕНЬШЕНИЯ ЭНЕРГИИ (Каждые 2 минуты -5%) ---
current_time = datetime.now()
last_time_obj = datetime.strptime(data["last_time"], "%Y-%m-%d %H:%M:%S")
time_passed = (current_time - last_time_obj).total_seconds()

if time_passed >= 120 and data["pet_chosen"]:
    intervals = int(time_passed // 120)
    data["fullness"] = max(10, data["fullness"] - (intervals * 5))
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
        "desc": "Умный и сообразительный. Знает всё про карманные расходы и как находить самые выгодные скидки.",
        "happy": "https://icons8.com",
        "sad": "https://icons8.com"
    },
    "Панда Копич 🐼": {
        "desc": "Спокойный и мудрый. Помогает откладывать деньги на большие цели и оберегает от лишних трат.",
        "happy": "https://icons8.com",
        "sad": "https://icons8.com"
    }
}

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# ШАГ 1: ЛИЧНЫЙ КАБИНЕТ - ВЫБОР ПИТОМЦА
if not data["pet_chosen"]:
    st.title("🏙️ Финансовый питомец Москвы")
    st.subheader("Создай своего цифрового помощника")
    st.write("Добро пожаловать! Выберите одного из трех уникальных зверьков для создания Личного кабинета:")
    
    chosen = st.radio("Доступные питомцы:", list(PET_GRAPHICS.keys()))
    st.info(PET_GRAPHICS[chosen]["desc"])
    
    st.image(PET_GRAPHICS[chosen]["happy"], width=150, caption="Так он выглядит, когда сыт!")
    
    if st.button("Создать личный кабинет и питомца ✨", use_container_width=True, type="primary"):
        data["pet_chosen"] = chosen
        data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(data)
        st.rerun()

# ШАГ 2: ИГРОВОЙ ЭКРАН
else:
    st.title("🪪 Личный кабинет участника ЛЦТ")
    
    with st.container(border=True):
        st.subheader("📋 Мой профиль")
        col_user, col_stats = st.columns(2)
        
        with col_user:
            st.write("👤 **Игрок:** Настя")
            st.write(f"🌟 **Уровень:** {data['pet_level']}")
            
        with col_stats:
            rank = "Новичок" if data['pet_level'] < 3 else "Финансовый эксперт"
            st.write(f"🏆 **Статус:** {rank}")
            st.write(f"✅ **Миссии:** {len(data['missions_completed'])} из 2")
            
    st.markdown("---")
    st.header(f"🏠 Домик: {data['pet_chosen']}")
    
    pet_name = data["pet_chosen"]
    if data["fullness"] > 40:
        st.image(PET_GRAPHICS[pet_name]["happy"], width=200)
        st.success(f"✨ {pet_name} счастлив и готов учиться!")
    else:
        st.image(PET_GRAPHICS[pet_name]["sad"], width=200)
        st.warning(f"⚠️ {pet_name} проголодался и загрустил! Покормите его.")
        
    col_c, col_f = st.columns(2)
    col_c.metric("Монеты в кошельке", f"{data['coins']} 🪙")
    col_f.metric("Сытость питомца", f"{data['fullness']}%")
    
    st.progress(data["fullness"] / 100)
    
    # Механика кормления
    if st.button("🍎 Покормить питомца — 20 монет", use_container_width=True, type="primary"):
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
                st.warning("Питомец уже сыт и доволен!")
        else:
            st.error("Не хватает монет на еду! Нужно пройти финансовую миссию.")
            
    st.markdown("---")
    st.header("🎯 Финансовые миссии Департамента")
    
    any_mission_available = False
    
    # Миссия 1
    if "m1" not in data["missions_completed"]:
        any_mission_available = True
        with st.container(border=True):
            st.subheader("🛡️ Безопасность в интернете")
            st.write("Вам пришло сообщение: «Вы выиграли приз!». В нём просят отправить пароль от вашей карты или личного кабинета. Что нужно сделать?")
            
            m1_options = [
                "Быстро отправить пароль, пока приз не отдали другому",
                "Остановиться и рассказать взрослому, которому вы доверяете",
                "Переслать сообщение всем друзьям в чат",
                "Придумать и отправить неверный пароль ради шутки"
            ]
            ans1 = st.radio("Выберите правильный ответ:", m1_options, key="ans1")
            
            if st.button("Проверить ответ 🕵️‍♂️", use_container_width=True):
                if ans1 == "Остановиться и рассказать взрослому, которому вы доверяете":
                    data["coins"] += 50
                    data["missions_completed"].append("m1")
                    data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_profile(data)
                    st.success("Идеально! Награда +50 🪙 сохранена в ваш профиль.")
                    st.rerun()
                else:
                    st.error("Неверно. Никогда не передавайте пароли посторонним.")
                    
    # Миссия 2
    if "m2" not in data["missions_completed"]:
        any_mission_available = True
        with st.container(border=True):
            st.subheader("📊 Приоритезация расходов")
            st.write("Ваш баланс монет на исходе, а питомец проголодался. Какое решение будет финансово грамотным?")
            
            m2_options = [
                "Купить красивые новые обои для домика питомца",
                "Купить полезную еду (яблоко) для восстановления сытости",
                "Потратить всё на лотерейный билет в игре"
            ]
            ans2 = st.radio("Выберите правильный ответ:", m2_options, key="ans2")
            
            if st.button("Проверить ответ 📊", use_container_width=True):
                if ans2 == "Купить полезную еду (яблоко) для восстановления сытости":
                    data["coins"] += 60
                    data["missions_completed"].append("m2")
                    data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_profile(data)
                    st.success("Отлично! Сначала закрываем обязательные нужды. Награда +60 🪙 сохранена.")
                    st.rerun()
                else:
                    st.error("Ошибка. Приоритет бюджета должен быть на жизненно важных расходах.")
                    
    if not any_mission_available:
        st.success("🏆 Все доступные миссии Личного кабинета успешно пройдены!")
        
    st.markdown(" ")
    if st.button("🔄 Сбросить профиль (Начать сначала)", type="secondary", use_container_width=True):
        data["pet_chosen"] = None
        data["coins"] = 100
        data["fullness"] = 70
        data["pet_level"] = 1
        data["missions_completed"] = []
        data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(data)
        st.rerun()
