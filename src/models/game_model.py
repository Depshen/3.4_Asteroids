"""Модуль математической модели, физики и взаимодействия объектов."""

import math
import random
from typing import List, Set, Tuple

from src import config


def angle_to_vector(ang: float) -> Tuple[float, float]:
    """Преобразует угол в радианах в единичный вектор направления."""
    return math.cos(ang), math.sin(ang)


def dist(p: Tuple[float, float], q: Tuple[float, float]) -> float:
    """Вычисляет евклидово расстояние между двумя точками на плоскости."""
    return math.hypot(p[0] - q[0], p[1] - q[1])


class ImageInfo:
    """Класс метаданных для хранения параметров тайлов и спрайтов."""

    def __init__(
        self,
        center: Tuple[float, float],
        size: Tuple[int, int],
        radius: float = 0.0,
        lifespan: float = float("inf"),
        animated: bool = False,
    ) -> None:
        """Инициализирует геометрические параметры и время жизни спрайта."""
        self.center = center
        self.size = size
        self.radius = radius
        self.lifespan = lifespan
        self.animated = animated


class Ship:
    """Класс космического корабля, управляемого игроком."""

    def __init__(
        self, pos: Tuple[float, float], vel: Tuple[float, float], angle: float
    ) -> None:
        """Инициализирует координаты, скорость, угол и состояние тяги."""
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.vx = float(vel[0])
        self.vy = float(vel[1])
        self.angle = float(angle)
        self.angle_vel = 0.0
        self.thrust = False
        self.radius = config.SHIP_RADIUS

    def set_thrust(self, on: bool) -> None:
        """Включает или выключает маршевый двигатель корабля."""
        self.thrust = on

    def increment_angle_vel(self) -> None:
        """Увеличивает угловую скорость (вращение по часовой стрелке)."""
        self.angle_vel += config.SHIP_ANGULAR_VEL

    def decrement_angle_vel(self) -> None:
        """Уменьшает угловую скорость (вращение против часовой стрелки)."""
        self.angle_vel -= config.SHIP_ANGULAR_VEL

    def respawn(self) -> None:
        """Возрождает неподвижный корабль в центре игрового поля."""
        self.x = config.CANVAS_WIDTH / 2
        self.y = config.CANVAS_HEIGHT / 2
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.angle_vel = 0.0
        self.thrust = False

    def shoot(self) -> "Sprite":
        """Создает ракету, вылетающую из носа корабля по его ориентации."""
        forward_x, forward_y = angle_to_vector(self.angle)

        # Координаты носа корабля: центр смещается на радиус вперед
        missile_x = self.x + self.radius * forward_x
        missile_y = self.y + self.radius * forward_y

        # Скорость ракеты складывается со скоростью корабля
        missile_vx = self.vx + forward_x * config.MISSILE_SPEED
        missile_vy = self.vy + forward_y * config.MISSILE_SPEED

        info = ImageInfo(
            center=(8, 8),
            size=config.MISSILE_TILE_SIZE,
            radius=config.MISSILE_RADIUS,
            lifespan=config.MISSILE_LIFESPAN,
        )
        return Sprite(
            pos=(missile_x, missile_y),
            vel=(missile_vx, missile_vy),
            angle=self.angle,
            angle_vel=0.0,
            kind="missile",
            image_info=info,
        )

    def update(self) -> None:
        """Обновляет угол, скорость и положение корабля (тороидальное поле)."""
        self.angle += self.angle_vel

        # Перемещение с учетом тороидальной геометрии границ экрана
        self.x = (self.x + self.vx) % config.CANVAS_WIDTH
        self.y = (self.y + self.vy) % config.CANVAS_HEIGHT

        # Ускорение вдоль вектора ориентации при включенном двигателе
        if self.thrust:
            forward_x, forward_y = angle_to_vector(self.angle)
            self.vx += forward_x * config.SHIP_THRUST_ACCEL
            self.vy += forward_y * config.SHIP_THRUST_ACCEL

        # Сопротивление среды: постепенное замедление до полной остановки
        self.vx *= 1.0 - config.SHIP_FRICTION
        self.vy *= 1.0 - config.SHIP_FRICTION
        if math.hypot(self.vx, self.vy) < 0.01:
            self.vx = 0.0
            self.vy = 0.0


class Sprite:
    """Универсальный класс для астероидов, ракет и анимации взрывов."""

    def __init__(
        self,
        pos: Tuple[float, float],
        vel: Tuple[float, float],
        angle: float,
        angle_vel: float,
        kind: str,
        image_info: ImageInfo,
    ) -> None:
        """Инициализирует физические параметры и метаданные спрайта."""
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.vx = float(vel[0])
        self.vy = float(vel[1])
        self.angle = float(angle)
        self.angle_vel = float(angle_vel)
        self.kind = kind
        self.radius = image_info.radius
        self.lifespan = image_info.lifespan
        self.animated = image_info.animated
        self.age = 0

    def update(self) -> bool:
        """Обновляет состояние объекта; возвращает True, если время истекло."""
        self.angle += self.angle_vel
        self.x = (self.x + self.vx) % config.CANVAS_WIDTH
        self.y = (self.y + self.vy) % config.CANVAS_HEIGHT
        self.age += 1
        return self.age >= self.lifespan

    def collide(self, other: object) -> bool:
        """Проверяет столкновение двух круглых объектов по их радиусам."""
        other_x = getattr(other, "x", 0.0)
        other_y = getattr(other, "y", 0.0)
        other_r = getattr(other, "radius", 0.0)
        distance = dist((self.x, self.y), (other_x, other_y))
        return distance <= (self.radius + other_r)


class GameModel:
    """Главный класс модели, управляющий логикой игры и коллекциями."""

    def __init__(self) -> None:
        """Инициализирует начальное состояние игры с активной заставкой."""
        self.lives = config.INITIAL_LIVES
        self.score = config.INITIAL_SCORE
        self.started = False
        self.debris_time = 0.0

        self.ship = Ship(
            pos=(config.CANVAS_WIDTH / 2, config.CANVAS_HEIGHT / 2),
            vel=(0.0, 0.0),
            angle=0.0,
        )
        self.rock_group: Set[Sprite] = set()
        self.missile_group: Set[Sprite] = set()
        self.explosion_group: Set[Sprite] = set()

    def is_splash_clicked(self, x: float, y: float) -> bool:
        """Проверяет, попал ли щелчок мыши строго внутрь рамки заставки."""
        half_w = config.SPLASH_WIDTH / 2
        half_h = config.SPLASH_HEIGHT / 2
        in_x = (
            config.SPLASH_CENTER_X - half_w
            <= x
            <= config.SPLASH_CENTER_X + half_w
        )
        in_y = (
            config.SPLASH_CENTER_Y - half_h
            <= y
            <= config.SPLASH_CENTER_Y + half_h
        )
        return in_x and in_y

    def start_game(self) -> None:
        """Запускает новую игру после щелчка по прямоугольнику заставки."""
        self.lives = config.INITIAL_LIVES
        self.score = config.INITIAL_SCORE
        self.started = True
        self.rock_group.clear()
        self.missile_group.clear()
        self.explosion_group.clear()
        self.ship.respawn()

    def spawn_rock(self) -> None:
        """Генерирует астероид в случайной точке со случайной скоростью."""
        if not self.started or len(self.rock_group) >= config.ROCK_MAX_COUNT:
            return

        # Выбираем координаты на безопасном расстоянии от корабля
        for _ in range(10):
            rx = random.uniform(0, config.CANVAS_WIDTH)
            ry = random.uniform(0, config.CANVAS_HEIGHT)
            if (
                dist((rx, ry), (self.ship.x, self.ship.y))
                > config.ROCK_SAFE_DIST
            ):
                break
        else:
            return

        speed = random.uniform(config.ROCK_MIN_SPEED, config.ROCK_MAX_SPEED)
        direction = random.uniform(0, 2 * math.pi)
        vx = math.cos(direction) * speed
        vy = math.sin(direction) * speed
        ang_vel = random.uniform(
            -config.ROCK_MAX_ANGULAR_VEL, config.ROCK_MAX_ANGULAR_VEL
        )

        info = ImageInfo(
            center=(45, 45),
            size=config.ROCK_TILE_SIZE,
            radius=config.ROCK_RADIUS,
        )
        rock = Sprite(
            pos=(rx, ry),
            vel=(vx, vy),
            angle=0.0,
            angle_vel=ang_vel,
            kind="rock",
            image_info=info,
        )
        self.rock_group.add(rock)

    def shoot_missile(self) -> None:
        """Производит выстрел ракетой, если игра активна."""
        if self.started:
            self.missile_group.add(self.ship.shoot())

    def step(self) -> None:
        """Выполняет один такт физического цикла и обрабатывает коллизии."""
        self.debris_time += config.DEBRIS_SPEED

        if not self.started:
            return

        self.ship.update()
        self._update_sprite_group(self.rock_group)
        self._update_sprite_group(self.missile_group)
        self._update_sprite_group(self.explosion_group)

        # Проверка столкновений ракет с астероидами
        hits = self._group_group_collide(self.rock_group, self.missile_group)
        self.score += hits

        # Проверка столкновения корабля с астероидами
        if self._group_collide(self.rock_group, self.ship):
            self.lives -= 1
            self.ship.respawn()
            if self.lives <= 0:
                self.started = False
                self.rock_group.clear()
                self.missile_group.clear()
                self.explosion_group.clear()

    def _update_sprite_group(self, group: Set[Sprite]) -> None:
        """Обновляет все спрайты в группе и удаляет объекты с истекшим веком."""
        expired: List[Sprite] = [s for s in group if s.update()]
        for sprite in expired:
            group.discard(sprite)

    def _group_collide(
        self, group: Set[Sprite], other_obj: object, explode: bool = True
    ) -> bool:
        """Проверяет столкновение группы со спрайтом и удаляет объект."""
        collided: List[Sprite] = [
            s for s in group if s.collide(other_obj)
        ]
        for sprite in collided:
            group.discard(sprite)
            # Взрыв появляется, только если флаг explode равен True
            if explode:
                self._spawn_explosion((sprite.x, sprite.y))
        return len(collided) > 0

    def _group_group_collide(
        self, rocks: Set[Sprite], missiles: Set[Sprite]
    ) -> int:
        """Обрабатывает попадания ракет по астероидам; возвращает хиты."""
        hit_count = 0
        for rock in list(rocks):
            # Передаем explode=False, чтобы ракета исчезала без взрыва
            if self._group_collide(missiles, rock, explode=False):
                rocks.discard(rock)
                self._spawn_explosion((rock.x, rock.y))
                hit_count += 1
        return hit_count

    def _spawn_explosion(self, pos: Tuple[float, float]) -> None:
        """Создает тайловую анимацию взрыва в точке уничтожения астероида."""
        info = ImageInfo(
            center=(50, 50),
            size=config.EXPLOSION_TILE_SIZE,
            radius=config.EXPLOSION_RADIUS,
            lifespan=config.EXPLOSION_TILES,
            animated=True,
        )
        explosion = Sprite(
            pos=pos,
            vel=(0.0, 0.0),
            angle=0.0,
            angle_vel=0.0,
            kind="explosion",
            image_info=info,
        )
        self.explosion_group.add(explosion)
