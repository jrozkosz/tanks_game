import pygame
from pygame.locals import *
import math

from pygame.math import Vector2

class Tank(pygame.sprite.Sprite):
    def __init__(self, surface, tank_type, pos_x, pos_y):
        super().__init__()

        self.parent_screen = surface
        self.original_image = pygame.image.load(f"resources/{tank_type}").convert_alpha()
        # self.original_image = pygame.Surface((40, 40))
        # self.original_image.fill((0, 255, 0))
        self.original_image.get_rect(center = (pos_x, pos_y))
        self.image = self.original_image
        self.rect = self.image.get_rect(center = (pos_x, pos_y))
        self.angle = 0
        self.angle_speed = 1
        self.speed = 1
        self.bullets_fired = 0

        self.position = Vector2((pos_x, pos_y))
        self.direction = Vector2(0, 1)
    
    def rotate(self, right_direction):
        if self.angle_speed != 0:
            self.direction.rotate_ip(self.angle_speed) if right_direction else self.direction.rotate_ip(-self.angle_speed)
            self.angle += self.angle_speed if right_direction else -self.angle_speed
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, forward, prev_pos):
        prev_pos_copy = prev_pos.copy()
        self.position += self.direction * self.speed if forward else -self.direction * self.speed
        self.rect.center = self.position
        
        if 0 > self.position.x or 0 > self.position.y:
            self.position = prev_pos_copy
            self.rect.center = self.position
            # self.position -= self.direction * 10*self.speed
            # self.rect.center = self.position
        elif self.position.x > self.parent_screen.get_width() or self.position.y > self.parent_screen.get_height():
            self.position = prev_pos_copy
            self.rect.center = self.position
        # self.rect.y += round(self.speed*math.cos(-self.angle*math.pi/180))
        # self.rect.x += round(self.speed*math.sin(-self.angle*math.pi/180))
    
    def fire_bullet(self, facing_down):
        self.bullets_fired += 1
        return Bullet(self.parent_screen, self.rect.x + round(self.image.get_width()/2), 
            self.rect.y + round(self.image.get_height()/2), self.direction, facing_down)
    
    def reload(self):
        # return Clip(self.rect.x + round(self.image.get_width()/2), self.rect.y+50, (0, 0, 255))
        return Clip(self, self.rect, (0, 0, 255))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, surface, pos_x, pos_y, direction, facing_down):
        super().__init__()

        self.direction = direction.copy()
        self.position = Vector2((pos_x, pos_y))
        self.facing_down = facing_down
        self.parent_screen = surface
        self.image = pygame.Surface((6, 6))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center = (pos_x, pos_y))
        self.speed = 2.2
    
    def update(self):
        self.position += self.direction * self.speed if self.facing_down else -self.direction * self.speed
        self.rect.center = self.position

        if self.rect.x >= self.parent_screen.get_width()+100 or -100 >= self.rect.x or \
                self.rect.y >= self.parent_screen.get_height()+100 or -100 >= self.rect.y:
            self.kill()


class Clip(pygame.sprite.Sprite):
    def __init__(self, tank: Tank, rect, color):
        super().__init__()

        self.image = pygame.Surface((50, 10))
        self.image.fill(color)
        self.rect = rect
        self.progress = 0
        self.tank = tank

    def update(self, rect):
        self.progress += 0.1
        self.progress = round(self.progress, 1)
        self.image = pygame.Surface((50-self.progress, 5))
        self.rect = rect
        if self.progress == 50:
            self.tank.bullets_fired = 0
            self.kill()

class GameOver(pygame.sprite.Sprite):
    def __init__(self, blue_won: bool, pos_x, pos_y):
        super().__init__()

        if blue_won:
            self.image = pygame.image.load(f"resources/blue_won.png").convert_alpha()
        else:
            self.image = pygame.image.load(f"resources/red_won.png").convert_alpha()
        self.rect = self.image.get_rect(center = (pos_x, pos_y))




class Game:
    def __init__(self):
        pygame.init()
        self.running = False
        self.initialize_game()
    
    def initialize_game(self):
        self.surface = pygame.display.set_mode((700, 600))
        self.surface.fill((255, 255, 255))
        pygame.display.flip()
        self.tank_group = pygame.sprite.Group()
        self.blue_tank = Tank(self.surface, "blue_tank40.png", 100, 100)
        self.tank_group.add(self.blue_tank)
        self.red_tank = Tank(self.surface, "red_tank40.png", 600, 500)
        self.tank_group.add(self.red_tank)
        self.blue_bullet_group = pygame.sprite.Group()
        self.red_bullet_group = pygame.sprite.Group()
        self.clip_blue_group = pygame.sprite.GroupSingle()
        self.clip_red_group = pygame.sprite.GroupSingle()
        self.blue_bullets_fired = 0
        self.red_bullets_fired = 0
        self.red_won = False
        self.blue_won = False
        self.game_over_group = pygame.sprite.GroupSingle()


    def handle_reloading(self):
        if self.blue_tank.bullets_fired >= 5 and len(self.clip_blue_group) == 0:
            self.clip_blue_group.add(self.blue_tank.reload())
        if self.red_tank.bullets_fired >= 5 and len(self.clip_red_group) == 0:
            self.clip_red_group.add(self.red_tank.reload())
    
    def handle_collisions(self):
        red_bullet_that_hit = pygame.sprite.spritecollide(self.blue_tank, self.red_bullet_group, False)
        if red_bullet_that_hit:
            # if (self.blue_tank.position.x-int(self.blue_tank.rect.width/2)+7 < \
            #     bullet_that_hit[0].position.x < self.blue_tank.position.x+int(self.blue_tank.rect.width/2)-7):
            if (self.blue_tank.position.x-int(0.7*(self.blue_tank.rect.width/2)) < \
                    red_bullet_that_hit[0].position.x < self.blue_tank.position.x+int(0.7*(self.blue_tank.rect.width/2)) and
                    self.blue_tank.position.y-int(0.7*(self.blue_tank.rect.width/2)) < \
                    red_bullet_that_hit[0].position.y < self.blue_tank.position.y+int(0.7*(self.blue_tank.rect.width/2))):
                print("BLUE HIT!")
                red_bullet_that_hit[0].kill()
                self.red_won = True
        blue_bullet_that_hit = pygame.sprite.spritecollide(self.red_tank, self.blue_bullet_group, False)
        if blue_bullet_that_hit:
            if (self.red_tank.position.x-int(0.7*(self.red_tank.rect.width/2)) < \
                    blue_bullet_that_hit[0].position.x < self.red_tank.position.x+int(0.7*(self.red_tank.rect.width/2)) and
                    self.red_tank.position.y-int(0.7*(self.red_tank.rect.width/2)) < \
                    blue_bullet_that_hit[0].position.y < self.red_tank.position.y+int(0.7*(self.red_tank.rect.width/2))):
                print("RED HIT!")
                blue_bullet_that_hit[0].kill()
                self.blue_won = True
    
    def draw_and_update(self):
        self.surface.fill((255, 255, 255))
        self.blue_bullet_group.draw(self.surface)
        self.red_bullet_group.draw(self.surface)
        self.blue_bullet_group.update()
        self.red_bullet_group.update()
        self.clip_blue_group.draw(self.surface)
        self.clip_red_group.draw(self.surface)
        self.clip_blue_group.update(self.blue_tank.rect)
        self.clip_red_group.update(self.red_tank.rect)
        self.tank_group.draw(self.surface)
        pygame.display.flip()
    
    def handle_key_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                if event.key == K_SPACE:
                    if self.blue_tank.bullets_fired < 5:
                        self.blue_bullet_group.add(self.blue_tank.fire_bullet(True))
                if event.key == K_q:
                    if self.red_tank.bullets_fired < 5:
                        self.red_bullet_group.add(self.red_tank.fire_bullet(False))
            elif event.type == QUIT:
                self.running = False
        if pygame.key.get_pressed()[K_UP]:
            self.blue_tank.move(True, self.blue_tank.position)
        if pygame.key.get_pressed()[K_DOWN]:
            self.blue_tank.move(False, self.blue_tank.position)
        if pygame.key.get_pressed()[K_RIGHT]:
            self.blue_tank.rotate(True)
        if pygame.key.get_pressed()[K_LEFT]:
            self.blue_tank.rotate(False)
        if pygame.key.get_pressed()[K_w]:
            self.red_tank.move(False, self.red_tank.position)
        if pygame.key.get_pressed()[K_s]:
            self.red_tank.move(True, self.red_tank.position)
        if pygame.key.get_pressed()[K_d]:
            self.red_tank.rotate(True)
        if pygame.key.get_pressed()[K_a]:
            self.red_tank.rotate(False)
    
    def handle_restart(self):
        restart = False
        if self.blue_won:
            self.game_over_group.add(GameOver(True, 350, 300))
        elif self.red_won:
            self.game_over_group.add(GameOver(False, 350, 300))
        self.game_over_group.draw(self.surface)
        self.game_over_group.update()
        pygame.display.flip()
        while not restart:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                        restart = True
                    if event.key == K_r:
                        restart = True
                        self.initialize_game()
                elif event.type == QUIT:
                    self.running = False
                    restart = True
    
    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            self.handle_key_events()
            self.handle_reloading()
            self.handle_collisions()
            self.draw_and_update()
            if self.blue_won or self.red_won:
                self.handle_restart()
            clock.tick(120)