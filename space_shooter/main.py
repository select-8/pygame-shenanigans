import pygame
import os
import time
import random
import logging

pygame.font.init()

WIDTH, HEIGHT = 620, 820
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shooter')

RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))

RED_LAZER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
GREEN_LAZER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
BLUE_LAZER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
YELLOW_LAZER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))


BG = pygame.transform.scale(pygame.image.load('assets/background-black.png'), (WIDTH, HEIGHT))
BG.convert()


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self) # self here gives access to a specific instance of a laser

# abstract class to define Ships
class Ship:
    COOLDOWN = 25 # half FPS i.e. half a second

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for l in self.lasers:
            l.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for l in self.lasers:
            l.move(vel)
            if l.off_screen(HEIGHT):
                self.lasers.remove(l)
            elif l.collision(obj):
                obj.health -= 10
                self.lasers.remove(l)

    # func to time how fast you can shoot
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Players inherit from Ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) # use Ship's __init__ method on Player
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LAZER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # this will override the parent class move_lasers method
    def move_lasers(self, vel, objs):
        self.cooldown()
        for l in self.lasers:
            l.move(vel)
            if l.off_screen(HEIGHT):
                self.lasers.remove(l)
            else:
                for obj in objs:
                    if l.collision(obj):
                        objs.remove(obj)
                        if l in self.lasers:
                            self.lasers.remove(l)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

# Enemys inherit from Ship
class Enemy(Ship):
    COLOUR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LAZER),
        "green": (GREEN_SPACE_SHIP, GREEN_LAZER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LAZER)
    }
    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health) # use Ship's __init__ method on Player
        self.ship_img, self.laser_img = self.COLOUR_MAP[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel # enemy ships only move down

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x # the distance from obj1 to obj2 (top left x's) 
    offset_y = obj2.y - obj1.y # the distance from obj1 to obj2 (top left y's) 
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # is obj1 mask overlapping obj2 mask with the offset


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('robotoboldttf', 26)
    lost_font = pygame.font.SysFont('robotoboldttf', 50)
    enemy_cnt_fnt = pygame.font.SysFont('robotoboldttf', 15)

    enemies = []
    wave_length = 0

    enemy_velocity = 1
    player_velocity = 5

    laser_velocity = 5

    player = Player(int(WIDTH/2 - 50), 700)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        # draw background image
        WIN.blit(BG, (0,0))

        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255 , 255))
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 5 , 5))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255 , 255))
        WIN.blit(level_label, (5,5))
        enemy_label = enemy_cnt_fnt.render(f"Enemies: {len(enemies)}", 1, (255, 255 , 255))
        WIN.blit(enemy_label, (5, HEIGHT - enemy_label.get_height() - 5 ))

        # draw enemy ships
        for en in enemies:
            en.draw(WIN)

        # draw Player's ship
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render('YOU LOOSE!!!', 1, (255, 0, 0))
            WIN.blit(lost_label, ( WIDTH/2 - lost_label.get_width()/2, 300))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1 # move up a level if no more enemies
            wave_length += 5 # add more enemies
            # enemy_velocity = level
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-800, -100), random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if keys[pygame.K_UP] and player.y - player_velocity > 0:
            player.y -= player_velocity
        if keys[pygame.K_DOWN] and player.y + player_velocity + player.get_height() + 15 < HEIGHT: # the last 15 is the healthbar height
            player.y += player_velocity
        if keys[pygame.K_z]:
            player.shoot()

        for en in enemies[:]: # iterates over a copy of the enemies list
            en.move(enemy_velocity)
            en.move_lasers(laser_velocity, player)

            if random.randrange(0, 2*30) == 1:
                en.shoot()

            if collide(en, player):
                player.health -= 10
                enemies.remove(en)
            elif en.y + en.get_height() > HEIGHT: # if y is > height enemies have gone off the screen: loose and life, remove that enemy from the enemy list
                lives -= 1
                enemies.remove(en) # once at 0 we hit the condition 'if len(enemies) == 0:'


        player.move_lasers(-laser_velocity, enemies)

def main_menu():
    title_font = pygame.font.SysFont('calibriboldttf', 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350) )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menu()