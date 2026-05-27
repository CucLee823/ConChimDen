import asyncio
import pygame
import random
pygame.init()

p=0.5
bird_y=0
obs_speed=3
MAX_SPEED=10
score=0
game_play=True
h_score=0
game_font=pygame.font.Font("assets/04B_19.TTF",40)
font_big=pygame.font.Font("assets/04B_19.TTF",40)
font_mid=pygame.font.Font("assets/04B_19.TTF",32)

# state: "menu" | "play" | "dead"
state = "menu"

def score_view():
    if state == "play":
        score_f=game_font.render(f"Score: {str(int(score))}",True,(0,0,0))
        screen.blit(score_f, score_f.get_rect(center=(200,30)))
    else:
        score_f = game_font.render(f"Score:{str(int(score))}", True, (0, 0, 0))
        screen.blit(score_f, score_f.get_rect(center=(200, 30)))
        h_score_f = game_font.render(f"High Score:{str(int(h_score))}", True, (255, 0, 0))
        screen.blit(h_score_f, h_score_f.get_rect(center=(200, 70)))

pygame.display.set_caption("Con chim den")

icon = pygame.image.load("assets/yellowbird-downflap.png")
bg = pygame.image.load("assets/background-night.png")
fl_orig = pygame.image.load("assets/floor.png")
FL_W = fl_orig.get_width()
FL_Y = 570
bg=pygame.transform.scale2x(bg)
pygame.display.set_icon(icon)
fl_x=0

screen=pygame.display.set_mode((400,670))
clock=pygame.time.Clock()

bird1 = pygame.image.load("assets/yellowbird-downflap.png")
bird1=pygame.transform.scale2x(bird1)
bird_hcn=bird1.get_rect(center=(100,350))

bird_over = pygame.transform.scale(pygame.image.load("assets/yellowbird-midflap.png"), (60,50))

load_img = pygame.image.load("assets/load.png")
load_img = pygame.transform.scale(load_img, (100,100))
load_rect = load_img.get_rect(center=(200, 500))

ready_img = pygame.image.load("assets/ready.png")
ready_img = pygame.transform.scale(ready_img, (180, 160))
ready_rect = ready_img.get_rect(center=(200, 420))

pipe_img = pygame.image.load("assets/pipe-green.png")
pipe_img = pygame.transform.scale(pipe_img, (70, 400))
pipe_flip = pygame.transform.flip(pipe_img, False, True)

rong_img = pygame.image.load("assets/rong.png")
rong_img = pygame.transform.scale(rong_img, (120, 150))

sutu_img = pygame.image.load("assets/sutu.png")
sutu_img = pygame.transform.scale(sutu_img, (150, 120))

da_img = pygame.image.load("assets/da.png")
da_img = pygame.transform.scale(da_img, (70, 60))

PIPE_GAP = 180
PIPE_INTERVAL = 180
OBS_INTERVAL = 100
ROCK_INTERVAL = 200

pipes = []
obstacles = []
rocks = []
pipe_timer = 0
obs_timer = 0
rock_timer = 0

def draw_floor():
    x = fl_x % FL_W - FL_W
    while x < 400:
        screen.blit(fl_orig, (x, FL_Y))
        x += FL_W

def draw_menu():
    # Ten game
    t1 = font_big.render("  CHOI CHIM DEEE", True, (200, 80, 0))
    screen.blit(t1, t1.get_rect(center=(200, 180)))
    # Con chim
    screen.blit(bird_over, bird_over.get_rect(center=(200, 300)))
    # Nut Ready
    screen.blit(ready_img, ready_rect)

def draw_gameover():
    overlay = pygame.Surface((400, 670), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    t1 = font_big.render("CON CHIM DEN", True, (200, 80, 0))
    screen.blit(t1, t1.get_rect(center=(200, 180)))
    t2 = font_mid.render("STUPIP", True, (220, 30, 30))
    screen.blit(t2, t2.get_rect(center=(200, 260)))
    t3 = font_mid.render("CHOI LAI DE !", True, (50, 200, 50))
    screen.blit(t3, t3.get_rect(center=(200, 320)))
    screen.blit(bird_over, bird_over.get_rect(center=(200, 400)))
    screen.blit(load_img, load_rect)

def spawn_pipe():
    gap_y = random.randint(200, 430)
    pipes.append({"x": 420, "gap_y": gap_y, "scored": False})

def spawn_obstacle():
    kind = random.choice(["rong", "sutu"])
    img = rong_img if kind == "rong" else sutu_img
    y = FL_Y - img.get_height()
    obstacles.append({"x": 420, "y": y, "img": img, "scored": False})

def spawn_rock():
    x = random.randint(50, 350)
    rocks.append({"x": x, "y": -60, "vy": 5})

def draw_pipes():
    for pipe in pipes:
        top_rect = pipe_flip.get_rect(bottomleft=(pipe["x"], pipe["gap_y"] - PIPE_GAP // 2))
        bot_rect = pipe_img.get_rect(topleft=(pipe["x"], pipe["gap_y"] + PIPE_GAP // 2))
        screen.blit(pipe_flip, top_rect)
        screen.blit(pipe_img, bot_rect)

def draw_obstacles():
    for obs in obstacles:
        screen.blit(obs["img"], (obs["x"], obs["y"]))

def draw_rocks():
    for rock in rocks:
        screen.blit(da_img, (rock["x"], rock["y"]))

def check_pipe_collision():
    for pipe in pipes:
        top_rect = pipe_flip.get_rect(bottomleft=(pipe["x"], pipe["gap_y"] - PIPE_GAP // 2))
        bot_rect = pipe_img.get_rect(topleft=(pipe["x"], pipe["gap_y"] + PIPE_GAP // 2))
        if bird_hcn.colliderect(top_rect) or bird_hcn.colliderect(bot_rect):
            return True
    return False

def check_obs_collision():
    for obs in obstacles:
        if bird_hcn.colliderect(obs["img"].get_rect(topleft=(obs["x"], obs["y"]))):
            return True
    return False

def check_rock_collision():
    for rock in rocks:
        if bird_hcn.colliderect(da_img.get_rect(topleft=(rock["x"], rock["y"]))):
            return True
    return False

def reset_game():
    global bird_y, obs_speed, score, state, fl_x, bird_hcn
    global pipes, pipe_timer, obstacles, obs_timer, rocks, rock_timer
    bird_y = 0
    obs_speed = 3
    score = 0
    state = "play"
    fl_x = 0
    bird_hcn.center = (100, 350)
    pipes = []
    obstacles = []
    rocks = []
    pipe_timer = 0
    obs_timer = 0
    rock_timer = 0

def check_vc():
    if bird_hcn.bottom >= FL_Y or bird_hcn.top <= 0:
        return False
    if check_pipe_collision(): return False
    if check_obs_collision():  return False
    if check_rock_collision(): return False
    return True

async def main():
    global bird_y, obs_speed, score, state, h_score, fl_x, bird_hcn
    global pipes, pipe_timer, obstacles, obs_timer, rocks, rock_timer

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    reset_game()
                elif state == "play":
                    bird_y = -10
                    obs_speed = min(obs_speed + 0.5, MAX_SPEED)
                elif state == "dead":
                    reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    if ready_rect.collidepoint(event.pos):
                        reset_game()
                elif state == "play":
                    bird_y = -10
                    obs_speed = min(obs_speed + 0.5, MAX_SPEED)
                elif state == "dead":
                    reset_game()

        screen.blit(bg, (0, 0))

        if state == "play":
            obs_speed = max(obs_speed - 0.01, 2)

            pipe_timer += 1
            if pipe_timer >= PIPE_INTERVAL:
                spawn_pipe()
                pipe_timer = 0
            for pipe in pipes:
                pipe["x"] -= int(obs_speed)
                if not pipe["scored"] and pipe["x"] + 70 < bird_hcn.left:
                    pipe["scored"] = True
                    score += 1
            pipes[:] = [p for p in pipes if p["x"] > -80]

            obs_timer += 1
            if obs_timer >= OBS_INTERVAL:
                spawn_obstacle()
                obs_timer = 0
            for obs in obstacles:
                obs["x"] -= int(obs_speed)
                if not obs["scored"] and obs["x"] + obs["img"].get_width() < bird_hcn.left:
                    obs["scored"] = True
                    score += 1
            obstacles[:] = [o for o in obstacles if o["x"] > -160]

            rock_timer += 1
            if rock_timer >= ROCK_INTERVAL:
                spawn_rock()
                rock_timer = random.randint(-60, 0)
            for rock in rocks:
                rock["y"] += rock["vy"]
            rocks[:] = [r for r in rocks if r["y"] < 560]

            fl_x -= int(obs_speed)

        draw_pipes()
        draw_obstacles()
        draw_rocks()
        draw_floor()

        if state == "menu":
            draw_menu()
        elif state == "play":
            screen.blit(bird1, bird_hcn)
            bird_y += p
            bird_hcn.centery += int(bird_y)
            if score > h_score:
                h_score = score
            score_view()
            if not check_vc():
                state = "dead"
        elif state == "dead":
            draw_gameover()
            score_view()

        pygame.display.update()
        await asyncio.sleep(0)

asyncio.run(main())
