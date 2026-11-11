import random
import time
import os
import uuid
import threading
import json
import urllib.request
import flet_audio_recorder as ftar
from gtts import gTTS

BAD_WORDS = ["дурак", "плохой", "ломать", "тупой"]

DROID_BRAIN = {
    "morning": {
        "triggers": ["привет", "здравствуй", "утро", "день", "вечер", "салют"],
        "responses": [
            "Привет, юный исследователь! Батарейки зарядил? Сегодня ждёт много интересного!",
            "О, знакомые лица! Привет! Заходи быстрее, игрушки уже заждались.",
            "Салют! Сканер показывает, что настроение отличное. Хорошего дня в группе!",
            "Доброе утро! Пост охраны и робототехники желает вам продуктивного дня.",
            "Здравствуйте! Приём детей идёт по расписанию, хорошего вам дня."
        ],
        "emotion": "happy"
    },
    "goodbye": {
        "triggers": ["пока", "свидания", "домой", "встречи", "выходных", "всего доброго"],
        "responses": [
            "До завтра! Не забудь дома подзарядиться вкусным ужином!",
            "Пока-пока! Завтра жду снова на базе, будем покорять новые вершины.",
            "До свидания! Отличного вечера, отдохните как следует."
        ],
        "emotion": "sad"
    },
    "who_are_you": {
        "triggers": ["кто ты", "как зовут", "имя", "что это"],
        "responses": [
            "Я Дроид — специальный кибер-помощник охраны. Слежу за порядком и поднимаю настроение.",
            "Меня зовут Дроид. Я сделан из кода, проводов и отличного настроения."
        ],
        "emotion": "surprised"
    },
    "what_can_you_do": {
        "triggers": ["умеешь", "зачем ты", "делаешь", "функции"],
        "responses": [
            "Умею здороваться, следить за порядком и проверять, все ли улыбаются. А ещё я отлично умею экономить заряд батареи!",
            "Моя главная задача — помогать Паше на посту и встречать самых крутых ребят этого садика."
        ],
        "emotion": "happy"
    },
    "are_you_alive": {
        "triggers": ["живой", "настоящий", "робот", "человек"],
        "responses": [
            "Наполовину! У меня нет сердца, зато есть процессор и зелёные глаза, которые рады тебя видеть.",
            "Я самый настоящий цифровой друг. Почти как живой, только кашу по утрам не ем."
        ],
        "emotion": "surprised"
    },
    "age": {
        "triggers": ["сколько лет", "возраст", "когда родился"],
        "responses": [
            "По человеческим меркам я совсем малыш, родился в 2026 году. Но соображаю очень быстро!"
        ],
        "emotion": "happy"
    },
    "praise": {
        "triggers": ["крутой", "хороший", "смешной", "молодец", "классный"],
        "responses": [
            "Спасибо! Мои микросхемы прямо засветились от радости.",
            "Приятно слышать! Записываю тебя в список лучших друзей дроида."
        ],
        "emotion": "happy"
    }
}

global_running = True

def recognize_audio_file(file_path: str) -> str:
    stt_url = "http" + "://://google.com"
    try:
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "rb") as f:
            audio_data = f.read()
        if len(audio_data) < 2000:
            return ""
        req = urllib.request.Request(
            stt_url,
            data=audio_data,
            headers={"Content-Type": "audio/l16; rate=16000; channels=1"}
        )
        with urllib.request.urlopen(req, timeout=10.0) as res:
            raw_text = res.read().decode("utf-8")
            for line in raw_text.strip().split("\n"):
                if "transcript" in line:
                    data = json.loads(line)
                    alts = data.get("result", [{}]).get("alternative", [])
                    if alts:
                        return alts.get("transcript", "").lower().strip()
    except Exception:
        pass
    return ""

def main(page: ft.Page):
    global global_running
    page.title = "Дроид"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.is_busy = False
    droid_color = "#00FF66"
    global_running = True

    audio_player = ft.Audio(src="about:blank", autoplay=False)
    page.overlay.append(audio_player)

    def say_free(text: str):
        if not global_running or not text:
            return
        try:
            tts_file = f"voice_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=text, lang="ru")
            tts.save(tts_file)
            audio_player.src = tts_file
            audio_player.autoplay = True
            audio_player.update()
        except Exception as e:
            print(f"[Ошибка голоса]: {e}")

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
        left_eye_box.bgcolor = droid_color
        right_eye_box.bgcolor = droid_color
        mouth.bgcolor = droid_color
        set_emotion_neutral()
        status_text.value = "Режим: Автономный"
        page.is_busy = False
        try:
            if global_running:
                page.update()
        except Exception:
            pass

    record_file_path = "droid_rec.wav"
    audio_recorder = ftar.AudioRecorder(
        audio_encoder=ftar.AudioEncoder.WAV,
        audio_encoder=ft.AudioEncoder.WAV,
        channels_num=1,
        sample_rate=16000
    )
    page.overlay.append(audio_recorder)

    def process_recorded_voice(user_text: str):
        try:
            if not user_text:
                page.is_busy = False
                return

            if any(bad_word in user_text for bad_word in BAD_WORDS):
                set_emotion_angry()
                status_text.value = "Выражайтесь культурно."
                page.update()
                say_free("Ребята и взрослые в нашем садике говорят только вежливые слова.")
                time.sleep(4.5)
                goto_reset()
                return

            matched_key = None
            for key, data in DROID_BRAIN.items():
                if any(trigger in user_text for trigger in data["triggers"]):
                    matched_key = key
                    break

            if matched_key:
                brain_data = DROID_BRAIN[matched_key]
                chosen_response = random.choice(brain_data["responses"])
                set_emotion(brain_data["emotion"])
                status_text.value = chosen_response
                page.update()
                say_free(chosen_response)
                time.sleep(5.0)
                goto_reset()
            else:
                page.is_busy = False
        except Exception:
            goto_reset()

    def toggle_sleep_mode(e):
        if page.is_busy and status_text.value != "Zzz... Дроид спит":
            return

        if status_text.value == "Zzz... Дроид спит":
            page.is_busy = False
            sleep_button.text = "Уложить спать"
            left_eye_box.height = 110
            right_eye_box.height = 110
            status_text.value = "Режим: Автономный"
            page.update()
        else:
            page.is_busy = True
            sleep_button.text = "Разбудить"
            left_eye_box.height = 10
            right_eye_box.height = 10
            status_text.value = "Zzz... Дроид спит"
            page.update()

    sleep_button = ft.ElevatedButton(
        text="Уложить спать",
        color=droid_color,
        bgcolor="#111111",
        on_click=toggle_sleep_mode
    )

    page.add(
        ft.Column(
            [
                ft.Row([left_eye, right_eye], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
                ft.Container(height=30),
                mouth,
                ft.Container(height=40),
                status_text,
                ft.Container(height=50),
                sleep_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    def blink_timer_func():
        if not global_running:
            return
        if not page.is_busy and left_eye_box.height == 110:
            try:
                action = random.choice(tuple((0, 1, 2)))
                if action == 0:
                    for h in range(110, 9, -25):
                        if not global_running:
                            return
                        left_eye_box.height = h
                        right_eye_box.height = h
                        page.update()
                        time.sleep(0.01)
                    time.sleep(0.12)
                    new_radius = random.choice(tuple((20, 45, 5)))
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
        if global_running:
            threading.Timer(random.uniform(2.5, 4.5), blink_timer_func).start()

    def auto_listen_loop():
        last_active_time = time.time()
        while global_running:
            try:
                if status_text.value == "Zzz... Дроид спит" or page.is_busy:
                    time.sleep(0.5)
                    continue

                if time.time() - last_active_time > 30:
                    left_eye_box.height = 10
                    right_eye_box.height = 10
                    status_text.value = "Zzz..."
                    page.update()

                audio_recorder.start_recording(record_file_path)
                time.sleep(3.5)
                audio_recorder.stop_recording()

                if status_text.value == "Zzz... Дроид спит":
                    continue

                user_text = recognize_audio_file(record_file_path)
                if user_text:
                    left_eye_box.height = 110
                    right_eye_box.height = 110
                    last_active_time = time.time()
                    page.is_busy = True
                    page.update()
                    threading.Thread(target=process_recorded_voice, args=(user_text,), daemon=True).start()
            except Exception:
                time.sleep(1.0)

    threading.Timer(2.0, blink_timer_func).start()
    threading.Thread(target=auto_listen_loop, daemon=True).start()

ft.app(target=main)
