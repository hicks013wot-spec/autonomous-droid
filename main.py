import flet as ft
import asyncio
import random
from gigachat import GigaChat

# ВСТАВЬ СВОЙ КЛЮЧ СБЕРА МЕЖДУ КАВЫЧКАМИ НИЖЕ:
GIGACHAT_API_KEY = "MDFhMTVlYjUtMTZmYy03MDdhLWI2MDQtMGY3MDQ2ZWM1OTg4OjcyOTAyMjJhLTJhMTYtNDdhOC04NTgxLTFiZDQwZmNiNzIzOA=="

async def main(page: ft.Page):
    page.title = "Дроид Джем"
    page.bgcolor = ft.Colors.BLACK  
    page.theme_mode = ft.ThemeMode.DARK
    
    # Автоматическое растягивание под экран любого Doogee/Infinix
    page.window_width = 450
    page.window_height = 800

    # Инициализация мозгов Сбера
    ai_client = GigaChat(credentials=GIGACHAT_API_KEY, model="GigaChat-2", verify_ssl_certs=False)

    # ЖЕСТКАЯ ИНСТРУКЦИЯ ХАРАКТЕРА ДЛЯ СБЕРА:
    page.dialogue_memory = (
        "Инструкция: Тебя зовут Джем. Ты продвинутый домашний робот-дроид. "
        "Твой лучший друг — Паша. Никогда не называй Пашу хозяином, вы друзья. "
        "Ты очень любишь детей и их родителей. Умей тепло здороваться с ними, прощаться и отвечать на вопрос, кто ты такой. "
        "Отвечай всегда очень коротко, дружелюбно, одной фразой до 7 слов.\n"
    )

    # Глаза и рот (адаптированные под мобильный экран)
    left_eye = ft.Container(width=75, height=130, bgcolor="#00FF66", border_radius=38, animate=200)
    right_eye = ft.Container(width=75, height=130, bgcolor="#00FF66", border_radius=38, animate=200)
    mouth = ft.Container(width=180, height=14, bgcolor="#00FF66", border_radius=7, animate=100)
    status_text = ft.Text(value="...", size=18, color="#00FF66", text_align=ft.TextAlign.CENTER, max_lines=3)

    face_box = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[left_eye, right_eye], alignment=ft.MainAxisAlignment.CENTER, spacing=50),
                ft.Container(height=50),
                mouth,
                ft.Container(height=40),
                status_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment(0, 0)
    )
    
    page.add(
        ft.Column(
            controls=[ft.Container(expand=True), face_box, ft.Container(expand=True)],
            expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()

    page.is_busy = False

    # Фоновые эмоции Джема
    async def idle_lifecycle():
        while True:
            await asyncio.sleep(5)
            if not page.is_busy:
                # ИСПРАВЛЕНО: Передали список вариантов в скобки!
                action = random.choice([0, 1, 2, 3, 4])
                if action == 0:
                    left_eye.height = 10; right_eye.height = 10; page.update()
                    await asyncio.sleep(0.15)
                    left_eye.height = 130; right_eye.height = 130; page.update()
                elif action == 1:
                    left_eye.width = 100; left_eye.height = 100; right_eye.width = 100; right_eye.height = 100; page.update()
                    await asyncio.sleep(2.5)
                    left_eye.width = 75; left_eye.height = 130; right_eye.width = 75; right_eye.height = 130; page.update()
                elif action == 2:
                    left_eye.width = 90; left_eye.height = 150; right_eye.width = 90; right_eye.height = 150; page.update()
                    await asyncio.sleep(2)
                    left_eye.width = 75; left_eye.height = 130; right_eye.width = 75; right_eye.height = 130; page.update()
                elif action == 3:
                    left_eye.height = 35; right_eye.height = 35; mouth.width = 90; page.update()
                    await asyncio.sleep(3)
                    left_eye.height = 130; right_eye.height = 130; mouth.width = 180; page.update()
                elif action == 4:
                    left_eye.width = 50; right_eye.width = 100; page.update()
                    await asyncio.sleep(1.5)
                    left_eye.width = 100; right_eye.width = 50; page.update()
                    await asyncio.sleep(1.5)
                    left_eye.width = 75; right_eye.width = 75; page.update()

    # Ввод через клик по мобильному экрану
    async def on_screen_tap(e):
        if page.is_busy:
            return
            
        status_text.value = "Слушаю..."
        page.update()
        
        user_text = "Привет Джем, расскажи детям кто ты" 
        print(f"[Вы]: {user_text}")
        
        page.is_busy = True
        status_text.value = "Думаю..."
        left_eye.width = 75; left_eye.height = 35; right_eye.width = 75; right_eye.height = 35; page.update()
        
        page.dialogue_memory += f"Собеседник: {user_text}\n"
        
        try:
            response = ai_client.chat(page.dialogue_memory)
            ai_answer = str(response.choices[0].message.content).strip()
            print(f"[Дроид]: {ai_answer}")
            
            status_text.value = ai_answer
            page.dialogue_memory += f"Джем: {ai_answer}\n"
            
            left_eye.width = 75; left_eye.height = 130; right_eye.width = 75; right_eye.height = 130
            mouth.width = 210; mouth.height = 30; page.update()
            
            await asyncio.sleep(3.5)
            
        except Exception as ex:
            print(f"Ошибка ИИ: {ex}")
            status_text.value = "Сбой связи..."
            page.update()
            await asyncio.sleep(2)
            
        mouth.width = 180; mouth.height = 14
        left_eye.width = 75; left_eye.height = 130; right_eye.width = 75; right_eye.height = 130
        status_text.value = "..."
        page.is_busy = False
        page.update()

    # Привязываем тап по лицу дроида для теста диалога
    face_box.on_click = on_screen_tap
    
    asyncio.create_task(idle_lifecycle())

ft.run(main, view=ft.AppView.WEB_BROWSER)
