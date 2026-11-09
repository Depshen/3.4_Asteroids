"""Модуль главного окна приложения и обработчиков пользовательских событий."""

import tkinter as tk
from typing import Set

from src import config
from src.models.game_model import GameModel
from src.renderers.renderer import Renderer
from src.widgets.controls import ControlPanel


class App:
    """Главный класс приложения, управляющий окном, вводом и циклом игры."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализирует интерфейс, привязывает события и запускает таймеры."""
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.model = GameModel()
        self.controls = ControlPanel(self.root)

        self.canvas = tk.Canvas(
            self.root,
            width=config.CANVAS_WIDTH,
            height=config.CANVAS_HEIGHT,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.RIGHT, padx=6, pady=6)

        self.renderer = Renderer(self.canvas, self.model)
        self._pressed_keys: Set[str] = set()

        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)
        self.canvas.bind("<Button-1>", self._on_mouse_click)

        self._spawn_timer()
        self._game_loop()

    def _on_mouse_click(self, event: tk.Event) -> None:
        """Обрабатывает клик мыши: запускает игру при клике по заставке."""
        self.controls.set_mouse_status(event.x, event.y)
        self.root.focus_set()

        if not self.model.started and self.model.is_splash_clicked(
            event.x, event.y
        ):
            self.model.start_game()

    def _on_key_down(self, event: tk.Event) -> None:
        """Обрабатывает нажатия клавиш вращения, ускорения и стрельбы."""
        key = event.keysym
        self.controls.set_key_status(f"Down {key}")

        if key in self._pressed_keys:
            return
        self._pressed_keys.add(key)

        if key == "Left":
            self.model.ship.decrement_angle_vel()
        elif key == "Right":
            self.model.ship.increment_angle_vel()
        elif key == "Up":
            self.model.ship.set_thrust(True)
        elif key == "space":
            self.model.shoot_missile()

    def _on_key_up(self, event: tk.Event) -> None:
        """Обрабатывает отпускание клавиш управления кораблем."""
        key = event.keysym
        self.controls.set_key_status(f"Up {key}")

        if key not in self._pressed_keys:
            return
        self._pressed_keys.discard(key)

        if key == "Left":
            self.model.ship.increment_angle_vel()
        elif key == "Right":
            self.model.ship.decrement_angle_vel()
        elif key == "Up":
            self.model.ship.set_thrust(False)

    def _spawn_timer(self) -> None:
        """Периодически вызывает генерацию нового астероида по таймеру."""
        self.model.spawn_rock()
        self.root.after(config.ROCK_SPAWN_INTERVAL_MS, self._spawn_timer)

    def _game_loop(self) -> None:
        """Обновляет физическую модель и перерисовывает экран каждый кадр."""
        self.model.step()
        self.renderer.render()
        self.root.after(config.FRAME_DELAY_MS, self._game_loop)
