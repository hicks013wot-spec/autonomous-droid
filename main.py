import random
import time
import os
import uuid
import threading
import httpx
import flet as ft
import speech_recognition as sr

BAD_WORDS = ["дурак", "плохой", "ломать", "тупой"]
GIGACHAT_CREDENTIALS = "MDFhMTVlYjUtMTZmYy03MDdhLWI2MDQtMGY3MDQ2ZWM1OTg4OjcyOTAyMjJhLTJhMTYtNDdhOC04NTgxLTFiZDQwZmNiNzIzOA=="

recognizer = sr.Recognizer()
microphone = None
global_running = True
is_recording_ptt = False

def ask_gigachat(prompt: str) -> str:
    auth_url = "https" + "://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    chat_url = "https" + "://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    try:
        with httpx.Client(verify=False, timeout=15.0) as client:
            auth_res = client.post(
                auth_url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": str(uuid.uuid4()),
                    "Authorization": f"Basic {GIGACHAT_CREDENTIALS}"
                },
                data={"scope": "GIGACHAT_API_PERS"}
            )
            token = auth_res.json().get("access_token")
            if not token:
                return "Не удалось связаться со Сбером. Проверьте интернет."

            chat_res = client.post(
                chat_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "model": "GigaChat-2-Max",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты — добрый, вежливый и весёлый робот-помощник по имени Дроид в детском саду. Отвечай коротко (1-2 предложения), доступно для детей, позитивно и всегда уважительно."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            choices = chat_res.json().get("choices", [])
            if choices:
                return next(iter(choices))["message"]["content"]
            return "Не получил ответ от нейросети."
    except Exception as e:
        print(f"[Ошибка GigaChat]: {e}")
        return "Извините, у меня слегка закружились шестерёнки. Повторите, пожалуйста!"
def main(page: ft.Page):
    global microphone, global_running
    page.title = "Дроид"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.is_busy = False
    droid_color = "#00FF66"
    global_running = True

    def say_free(text: str):
        if not global_running:
            return
        print(f"[Голос дроида]: {text}")

    def on_close_app(e):
        global global_running
        global_running = False
        os._exit(0)
    page.on_close = on_close_app

    left_eye_box = ft.Container(width=90, height=110, bgcolor=droid_color, border_radius=20)
    right_eye_box = ft.Container(width=90, height=110, bgcolor=droid_color, border_radius=20)
    left_eye = ft.Container(content=left_eye_box, width=110, height=120, alignment=ft.alignment.center)
    right_eye = ft.Container(content=right_eye_box, width=110, height=120, alignment=ft.alignment.center)
    mouth = ft.Container(
        width=220, height=35, bgcolor=droid_color,
        border_radius=ft.border_radius.only(top_left=10, top_right=10, bottom_left=25, bottom_right=25),
        margin=ft.margin.only(top=40, bottom=40)
    )
    status_text = ft.Text(value="Режим: Автономный", color=droid_color, size=18, text_align=ft.TextAlign.CENTER, width=350)

    def set_emotion(emotion_type):
        if not global_running:
            return
        left_eye.alignment = ft.alignment.center
        right_eye.alignment = ft.alignment.center
        if emotion_type == "happy":
            left_eye_box.width, left_eye_box.height = 90, 110
            right_eye_box.width, right_eye_box.height = 90, 110
            mouth.border_radius = ft.border_radius.only(top_left=5, top_right=5, bottom_left=35, bottom_right=35)
            mouth.height = 45
        elif emotion_type == "sad":
            mouth.border_radius = 5
            mouth.height = 10
        elif emotion_type == "surprised":
            left_eye_box.width, left_eye_box.height = 105, 115
            right_eye_box.width, right_eye_box.height = 105, 115
            mouth.border_radius = 15
            mouth.height = 55
        try:
            if global_running:
                page.update()
        except Exception:
            pass

    def set_emotion_neutral():
        if not global_running:
            return
        left_eye.alignment = ft.alignment.center
        right_eye.alignment = ft.alignment.center
        left_eye_box.width, left_eye_box.height = 90, 110
        right_eye_box.width, right_eye_box.height = 90, 110
        mouth.border_radius = ft.border_radius.only(top_left=10, top_right=10, bottom_left=25, bottom_right=25)
        mouth.height = 35
        try:
            if global_running:
                page.update()
        except Exception:
            pass

    def set_emotion_angry():
        if not global_running:
            return
        left_eye_box.bgcolor = "#FF3333"
        right_eye_box.bgcolor = "#FF3333"
        mouth.bgcolor = "#FF3333"
        mouth.height = 10
        try:
            if global_running:
                page.update()
        except Exception:
            pass

    def goto_reset():
        if not global_running:
            return
        set_emotion_neutral()
        status_text.value = "Режим: Автономный" if mode_switch.value else "Режим: AI-мозг (Зажмите MIC)"
        page.is_busy = False
        try:
            if global_running:
                page.update()
        except Exception:
            pass
    def on_mode_change(e):
        status_text.value = "Режим: Автономный" if mode_switch.value else "Режим: AI-мозг (Зажмите MIC)"
        page.update()

    def on_mic_hold(e):
        global is_recording_ptt
        if not global_running or mode_switch.value:
            return
        is_recording_ptt = True
        status_text.value = "Дроид внимательно слушает..."
        set_emotion("surprised")
        page.update()

    def on_mic_release(e):
        global is_recording_ptt
        if not global_running or mode_switch.value:
            return
        is_recording_ptt = False

    mode_switch = ft.Switch(
        label="Автономный",
        value=True,
        label_style=ft.TextStyle(color=droid_color, size=12),
        active_color=droid_color,
        on_change=on_mode_change
    )
    mic_button = ft.GestureDetector(
        on_pan_start=on_mic_hold,
        on_pan_end=on_mic_release,
        content=ft.Container(
            content=ft.Icon(ft.icons.MIC, color="#000000", size=24),
            bgcolor=droid_color,
            shape=ft.BoxShape.CIRCLE,
            padding=10
        )
    )
    bottom_buttons_row = ft.Row(
        controls=[mode_switch, mic_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(
        ft.Column(
            [
                ft.Row([left_eye, right_eye], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
                ft.Container(height=30),
                mouth,
                ft.Container(height=40),
                status_text,
                ft.Container(height=60),
                bottom_buttons_row
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    try:
        microphone = sr.Microphone()
    except Exception:
        microphone = None

    def blink_timer_func():
        if not global_running:
            return
        if not page.is_busy and left_eye_box.height == 110:
            try:
                action = random.choice([0, 1, 2])
                if action == 0:
                    for h in range(110, 9, -25):
                        if not global_running:
                            return
                        left_eye_box.height = h
                        right_eye_box.height = h
                        page.update()
                        time.sleep(0.01)
                    time.sleep(0.12)
                    new_radius = random.choice([10, 20, 30])
                    left_eye_box.border_radius = new_radius
                    right_eye_box.border_radius = new_radius
                    for h in range(10, 111, 25):
                        if not global_running:
                            return
                        left_eye_box.height = h
                        right_eye_box.height = h
                        page.update()
                        time.sleep(0.01)
                elif action == 1:
                    side = random.choice([ft.alignment.center_left, ft.alignment.center_right, ft.alignment.center])
                    if side == ft.alignment.center:
                        left_eye.alignment = ft.alignment.center_right
                        right_eye.alignment = ft.alignment.center_left
                    else:
                        left_eye.alignment = side
                        right_eye.alignment = side
                    page.update()
                    time.sleep(random.uniform(0.8, 1.5))
                    left_eye.alignment = ft.alignment.center
                    right_eye.alignment = ft.alignment.center
                    page.update()
                elif action == 2:
                    for w in range(90, 106, 5):
                        if not global_running:
                            return
                        left_eye_box.width = w
                        right_eye_box.width = w
                        left_eye_box.height = 110 + (w - 90)
                        right_eye_box.height = 110 + (w - 90)
                        page.update()
                        time.sleep(0.02)
                    time.sleep(0.5)
                    left_eye_box.width = 90
                    right_eye_box.width = 90
                    left_eye_box.height = 110
                    right_eye_box.height = 110
                    page.update()
            except Exception:
                pass
        elif page.is_busy and left_eye_box.height == 110:
            try:
                left_eye_box.height = 10
                right_eye_box.height = 10
                page.update()
                time.sleep(0.15)
                left_eye_box.height = 110
                right_eye_box.height = 110
                page.update()
            except Exception:
                pass
        if global_running:
            threading.Timer(random.uniform(2.5, 4.5), blink_timer_func).start()

    threading.Timer(2.0, blink_timer_func).start()
    def mic_loop_worker():
        global recognizer, microphone, global_running, is_recording_ptt
        if not microphone:
            return
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            last_active_time = time.time()
            while global_running:
                try:
                    if not mode_switch.value:
                        if not is_recording_ptt:
                            time.sleep(0.1)
                            continue
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                        user_text = recognizer.recognize_google(audio, language="ru-RU").strip().lower()
                        status_text.value = "🤔 Думаю..."
                        page.update()
                        ai_answer = ask_gigachat(user_text)
                        set_emotion("happy")
                        status_text.value = ai_answer
                        page.update()
                        say_free(ai_answer)
                        time.sleep(4.5)
                        goto_reset()
                        continue

                    if time.time() - last_active_time > 30 and not page.is_busy:
                        try:
                            left_eye_box.height = 10
                            right_eye_box.height = 10
                            status_text.value = "Zzz..."
                            page.update()
                        except Exception:
                            pass

                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=4)
                    if not global_running or not mode_switch.value:
                        continue
                    if len(audio.frame_data) < 1000:
                        continue
                    user_text = recognizer.recognize_google(audio, language="ru-RU").strip().lower()

                    try:
                        left_eye_box.height = 110
                        right_eye_box.height = 110
                        last_active_time = time.time()
                        page.update()
                    except Exception:
                        pass

                    if any(bad_word in user_text for bad_word in BAD_WORDS):
                        page.is_busy = True
                        try:
                            set_emotion_angry()
                            status_text.value = "🚫️ Выражайтесь культурно."
                            page.update()
                        except Exception:
                            pass
                        say_free("Ребята и взрослые в нашем садике говорят только вежливые слова.")
                        time.sleep(4.5)
                        try:
                            left_eye_box.bgcolor = droid_color
                            right_eye_box.bgcolor = droid_color
                            mouth.bgcolor = droid_color
                            goto_reset()
                        except Exception:
                            pass
                        continue

                    page.is_busy = True
                    answer = None
                    if any(p in user_text for p in ["привет", "здравствуй"]):
                        answer = "Здравствуйте! Рады видеть вас."
                        set_emotion("happy")
                    elif "доброе утро" in user_text:
                        answer = "Доброе утро! Прекрасного вам дня."
                        set_emotion("happy")
                    elif "добрый день" in user_text:
                        answer = "Добрый день! Добро пожаловать."
                        set_emotion("happy")
                    elif "добрый вечер" in user_text:
                        answer = "Добрый вечер! Рады вам."
                        set_emotion("happy")
                    elif any(p in user_text for p in ["до свидания", "всего хорошего", "всего доброго"]):
                        answer = "До свидания! Хорошего вам вечера."
                        set_emotion("sad")
                    elif any(p in user_text for p in ["хорошего дня", "хорошего вам дня"]):
                        answer = "Спасибо! И вам прекрасного дня."
                        set_emotion("sad")
                    elif "хороших выходных" in user_text:
                        answer = "Спасибо! Желаю вам отличных выходных."
                        set_emotion("sad")
                    elif "пока" in user_text or "до встречи" in user_text:
                        answer = "Пока-пока! Приходите к нам ещё."
                        set_emotion("sad")
                    elif any(p in user_text for p in ["кто ты", "что ты", "кто это", "что это", "как зовут"]):
                        answer = "Я дроид, Паша создал меня для помощи по садику."
                        set_emotion("surprised")

                    if answer:
                        try:
                            status_text.value = answer
                            page.update()
                        except Exception:
                            pass
                        say_free(answer)
                        time.sleep(4.5)
                        goto_reset()
                    else:
                        page.is_busy = False
                except Exception:
                    continue

    threading.Thread(target=mic_loop_worker, daemon=True).start()

ft.app(target=main)
