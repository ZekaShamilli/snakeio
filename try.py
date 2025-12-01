import pygame
import random
import math
import sys

# ---------- Başlat ----------
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Dash — Ultimate 🚀")
clock = pygame.time.Clock()

font_size = max(24, WIDTH // 50)
font = pygame.font.SysFont(None, font_size)
big_font = pygame.font.SysFont(None, font_size*2)

FPS = 60
PLAYER_SPEED = 6
ASTEROID_MIN_SPEED = 2
ASTEROID_MAX_SPEED = 5
ASTEROID_SPAWN_TIME = 800
COLLECTIBLE_SPAWN_TIME = 3000
DIFFICULTY_INCREASE_EVERY = 10
BULLET_SPEED = 10
SLOWDOWN_FACTOR = 0.5  # yavaşlatma modu
SLOWDOWN_COOLDOWN = 3000  # ms

# ---------- Yardımcı Fonksiyonlar ----------
def draw_text(surf, text, size, x, y, center=True):
    f = big_font if size >= 60 else font
    img = f.render(text, True, (255, 255, 255))
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(img, rect)

def clamp(n, a, b):
    return max(a, min(b, n))

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

# ---------- Oyun Nesneleri ----------
class Player:
    def __init__(self):
        self.w = 40
        self.h = 50
        self.x = WIDTH // 2
        self.y = HEIGHT - self.h - 20
        self.speed = PLAYER_SPEED
        self.color = (50, 200, 255)
        self.alive = True
        self.blink = 0
        self.bullets = []
        self.multi_shot = True

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        self.x = clamp(self.x, self.w//2, WIDTH - self.w//2)
        if self.blink > 0:
            self.blink -= 1

    def draw(self, surf):
        points = [
            (self.x, self.y - self.h//2),
            (self.x - self.w//2, self.y + self.h//2),
            (self.x + self.w//2, self.y + self.h//2),
        ]
        if self.blink % 10 < 5:
            pygame.draw.polygon(surf, self.color, points)
            pygame.draw.polygon(surf, (255, 180, 0), [(self.x - 8, self.y + self.h//2),
                                                      (self.x, self.y + self.h//2 + random.randint(6,12)),
                                                      (self.x + 8, self.y + self.h//2)])

    def shoot(self):
        if self.multi_shot:
            offsets = [-15, 0, 15]
            for o in offsets:
                self.bullets.append(Bullet(self.x + o, self.y - self.h//2))
        else:
            self.bullets.append(Bullet(self.x, self.y - self.h//2))

    def get_pos(self):
        return (self.x, self.y)

class Bullet:
    def __init__(self, x, y, speed=BULLET_SPEED):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (255, 255, 0)
        self.speed = speed

    def update(self):
        self.y -= self.speed

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return self.y < -10

    def pos(self):
        return (self.x, self.y)

class Asteroid:
    def __init__(self, x=None, speed=None, size=None):
        self.size = size if size else random.randint(25, 50)
        self.x = x if x is not None else random.randint(self.size, WIDTH - self.size)
        self.y = -self.size - random.randint(0, 100)
        self.speed = speed if speed is not None else random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        self.color = (180, 180, 180)
        self.spin = random.uniform(-3, 3)
        self.angle = random.uniform(0, 360)
        self.hp = max(1, self.size // 15)

    def update(self, slowdown=False):
        factor = SLOWDOWN_FACTOR if slowdown else 1
        self.y += self.speed * factor
        self.angle = (self.angle + self.spin) % 360

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, (120,120,120), (int(self.x - self.size//3), int(self.y - self.size//4)), max(4, self.size//6))

    def off_screen(self):
        return self.y - self.size > HEIGHT + 50

    def pos(self):
        return (self.x, self.y)

class Collectible:
    def __init__(self):
        self.size = 14
        self.x = random.randint(self.size, WIDTH - self.size)
        self.y = -self.size - random.randint(0, 200)
        self.speed = 2.5
        self.color = (255, 100, 140)

    def update(self, slowdown=False):
        factor = SLOWDOWN_FACTOR if slowdown else 1
        self.y += self.speed * factor

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        s = self.size
        pygame.draw.circle(surf, self.color, (cx - s//2, cy - s//3), s//2)
        pygame.draw.circle(surf, self.color, (cx + s//2, cy - s//3), s//2)
        pygame.draw.polygon(surf, self.color, [(cx - s, cy), (cx + s, cy), (cx, cy + s)])

    def off_screen(self):
        return self.y - self.size > HEIGHT + 50

    def pos(self):
        return (self.x, self.y)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = random.randint(20, 35)
        self.color = (255, random.randint(100, 200), 0)
        self.alive = True

    def update(self):
        self.radius += 4
        if self.radius >= self.max_radius:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius, 2)

# ---------- Oyun Döngüsü Değişkenleri ----------
player = Player()
asteroids = []
collectibles = []
explosions = []

score = 0
best = 0
running = True
game_active = False
last_asteroid_spawn = pygame.time.get_ticks()
last_collectible_spawn = pygame.time.get_ticks()
difficulty_level = 0
slowdown_timer = 0

# ---------- Ana Döngü ----------
while running:
    dt = clock.tick(FPS)
    now = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and game_active:
                for a in asteroids:
                 explosions.append(Explosion(a.x, a.y))
                 score += 10  # asteroid patlatınca puan ekle
                asteroids.clear()

            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and not game_active:
                player = Player()
                asteroids = []
                collectibles = []
                explosions = []
                score = 0
                game_active = True
                last_asteroid_spawn = now
                last_collectible_spawn = now
                difficulty_level = 0
                slowdown_timer = 0
            if (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT) and player.alive:
                player.shoot()

    screen.fill((10, 10, 30))
    # yıldız efekti
    for i in range(40):
        x = (i * 53 + now//10) % WIDTH
        y = (i * 97 + now//15) % HEIGHT
        s = (i % 3) + 1
        pygame.draw.circle(screen, (200,200,230), (x, y), s)

    if game_active and player.alive:
        player.update(keys)

        # asteroid spawn
        if now - last_asteroid_spawn > ASTEROID_SPAWN_TIME:
            
            max_spawn = 5  # ekranda bir anda çok fazla asteroid olmasın
            spawn_count = min(1 + difficulty_level//2, max_spawn)
            for _ in range(spawn_count):
                speed = random.uniform(ASTEROID_MIN_SPEED + difficulty_level*0.4,
                                       ASTEROID_MAX_SPEED + difficulty_level*0.6)
                size = random.randint(max(20 - difficulty_level, 15), min(70, 45 + difficulty_level))
                asteroids.append(Asteroid(speed=speed, size=size))
            last_asteroid_spawn = now

        # collectible spawn
        if now - last_collectible_spawn > COLLECTIBLE_SPAWN_TIME:
            collectibles.append(Collectible())
            last_collectible_spawn = now

        # slowdown modu
        slowdown = keys[pygame.K_s] and now - slowdown_timer > SLOWDOWN_COOLDOWN
        if slowdown:
            slowdown_timer = now

        # asteroids update/draw
        for a in asteroids:
            a.update(slowdown)
            a.draw(screen)

        # collectibles update/draw
        for c in collectibles:
            c.update(slowdown)
            c.draw(screen)

        # bullets update/draw
        for b in player.bullets[:]:
            b.update()
            b.draw(screen)
            if b.off_screen():
                player.bullets.remove(b)
            else:
                for a in asteroids[:]:
                    if dist(b.pos(), a.pos()) < a.size:
                        a.hp -= 1
                        if a.hp <= 0:
                            score += 10
                            explosions.append(Explosion(a.x, a.y))
                            asteroids.remove(a)
                        if b in player.bullets:
                            player.bullets.remove(b)
                        break

        player.draw(screen)

        # asteroid-player çarpışma
        for a in asteroids[:]:
            if dist(player.get_pos(), a.pos()) < (a.size + max(player.w, player.h)/2 - 6):
                if player.blink <= 0:
                    player.alive = False

        # collectible toplama
        for c in collectibles[:]:
            if dist(player.get_pos(), c.pos()) < (c.size + max(player.w, player.h)/2 - 8):
                score += 5
                collectibles.remove(c)

        # temizleme
        asteroids = [a for a in asteroids if not a.off_screen()]
        collectibles = [c for c in collectibles if not c.off_screen()]
        explosions = [e for e in explosions if e.alive]
        for e in explosions:
            e.update()
            e.draw(screen)

        # zamanla puan
        score += 0.01 * (dt/16)
        DIFFICULTY_STEP = 100  # skor aralığı
        new_level = int(score) // DIFFICULTY_STEP
        if new_level > difficulty_level:
          difficulty_level = new_level
        # asteroid spawn süresini çok az azalt
          ASTEROID_SPAWN_TIME = max(250, ASTEROID_SPAWN_TIME - 10)


        padding = font_size
        draw_text(screen, f"Score: {int(score)}", font_size, padding, padding, center=False)
        draw_text(screen, f"Best: {int(best)}", font_size, WIDTH - padding - 200, padding, center=False)

    else:
        if player.alive:
            draw_text(screen, "SPACE ROCK", font_size*3, WIDTH//2, HEIGHT//3)
            draw_text(screen, "A/D debermey ucun", font_size, WIDTH//2, HEIGHT//2 - 10)
         #  draw_text(screen, "Shift ile çoklu mermi at!", font_size, WIDTH//2, HEIGHT//2 + 30)
         #   draw_text(screen, "S tuşu: yavaşlatma modu", font_size, WIDTH//2, HEIGHT//2 + 60)
            draw_text(screen, "LALEE SPACE BASANDA OYUN BASDIR", font_size*1.5, WIDTH//2, HEIGHT - 120)
            draw_text(screen, f"En yaxsu: {int(best)}", font_size, WIDTH - 200, 20, center=False)
        else:
            if score > best:
                best = int(score)
            draw_text(screen, "OYUN KUTARDU LALEEEE", font_size*3, WIDTH//2, HEIGHT//3)
            draw_text(screen, f"Score: {int(score)}", font_size*2, WIDTH//2, HEIGHT//2 - 10)
            draw_text(screen, f"Best: {int(best)}", font_size*2, WIDTH//2, HEIGHT//2 + 40)
            draw_text(screen, "Spacenen tekrar basda, ESC nen cix", font_size, WIDTH//2, HEIGHT - 120)
            for i in range(6):
                ax = WIDTH//2 + math.cos(i*1.2 + now/500) * (80 + i*8)
                ay = HEIGHT//2 + math.sin(i*1.3 + now/500) * (40 + i*5)
                pygame.draw.circle(screen, (180, 120, 120), (int(ax), int(ay)), 8 + i)

    pygame.display.flip()

pygame.quit()
sys.exit()
