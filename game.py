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

# Enable hardware acceleration and double buffering
screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption('Flappy Bird')

# define font
font = pygame.font.SysFont('Bauhaus 93', 60)

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

# Define medal size
medal_size = (50, 50)  # Taille des médailles

# Optimize image loading with caching and pre-scaling
image_cache = {}
def load_image(path, scale=None):
    if path not in image_cache:
        image = pygame.image.load(path)
        if scale:
            image = pygame.transform.smoothscale(image, scale)
        image_cache[path] = image.convert_alpha()
    return image_cache[path]

# Pre-scale images for better performance
bg = load_image('img/bg.png')
ground_img = load_image('img/ground.png')
button_img = load_image('img/restart.png')
start_img = load_image('img/start.png')
quit_img = load_image('img/quit.png')
menu_img = load_image('img/HOME.png')
sound_on_img = load_image('img/soundon.png')
sound_off_img = load_image('img/soundoff.png')
gold_medal = load_image('img/medailles/or.png', (50, 50))
silver_medal = load_image('img/medailles/argent.png', (50, 50))
bronze_medal = load_image('img/medailles/bronz.png', (50, 50))

# Create optimized surfaces with pre-rendered content
background = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
background.blit(bg, (0, 0))

ground_surface = pygame.Surface((screen_width * 2, 100), pygame.SRCALPHA)
ground_surface.blit(ground_img, (0, 0))
ground_surface.blit(ground_img, (screen_width, 0))

# Pre-render score text surface
score_surface = pygame.Surface((100, 50), pygame.SRCALPHA)
score_rect = score_surface.get_rect(center=(screen_width // 2, 20))

# Optimize sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# submit score, dev2
score_submitted = False

def submit_score(score, name="Unknown"):
    url = "http://localhost:8000/score"
    data = {"name": name, "score": score}
    try:
        requests.post(url, json=data)
    except:
        pass

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

def get_top_scores():
    try:
        response = requests.get("http://localhost:8000/leaderboard", timeout=1)  # Ajout d'un timeout
        if response.status_code == 200:
            return response.json()[:3]
    except:
        return []  # Retourne une liste vide en cas d'erreur
    return []

def main_menu():
    # Position des boutons ajustée et séparée
    button_spacing = 20  # Espacement horizontal entre les boutons
    
    # Calculer la position Y pour les boutons (sous le tableau des scores)
    score_panel_bottom = 150 + 280 + 20  # score_y + score_height + marge
    
    # Calculer les positions X pour centrer les trois boutons avec l'espacement
    total_width = start_img.get_width() + button_spacing + quit_img.get_width() + button_spacing + sound_on_img.get_width()
    start_x = screen_width // 2 - total_width // 2
    quit_x = start_x + start_img.get_width() + button_spacing
    sound_x = quit_x + quit_img.get_width() + button_spacing
    
    # Créer les boutons avec les nouvelles positions
    play_button = Button(start_x, score_panel_bottom, start_img)
    quit_button = Button(quit_x, score_panel_bottom, quit_img)
    sound_button = Button(sound_x, score_panel_bottom, sound_on_img)
    
    # État initial de la musique
    music_on = True
    pygame.mixer.music.set_volume(0.1)

    menu_pipes = pygame.sprite.Group()
    
    # Local ground scroll for menu animation
    local_ground_scroll = 0

    # Cache des scores pour éviter les requêtes trop fréquentes
    top_scores = get_top_scores()
    last_score_update = pygame.time.get_ticks()
    score_update_delay = 5000  # Mise à jour des scores toutes les 5 secondes
    
    # Définir les polices
    title_font = pygame.font.SysFont('Bauhaus 93', 70)
    score_title_font = pygame.font.SysFont('Bauhaus 93', 45)
    score_font = pygame.font.SysFont('Bauhaus 93', 35)
    
    # Couleurs améliorées
    gold = (255, 223, 0)
    silver = (192, 192, 192)
    bronze = (205, 127, 50)
    text_color = (255, 255, 255)
    bg_color = (0, 0, 0, 160)  # Fond plus transparent

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Mise à jour périodique des scores
        if current_time - last_score_update > score_update_delay:
            top_scores = get_top_scores()
            last_score_update = current_time

        # Draw background
        screen.blit(bg, (0, 0))

        # Update ground scroll for menu animation
        local_ground_scroll -= scroll_speed
        if abs(local_ground_scroll) > 35:
            local_ground_scroll = 0
            
        # Draw ground
        screen.blit(ground_img, (local_ground_scroll, screen_height - 100))

        # Titre principal avec effet d'ombre
        shadow_offset = 3
        title_shadow = title_font.render("Flappy Bird", True, (0, 0, 0))
        title_text = title_font.render("Flappy Bird", True, text_color)
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_shadow, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        screen.blit(title_text, title_rect)

        # Fond semi-transparent pour les scores avec effet de flou
        if top_scores:
            # Fond principal avec dégradé
            score_height = 280
            score_width = 500
            score_x = screen_width // 2 - score_width // 2
            score_y = 150
            
            # Fond principal avec effet de transparence et bordure
            score_bg = pygame.Surface((score_width, score_height), pygame.SRCALPHA)
            score_bg.fill((0, 0, 0, 180))  # Fond un peu plus foncé pour un meilleur contraste
            screen.blit(score_bg, (score_x, score_y))
            
            # Ajouter une bordure dorée
            pygame.draw.rect(screen, (255, 215, 0), (score_x-2, score_y-2, score_width+4, score_height+4), 2)
            
            # Titre du tableau des scores avec effet d'ombre
            score_title = score_title_font.render("Top Scores", True, (255, 215, 0))  # Texte doré
            title_shadow = score_title_font.render("Top Scores", True, (0, 0, 0))
            title_x = screen_width // 2 - score_title.get_width() // 2
            screen.blit(title_shadow, (title_x + 2, score_y + 22))
            screen.blit(score_title, (title_x, score_y + 20))

            # Afficher les scores avec les médailles
            for i, score_data in enumerate(top_scores):
                y_offset = score_y + 80 + i * 60
                medal_x = score_x + 30
                name_x = medal_x + medal_size[0] + 30
                score_x_pos = score_x + score_width - 120

                # Fond pour chaque ligne de score
                score_line_bg = pygame.Surface((score_width - 60, 50), pygame.SRCALPHA)
                score_line_bg.fill((255, 255, 255, 20))
                screen.blit(score_line_bg, (score_x + 30, y_offset))

                # Afficher la médaille appropriée avec effet de brillance
                if i == 0:
                    screen.blit(gold_medal, (medal_x, y_offset))
                elif i == 1:
                    screen.blit(silver_medal, (medal_x, y_offset))
                else:
                    screen.blit(bronze_medal, (medal_x, y_offset))

                # Afficher le nom et le score avec ombre
                name_shadow = score_font.render(score_data['name'], True, (0, 0, 0))
                name_text = score_font.render(score_data['name'], True, text_color)
                score_shadow = score_font.render(str(score_data['score']), True, (0, 0, 0))
                score_text = score_font.render(str(score_data['score']), True, text_color)

                # Ajouter les ombres
                screen.blit(name_shadow, (name_x + 2, y_offset + 12))
                screen.blit(score_shadow, (score_x_pos + 2, y_offset + 12))
                # Ajouter le texte
                screen.blit(name_text, (name_x, y_offset + 10))
                screen.blit(score_text, (score_x_pos, y_offset + 10))

        # Buttons avec effet de survol
        if play_button.draw():
            print("[DEBUG] Play button pressed, starting game")
            menu_pipes.empty()
            return "play"
            
        if quit_button.draw():
            print("[DEBUG] Quit button pressed")
            return "quit"
            
        if sound_button.draw():
            print("[DEBUG] Sound button pressed")
            music_on = not music_on
            if music_on:
                pygame.mixer.music.unpause()
                sound_button.image = sound_on_img
                sound_button.original_image = sound_on_img
                sound_button.hover_image = pygame.transform.scale(sound_on_img, 
                    (int(sound_on_img.get_width() * 1.1), int(sound_on_img.get_height() * 1.1)))
            else:
                pygame.mixer.music.pause()
                sound_button.image = sound_off_img
                sound_button.original_image = sound_off_img
                sound_button.hover_image = pygame.transform.scale(sound_off_img, 
                    (int(sound_off_img.get_width() * 1.1), int(sound_off_img.get_height() * 1.1)))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[DEBUG] Quit event in main menu")
                return "quit"

        pygame.display.update()
        clock.tick(60)  # Limite stricte à 60 FPS

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
        self.original_image = image
        # Créer une version plus grande pour l'effet de survol
        self.hover_image = pygame.transform.scale(image, 
            (int(image.get_width() * 1.1), int(image.get_height() * 1.1)))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.hovering = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        
        # Reset clicked state if mouse button is released
        if not pos:
            self.clicked = False

        # check if mouse is over the button
        if self.rect.collidepoint(mouse_pos):
            if not self.hovering:
                self.hovering = True
                self.image = self.hover_image
                # Ajuster la position pour centrer l'image agrandie
                self.rect.x -= (self.hover_image.get_width() - self.original_image.get_width()) // 2
                self.rect.y -= (self.hover_image.get_height() - self.original_image.get_height()) // 2
            
            if pos and not self.clicked:
                self.clicked = True
                action = True
        else:
            if self.hovering:
                self.hovering = False
                self.image = self.original_image
                # Restaurer la position originale
                self.rect.x += (self.hover_image.get_width() - self.original_image.get_width()) // 2
                self.rect.y += (self.hover_image.get_height() - self.original_image.get_height()) // 2

        # draw button
        screen.blit(self.image, self.rect)

        return action

# Initialize game objects
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create button instances
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)
menu_button = Button(screen_width // 2 - 50, screen_height // 2 + 20, menu_img)

# Get the player name before starting the game
player_name = get_player_name()

# Main game loop
run = True
show_menu = True

def main_game_loop():
    global ground_scroll, flying, game_over, score, pass_pipe, last_pipe, score_submitted
    
    # Store the final positions when game over occurs
    final_ground_scroll = 0
    final_pipe_positions = []
    
    # Create a surface for the game over overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    
    while True:
        # Cap FPS at 60
        clock.tick(60)
        
        # Clear the screen efficiently
        screen.blit(background, (0, 0))
        
        # Draw bird and pipes
        bird_group.draw(screen)
        bird_group.update()
        
        if not game_over:
            # Update and draw pipes normally
            pipe_group.draw(screen)
            pipe_group.update()
            
            # Update ground scroll
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0
                
            # Store pipe positions for game over state
            final_pipe_positions = [(pipe.rect.x, pipe.rect.y) for pipe in pipe_group]
            final_ground_scroll = ground_scroll
            
            # Draw ground efficiently
            screen.blit(ground_surface, (ground_scroll, screen_height - 100))
        else:
            # When game over, draw everything at final positions
            for pipe, (x, y) in zip(pipe_group, final_pipe_positions):
                pipe.rect.x = x
                pipe.rect.y = y
                screen.blit(pipe.image, pipe.rect)
            
            # Draw ground at final position
            screen.blit(ground_surface, (final_ground_scroll, screen_height - 100))
            
            # Draw semi-transparent overlay
            screen.blit(overlay, (0, 0))
        
        # Game logic - only update if not game over
        if not game_over and flying:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now
        
        # Score handling - only update if not game over
        if len(pipe_group) > 0 and not game_over:
            if (bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and
                bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and
                not pass_pipe):
                pass_pipe = True
            if pass_pipe and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
        
        # Draw score with improved visibility
        score_text = font.render(str(score), True, white)
        score_shadow = font.render(str(score), True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(screen_width // 2, 50))
        
        # Draw score shadow
        screen.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        # Draw score
        screen.blit(score_text, score_rect)
        
        # Collision detection
        if (pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or 
            flappy.rect.top < 0 or 
            flappy.rect.bottom >= screen_height - 100):
            game_over = True
            flying = False
            if not score_submitted:
                threading.Thread(target=submit_score, args=(score, player_name), daemon=True).start()
                score_submitted = True
        
        # Game over handling
        if game_over:
            if button.draw():
                fade_out()
                game_over = False
                score = reset_game()
                score_submitted = False
                flying = False
                pipe_group.empty()
                last_pipe = pygame.time.get_ticks() - pipe_frequency
            
            if menu_button.draw():
                fade_out()
                return "menu"
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
                flying = True
        
        pygame.display.update()

# Modify the main loop to use the optimized game loop
while run:
    if show_menu:
        menu_choice = main_menu()
        if menu_choice == "play":
            show_menu = False
            game_over = False
            flying = False
            score = 0
            reset_game()
            last_pipe = pygame.time.get_ticks() - pipe_frequency
        elif menu_choice == "quit":
            run = False
    else:
        result = main_game_loop()
        if result == "menu":
            show_menu = True
            game_over = False
            flying = False
            score_submitted = False
            pipe_group.empty()
            reset_game()
            pygame.event.clear()
        elif result == "quit":
            run = False

pygame.quit()