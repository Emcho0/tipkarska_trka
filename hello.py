# Igra: "Tipkarska trka" u pythonu uz pomoc pygame
# Biblioteke pygame, random, copy i kasnije nltk za vokabular
import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])

pygame.display.set_caption("Tipkarska Trka - Pygame")
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# ucitavati slike, fontove, zvucne efekte i ostalo


run = True
while run:
    screen.fill('gray')
    timer.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.flip()
