import pygame
import sys
import random
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# --------------------------
# AUDIO GENERATION
# --------------------------
def generate_beep(freq=600, duration=0.12, volume=0.4):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(freq * t * 2 * np.pi)
    audio = (wave * 32767 * volume).astype(np.int16)
    return pygame.mixer.Sound(buffer=audio)

eat_sound = generate_beep(800, 0.08, 0.5)
gameover_sound = generate_beep(200, 0.4, 0.6)
sound_enabled = True

# --------------------------
# GAME SETTINGS
# --------------------------
WIDTH, HEIGHT = 640, 480
CELL = 20
COLUMNS = WIDTH // CELL
ROWS = HEIGHT // CELL

BG = (20, 20, 20)
GRID = (40, 40, 40)
WHITE = (255, 255, 255)
FOOD = (255, 60, 60)

# --------------------------
# SKINS
# --------------------------
SKINS = {
    1: (0, 255, 0),      # Green
    2: (255, 0, 0),      # Red
    3: (0, 100, 255),    # Blue
    4: "rainbow",        # Rainbow
    5: (255, 215, 0)     # GOLD
}
current_skin = 4  # Rainbow default

# --------------------------
# LEVEL SETTINGS
# --------------------------
LEVELS = {
    1: [],  # no walls
    2: [(i,0) for i in range(COLUMNS)] + [(i,ROWS-1) for i in range(COLUMNS)] +
       [(0,i) for i in range(ROWS)] + [(COLUMNS-1,i) for i in range(ROWS)],
    3: [(i,5) for i in range(5, COLUMNS-5)] + [(i,ROWS-6) for i in range(5, COLUMNS-5)]
}
current_level = 1

# --------------------------
# PYGAME SETUP
# --------------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Deluxe")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 28)

# --------------------------
# GAME FUNCTIONS
# --------------------------
def reset_game():
    snake = [(10,10),(9,10),(8,10)]
    direction = (1,0)
    score = 0
    food = place_food(snake)
    return snake, direction, score, food

def place_food(snake):
    while True:
        x = random.randint(0,COLUMNS-1)
        y = random.randint(0,ROWS-1)
        if (x,y) not in snake and (x,y) not in LEVELS[current_level]:
            return (x,y)

def draw_text(text, y, size=28):
    fnt = pygame.font.SysFont("Arial", size)
    surf = fnt.render(text, True, WHITE)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def draw_snake(snake):
    for i, (x, y) in enumerate(snake):
        if current_skin == 4:  # Rainbow skin
            color = ((i*40)%256, (i*80)%256, (i*120)%256)
        else:
            color = SKINS.get(current_skin, (0,255,0))  # default green
        pygame.draw.rect(screen, color, (x*CELL, y*CELL, CELL, CELL))


def draw_grid():
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0,y), (WIDTH,y))

def draw_walls():
    for wall in LEVELS[current_level]:
        pygame.draw.rect(screen, (150,75,0), (wall[0]*CELL, wall[1]*CELL, CELL, CELL))

# --------------------------
# BUTTON CLASS
# --------------------------
class Button:
    def __init__(self, text, x, y, w, h, color, hover_color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        txt = FONT.render(self.text, True, WHITE)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)
        if click and self.rect.collidepoint(mouse_pos):
            pygame.time.delay(150)  # debounce click
            self.action()

# --------------------------
# GAME VARIABLES
# --------------------------
snake, direction, score, food = reset_game()
speed = 10
current_state = "menu"

# --------------------------
# BUTTON ACTIONS
# --------------------------
def start_game():
    global current_state
    current_state = "game"

def open_settings():
    global current_state
    current_state = "settings"

def exit_game():
    pygame.quit()
    sys.exit()

# --------------------------
# BUTTONS
# --------------------------
buttons_menu = [
    Button("Start Game", 220, 200, 200, 50, (50,150,50), (100,200,100), start_game),
    Button("Settings", 220, 270, 200, 50, (50,50,150), (100,100,200), open_settings),
    Button("Exit", 220, 340, 200, 50, (150,50,50), (200,100,100), exit_game)
]

buttons_settings = [
    Button("Sound ON/OFF (S)", 180, 180, 280, 50, (100,100,100), (150,150,150), lambda: toggle_sound()),
    Button("Skin 1-Green", 180, 240, 130, 50, (0,255,0), (50,255,50), lambda: set_skin(1)),
    Button("Skin 2-Red", 330, 240, 130, 50, (255,0,0), (255,50,50), lambda: set_skin(2)),
    Button("Skin 3-Blue", 180, 300, 130, 50, (0,100,255), (50,150,255), lambda: set_skin(3)),
    Button("Skin 4-Rainbow", 330, 300, 130, 50, (200,200,200), (255,255,255), lambda: set_skin(4)),
    Button("Skin 5-Gold", 180, 360, 280, 50, (255,215,0), (255,240,50), lambda: set_skin(5)),
    Button("Back", 220, 420, 200, 50, (100,100,100), (150,150,150), lambda: back_to_menu()),
]

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled

def set_skin(n):
    global current_skin
    current_skin = n

def back_to_menu():
    global current_state
    current_state = "menu"

# --------------------------
# MAIN LOOP
# --------------------------
while True:
    screen.fill(BG)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.KEYDOWN:
            if current_state=="game":
                if event.key==pygame.K_UP and direction!=(0,1): direction=(0,-1)
                if event.key==pygame.K_DOWN and direction!=(0,-1): direction=(0,1)
                if event.key==pygame.K_LEFT and direction!=(1,0): direction=(-1,0)
                if event.key==pygame.K_RIGHT and direction!=(-1,0): direction=(1,0)
                if event.key==pygame.K_r: snake,direction,score,food=reset_game()
                if event.key==pygame.K_m: current_state="menu"
            if current_state=="settings" and event.key==pygame.K_s: toggle_sound()

    # --------------------------
    # MENU STATE
    # --------------------------
    if current_state=="menu":
        draw_text("SNAKE DELUXE",120,50)
        for btn in buttons_menu: btn.draw(screen)
        pygame.display.update()
        continue

    # --------------------------
    # SETTINGS STATE
    # --------------------------
    if current_state=="settings":
        draw_text("SETTINGS",100,40)
        for btn in buttons_settings: btn.draw(screen)
        pygame.display.update()
        continue

    # --------------------------
    # GAME STATE
    # --------------------------
    if current_state=="game":
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x+dx, head_y+dy)

        if new_head in snake or new_head in LEVELS[current_level] or not (0<=new_head[0]<COLUMNS and 0<=new_head[1]<ROWS):
            if sound_enabled: gameover_sound.play()
            current_state="gameover"
        else:
            snake.insert(0,new_head)
            if new_head==food:
                score+=1
                if sound_enabled: eat_sound.play()
                food=place_food(snake)
            else: snake.pop()

        draw_grid()
        draw_walls()
        draw_snake(snake)
        pygame.draw.ellipse(screen, FOOD, (food[0]*CELL, food[1]*CELL, CELL, CELL))
        sc = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(sc,(10,10))
        pygame.display.update()
        clock.tick(speed)

    # --------------------------
    # GAME OVER STATE
    # --------------------------
    if current_state=="gameover":
        draw_text("GAME OVER!",150,50)
        draw_text(f"Score: {score}",200,28)
        draw_text("Press R to Restart | M for Menu",250,28)
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            snake,direction,score,food=reset_game()
            current_state="game"
        if keys[pygame.K_m]:
            current_state="menu"
