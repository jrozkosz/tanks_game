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
        self.angle_speed = 0.8
        self.speed = 1

        self.position = Vector2((pos_x, pos_y))
        self.direction = Vector2(0, 1)
    
    def rotate(self, right_direction):
        print(self.direction)
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
        return Bullet(self.parent_screen, self.rect.x + round(self.image.get_width()/2), 
            self.rect.y + round(self.image.get_height()/2), self.direction, facing_down)
    
    def reload(self):
        # return Clip(self.rect.x + round(self.image.get_width()/2), self.rect.y+50, (0, 0, 255))
        return Clip(self.rect, (0, 0, 255))


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
        self.speed = 2
    
    def update(self):
        self.position += self.direction * self.speed if self.facing_down else -self.direction * self.speed
        self.rect.center = self.position

        if self.rect.x >= self.parent_screen.get_width()+100 or -100 >= self.rect.x or \
                self.rect.y >= self.parent_screen.get_height()+100 or -100 >= self.rect.y:
            self.kill()


class Clip(pygame.sprite.Sprite):
    def __init__(self, rect, color):
        super().__init__()

        self.image = pygame.Surface((50, 10))
        self.image.fill(color)
        self.rect = rect
        self.progress = 0

    def update(self, rect):
        self.progress += 0.1
        self.progress = round(self.progress, 1)
        self.image = pygame.Surface((50-self.progress, 5))
        self.rect = rect
        if self.progress == 50:
            self.kill()




class Game:
    def __init__(self):
        pygame.init()
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
        # all_groups = [self.tank_group, self.blue_bullet_group, self.red_bullet_group, 
        #     self.clip_blue_group, self.clip_red_group]
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:   
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if len(self.clip_blue_group) == 0:
                        if event.key == K_SPACE:
                            if len(self.blue_bullet_group) < 5:
                                self.blue_bullet_group.add(self.blue_tank.fire_bullet(True))
                            else:
                                self.clip_blue_group.add(self.blue_tank.reload())
                    if len(self.clip_red_group) == 0:
                        if event.key == K_q:
                            if len(self.red_bullet_group) < 5:
                                self.red_bullet_group.add(self.red_tank.fire_bullet(False))
                            else:
                                self.clip_red_group.add(self.red_tank.reload())
                elif event.type == QUIT:
                    running = False
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

            if pygame.sprite.spritecollide(self.blue_tank, self.red_bullet_group, True):
                print("BLUE HIT!")
            if pygame.sprite.spritecollide(self.red_tank, self.blue_bullet_group, True):
                print("RED HIT!")
            
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
            clock.tick(120)