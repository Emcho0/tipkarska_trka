"""Igra: "Tipkarska trka" u pythonu uz pomoc pygame biblioteke.

Biblioteke upotrijebljene za projekat: pygame, random i copy
"""

import copy
import random

import pygame

pygame.init()

# Postavke ekrana
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_icon(pygame.image.load("assets/images/logo.png"))
WIDTH, HEIGHT = screen.get_size()

# Bazna rezolucija (koristi se za odnose kod skaliranja)
BASE_WIDTH, BASE_HEIGHT = 800, 600

pygame.display.set_caption("Tipkarska Trka")
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# Globalne varijable
fullscreen = True


def get_scaled_font(base_font_size):
    scaling_factor = min(WIDTH / BASE_WIDTH * 0.60, HEIGHT / BASE_HEIGHT * 0.60)
    return int(base_font_size * scaling_factor)


def get_scaled_value(base_value):
    scaling_factor = 0.90 * min(WIDTH / BASE_WIDTH, HEIGHT / BASE_HEIGHT)
    return int(base_value * scaling_factor)


def adjust_game_elements():
    global pause_menu_rect
    pause_menu_width = get_scaled_value(WIDTH // 3)
    pause_menu_height = get_scaled_value(HEIGHT // 3)
    pause_menu_rect = pygame.Rect(
        (WIDTH - pause_menu_width) // 3,
        (HEIGHT - pause_menu_height) // 3,
        pause_menu_width,
        pause_menu_height,
    )


def toggle_screen_resolution():
    global screen, fullscreen, WIDTH, HEIGHT
    if fullscreen:
        screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    fullscreen = not fullscreen
    WIDTH, HEIGHT = screen.get_size()
    adjust_game_elements()


def load_words(file_path):
    try:
        with open(file_path, encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Greska: Lista rijeci za {file_path} nije pronadjena.")
        return []


class Language:
    def __init__(self, languages):
        self.languages = languages
        self.current_language = "english"
        self.wordlist = self.load_words("assets/words/english.txt")
        self.len_indexes = self.calculate_len_indexes(self.wordlist)

    def load_words(self, file_path):
        words = load_words(file_path)
        words.sort(key=len)
        return words

    def set_language(self, lang):
        self.current_language = lang
        self.wordlist = self.load_words(f"assets/words/{lang}.txt")
        self.len_indexes = self.calculate_len_indexes(self.wordlist)

    def calculate_len_indexes(self, wordlist):
        len_indexes = []
        length = 1
        for i in range(len(wordlist)):
            if len(wordlist[i]) > length:
                length += 1
                len_indexes.append(i)
        len_indexes.append(len(wordlist))
        return len_indexes


# Inicijalizacija jezika i njihovih vrijednosti
# Ovdje se mogu dodati i drugi jezici uz pomoc tuple (naziv jezika, ime fajla)
languages = [("English", "english"), ("Bosanski", "bosnian")]
language_manager = Language(languages)

# Varijable za igru
level = 1
active_string = ""
score = 0
lives = 8
paused = True
submit = ""

# Postavljanje bosanskih i engleskih slova za igru
english_letters = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
]
bosnian_letters = [
    "a", "b", "c", "č", "ć", "d", "dž", "đ", "e", "f", "g", "h", "i". "j", "k", "l", "lj", "m", "n", "nj", "o", "p", "r", "s", "š", "t", "u", "v", "z", "ž"
]
# Za slucaj da rijeci sadrze i druge karaktere osim slova
other_chars = [" ", ".", ",", "!", "?", ":", ";", "-", "_", "(", ")", "[", "]", "'"]

letters = english_letters + [
    letter for letter in bosnian_letters if letter not in english_letters
]

letters += other_chars

word_objects = []
new_level = True

choices = [False, True, False, False, False, False, False]

# Ucitavanje fontova
header_font = pygame.font.Font("assets/fonts/GeistMono-Medium.ttf", get_scaled_font(45))
pause_font = pygame.font.Font("assets/fonts/1up.ttf", get_scaled_font(20))
banner_font = pygame.font.Font("assets/fonts/Square.otf", get_scaled_font(38))
font = pygame.font.Font("assets/fonts/GeistMono-Medium.ttf", get_scaled_font(45))

pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/music.mp3")
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)

click = pygame.mixer.Sound("assets/sounds/mech-click.mp3")
woosh = pygame.mixer.Sound("assets/sounds/Swoosh.mp3")
wrong = pygame.mixer.Sound("assets/sounds/Instrument Strum.mp3")

click.set_volume(0.7)
woosh.set_volume(0.5)
wrong.set_volume(0.75)

try:
    with open("score/score.txt") as file:
        read = file.readlines()
        if read:
            high_score = int(read[0])
        else:
            high_score = 0
except FileNotFoundError:
    high_score = 0
    with open("score/score.txt", "w") as file:
        file.write("0")
except ValueError:
    high_score = 0
    with open("score/score.txt", "w") as file:
        file.write("0")


class Word:
    def __init__(self, text, speed, y_pos, x_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.speed = speed

    def draw(self):
        color = themes[current_theme]["text_color"]
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(
                font.render(active_string, True, "#40a02b"),
                (self.x_pos, self.y_pos),
            )

    def update(self):
        self.x_pos -= self.speed


# Vise informacija o temama mozete pronaci na linku
# https://github.com/yorumicolors
themes = {
    "abyss": {
        "background": "#060914",
        "foreground": "#BDBFCB",
        "text_color": "#BDBFCB",
        "lives_color": "#8CB167",
        "rect_color": "#0D2C4E",
        "selection_background": "#343742",
    },
    "mist": {
        "background": "#BDBFCB",
        "foreground": "#060914",
        "text_color": "#060914",
        "lives_color": "#697F4D",
        "rect_color": "#A7A9B5",
        "selection_background": "#343742",
    },
    # Nove zvanicne teme "shade" i "kraken"
    "shade": {
        "background": "#0F1015",
        "foreground": "#BDBFCB",
        "text_color": "#BDBFCB",
        "lives_color": "#697F4D",
        "rect_color": "#4A4D59",
        "selection_background": "#343742",
    },
    "kraken": {
        "background": "#0E0D17",
        "foreground": "#C0BCE6",
        "text_color": "#C0BCE6",
        "lives_color": "#A9D07C",
        "rect_color": "#1D202B",
        "selection_background": "#121520",
    },
}

current_theme = "mist"


def apply_theme(theme):
    global current_theme
    current_theme = theme
    screen.fill(themes[theme]["background"])


# Bazne vrijednosti za pozicije UI elemenata
PAUSE_BUTTON_BASE_X = 750
PAUSE_BUTTON_BASE_Y = 636

SCORE_X_BASE = 250
SCORE_Y_BASE = 10

HIGH_SCORE_X_BASE = 550
HIGH_SCORE_Y_BASE = 10

LIVES_X_BASE = 10
LIVES_Y_BASE = 10

LEVEL_X_BASE = 10
LEVEL_Y_OFFSET = 45


class Button:
    def __init__(self, x_pos, y_pos, text, clicked, surface, shape="circle"):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surface = surface
        self.shape = shape

        if shape == "circle":
            self.radius = get_scaled_value(25)
            self.width = None
            self.height = None
        else:
            text_w, text_h = pause_font.size(self.text)
            pad_x = 15
            pad_y = 10
            self.width = get_scaled_value(text_w + pad_x)
            self.height = get_scaled_value(text_h + pad_y)

    def draw(self):
        if self.shape == "circle":
            circle = pygame.draw.circle(
                self.surface,
                (23, 146, 153),
                (self.x_pos, self.y_pos),
                self.radius,
            )
            if circle.collidepoint(pygame.mouse.get_pos()):
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    pygame.draw.circle(
                        self.surface,
                        (32, 159, 181),
                        (self.x_pos, self.y_pos),
                        self.radius,
                    )
                    self.clicked = True
                else:
                    pygame.draw.circle(
                        self.surface,
                        (210, 15, 57),
                        (self.x_pos, self.y_pos),
                        self.radius,
                    )
            pygame.draw.circle(
                self.surface,
                "white",
                (self.x_pos, self.y_pos),
                self.radius,
                3,
            )
        else:
            rect = pygame.draw.rect(
                self.surface,
                (23, 146, 153),
                (
                    self.x_pos - self.width // 2,
                    self.y_pos - self.height // 2,
                    self.width,
                    self.height,
                ),
                border_radius=10,
            )
            if rect.collidepoint(pygame.mouse.get_pos()):
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    pygame.draw.rect(
                        self.surface,
                        (32, 159, 181),
                        (
                            self.x_pos - self.width // 2,
                            self.y_pos - self.height // 2,
                            self.width,
                            self.height,
                        ),
                        border_radius=10,
                    )
                    self.clicked = True
                else:
                    pygame.draw.rect(
                        self.surface,
                        (210, 15, 57),
                        (
                            self.x_pos - self.width // 2,
                            self.y_pos - self.height // 2,
                            self.width,
                            self.height,
                        ),
                        border_radius=10,
                    )
            pygame.draw.rect(
                self.surface,
                "white",
                (
                    self.x_pos - self.width // 2,
                    self.y_pos - self.height // 2,
                    self.width,
                    self.height,
                ),
                3,
                border_radius=10,
            )
        # crta tekst unutra
        text_w, text_h = pause_font.size(self.text)
        self.surface.blit(
            pause_font.render(self.text, True, "white"),
            (self.x_pos - text_w // 2, self.y_pos - text_h // 2),
        )


def draw_screen():
    pygame.draw.rect(
        screen,
        themes[current_theme]["rect_color"],
        [0, HEIGHT - get_scaled_value(60), WIDTH, get_scaled_value(60)],
        0,
    )
    pygame.draw.rect(screen, "white", [0, 0, WIDTH, HEIGHT], 5)

    pygame.draw.line(
        screen,
        "white",
        (get_scaled_value(250), HEIGHT - get_scaled_value(60)),
        (get_scaled_value(250), HEIGHT),
        3,
    )
    pygame.draw.line(
        screen,
        "white",
        (get_scaled_value(700), HEIGHT - get_scaled_value(60)),
        (get_scaled_value(700), HEIGHT),
        3,
    )
    pygame.draw.line(
        screen,
        "white",
        (0, HEIGHT - get_scaled_value(60)),
        (WIDTH, HEIGHT - get_scaled_value(60)),
        3,
    )
    pygame.draw.rect(screen, "black", [0, 0, WIDTH, HEIGHT], 2)

    screen.blit(
        header_font.render(f"NIVO:{level}", True, "white"),
        (get_scaled_value(LEVEL_X_BASE), HEIGHT - get_scaled_value(LEVEL_Y_OFFSET)),
    )
    screen.blit(
        header_font.render(f'"{active_string}"', True, "white"),
        (get_scaled_value(280), HEIGHT - get_scaled_value(LEVEL_Y_OFFSET)),
    )

    pause_button = Button(
        get_scaled_value(PAUSE_BUTTON_BASE_X),
        get_scaled_value(PAUSE_BUTTON_BASE_Y),
        "II",
        False,
        screen,
    )
    pause_button.draw()

    screen.blit(
        banner_font.render(f"Score: {score}", True, "white"),
        (get_scaled_value(SCORE_X_BASE), get_scaled_value(SCORE_Y_BASE)),
    )
    screen.blit(
        banner_font.render(f"H. score: {high_score}", True, "white"),
        (get_scaled_value(HIGH_SCORE_X_BASE), get_scaled_value(HIGH_SCORE_Y_BASE)),
    )
    screen.blit(
        banner_font.render(
            f"Lives: {lives}",
            True,
            themes[current_theme]["lives_color"],
        ),
        (get_scaled_value(LIVES_X_BASE), get_scaled_value(LIVES_Y_BASE)),
    )
    return pause_button.clicked


def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    menu_width = get_scaled_value(600)
    menu_height = get_scaled_value(450)
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2

    pygame.draw.rect(
        surface,
        (0, 0, 0, 100),
        [menu_x, menu_y, menu_width, menu_height],
        0,
        10,
    )
    pygame.draw.rect(
        surface,
        (0, 0, 0, 200),
        [menu_x, menu_y, menu_width, menu_height],
        5,
        10,
    )

    resume_btn = Button(
        menu_x + get_scaled_value(120),
        menu_y + get_scaled_value(90),
        ">",
        False,
        surface,
        shape="circle",
    )
    resume_btn.draw()

    quit_btn = Button(
        menu_x + get_scaled_value(300),
        menu_y + get_scaled_value(90),
        "X",
        False,
        surface,
        shape="circle",
    )
    quit_btn.draw()

    surface.blit(
        header_font.render("MENI", True, "white"),
        (menu_x + get_scaled_value(20), menu_y + get_scaled_value(30)),
    )
    surface.blit(
        header_font.render("IGRAJ", True, "white"),
        (menu_x + get_scaled_value(160), menu_y + get_scaled_value(75)),
    )
    surface.blit(
        header_font.render("IZAĐI", True, "white"),
        (menu_x + get_scaled_value(330), menu_y + get_scaled_value(75)),
    )

    surface.blit(
        header_font.render("DUŽINA RIJEČI:", True, "white"),
        (menu_x + get_scaled_value(20), menu_y + get_scaled_value(240)),
    )
    for i in range(len(choices)):
        btn = Button(
            menu_x + get_scaled_value(80) + (i * get_scaled_value(60)),
            menu_y + get_scaled_value(320),
            str(i + 2),
            False,
            surface,
            shape="circle",
        )
        btn.draw()
        if btn.clicked:
            choice_commits[i] = not choice_commits[i]
        if choices[i]:
            pygame.draw.circle(
                surface,
                "#40a02b",
                (
                    menu_x + get_scaled_value(80) + (i * get_scaled_value(60)),
                    menu_y + get_scaled_value(320),
                ),
                get_scaled_value(25),
                3,
            )

    # Jezici
    surface.blit(
        header_font.render("ODABERI JEZIK:", True, "white"),
        (menu_x + get_scaled_value(20), menu_y + get_scaled_value(370)),
    )
    language_buttons = [
        Button(
            menu_x + get_scaled_value(90),
            menu_y + get_scaled_value(425),
            "English",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + get_scaled_value(300),
            menu_y + get_scaled_value(425),
            "Bosanski",
            False,
            surface,
            shape="rectangle",
        ),
    ]

    for btn in language_buttons:
        btn.draw()
        if btn.clicked:
            language_manager.set_language(btn.text.lower())
        if language_manager.current_language == btn.text.lower():
            text_w, text_h = pause_font.size(btn.text)
            width = get_scaled_value(text_w + 15)
            height = get_scaled_value(text_h + 10)
            pygame.draw.rect(
                surface,
                "#40a02b",
                (btn.x_pos - width // 2, btn.y_pos - height // 2, width, height),
                3,
                border_radius=10,
            )

    surface.blit(
        header_font.render("ODABERI TEMU:", True, "white"),
        (menu_x + get_scaled_value(20), menu_y + get_scaled_value(135)),
    )
    theme_buttons = [
        Button(
            menu_x + get_scaled_value(90),
            menu_y + get_scaled_value(205),
            "abyss",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + get_scaled_value(200),
            menu_y + get_scaled_value(205),
            "mist",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + get_scaled_value(310),
            menu_y + get_scaled_value(205),
            "shade",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + get_scaled_value(440),
            menu_y + get_scaled_value(205),
            "kraken",
            False,
            surface,
            shape="rectangle",
        ),
    ]

    for btn in theme_buttons:
        btn.draw()
        if btn.clicked:
            apply_theme(btn.text.lower())

    screen.blit(surface, (0, 0))
    return resume_btn.clicked, choice_commits, quit_btn.clicked


def check_answer(score):
    for word in word_objects:
        if word.text == submit:
            points = word.speed * len(word.text) * 10 * (len(word.text) / 3)
            score += int(points)
            word_objects.remove(word)
            woosh.play()
    return score


def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT - 150) // level
    if True not in choices:
        choices[0] = True
    for i in range(len(choices)):
        if choices[i] and i + 1 < len(language_manager.len_indexes):
            include.append(
                (language_manager.len_indexes[i], language_manager.len_indexes[i + 1]),
            )
    for i in range(level):
        speed = random.randint(4, 6)
        y_pos = random.randint(10 + (i * vertical_spacing), (i + 1) * vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH + 1000)
        ind_sel = random.choice(include)
        index = random.randint(ind_sel[0], ind_sel[1] - 1)
        text = language_manager.wordlist[index].lower()
        new_word = Word(text, speed, y_pos, x_pos)
        word_objs.append(new_word)
    return word_objs


def check_highscore():
    global high_score
    if score > high_score:
        high_score = score
        with open("score/score.txt", "w") as file:
            file.write(str(int(high_score)))


run = True
while run:
    screen.fill(themes[current_theme]["background"])
    timer.tick(fps)
    pause_but = draw_screen()

    if paused:
        resume_but, changes, quit_but = draw_pause()
        if resume_but:
            paused = False
        if quit_but:
            check_highscore()
            run = False

    if new_level and not paused:
        word_objects = generate_level()
        new_level = False
    else:
        for w in word_objects:
            w.draw()
            if not paused:
                w.update()
            if w.x_pos < -200:
                word_objects.remove(w)
                lives -= 1

    if len(word_objects) <= 0 and not paused:
        level += 1
        new_level = True

    if submit != "":
        init = score
        score = check_answer(score)
        submit = ""
        if init == score:
            wrong.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_highscore()
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                toggle_screen_resolution()
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    click.play()
                if event.key == pygame.K_BACKSPACE and len(active_string) > 0:
                    active_string = active_string[:-1]
                    click.play()
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    submit = active_string
                    active_string = ""
        elif event.type == pygame.VIDEORESIZE:
            if not fullscreen:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                adjust_game_elements()
        if event.type == pygame.MOUSEBUTTONUP and paused:
            if event.button == 1:
                choices = changes

    if pause_but:
        paused = True

    if lives < 0:
        paused = True
        level = 1
        lives = 8
        word_objects = []
        new_level = True
        check_highscore()
        score = 0

    pygame.display.flip()

pygame.quit()
