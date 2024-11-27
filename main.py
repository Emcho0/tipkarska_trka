"""Igra: "Tipkarska trka" u pythonu uz pomoc pygame
Biblioteke pygame, random, copy i kasnije nltk za vokabular.
"""

# nltk biblioteka za listu rijeci
import random

# Potrebno kako bi igra normalno funkcionisala
import nltk

nltk.download("words")

import pygame
from nltk.corpus import words

pygame.init()

wordlist = words.words()
len_indexes = []
length = 1

# mehanizam za sortiranje liste rijeci

wordlist.sort(key=len)

for i in range(len(wordlist)):
    if len(wordlist[i]) > length:
        length += 1
        len_indexes.append(i)

len_indexes.append(len(wordlist))
print(len_indexes)

# inicijaliziranje pygame igre
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])

pygame.display.set_caption("Tipkarska Trka - Pygame")
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# Varijable za igru
level = 1
active_string = ""
score = 0
high_score = 1
lives = 5
paused = False
letters = [
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
submit = ""
word_objects = []
new_level = True
# izbori duzine rijeci (od 2 do 8)
choices = [False, True, False, False, False, False, False]
# ucitavati slike, fontove, zvucne efekte i ostalo
header_font = pygame.font.Font("assets/fonts/Square.ttf", 50)
pause_font = pygame.font.Font("assets/fonts/1up.ttf", 38)
banner_font = pygame.font.Font("assets/fonts/BungeeInline-Regular.ttf", 28)
font = pygame.font.Font("assets/fonts/AldotheApache.ttf", 48)


class Word:
    def __init__(self, text, speed, y_pos, x_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.speed = speed

    def draw(self):
        color = "#c6d0f5"
        screen.blit(font.render(self.text, True, color), (self.x_pos, self.y_pos))
        act_len = len(active_string)
        if active_string == self.text[:act_len]:
            screen.blit(
                font.render(active_string, True, "#40a02b"), (self.x_pos, self.y_pos)
            )

    def update(self):
        self.x_pos -= self.speed


class Button:
    def __init__(self, x_pos, y_pos, text, clicked, surface):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text = text
        self.clicked = clicked
        self.surface = surface

    def draw(self):
        circle = pygame.draw.circle(
            self.surface, (23, 146, 153), (self.x_pos, self.y_pos), 35
        )
        if circle.collidepoint(pygame.mouse.get_pos()):
            buttons = pygame.mouse.get_pressed()
            if buttons[0]:
                pygame.draw.circle(
                    self.surface, (32, 159, 181), (self.x_pos, self.y_pos), 35
                )
                self.clicked = True
            else:
                pygame.draw.circle(
                    self.surface, (210, 15, 57), (self.x_pos, self.y_pos), 35
                )
        pygame.draw.circle(self.surface, "white", (self.x_pos, self.y_pos), 35, 3)

        self.surface.blit(
            pause_font.render(self.text, True, "white"),
            (self.x_pos - 15, self.y_pos - 25),
        )


def draw_screen():
    # oblik pozadine i podrucje sa naslovom o nivou i sl.
    pygame.draw.rect(screen, (114, 135, 253), [0, HEIGHT - 100, WIDTH, 100], 0)
    pygame.draw.rect(screen, "white", [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.line(screen, "white", (250, HEIGHT - 100), (250, HEIGHT), 2)
    pygame.draw.line(screen, "white", (700, HEIGHT - 100), (700, HEIGHT), 2)
    pygame.draw.line(screen, "white", (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
    pygame.draw.rect(screen, "black", [0, 0, WIDTH, HEIGHT], 2)
    # Tekst koji prikazuje trenutni nivo, trenutni otkucaji, skor, zivoti
    screen.blit(header_font.render(f"Nivo:{level}", True, "white"), (10, HEIGHT - 75))
    screen.blit(
        header_font.render(f'"{active_string}"', True, "white"), (270, HEIGHT - 75)
    )
    # Tipka za pauziranje
    pause_but = Button(748, HEIGHT - 52, "II", False, screen)
    pause_but.draw()
    screen.blit(banner_font.render(f"Score: {score}", True, "white"), (250, 10))
    screen.blit(banner_font.render(f"Best: {high_score}", True, "white"), (550, 10))
    screen.blit(banner_font.render(f"Lives: {lives}", True, "white"), (10, 10))
    return pause_but.clicked


def draw_pause():
    pass


# funkcija koja provjerava korisnikov unos


def check_answer(score):
    for word in word_objects:
        if word.text == submit:
            points = word.speed * len(word.text) * 10 * (len(word.text) / 3)
            score += int(points)
            word_objects.remove(word)
            # pusti zvuk kada je uspjesan korisnicki unos
    return score


def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT - 150) // level
    if True not in choices:
        choices[0] = True
    for i in range(len(choices)):
        if choices[i]:
            include.append((len_indexes[i], len_indexes[i + 1]))
    for i in range(level):
        # brzine od-do koji uticu na tezinu igre
        speed = random.randint(2, 3)
        y_pos = random.randint(10 + (i * vertical_spacing), (i + 1) * vertical_spacing)
        x_pos = random.randint(WIDTH, WIDTH + 1000)
        ind_sel = random.choice(include)
        index = random.randint(ind_sel[0], ind_sel[1])
        text = wordlist[index].lower()
        new_word = Word(text, speed, y_pos, x_pos)
        word_objs.append(new_word)
    return word_objs


run = True
while run:
    screen.fill("#4c4f69")
    timer.tick(fps)
    pause_but = draw_screen()

    if paused:
        draw_pause()
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
            # pusti zvuk za netacno kucanje (wrong entry sound)
            pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                if event.key == pygame.K_BACKSPACE and len(active_string) > 0:
                    active_string = active_string[:-1]
                # Uslov vraca string (rijec) ako je pritisnut razmak ili enter
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ""

    pygame.display.flip()
pygame.quit()
