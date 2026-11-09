"""Точка входа в приложение «Астероиды»."""

import tkinter as tk

from src.app import App


def main() -> None:
    """Создает корневое окно Tkinter и запускает главный цикл игры."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
