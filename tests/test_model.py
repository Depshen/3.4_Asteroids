"""Модульные тесты для проверки физики и логики игры «Астероиды»."""

import unittest

from src import config
from src.models.game_model import GameModel


class TestAsteroidsModel(unittest.TestCase):
    """Тестовый набор для проверки модели корабля, ракет, камней и коллизий."""

    def setUp(self) -> None:
        """Создает свежий экземпляр модели перед каждым тестом."""
        self.model = GameModel()

    def test_initial_state_and_splash_click(self) -> None:
        """Проверяет старт игры только по клику внутри рамки заставки."""
        self.assertFalse(self.model.started)
        self.assertEqual(self.model.lives, 3)
        self.assertEqual(self.model.score, 0)

        # Клик вне заставки (в углу поля) должен игнорироваться
        self.assertFalse(self.model.is_splash_clicked(10, 10))
        # Клик по центру заставки должен быть валидным
        self.assertTrue(
            self.model.is_splash_clicked(
                config.SPLASH_CENTER_X, config.SPLASH_CENTER_Y
            )
        )

    def test_toroidal_geometry(self) -> None:
        """Проверяет переход корабля через левую границу на правую."""
        self.model.start_game()
        self.model.ship.x = 2.0
        self.model.ship.vx = -10.0
        self.model.ship.update()
        self.assertGreater(self.model.ship.x, config.CANVAS_WIDTH - 15)

    def test_missile_lifespan_constraint(self) -> None:
        """Проверяет, что дальность полета ракеты меньше высоты поля."""
        max_distance = config.MISSILE_SPEED * config.MISSILE_LIFESPAN
        min_dimension = min(config.CANVAS_WIDTH, config.CANVAS_HEIGHT)
        self.assertLess(max_distance, min_dimension)

    def test_missile_rock_collision_and_explosion(self) -> None:
        """Проверяет начисление очка и появление взрыва при сбитии камня."""
        self.model.start_game()
        self.model.spawn_rock()
        rock = next(iter(self.model.rock_group))
        rock.x, rock.y = 200.0, 200.0
        rock.vx, rock.vy = 0.0, 0.0

        missile = self.model.ship.shoot()
        missile.x, missile.y = 200.0, 200.0
        self.model.missile_group.add(missile)

        self.model.step()
        self.assertEqual(self.model.score, 1)
        self.assertEqual(len(self.model.rock_group), 0)
        self.assertEqual(len(self.model.explosion_group), 1)


if __name__ == "__main__":
    unittest.main()
