import math
import pygame
from .tower import Tower
import os
from menu.menu import Menu

menu_bg = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "menu.png")).convert_alpha(), (120, 70))
upgrade_btn = pygame.transform.scale(pygame.image.load(os.path.join("game_assets", "upgrade.png")).convert_alpha(), (50, 50))

tower_imgs = []
archer_imgs = []

# Load archer tower images
for x in range(15, 18):
    tower_imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/stone_towers", str(x) + ".png")).convert_alpha(),
        (90, 90)))

# Load rock image
for x in range(29, 30):
    archer_imgs.append(pygame.transform.scale(
        pygame.image.load(os.path.join("game_assets/stone_towers", str(x) + ".png")).convert_alpha(),
        (25, 25)))
    rock_img = archer_imgs[0]


class StoneTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tower_imgs = tower_imgs[:]
        self.archer_imgs = archer_imgs[:]
        self.archer_count = 0
        self.range = 200
        self.original_range = self.range
        self.inRange = False
        self.left = True
        self.price = [1500, 4000, "MAX"]
        self.damage = 1
        self.original_damage = self.damage
        self.attack_speed = 60  # Attack speed
        self.projectiles = []  # List to store projectiles
        self.width = self.height = 90
        self.moving = False
        self.name = "stone"
        self.attack_type = "physical"

        self.menu = Menu(self, self.x, self.y, menu_bg, self.price)
        self.menu.add_btn(upgrade_btn, "Upgrade")

        self.attack_count = 0  # Attack counter
        self.attack_speed = 60  # Attack speed (frames, 60 means once per second)

    def get_upgrade_cost(self):
        """
        Get the upgrade cost
        :return: int
        """
        return self.menu.get_item_cost()

    def draw(self, win):
        """
        Draw the tower and its animated projectile
        :param win: surface
        :return: int
        """
        super().draw_radius(win)
        super().draw(win)

        # Sine wave control for amplitude and frequency
        amplitude = 12  # Amplitude controlling the wave size
        frequency = 450  # Frequency controlling wave speed (higher = slower)

        # Calculate the vertical offset using a sine function
        rock_offset = int(amplitude * math.sin(pygame.time.get_ticks() / frequency))

        # Horizontal and vertical adjustment offsets
        horizontal_offset = -6  # Horizontal fine-tuning
        vertical_offset = -10  # Vertical fine-tuning

        # Calculate rock position
        rock_x = self.x + horizontal_offset
        rock_y = (
            self.y
            - self.tower_imgs[0].get_height() // 2
            - rock_img.get_height() // 2
            + vertical_offset
            + rock_offset
        )

        # Draw the rock
        win.blit(rock_img, (rock_x - rock_img.get_width() // 2, rock_y))

        # Draw all projectiles
        for projectile in self.projectiles:
            projectile.draw(win)

    def change_range(self, r):
        """
        Change the tower's attack range
        :param r: int
        :return: None
        """
        self.range = r

    def attack(self, enemies):
        """
        Attack enemies within range
        :param enemies: list of enemies
        :return: int (money earned)
        """
        self.attack_count += 1  # Increment attack counter per frame
        if self.attack_count < self.attack_speed:
            return 0  # Skip attack if attack speed threshold not met

        money = 0
        self.attack_count = 0  # Reset attack counter
        self.inRange = False
        enemy_closest = []

        # Check for enemies within range
        for enemy in enemies:
            x, y = enemy.x, enemy.y
            dis = math.sqrt((self.x - enemy.img.get_width() / 2 - x) ** 2 +
                            (self.y - enemy.img.get_height() / 2 - y) ** 2)
            if dis < self.range:
                self.inRange = True
                enemy_closest.append(enemy)

        # Sort enemies by path position to prioritize closest ones
        enemy_closest.sort(key=lambda x: x.path_pos)

        # Attack the first enemy in range
        if len(enemy_closest) > 0:
            first_enemy = enemy_closest[0]
            if first_enemy.hit(self.damage):
                money += first_enemy.money
                enemies.remove(first_enemy)

        return money

    def update_projectiles(self, enemies):
        """
        Update projectile positions and handle hit logic
        :param enemies: list of enemies
        """
        for projectile in self.projectiles[:]:
            projectile.move()
            if projectile.hit_target:  # If projectile hits the target
                if projectile.target in enemies:
                    if projectile.target.hit(projectile.damage):  # Target takes damage
                        enemies.remove(projectile.target)  # Remove if target dies
                self.projectiles.remove(projectile)  # Remove projectile on hit


class Projectile:
    def __init__(self, x, y, target, img, damage):
        """
        Initialize a projectile
        :param x: initial x-coordinate
        :param y: initial y-coordinate
        :param target: target enemy
        :param img: projectile image
        :param damage: projectile damage
        """
        self.x = x
        self.y = y
        self.target = target
        self.img = img
        self.damage = damage
        self.speed = 10  # Projectile speed
        self.hit_target = False  # Whether it hit the target

    def move(self):
        """
        Move the projectile towards the target
        """
        if self.target and self.target.health > 0:  # Check if the target is valid
            target_x = self.target.x + self.target.img.get_width() // 2
            target_y = self.target.y + self.target.img.get_height() // 2
            dir_x, dir_y = target_x - self.x, target_y - self.y
            dist = math.sqrt(dir_x ** 2 + dir_y ** 2)

            if dist > 0:
                dir_x, dir_y = dir_x / dist, dir_y / dist
                self.x += dir_x * self.speed
                self.y += dir_y * self.speed

            # Check if it hits the target
            if dist < 10:  # Hit distance
                self.hit_target = True
        else:
            self.hit_target = True  # If target is invalid, mark as hit

    def draw(self, win):
        """
        Draw the projectile
        """
        win.blit(self.img, (self.x - self.img.get_width() // 2, self.y - self.img.get_height() // 2))
