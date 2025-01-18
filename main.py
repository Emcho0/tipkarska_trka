"""Igra: "Tipkarska trka" u pythonu uz pomoc pygame biblioteke
Biblioteke upotrijebljene:
pygame, random i copy
"""

import copy
import random

import pygame

pygame.init()

# Inicijalizacija pygame prozora u fullscreen modu
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Tipkarska Trka - Pygame")
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60


# Ucitavanje rijeci sa tekstualnog fajla
def load_words(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Greska: Lista rijeci za {file_path} nije pronadjena.")
        return []


class Language:
    """
    Klasa koja manipulise jezicima i rijecima

    Argumenti:
        languages (list): Lista jezika koja sadrzi tuple (naziv jezika, ime fajla)
        current_language (str): Trenutni jezik
        wordlist (list): Lista rijeci za trenutni jezik
        len_indexes (list): Lista indeksa za duzine rijeci
    """

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
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

bosnian_letters = [
    "a",
    "b",
    "c",
    "č",
    "ć",
    "d",
    "đ",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "lj",
    "m",
    "n",
    "nj",
    "o",
    "p",
    "r",
    "s",
    "š",
    "t",
    "dž",
    "u",
    "v",
    "z",
    "ž",
]

# Za slucaj da rijeci sadrze i druge karaktere osim slova
other_chars = [" ", ".", ",", "!", "?", ":", ";", "-", "_", "(", ")", "[", "]", "'"]

letters = english_letters + [
    letter for letter in bosnian_letters if letter not in english_letters
]

# Napraviti listu koja sadrzi sve karaktere koje korisnik moze koristiti
letters += other_chars

word_objects = []
new_level = True

# Izbori duzine rijeci (od 2 do 8)
choices = [False, True, False, False, False, False, False]

# Ucitavanje slika, fontova, zvucnih efekata i ostalo
header_font = pygame.font.Font("assets/fonts/GeistMono-Medium.ttf", 55)
pause_font = pygame.font.Font("assets/fonts/1up.ttf", 38)
banner_font = pygame.font.Font("assets/fonts/Square.otf", 38)
font = pygame.font.Font("assets/fonts/GeistMono-Medium.ttf", 48)

# Zvucni efekti i muzika
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

# Generisanje score unutar score.txt fajla
try:
    with open("score/score.txt", "r") as file:
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
                font.render(active_string, True, "#40a02b"), (self.x_pos, self.y_pos)
            )

    def update(self):
        self.x_pos -= self.speed


# Menadzment tema za igru
# Tema yorumi se moze pronaci na githubu:
# https://www.github.com/yorumicolors
themes = {
    "abyss": {
        "background": "#060914",
        "foreground": "#BDBFCB",
        "text_color": "#BDBFCB",
        "lives_color": "#8CB167",
        "rect_color": "#343742",
        "selection_background": "#343742",
    },
    "mist": {
        "background": "#BDBFCB",
        "foreground": "#060914",
        "text_color": "#060914",
        "lives_color": "#697F4D",
        "rect_color": "#1D202B",
        "selection_background": "#343742",
    },
}
current_theme = "abyss"


# Funkcija koja mijenja temu bazirano na osnovu korisnikovog odabira
def apply_theme(theme):
    global current_theme
    current_theme = theme
    screen.fill(themes[theme]["background"])


class Button:
    """Klasa za kreiranje dugmadi u igri

    Args:
        x_pos (int): x koordinata
        y_pos (int): y koordinata
        text (str): tekst na dugmetu
        clicked (bool): da li je dugme kliknuto
        surface (pygame.Surface): povrsina na kojoj se crta dugme
        shape (str): oblik dugmeta, moze biti "circle" ili "rectangle"
    """

    def __init__(self, x_pos, y_pos, text, clicked, surface, shape="circle"):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surface = surface
        self.shape = shape

    def draw(self):
        if self.shape == "circle":
            radius = 35
            circle = pygame.draw.circle(
                self.surface, (23, 146, 153), (self.x_pos, self.y_pos), radius
            )
            if circle.collidepoint(pygame.mouse.get_pos()):
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    pygame.draw.circle(
                        self.surface, (32, 159, 181), (self.x_pos, self.y_pos), radius
                    )
                    self.clicked = True
                else:
                    pygame.draw.circle(
                        self.surface, (210, 15, 57), (self.x_pos, self.y_pos), radius
                    )
            pygame.draw.circle(
                self.surface, "white", (self.x_pos, self.y_pos), radius, 3
            )
        else:  # Zaobljeni pravougaonik
            text_size = pause_font.size(self.text)
            width = text_size[0] + 20
            height = text_size[1] + 20
            rect = pygame.draw.rect(
                self.surface,
                (23, 146, 153),
                (self.x_pos - width // 2, self.y_pos - height // 2, width, height),
                border_radius=10,
            )
            if rect.collidepoint(pygame.mouse.get_pos()):
                buttons = pygame.mouse.get_pressed()
                if buttons[0]:
                    pygame.draw.rect(
                        self.surface,
                        (32, 159, 181),
                        (
                            self.x_pos - width // 2,
                            self.y_pos - height // 2,
                            width,
                            height,
                        ),
                        border_radius=10,
                    )
                    self.clicked = True
                else:
                    pygame.draw.rect(
                        self.surface,
                        (210, 15, 57),
                        (
                            self.x_pos - width // 2,
                            self.y_pos - height // 2,
                            width,
                            height,
                        ),
                        border_radius=10,
                    )
            pygame.draw.rect(
                self.surface,
                "white",
                (self.x_pos - width // 2, self.y_pos - height // 2, width, height),
                3,
                border_radius=10,
            )
        self.surface.blit(
            pause_font.render(self.text, True, "white"),
            (
                self.x_pos - pause_font.size(self.text)[0] // 2,
                self.y_pos - pause_font.size(self.text)[1] // 2,
            ),
        )


# Funkcija koja crta ekran igre na osnovu rezolucije i teme koju korisnik odabere
def draw_screen():
    pygame.draw.rect(
        screen,
        themes[current_theme]["rect_color"],
        [0, HEIGHT - int(HEIGHT * 0.1), WIDTH, int(HEIGHT * 0.1)],
        0,
    )
    pygame.draw.rect(screen, "white", [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.line(
        screen,
        "white",
        (int(WIDTH * 0.3125), HEIGHT - int(HEIGHT * 0.1)),
        (int(WIDTH * 0.3125), HEIGHT),
        3,
    )
    pygame.draw.line(
        screen,
        "white",
        (int(WIDTH * 0.875), HEIGHT - int(HEIGHT * 0.1)),
        (int(WIDTH * 0.875), HEIGHT),
        3,
    )
    pygame.draw.line(
        screen,
        "white",
        (0, HEIGHT - int(HEIGHT * 0.1)),
        (WIDTH, HEIGHT - int(HEIGHT * 0.1)),
        3,
    )
    pygame.draw.rect(screen, "black", [0, 0, WIDTH, HEIGHT], 2)
    screen.blit(
        header_font.render(f"NIVO:{level}", True, "white"),
        (10, HEIGHT - int(HEIGHT * 0.075)),
    )
    screen.blit(
        header_font.render(f'"{active_string}"', True, "white"),
        (int(WIDTH * 0.34375), HEIGHT - int(HEIGHT * 0.075)),
    )
    pause_but = Button(
        int(WIDTH * 0.9375), HEIGHT - int(HEIGHT * 0.052), "II", False, screen
    )
    pause_but.draw()
    screen.blit(
        banner_font.render(f"Score: {score}", True, "white"), (int(WIDTH * 0.3125), 10)
    )
    screen.blit(
        banner_font.render(f"H. score: {high_score}", True, "white"),
        (int(WIDTH * 0.6875), 10),
    )
    screen.blit(
        banner_font.render(
            f"Lives: {lives}", True, themes[current_theme]["lives_color"]
        ),
        (10, 10),
    )
    return pause_but.clicked


def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Kalkulisati dimenzije menija za pauziranje
    menu_width = int(WIDTH * 0.75)
    menu_height = int(HEIGHT * 0.75)
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2

    pygame.draw.rect(
        surface, (0, 0, 0, 100), [menu_x, menu_y, menu_width, menu_height], 0, 10
    )
    pygame.draw.rect(
        surface, (0, 0, 0, 200), [menu_x, menu_y, menu_width, menu_height], 5, 10
    )

    # Tipke za meni za pauziranje
    resume_btn = Button(
        menu_x + int(menu_width * 0.1),
        menu_y + int(menu_height * 0.2),
        ">",
        False,
        surface,
        shape="circle",
    )
    resume_btn.draw()
    quit_btn = Button(
        menu_x + int(menu_width * 0.5),
        menu_y + int(menu_height * 0.2),
        "X",
        False,
        surface,
        shape="circle",
    )
    quit_btn.draw()

    # Definisati tekst za meni za pauziranje
    surface.blit(
        header_font.render("MENI", True, "white"),
        (menu_x + int(menu_width * 0.03), menu_y + int(menu_height * 0.05)),
    )
    surface.blit(
        header_font.render("IGRAJ", True, "white"),
        (menu_x + int(menu_width * 0.14), menu_y + int(menu_height * 0.19)),
    )
    surface.blit(
        header_font.render("IZAĐI", True, "white"),
        (menu_x + int(menu_width * 0.6), menu_y + int(menu_height * 0.19)),
    )
    surface.blit(
        header_font.render("DUŽINA RIJEČI: ", True, "white"),
        (menu_x + int(menu_width * 0.03), menu_y + int(menu_height * 0.45)),
    )

    # Definisati tipke za duzinu rijeci (koliko slova ima ta rijec)
    for i in range(len(choices)):
        btn = Button(
            menu_x + int(menu_width * 0.1) + (i * int(menu_width * 0.1)),
            menu_y + int(menu_height * 0.6),
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
                    menu_x + int(menu_width * 0.1) + (i * int(menu_width * 0.1)),
                    menu_y + int(menu_height * 0.6),
                ),
                35,
                5,
            )

    # Dodati tekst za odabir jezika
    surface.blit(
        header_font.render("ODABERI JEZIK: ", True, "white"),
        (menu_x + int(menu_width * 0.03), menu_y + int(menu_height * 0.75)),
    )

    # Definisati tipke za odabir jezika
    language_buttons = [
        Button(
            menu_x + int(menu_width * 0.6),
            menu_y + int(menu_height * 0.8),
            "English",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + int(menu_width * 0.85),
            menu_y + int(menu_height * 0.8),
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
            text_size = pause_font.size(btn.text)
            width = text_size[0] + 20
            height = text_size[1] + 20
            pygame.draw.rect(
                surface,
                "#40a02b",
                (btn.x_pos - width // 2, btn.y_pos - height // 2, width, height),
                5,
                border_radius=10,
            )

    # Dodati tekst za odabir teme
    surface.blit(
        header_font.render("ODABERI TEMU: ", True, "white"),
        (menu_x + int(menu_width * 0.03), menu_y + int(menu_height * 0.9)),
    )
    theme_buttons = [
        Button(
            menu_x + int(menu_width * 0.6),
            menu_y + int(menu_height * 0.95),
            "abyss",
            False,
            surface,
            shape="rectangle",
        ),
        Button(
            menu_x + int(menu_width * 0.87),
            menu_y + int(menu_height * 0.95),
            "mist",
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


# Funkcija koja provjerava korisnikov unos
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
                (language_manager.len_indexes[i], language_manager.len_indexes[i + 1])
            )
    for i in range(level):
        # Moze se prilagoditi brzina i pozicija rijeci
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


# Glavna petlja igra koja se izvrsava sve dok se ne zavrsi igra
run = True
while run:
    screen.fill(themes[current_theme]["background"])
    timer.tick(fps)
    pause_but = draw_screen()

    if paused:
        # Prikazi meni za pauziranje ako je igra pauzirana, a ako nije, generisi novi nivo
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
        # Provjeriti da li je korisnik kliknuo na dugme
        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    click.play()
                if event.key == pygame.K_BACKSPACE and len(active_string) > 0:
                    active_string = active_string[:-1]
                    click.play()
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ""
            if event.key == pygame.K_ESCAPE:
                paused = not paused
        if event.type == pygame.MOUSEBUTTONUP and paused:
            if event.button == 1:
                choices = changes
    if pause_but:
        paused = True

    if lives < 0:
        # Provjeriti da li je korisnik postavio novi highscore i da li su zivoti manje od 0
        paused = True
        level = 1
        lives = 8
        word_objects = []
        new_level = True
        check_highscore()
        score = 0

    pygame.display.flip()
pygame.quit()
