import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 420, 620
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

# abstract class to define Ships
class Ship:
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


def main():
    run = True
    FPS = 60
    level = 1
    lives = 5
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont('robotoboldttf', 26)
    player_velocity = 5
    player = Player(200, 500)

    def redraw_window():
        # draw background image
        WIN.blit(BG, (0,0))

        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255 , 255))
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 5 , 5))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255 , 255))
        WIN.blit(level_label, (5,5))
        
        # draw Player's ship
        player.draw(WIN)
        
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity
        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() < WIDTH:
            player.x += player_velocity
        if keys[pygame.K_UP] and player.y - player_velocity > 0:
            player.y -= player_velocity
        if keys[pygame.K_DOWN] and player.y + player_velocity + player.get_height() < HEIGHT:
            player.y += player_velocity

main()