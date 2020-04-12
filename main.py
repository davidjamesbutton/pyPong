import os
import random
import pygame
from pygame.locals import *


BLACK = Color(0, 0, 0)
BLUE = Color(0, 0, 255)
RED = Color(255, 0, 0)
WHITE = Color(255, 255, 255)

FPS = 60

SCORE_EVENT = pygame.USEREVENT + 1


def load_sound(filename):
    file_path = os.path.join('sound', filename)
    return pygame.mixer.Sound(file_path)


class Ball(pygame.sprite.Sprite):

    color = RED
    width = 20
    speed = 4

    def __init__(self, get_left_paddle_rect, get_right_paddle_rect, **kwargs):
        pygame.sprite.Sprite.__init__(self)

        self.get_left_paddle_rect = get_left_paddle_rect
        self.get_right_paddle_rect = get_right_paddle_rect

        self.image = pygame.Surface((Ball.width, Ball.width)).convert()
        self.image.fill(Ball.color)

        self.rect = self.image.get_rect(**kwargs)

        self.paddle_bounce_sound = load_sound('paddle_bounce.wav')
        self.wall_bounce_sound = load_sound('wall_bounce.wav')

        self.x_speed = Ball.speed
        self.y_speed = Ball.speed

    def update(self):
        screen_rect = pygame.display.get_surface().get_rect()

        new_rect = self.rect.move(self.x_speed, self.y_speed)

        # Bounce horizontal wall
        if new_rect.top < 0 or new_rect.bottom > screen_rect.bottom:
            self.wall_bounce_sound.play()
            self.y_speed *= -1

        # Bounce paddles
        if new_rect.colliderect(self.get_left_paddle_rect()):
            self.paddle_bounce_sound.play()
            self.x_speed = Ball.speed

        if new_rect.colliderect(self.get_right_paddle_rect()):
            self.paddle_bounce_sound.play()
            self.x_speed = -Ball.speed

        # Score!
        if new_rect.right > screen_rect.right:
            self._post_score_event(player=1)

        if new_rect.left < screen_rect.left:
            self._post_score_event(player=2)

        self.rect = new_rect.clamp(screen_rect)

    def _post_score_event(self, player):
        score_event = pygame.event.Event(SCORE_EVENT, player=player)
        pygame.event.post(score_event)

    def reset(self):
        screen_rect = pygame.display.get_surface().get_rect()

        self.rect.center = screen_rect.center

        self.x_speed = random.choice([1, -1]) * Ball.speed
        self.y_speed = random.choice([1, -1]) * Ball.speed


class Paddle(pygame.sprite.Sprite):

    color = BLUE
    width, height = 20, 100
    speed = 4

    def __init__(self, up_key, down_key, **kwargs):
        pygame.sprite.Sprite.__init__(self)

        self.up_key = up_key
        self.down_key = down_key

        self.image = pygame.Surface((Paddle.width, Paddle.height)).convert()
        self.image.fill(Paddle.color)

        self.rect = self.image.get_rect(**kwargs)

    def update(self, *args):
        keys = pygame.key.get_pressed()

        change = 0

        if keys[self.up_key]:
            change -= Paddle.speed
        if keys[self.down_key]:
            change += Paddle.speed

        screen_rect = pygame.display.get_surface().get_rect()
        new_rect = self.rect.move(0, change).clamp(screen_rect)

        self.rect = new_rect


class Score(pygame.sprite.Sprite):

    color = WHITE

    def __init__(self, **kwargs):
        pygame.sprite.Sprite.__init__(self)

        self.value = 0

        self.font = pygame.font.SysFont('Arial Black', 48)

        self.image = self.font.render(str(self.value), True, Score.color)
        self.rect = self.image.get_rect(**kwargs)

    def increment(self):
        self.value += 1
        self.image = self.font.render(str(self.value), True, Score.color)


def main():
    pygame.init()

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("pyPong")

    background = pygame.Surface(screen.get_size()).convert()
    background.fill(BLACK)

    screen.blit(background, (0, 0))
    pygame.display.update()

    score_sound = load_sound('score.wav')

    left_score = Score(top=1.5*Paddle.width, right=screen.get_rect().centerx-50)
    right_score = Score(top=1.5*Paddle.width, left=screen.get_rect().centerx+50)

    left_paddle = Paddle(up_key=K_w, down_key=K_s, left=1.5*Paddle.width, centery=100)
    right_paddle = Paddle(up_key=K_UP, down_key=K_DOWN, right=screen.get_width()-1.5*Paddle.width, centery=100)

    ball = Ball(lambda: left_paddle.rect, lambda: right_paddle.rect)
    ball.reset()

    all_sprites = pygame.sprite.RenderPlain([left_paddle, right_paddle, ball, left_score, right_score])

    clock = pygame.time.Clock()

    while True:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                quit()

            if event.type == SCORE_EVENT:
                if event.player == 1:
                    left_score.increment()
                if event.player == 2:
                    right_score.increment()
                score_sound.play()
                ball.reset()

        all_sprites.update()

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()