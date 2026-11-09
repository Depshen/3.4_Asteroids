"""Модуль боковой панели индикации событий клавиатуры и мыши."""

import tkinter as tk

from src import config


class ControlPanel:
    """Класс левой панели управления с индикаторами Key и Mouse."""

    def __init__(self, parent: tk.Widget) -> None:
        """Создает панель и размещает блоки Key и Mouse в нижней части."""
        self.frame = tk.Frame(
            parent,
            width=config.PANEL_WIDTH,
            bg="#f0f0f0",
            padx=8,
            pady=10,
        )
        self.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.frame.pack_propagate(False)

        # Нижний блок для отображения координат щелчка мыши
        self.mouse_box = tk.LabelFrame(
            self.frame,
            text="Mouse",
            bg="#f0f0f0",
            fg="black",
            font=("Arial", 10),
        )
        self.mouse_box.pack(side=tk.BOTTOM, fill=tk.X, pady=(6, 20))

        self.mouse_label = tk.Label(
            self.mouse_box,
            text=" ",
            bg="#f0f0f0",
            fg="black",
            font=("Arial", 10),
            anchor=tk.W,
            padx=4,
            pady=4,
        )
        self.mouse_label.pack(fill=tk.X)

        # Блок над ним для отображения последней нажатой/отпущенной клавиши
        self.key_box = tk.LabelFrame(
            self.frame,
            text="Key",
            bg="#f0f0f0",
            fg="black",
            font=("Arial", 10),
        )
        self.key_box.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 6))

        self.key_label = tk.Label(
            self.key_box,
            text=" ",
            bg="#f0f0f0",
            fg="black",
            font=("Arial", 10),
            anchor=tk.W,
            padx=4,
            pady=4,
        )
        self.key_label.pack(fill=tk.X)

    def set_key_status(self, text: str) -> None:
        """Обновляет строку статуса клавиатуры (например, Down Left)."""
        self.key_label.config(text=text)

    def set_mouse_status(self, x: int, y: int) -> None:
        """Обновляет строку координат клика мыши (например, Click 491, 285)."""
        self.mouse_label.config(text=f"Click {x}, {y}")
