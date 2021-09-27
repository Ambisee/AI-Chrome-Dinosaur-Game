import os
import sys
import pygame
import random
from config import WIDTH, HEIGHT, GROUND_HEIGHT

pygame.init()

current_dir = os.path.dirname(__name__)
trex_animation_frames = []
cactus_sprites = []

trexJump = pygame.image.load(os.path.join(current_dir, 'resources/trex1.png'))
trex1 = pygame.image.load(os.path.join(current_dir, 'resources/trex3.png'))
trex2 = pygame.image.load(os.path.join(current_dir, 'resources/trex4.png'))
cactus1 = pygame.image.load(os.path.join(current_dir, 'resources/cactus1.png'))
cactus2 = pygame.image.load(os.path.join(current_dir, 'resources/cactus2.png'))
cactus3 = pygame.image.load(os.path.join(current_dir, 'resources/cactus3.png'))

trex_animation_frames.append(pygame.transform.scale(trex1, (50, 50)))
trex_animation_frames.append(pygame.transform.scale(trex2, (50, 50)))
trex_animation_frames.append(pygame.transform.scale(trexJump, (50, 50)))
cactus_sprites.append(pygame.transform.scale(cactus1, (40, 84)))
cactus_sprites.append(pygame.transform.scale(cactus2, (56, 60)))
cactus_sprites.append(pygame.transform.scale(cactus3, (69, 70)))


class Dinosaur(object):
    def __init__(self, x=400, y=GROUND_HEIGHT):
        self.x = x
        self.y = y - 50
        self.h = 0
        self.is_jump = False
        self.jump_count = 9
        self.animation_switch = False
        self.timer = 0
        self.sprites = trex_animation_frames
        self.current_sprite = self.sprites[0]

        self.width = self.current_sprite.get_width()

    
    def jump(self):
        self.is_jump = True


    def move(self):
        self.timer = 0 if self.timer > 10000 else self.timer

        if self.jump_count >= -9 and self.is_jump:
            neg = 1
            if self.jump_count < 0:
                neg = -1
            self.y -= (self.jump_count ** 2) * neg * 0.5
            self.jump_count -= 1
        else:
            self.is_jump = False
            self.jump_count = 9
                
        self.timer += 1


    def get_mask(self):
        return pygame.mask.from_surface(self.current_sprite)

    
    def draw(self, win, proceed_render_function):
        self.current_sprite = self.sprites[2]
        if not self.is_jump:
            if proceed_render_function():
                self.animation_switch = int(self.animation_switch ^ (self.timer % 5 == 0))
            self.current_sprite = self.sprites[self.animation_switch]

        win.blit(self.current_sprite, (self.x, self.y))


class Cactus(object):
    def __init__(self, x, y, sprite=0):
        self.sprite = random.choice(cactus_sprites)
        self.x = x
        self.y = y - self.sprite.get_height() + 7
        self.width = self.sprite.get_width()
        self.passed = False


    def move(self):
        self.x -= 20

    
    def draw(self, win):
        win.blit(self.sprite, (self.x, self.y))
    

    def check_collision(self, dino):
        dino_mask = dino.get_mask()
        cactus_mask = pygame.mask.from_surface(self.sprite)

        offset_x = self.x - round(dino.x)
        offset_y = self.y - round(dino.y)
        overlapping = cactus_mask.overlap(dino_mask, (offset_x, offset_y))

        if overlapping is not None: return True
        return False

    def set_passed(self):
        self.passed = True

    def is_passed(self):
        return self.passed

class Ground(object):
    def __init__(self, x=0, y=GROUND_HEIGHT):
        self.x = x
        self.y = y
        self.height = HEIGHT - self.y
        self.width = WIDTH
        self.surface = pygame.Surface((self.width, self.height))

    
    def draw(self, win):
        self.surface.fill(pygame.Color(200, 200, 200))
        win.blit(self.surface, (self.x, self.y))
