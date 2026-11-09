"""Модуль генерации тайловых спрайтов и отрисовки игрового поля."""

import math
import os
import random
import tkinter as tk
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageTk

from src import config
from src.models.game_model import GameModel, Sprite


class Renderer:
    """Класс рендерера для тайловой анимации и отрисовки сцены на Canvas."""

    HUD_COLOR = "#19ff19"
    HUD_FONT = ("Arial", 22)

    def __init__(self, canvas: tk.Canvas, model: GameModel) -> None:
        """Подготавливает графические ресурсы и кэш повернутых тайлов."""
        self.canvas = canvas
        self.model = model
        self._ensure_assets_exist()

        self.nebula_img = Image.open(
            os.path.join(config.ASSETS_DIR, "nebula.png")
        ).convert("RGBA")
        self.debris_img = Image.open(
            os.path.join(config.ASSETS_DIR, "debris.png")
        ).convert("RGBA")
        self.splash_img = Image.open(
            os.path.join(config.ASSETS_DIR, "splash.png")
        ).convert("RGBA")
        self.ship_sheet = Image.open(
            os.path.join(config.ASSETS_DIR, "ship_tiles.png")
        ).convert("RGBA")
        self.rock_img = Image.open(
            os.path.join(config.ASSETS_DIR, "asteroid.png")
        ).convert("RGBA")
        self.missile_img = Image.open(
            os.path.join(config.ASSETS_DIR, "missile.png")
        ).convert("RGBA")
        self.explosion_sheet = Image.open(
            os.path.join(config.ASSETS_DIR, "explosion_tiles.png")
        ).convert("RGBA")

        self.tk_splash = ImageTk.PhotoImage(self.splash_img)
        self.tk_missile = ImageTk.PhotoImage(self.missile_img)

        # Нарезка 2 тайлов корабля (0 — без огня, 1 — с включенным двигателем)
        w, h = config.SHIP_TILE_SIZE
        self.ship_tiles: List[Image.Image] = [
            self.ship_sheet.crop((0, 0, w, h)),
            self.ship_sheet.crop((w, 0, w * 2, h)),
        ]

        # Нарезка 16 тайлов анимации взрыва из горизонтального спрайт-листа
        ew, eh = config.EXPLOSION_TILE_SIZE
        self.explosion_frames: List[ImageTk.PhotoImage] = [
            ImageTk.PhotoImage(
                self.explosion_sheet.crop((i * ew, 0, (i + 1) * ew, eh))
            )
            for i in range(config.EXPLOSION_TILES)
        ]

        self._ship_cache: Dict[Tuple[int, int], ImageTk.PhotoImage] = {}
        self._rock_cache: Dict[int, ImageTk.PhotoImage] = {}
        self._bg_photo: ImageTk.PhotoImage | None = None

    def render(self) -> None:
        """Полностью отрисовывает кадр: фоны, объекты, взрывы, HUD и заставку."""
        self.canvas.delete("all")
        self._draw_backgrounds()

        if self.model.started:
            self._draw_ship()
            for rock in self.model.rock_group:
                self._draw_rock(rock)
            for missile in self.model.missile_group:
                self._draw_missile(missile)
            for explosion in self.model.explosion_group:
                self._draw_explosion(explosion)

        self._draw_hud()

        if not self.model.started:
            self.canvas.create_image(
                config.SPLASH_CENTER_X,
                config.SPLASH_CENTER_Y,
                image=self.tk_splash,
            )

    def _draw_backgrounds(self) -> None:
        """Рисует неподвижный фон и движущийся влево полупрозрачный фон."""
        w = config.CANVAS_WIDTH
        h = config.CANVAS_HEIGHT
        offset = int(self.model.debris_time) % w

        frame = self.nebula_img.copy()
        # Тайловый сдвиг полупрозрачного слоя астероидов влево
        left_part = self.debris_img.crop((offset, 0, w, h))
        right_part = self.debris_img.crop((0, 0, offset, h))
        frame.alpha_composite(left_part, (0, 0))
        frame.alpha_composite(right_part, (w - offset, 0))

        self._bg_photo = ImageTk.PhotoImage(frame)
        self.canvas.create_image(w / 2, h / 2, image=self._bg_photo)

    def _draw_ship(self) -> None:
        """Отрисовывает корабль с нужным тайлом тяги и углом поворота."""
        tile_idx = 1 if self.model.ship.thrust else 0
        deg = int(-math.degrees(self.model.ship.angle)) % 360
        deg_step = (deg // 3) * 3
        key = (tile_idx, deg_step)

        if key not in self._ship_cache:
            rotated = self.ship_tiles[tile_idx].rotate(
                deg_step, resample=Image.Resampling.BICUBIC
            )
            self._ship_cache[key] = ImageTk.PhotoImage(rotated)

        self.canvas.create_image(
            self.model.ship.x,
            self.model.ship.y,
            image=self._ship_cache[key],
        )

    def _draw_rock(self, rock: Sprite) -> None:
        """Отрисовывает вращающийся астероид."""
        deg = int(-math.degrees(rock.angle)) % 360
        deg_step = (deg // 5) * 5

        if deg_step not in self._rock_cache:
            rotated = self.rock_img.rotate(
                deg_step, resample=Image.Resampling.BICUBIC
            )
            self._rock_cache[deg_step] = ImageTk.PhotoImage(rotated)

        self.canvas.create_image(
            rock.x, rock.y, image=self._rock_cache[deg_step]
        )

    def _draw_missile(self, missile: Sprite) -> None:
        """Отрисовывает выпущенную кораблем ракету."""
        self.canvas.create_image(
            missile.x, missile.y, image=self.tk_missile
        )

    def _draw_explosion(self, explosion: Sprite) -> None:
        """Отрисовывает текущий кадр тайловой анимации взрыва."""
        idx = min(explosion.age, config.EXPLOSION_TILES - 1)
        self.canvas.create_image(
            explosion.x, explosion.y, image=self.explosion_frames[idx]
        )

    def _draw_hud(self) -> None:
        """Отрисовывает количество жизней (Lives) и очков (Score) сверху."""
        self.canvas.create_text(
            135,
            25,
            text=f"Lives: {self.model.lives}",
            fill=self.HUD_COLOR,
            font=self.HUD_FONT,
        )
        self.canvas.create_text(
            config.CANVAS_WIDTH - 135,
            25,
            text=f"Score: {self.model.score}",
            fill=self.HUD_COLOR,
            font=self.HUD_FONT,
        )

    def _ensure_assets_exist(self) -> None:
        """Генерирует растровые PNG-спрайты и тайлы, если они отсутствуют."""
        os.makedirs(config.ASSETS_DIR, exist_ok=True)
        nebula_path = os.path.join(config.ASSETS_DIR, "nebula.png")
        if os.path.exists(nebula_path):
            return

        rng = random.Random(42)
        w, h = config.CANVAS_WIDTH, config.CANVAS_HEIGHT

        # 1. Неподвижный фон космоса и туманности (nebula.png)
        nebula = Image.new("RGBA", (w, h), (15, 8, 20, 255))
        ndraw = ImageDraw.Draw(nebula)
        for _ in range(35):
            cx = rng.randint(0, w)
            cy = rng.randint(0, h)
            rad = rng.randint(60, 180)
            col = (
                rng.randint(80, 160),
                rng.randint(20, 55),
                rng.randint(15, 70),
                45,
            )
            ndraw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)
        # Яркая голубая звезда в центре туманности
        ndraw.ellipse((420, 220, 500, 300), fill=(40, 140, 255, 110))
        nebula = nebula.filter(ImageFilter.GaussianBlur(22))
        ndraw = ImageDraw.Draw(nebula)
        ndraw.ellipse((448, 248, 472, 272), fill=(220, 250, 255, 255))
        for _ in range(180):
            sx, sy = rng.randint(0, w - 1), rng.randint(0, h - 1)
            ndraw.point((sx, sy), fill=(255, 240, 240, 230))
        nebula.save(nebula_path)

        # 2. Полупрозрачный динамический фон мелких астероидов (debris.png)
        debris = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ddraw = ImageDraw.Draw(debris)
        for _ in range(65):
            dx = rng.randint(15, w - 15)
            dy = rng.randint(15, h - 15)
            dr = rng.randint(4, 12)
            ddraw.ellipse(
                (dx - dr, dy - dr, dx + dr, dy + dr),
                fill=(130, 120, 105, 145),
                outline=(85, 78, 68, 170),
            )
        debris.save(os.path.join(config.ASSETS_DIR, "debris.png"))

        # 3. Заставка игры RiceRocks (splash.png)
        sw, sh = config.SPLASH_WIDTH, config.SPLASH_HEIGHT
        splash = Image.new("RGBA", (sw, sh), (35, 35, 125, 185))
        sdraw = ImageDraw.Draw(splash)
        sdraw.rectangle(
            (0, 0, sw - 1, sh - 1), outline=(55, 95, 235, 255), width=3
        )
        sdraw.text(
            (sw / 2, sh * 0.42),
            "RiceRocks",
            fill=(235, 240, 255, 255),
            anchor="mm",
            font_size=54,
        )
        sdraw.text(
            (sw / 2, sh * 0.68),
            "CLICK TO START",
            fill=(255, 255, 255, 255),
            anchor="mm",
            font_size=22,
        )
        splash.save(os.path.join(config.ASSETS_DIR, "splash.png"))

        # 4. Тайловый лист корабля (ship_tiles.png: 2 тайла 90x90)
        tw, th = config.SHIP_TILE_SIZE
        ship_sheet = Image.new("RGBA", (tw * 2, th), (0, 0, 0, 0))
        for idx in range(2):
            tile = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
            tdraw = ImageDraw.Draw(tile)
            if idx == 1:
                # Пламя работающего двигателя во втором тайле
                tdraw.polygon(
                    [(4, 45), (24, 34), (24, 56)],
                    fill=(255, 140, 20, 245),
                )
                tdraw.polygon(
                    [(10, 45), (24, 39), (24, 51)],
                    fill=(255, 245, 130, 255),
                )
            # Корпус и крылья космического корабля
            tdraw.polygon(
                [(80, 45), (20, 16), (30, 45), (20, 74)],
                fill=(185, 192, 205, 255),
                outline=(90, 95, 110, 255),
            )
            tdraw.ellipse(
                (40, 37, 62, 53),
                fill=(60, 155, 245, 255),
                outline=(220, 35, 35, 255),
            )
            ship_sheet.paste(tile, (idx * tw, 0))
        ship_sheet.save(os.path.join(config.ASSETS_DIR, "ship_tiles.png"))

        # 5. Спрайт астероида с кратерами (asteroid.png)
        rw, rh = config.ROCK_TILE_SIZE
        rock = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(rock)
        pts = []
        for i in range(14):
            ang = i * (2 * math.pi / 14)
            rad = config.ROCK_RADIUS - rng.randint(0, 7)
            pts.append((45 + rad * math.cos(ang), 45 + rad * math.sin(ang)))
        rdraw.polygon(
            pts, fill=(135, 138, 142, 255), outline=(75, 78, 82, 255)
        )
        for cx, cy, cr in [(32, 30, 8), (56, 36, 10), (42, 58, 9)]:
            rdraw.ellipse(
                (cx - cr, cy - cr, cx + cr, cy + cr),
                fill=(95, 98, 104, 255),
                outline=(65, 68, 72, 255),
            )
        rock.save(os.path.join(config.ASSETS_DIR, "asteroid.png"))

        # 6. Спрайт ракеты (missile.png)
        mw, mh = config.MISSILE_TILE_SIZE
        missile = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        mdraw = ImageDraw.Draw(missile)
        mdraw.ellipse((2, 2, mw - 2, mh - 2), fill=(120, 225, 255, 200))
        mdraw.ellipse((5, 5, mw - 5, mh - 5), fill=(255, 255, 255, 255))
        missile.save(os.path.join(config.ASSETS_DIR, "missile.png"))

        # 7. Тайловая лента взрыва (explosion_tiles.png: 16 кадров 100x100)
        ew, eh = config.EXPLOSION_TILE_SIZE
        cnt = config.EXPLOSION_TILES
        exp_sheet = Image.new("RGBA", (ew * cnt, eh), (0, 0, 0, 0))
        for i in range(cnt):
            etile = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
            edraw = ImageDraw.Draw(etile)
            progress = (i + 1) / cnt
            outer_r = int(12 + 34 * math.sin(progress * math.pi))
            alpha = int(255 * (1.0 - progress * 0.75))
            edraw.ellipse(
                (50 - outer_r, 50 - outer_r, 50 + outer_r, 50 + outer_r),
                fill=(235, 110, 185, alpha),
            )
            inner_r = max(4, int(outer_r * 0.65))
            edraw.ellipse(
                (50 - inner_r, 50 - inner_r, 50 + inner_r, 50 + inner_r),
                fill=(255, 220, 95, min(255, alpha + 30)),
            )
            etile = etile.filter(ImageFilter.GaussianBlur(2))
            exp_sheet.paste(etile, (i * ew, 0))
        exp_sheet.save(
            os.path.join(config.ASSETS_DIR, "explosion_tiles.png")
        )
