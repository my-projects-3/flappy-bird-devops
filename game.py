import pygame
from pygame.locals import *
import random
import requests
import threading
import math

pygame.init()

# bg music
pygame.mixer.init()
pygame.mixer.music.load('sound/bg_music.mp3')  # or 'bg_music.ogg'
pygame.mixer.music.play(-1)  # -1 means loop forever
pygame.mixer.music.set_volume(0.1)  # optional: adjust volume (0.0 to 1.0)

flap_sound = pygame.mixer.Sound('sound/flap.wav')  # or 'sounds/flap.wav'
flap_sound.set_volume(0.3)  # optional: adjust volume

clock = pygame.time.Clock()
fps = 60

screen_width = 764
screen_height = 636

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# submit score, dev2
def submit_score(score, name="Unknown"):
    url = "http://localhost:8000/score"  # Your backend URL
    data = {"name": name, "score": score}
    try:
        response = requests.post(url, json=data)
        print("Score submitted:", response.status_code, response.text)
    except Exception as e:
        print("Failed to submit score:", e)

# define colours
white = (255, 255, 255)

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
show_menu = True  # New flag to control menu display

# load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
start_img = pygame.image.load('img/start.png')
quit_img = pygame.image.load('img/quit.png')
menu_img = pygame.image.load('img/menu.png')

class FloatingBird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('img/bird1.png')  # You can animate this later
        self.rect = self.image.get_rect(center=(x, y))
        self.start_y = y
        self.counter = 0

    def update(self):
        self.counter += 1
        self.rect.y = self.start_y + int(5 * math.sin(self.counter * 0.05))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
    
def fade_out(duration=2000):  # Duration in milliseconds
    overlay = pygame.Surface((screen_width, screen_height))  # Create a surface the size of the screen
    overlay.fill((0, 0, 0))  # Fill the surface with black
    fade_speed = 5  # The step size in which we increase the alpha value
    
    for alpha in range(0, 255, fade_speed):
        overlay.set_alpha(alpha)
        screen.blit(bg, (0, 0))  # Redraw background
        screen.blit(overlay, (0, 0))  # Overlay with increasing alpha
        pygame.display.update()
        pygame.time.delay(duration // 255)  # Delay for smoother fade-out effect, adjust based on duration

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flappy.vel = 0  # Reset velocity too
    return 0  # Return 0 for score

# Get Player Name Function
def get_player_name():
    input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 30, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    input_font = pygame.font.SysFont('Bauhaus 93', 30)  # Smaller font for input
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        # Draw background
        screen.blit(bg, (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))

        # Render the "Enter your name" label
        label_font = pygame.font.SysFont('Bauhaus 93', 40)
        label = label_font.render('Enter your name:', True, white)
        screen.blit(label, (screen_width // 2 - label.get_width() // 2, screen_height // 2 - 100))

        # Render the input box background
        pygame.draw.rect(screen, pygame.Color('black'), input_box)

        # Render the input box text
        txt_surface = input_font.render(text, True, white)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Change color of input box when active
        pygame.draw.rect(screen, color, input_box, 3)  # 3px border

        # Add a hint/instruction
        hint_font = pygame.font.SysFont('Arial', 20)
        hint = hint_font.render('Press Enter when done', True, white)
        screen.blit(hint, (screen_width // 2 - hint.get_width() // 2, input_box.bottom + 20))

        pygame.display.flip()
        clock.tick(30)

    return text if text != '' else "Unknown"



def main_menu():
    play_button = Button(screen_width // 2 - 100 + 60, screen_height // 2 - 100, start_img)
    quit_button = Button(screen_width // 2 - 100 + 60, screen_height // 2 + 20, quit_img)
    menu_pipes = pygame.sprite.Group()
    pipe_spawn_timer = pygame.time.get_ticks() - 2000  # start early
    
    # # Create a floating bird for the menu
    # menu_bird = FloatingBird(100, int(screen_height / 2))
    # menu_bird_group = pygame.sprite.Group()
    # menu_bird_group.add(menu_bird)
    
    # Local ground scroll for menu animation
    local_ground_scroll = 0

    running = True
    while running:
        # Draw background
        screen.blit(bg, (0, 0))

        

        # Update ground scroll for menu animation
        local_ground_scroll -= scroll_speed
        if abs(local_ground_scroll) > 35:
            local_ground_scroll = 0
            
        # Draw ground
        screen.blit(ground_img, (local_ground_scroll, screen_height - 100))
        
        # Update and draw pipes
        menu_pipes.update()
        menu_pipes.draw(screen)
        
        # Update and draw the floating bird
        # menu_bird_group.update()
        # menu_bird_group.draw(screen)

        # Title
        draw_text("Flappy Bird", font, white, screen_width // 2 - 160 + 45, 100)

        # Buttons
        if play_button.draw():
            print("[DEBUG] Play button pressed, starting game")
            menu_pipes.empty()
            return "play"
    

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[DEBUG] Quit event in main menu")
                return "quit"

        pygame.display.update()
        clock.tick(60)

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying == True:
            # gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < screen_height - 100:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
                flap_sound.play()
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False  # Track click state to prevent multiple actions

    def draw(self):
        action = False
        
        # Reset clicked state if mouse button is released
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# Initialize game objects
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create button instances
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)
menu_button = Button(screen_width // 2 - 50, screen_height // 2 + 20, menu_img)
score_submitted = False

# Get the player name before starting the game
player_name = get_player_name()

# Main game loop
run = True
show_menu = True

while run:
    if show_menu:
        # Show main menu
        menu_choice = main_menu()
        if menu_choice == "play":
            # Reset game state for a new game
            show_menu = False
            game_over = False
            flying = False
            score = 0
            score_submitted = False
            reset_game()
            last_pipe = pygame.time.get_ticks() - pipe_frequency
        elif menu_choice == "quit":
            run = False
    else:
        # Game play
        clock.tick(fps)

        # Draw background
        screen.blit(bg, (0, 0))

        # Draw bird and pipes
        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)

        # Draw the ground
        screen.blit(ground_img, (ground_scroll, screen_height - 100))

        # Check the score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False

        # Display score
        draw_text(str(score), font, white, int(screen_width / 2), 20)

        # Check for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True

        # Check if bird has hit the ground
        if flappy.rect.bottom >= screen_height - 100:
            game_over = True
            flying = False

        # Game logic when playing
        if game_over == False and flying == True:
            # Generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            # Draw and scroll the ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            pipe_group.update()

        # Check for game over and handle restart/menu buttons
        if game_over:
            if not score_submitted:
                threading.Thread(target=submit_score, args=(score, player_name), daemon=True).start()
                score_submitted = True

            if button.draw():  # Restart button
                print("[DEBUG] Restart button pressed")
                fade_out()
                game_over = False
                score = reset_game()
                score_submitted = False

            if menu_button.draw():  # When the menu button is pressed in game over
                # Reset game state and return to menu
                print("[DEBUG] Menu button pressed, should return to main menu")
                fade_out()
                show_menu = True  
                game_over = False
                flying = False
                score_submitted = False
                pipe_group.empty()
                reset_game()
                pygame.event.clear()  # Clear any leftover events
                print("[DEBUG] Event queue cleared; now in main menu state")

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
                flying = True

        pygame.display.update()

pygame.quit()