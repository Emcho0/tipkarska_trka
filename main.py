"""Igra: "Tipkarska trka" u pythonu uz pomoc pygame
Biblioteke pygame, random, copy i kasnije nltk za vokabular.
"""

import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])

pygame.display.set_caption("Tipkarska Trka - Pygame")
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# Varijable za igru
level = 0
active_string = "testni string"
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

# ucitavati slike, fontove, zvucne efekte i ostalo
header_font = pygame.font.Font("assets/fonts/Square.ttf", 50)
pause_font = pygame.font.Font("assets/fonts/1up.ttf", 38)
banner_font = pygame.font.Font("assets/fonts/BungeeInline-Regular.ttf", 28)
font = pygame.font.Font("assets/fonts/AldotheApache.ttf", 48)


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


run = True
while run:
    screen.fill("#4c4f69")
    timer.tick(fps)
    pause_but = draw_screen()

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
