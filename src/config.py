"""Глобальные параметры и конфигурационные константы игры «Астероиды»."""

import os

# Путь к директории с графическими ресурсами (спрайтами и тайлами)
ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets"
)

# Размеры игрового поля (холста) в пикселях
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Параметры боковой панели управления
PANEL_WIDTH = 190
WINDOW_TITLE = "Asteroids"

# Частота обновления экрана (мс между кадрами, ~60 кадров/сек)
FRAME_DELAY_MS = 16

# Начальные параметры игровой сессии
INITIAL_LIVES = 3
INITIAL_SCORE = 0

# Параметры динамического фона (движение обломков влево, пикс/кадр)
DEBRIS_SPEED = 1.2

# Геометрия заставки (координаты центра, ширина и высота рамки)
SPLASH_CENTER_X = CANVAS_WIDTH / 2
SPLASH_CENTER_Y = CANVAS_HEIGHT / 2
SPLASH_WIDTH = 400
SPLASH_HEIGHT = 300

# Физические параметры корабля игрока
SHIP_RADIUS = 35
SHIP_ANGULAR_VEL = 0.08  # Угловая скорость вращения (рад/кадр)
SHIP_THRUST_ACCEL = 0.22  # Линейное ускорение при включенном двигателе
SHIP_FRICTION = 0.018  # Коэффициент сопротивления среды (трение)
SHIP_TILE_SIZE = (90, 90)

# Параметры ракеты: время жизни выбрано так, чтобы путь (42 * 11 = 462 пикс)
# был строго меньше малого измерения игрового поля (CANVAS_HEIGHT = 600 пикс)
MISSILE_RADIUS = 4
MISSILE_SPEED = 11.0
MISSILE_LIFESPAN = 42
MISSILE_TILE_SIZE = (16, 16)

# Параметры генерации и движения астероидов
ROCK_RADIUS = 40
ROCK_MAX_COUNT = 12  # Максимальное число астероидов на экране
ROCK_SPAWN_INTERVAL_MS = 1000  # Интервал появления нового астероида (мс)
ROCK_MIN_SPEED = 1.0  # Минимальная линейная скорость астероида
ROCK_MAX_SPEED = 3.2  # Максимальная линейная скорость астероида
ROCK_MAX_ANGULAR_VEL = 0.06  # Максимальная угловая скорость вращения
ROCK_SAFE_DIST = 110.0  # Безопасная дистанция спавна от корабля игрока
ROCK_TILE_SIZE = (90, 90)

# Параметры тайловой анимации взрыва (16 тайлов в горизонтальной ленте)
EXPLOSION_TILES = 16
EXPLOSION_TILE_SIZE = (100, 100)
EXPLOSION_RADIUS = 45
