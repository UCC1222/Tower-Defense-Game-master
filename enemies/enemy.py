import pygame
import math
import os


class Enemy:
    def __init__(self):
        self.width = 64
        self.height = 64
        self.animation_count = 0
        self.health = 1
        self.vel = 3
        self.path = [(-10, 250),(100, 250), (190, 302), (200, 302), (553, 302), (607, 217), (641, 105), (717, 57), (814, 83), (852, 222), (900, 272), (973, 284), (1100, 366), (1100, 437), (1022, 513), (814, 513), (650, 580), (580, 580), (148, 580), (43, 520), (-10, 367), (-70, 367), (-100, 367)]
        self.x = self.path[0][0]
        self.y = self.path[0][1]
        self.img = pygame.image.load(os.path.join("game_assets/enemies/1", "1_enemies_1_run_000.png")).convert_alpha()
        self.dis = 0
        self.path_pos = 0
        self.move_count = 0
        self.move_dis = 0
        self.imgs = []
        self.flipped = False

        self.max_health = 1
        self.speed_increase = 1.2
        self.armor = 0
        self.magic_resistance = 0

    def draw(self, win):
        """
        Draws the enemy with the given images
        :param win: surface
        :return: None
        """
        self.img = self.imgs[self.animation_count]

        win.blit(self.img, (self.x - self.img.get_width()/2, self.y- self.img.get_height()/2 - 35))
        self.draw_health_bar(win)

    def draw_health_bar(self, win):
        """
        draw health bar above enemy
        :param win: surface
        :return: None
        """
        length = 50
        move_by = length / self.max_health
        health_bar = round(move_by * self.health)

        pygame.draw.rect(win, (255,0,0), (self.x-30, self.y-75, length, 10), 0)
        pygame.draw.rect(win, (0, 255, 0), (self.x-30, self.y - 75, health_bar, 10), 0)

    def collide(self, X, Y):
        """
        Returns if position has hit enemy
        :param x: int
        :param y: int
        :return: Bool
        """
        if X <= self.x + self.width and X >= self.x:
            if Y <= self.y + self.height and Y >= self.y:
                return True
        return False

    def move(self):
        """
        Move enemy
        :return: None
        """
        self.animation_count += 1
        if self.animation_count >= len(self.imgs):
            self.animation_count = 0

        x1, y1 = self.path[self.path_pos]
        x1 = x1 + 75
        if self.path_pos + 1 >= len(self.path):
            x2, y2 = (-10, 355)
        else:
            x2, y2 = self.path[self.path_pos+1]

        x2 = x2+75

        dirn = ((x2-x1)*2, (y2-y1)*2)
        length = math.sqrt((dirn[0])**2 + (dirn[1])**2)
        dirn = (dirn[0]/length * self.speed_increase, dirn[1]/length * self.speed_increase)

        if dirn[0] < 0 and not(self.flipped):
            self.flipped = True
            for x, img in enumerate(self.imgs):
                self.imgs[x] = pygame.transform.flip(img, True, False)

        move_x, move_y = ((self.x + dirn[0]), (self.y + dirn[1]))

        self.x = move_x
        self.y = move_y

        # Go to next point
        if dirn[0] >= 0:   # moving right
            if dirn[1] >= 0:   # moving down
                if self.x >= x2 and self.y >= y2:
                    self.path_pos += 1
            else:
                if self.x >= x2 and self.y <= y2:
                    self.path_pos += 1
        else:   # moving left
            if dirn[1] >= 0:  # moving down
                if self.x <= x2 and self.y >= y2:
                    self.path_pos += 1
            else:
                if self.x <= x2 and self.y >= y2:
                    self.path_pos += 1

    def hit(self, damage):
        """
        Returns if an enemy has died, and removes one health each call
        Used to calculate physical damage.

        return: Bool
        """
        # Deduct HP
        adjusted_damage = damage - self.armor
        if adjusted_damage < 0:
            adjusted_damage = 0

        self.health -= adjusted_damage

        # Determine if the monster is dead
        if self.health <= 0:
            return True
        return False

    def hit_magic(self, damage):
        """
        Returns if an enemy has died, and removes one health each call
        Used to calculate magical damage.

        return: Bool
        """
        # Deduct HP
        if self.magic_resistance > 1:
            adjusted_damage = 0
        else:
            adjusted_damage = damage * (1 - self.magic_resistance)

        self.health -= adjusted_damage

        # Determine if the monster is dead
        if self.health <= 0:
            return True
        return False
