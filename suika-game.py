import pygame
import random
import math
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 1500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Suika Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# settings
BALL_SCALE = 5  # 5x bigger
LINE_Y = 150  # game over line height
OVERLINE_TIME_LIMIT = 120  # 2 seconds at 60 FPS

# color levels
COLORS = [
    (255, 0, 0),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (0, 128, 255),
    (75, 0, 130),
    (128, 0, 255),
    (255, 105, 180),
    (160, 82, 45),
    (0, 0, 0),
    (255, 255, 255)
]

class Ball:
    def __init__(self, x, y, level):
        self.level = level
        self.radius = (20 + level * 6) * BALL_SCALE
        self.color = COLORS[level]
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.merged = False

    def update(self):
        self.vy += 0.6  # gravity
        self.x += self.vx
        self.y += self.vy

        # wall bounce
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -0.7
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -0.7

        # floor bounce
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -0.6
            self.vx *= 0.98

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.radius))

def check_collisions(balls):
    global score
    for i, a in enumerate(balls):
        for j, b in enumerate(balls):
            if i >= j:
                continue

            dx = a.x - b.x
            dy = a.y - b.y
            dist = math.hypot(dx, dy)
            min_dist = a.radius + b.radius

            if dist < min_dist:
                if dist == 0:
                    dist = 0.01
                nx = dx / dist
                ny = dy / dist
                overlap = (min_dist - dist)

                # push them apart
                a.x += nx * (overlap / 2)
                a.y += ny * (overlap / 2)
                b.x -= nx * (overlap / 2)
                b.y -= ny * (overlap / 2)

                # bounce
                rel_vx = a.vx - b.vx
                rel_vy = a.vy - b.vy
                dot = rel_vx * nx + rel_vy * ny
                if dot < 0:
                    impulse = dot * 0.9
                    a.vx -= impulse * nx
                    a.vy -= impulse * ny
                    b.vx += impulse * nx
                    b.vy += impulse * ny

                # merge
                if a.level == b.level and not a.merged and not b.merged and a.level < 10:
                    new_x = (a.x + b.x) / 2
                    new_y = (a.y + b.y) / 2
                    balls.append(Ball(new_x, new_y, a.level + 1))
                    a.merged = True
                    b.merged = True
                    score += 10 * 2 ** (a.level + 1)

    balls[:] = [b for b in balls if not b.merged]

def draw_score():
    score_text = font.render(f"Score: {score}", True, (30, 30, 30))
    screen.blit(score_text, (20, 20))

def draw_game_over_line():
    pygame.draw.line(screen, (255, 0, 0), (0, LINE_Y), (WIDTH, LINE_Y), 4)

def draw_preview(ball):
    if ball:
        pygame.draw.circle(screen, ball.color, (900, 100), int(ball.radius // 2))
        label = font.render("Next", True, (0, 0, 0))
        screen.blit(label, (865, 100))

def draw_hold(ball):
    if ball:
        pygame.draw.circle(screen, ball.color, (100, 150), int(ball.radius // 2))
    label = font.render("Hold", True, (0, 0, 0))
    screen.blit(label, (60, 100))

def make_random_ball():
    level = random.randint(0, 2)
    return Ball(WIDTH // 2, LINE_Y - 40, level)

def game_over():
    label = font.render("GAME OVER", True, (200, 0, 0))
    screen.blit(label, (WIDTH // 2 - 120, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2500)
    pygame.quit()
    sys.exit()

# game state
balls = []
current = None
next_ball = make_random_ball()
hold_ball = None
hold_used = False
score = 0
overline_timer = 0

# main loop
running = True
while running:
    screen.fill((240, 240, 255))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current:
                balls.append(current)
                current = next_ball
                next_ball = make_random_ball()
                hold_used = False
            elif event.key == pygame.K_c and current and not hold_used:
                if hold_ball is None:
                    hold_ball = current
                    current = next_ball
                    next_ball = make_random_ball()
                else:
                    hold_ball, current = current, hold_ball
                hold_used = True

        elif event.type == pygame.MOUSEBUTTONDOWN and current:
            balls.append(current)
            current = next_ball
            next_ball = make_random_ball()
            hold_used = False

    if current is None:
        current = next_ball
        next_ball = make_random_ball()

    # control
    if current:
        if keys[pygame.K_LEFT]:
            current.x -= 8
        if keys[pygame.K_RIGHT]:
            current.x += 8
        current.x = max(current.radius, min(WIDTH - current.radius, current.x))
        current.draw(screen)

    for b in balls:
        b.update()
        b.draw(screen)

    # overline check
    over_threshold = any(b.y - b.radius < LINE_Y for b in balls)
    if over_threshold:
        overline_timer += 1
    else:
        overline_timer = 0
    if overline_timer > OVERLINE_TIME_LIMIT:
        draw_game_over_line()
        draw_score()
        pygame.display.flip()
        pygame.time.wait(100)
        game_over()

    check_collisions(balls)

    # draw UI
    draw_score()
    draw_game_over_line()
    draw_preview(next_ball)
    draw_hold(hold_ball)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
