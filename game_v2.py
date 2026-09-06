import streamlit as st
from datetime import datetime

# Настройка страницы для мобильных устройств
st.set_page_config(
    page_title="Финансовый питомец Москвы",
    page_icon="🐾",
    layout="centered"
)

# --- ИЗОЛИРОВАННАЯ ИГРОВАЯ СЕССИЯ ДЛЯ КАЖДОГО ПОЛЬЗОВАТЕЛЯ ---
if "game_data" not in st.session_state:
    st.session_state.game_data = {
        "username": None,
        "pet_chosen": None,
        "coins": 100,
        "fullness": 70,
        "pet_level": 1,
        "missions_completed": [],
        "last_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

data = st.session_state.game_data

# --- БАЗА ДАННЫХ ПИТОМЦЕВ (Используем крупные нативные эмодзи) ---
PET_GRAPHICS = {
    "Енот Милли 🦝": {
        "desc": "Любознательный и шустрый. Обожает собирать монеты и раскладывать их по копилкам.",
        "icon": "🦝",
        "status_happy": "✨ Енот Милли счастлив и готов учиться!",
        "status_sad": "⚠️ Енот Милли проголодался! Покормите его."
    },
    "Лис Финник 🦊": {
        "desc": "Умный и сообразительный. Знает всё про кэшбэк и финансовую безопасность.",
        "icon": "🦊",
        "status_happy": "✨ Лис Финник счастлив и готов учиться!",
        "status_sad": "⚠️ Лис Финник проголодался! Покормите его."
    },
    "Панда Копич 🐼": {
        "desc": "Спокойный и мудрый. Помогает грамотно планировать бюджет и копить на крупные покупки.",
        "icon": "🐼",
        "status_happy": "✨ Панда Копич счастлив и готов учиться!",
        "status_sad": "⚠️ Панда Копич проголодался! Покормите его."
    }
}

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---

# ШАГ 1: ЭКРАН ВХОДА (Если имя или питомец еще не выбраны)
if not data["username"] or not data["pet_chosen"]:
    st.title("🏙️ Финансовый питомец Москвы")
    st.subheader("Создай своего цифрового помощника")
    st.write("Добро пожаловать! Введите ваше имя и выберите питомца для начала игры:")
    
    # Пустая строка ввода для каждого нового гостя
    user_name_input = st.text_input("Как вас зовут?", value="", placeholder="Введите ваше имя...")
    
    chosen = st.radio("Доступные питомцы:", list(PET_GRAPHICS.keys()))
    st.info(PET_GRAPHICS[chosen]["desc"])
    
    # Крупный красивый значок вместо ломающейся картинки
    st.markdown(f"<h1 style='text-align: center; font-size: 100px; margin: 0;'>{PET_GRAPHICS[chosen]['icon']}</h1>", unsafe_allow_html=True)
    
    if st.button("Создать личный кабинет и питомца ✨"):
        if user_name_input.strip() == "":
            st.error("Пожалуйста, введите своё имя перед стартом!")
        else:
            data["username"] = user_name_input.strip()
            data["pet_chosen"] = chosen
            data["last_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()

# ШАГ 2: ИГРОВОЙ ЭКРАН (У каждого свой персональный)
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
    
    st.subheader(f"🏡 Домик питомца")
    pet_name = data["pet_chosen"]
    
    # Отображение питомца в зависимости от сытости
    st.markdown(f"<h1 style='text-align: center; font-size: 120px; margin: 0;'>{PET_GRAPHICS[pet_name]['icon']}</h1>", unsafe_allow_html=True)
    
    if data["fullness"] > 40:
        st.success(PET_GRAPHICS[pet_name]["status_happy"])
    else:
        st.warning(PET_GRAPHICS[pet_name]["status_sad"])
        
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
                    st.success("Отлично! Сначала закрываем важные потребности, а потом развлечения. Получено 60 монет! 🪙")
                    st.rerun()
                else:
                    st.error("Ошибка. Приоритет должен быть на здоровье и еде питомца!")
                    
    if not any_mission_available:
        st.success("🏆 Все доступные миссии успешно выполнены!")
        
    st.markdown(" ")
    if st.button("🔄 Выйти из кабинета (Начать заново)"):
        st.session_state.clear()
        st.rerun()
