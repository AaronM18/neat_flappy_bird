import pygame
from pygame.locals import *
import neat
import time
import os
import random
pygame.font.init()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird1.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird2.png'))), pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird3.png')))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bg.png')))
STAT_FONT = pygame.font.SysFont('comicsans', 50)


class Bird:
  IMGS = BIRD_IMGS
  MAX_ROTATION = 25
  ROTATION_VELOCITY = 20
  ANIMATION_TIME = 5

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.velocity = 0
    self.height = self.y
    self.img_count = 0
    self.img = self.IMGS[0]

  def jump(self):
    self.velocity = -10.5
    self.tick_count = 0
    self.height = self.y

  def move(self):
    self.tick_count += 1
    # velocity * t + 1.5 * t^2 = parabola
    displacement = self.velocity * self.tick_count + 1.5 * self.tick_count**2 

    if displacement >= 16:
      displacement = 16

    if displacement < 0:
      displacement -= 2

    self.y = self.y + displacement

    if displacement < 0 or self.y < self.height + 50:
      if self.tilt < self.MAX_ROTATION:
        self.tilt = self.MAX_ROTATION
    else:
      if self.tilt > -90:
        self.tilt -= self.ROTATION_VELOCITY

  def draw(self, window):
    self.img_count += 1
    # Check what bird image to show
    if self.img_count < self.ANIMATION_TIME:
      self.img = self.IMGS[0]
    elif self.img_count < self.ANIMATION_TIME*2:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*3:
      self.img = self.IMGS[2]
    elif self.img_count < self.ANIMATION_TIME*4:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*4 + 1:
      self.img = self.IMGS[0]
      self.img_count = 0

    if self.tilt <= -80:
      self.img = self.IMGS[1]
      self.img_count =self.ANIMATION_TIME*2

    rotated_image = pygame.transform.rotate(self.img, self.tilt)
    new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
    window.blit(rotated_image, new_rectangle.topleft)

  def get_mask(self):
    return pygame.mask.from_surface(self.img)


class Pipe:
  GAP = 200
  VELOCITY = 5

  def __init__(self, x):
    self.x = x
    self.height =  0

    self.top = 0
    self.bottom = 0
    
    self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    self.PIPE_BOTTOM = PIPE_IMG

    self.passed = False
    self.set_height()

  def set_height(self):
    self.height = random.randrange(50, 450)
    self.top = self.height - self.PIPE_TOP.get_height()
    self.bottom = self.height + self.GAP

  def move(self):
    self.x -= self.VELOCITY

  def draw(self, window):
    window.blit(self.PIPE_TOP, (self.x, self.top))
    window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

  def collide(self, bird):
    bird_mask = bird.get_mask()
    top_mask = pygame.mask.from_surface(self.PIPE_TOP)
    bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

    top_offset = (self.x - bird.x, self.top - round(bird.y))
    bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

    bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
    top_point = bird_mask.overlap(top_mask, top_offset)

    if top_point or bottom_point:
      return True

    return False


class Base:
  VELOCITY = 5
  WIDTH = BASE_IMG.get_width()
  IMG = BASE_IMG

  def __init__(self, y):
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self):
    self.x1 -= self.VELOCITY
    self.x2 -= self.VELOCITY

    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH

    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH

  def draw(self, window):
    window.blit(self.IMG, (self.x1, self.y))
    window.blit(self.IMG, (self.x2, self.y))

"""
MAIN LOOP FOR WINDOW
"""
def draw_window(window, bird, pipes, base, score):
  window.blit(BG_IMG, (0,0))

  for pipe in pipes:
    pipe.draw(window)

  text = STAT_FONT.render('Score: ' + str(score), 1, (255,255,255))
  print(WINDOW_WIDTH - 10 - text.get_width())
  window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))
  base.draw(window)
  bird.draw(window)

  pygame.display.update()

def main():
  BASE_HEIGHT = 730
  PIPE_HEIGHT = 600

  bird = Bird(230,350)
  base = Base(BASE_HEIGHT)
  pipes = [Pipe(PIPE_HEIGHT)]

  score = 0

  window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
  run = True
  clock = pygame.time.Clock()

  while run:
    clock.tick(30)
    for event in pygame.event.get():
      if event.type == QUIT:
        run = False
    #bird.move()
    add_pipe = False
    rem = []
    for pipe in pipes:
      pipe.move()

      if pipe.collide(bird):
        pass

      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
        rem.append(pipe)

      if not pipe.passed and pipe.x < bird.x:
        pipe.passed = True
        add_pipe = True

    if add_pipe:
      score += 1
      pipes.append(Pipe(PIPE_HEIGHT))

    for r in rem:
      pipes.remove(r)

    if bird.y + bird.img.get_height() > BASE_HEIGHT:
      pass

    base.move()
    draw_window(window, bird, pipes, base, score)
  pygame.display.quit()
  pygame.quit()
  quit()

main()