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
# ucitavati slike, fontove, zvucne efekte i ostalo
header_font = pygame.font.Font("assets/fonts/square.ttf", 50)
pause_font = pygame.font.Font("assets/fonts/1up.ttf", 38)
banner_font = pygame.font.Font("assets/fonts/BungeeInline-Regular.ttf", 28)
font = pygame.font.Font("assets/fonts/AldotheApache.ttf", 48)


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
    # Postaviti tipku za pauziranje ovdje
    screen.blit(banner_font.render(f"Score: {score}", True, "white"), (250, 10))
    screen.blit(banner_font.render(f"Best: {high_score}", True, "white"), (550, 10))
    screen.blit(banner_font.render(f"Lives: {lives}", True, "white"), (10, 10))


run = True
while run:
    screen.fill("#4c4f69")
    timer.tick(fps)
    draw_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.flip()
