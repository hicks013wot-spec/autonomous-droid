name: Build Droid APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Java SDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Set up Flutter SDK
        uses: subosito/flutter-action@v2
        with:
          channel: 'stable'

      - name: Install System dependencies (Zip)
        run: |
          sudo apt-get update
          sudo apt-get install -y zip

      - name: Install Python dependencies globally
        run: |
          python -m pip install --upgrade pip
          pip install flet gTTS flet-audio flet-audio-recorder --break-system-packages

      - name: Build APK via Flet
        run: |
          flet build apk .

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: Droid-App-APK
          path: build/apk/*.apk
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
                action = random.choice()
                if action == 0:
                    for h in range(110, 9, -25):
                        if not global_running:
                            return
                        left_eye_box.height = h
                        right_eye_box.height = h
                        page.update()
                        time.sleep(0.01)
                    time.sleep(0.12)
                    new_radius = random.choice()
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

