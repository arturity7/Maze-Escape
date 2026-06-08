import pygame
from funcoes import (
    carregar_mapa
)
from sys import exit
from config import(
    WIDTH,
    HEIGHT,
    FPS,
    TITULO
)
pygame.init()
pygame.mixer.init()

#tamanho da tela--------
fullscreen = False
screen = pygame.display.set_mode(( WIDTH, HEIGHT ))

#area da musica fml-----------
pygame.mixer_music.load("assets\sons\soundtrack.mp3")
volume = max(0.0, min(1.0, 0.3))
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1, fade_ms=(3000))
visible_volume = False
volume_timer = 0

#player
player_y = 100
player_x = 100

player_width = 32
player_height = 32

player_speed = 5
player_direction = "down"

player_rect = pygame.Rect(
    100,
    100,
    32,
    32
)

#mapa
TILE_SIZE = 64 
mapa = carregar_mapa("../assets/imagens/map.txt")
paredes = []
paredes_visibilidade = {}
for y, linha in enumerate(mapa):
    for x, tile in enumerate(linha):
        if tile == "1":
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            paredes.append(rect)

#puderzin
onda = False
onda_x = 0
onda_y = 0
onda_radius = 0
onda_speed = 5
onda_max = 60

pygame.display.set_caption(TITULO)
clock = pygame.time.Clock()

while True:

    screen.fill((0, 0, 0))

    #fechar o game---------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        #tela cheia---------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
            if fullscreen:
                tela = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
            else:
                tela = pygame.display.set_mode(( WIDTH, HEIGHT ))

        #area da musica 2 (tecla - e = )-------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_MINUS:
                visible_volume = True
                volume -= 0.05
                volume = max(0.0, min(1.0, volume))
                pygame.mixer.music.set_volume(volume)
                volume_timer = pygame.time.get_ticks()

            if event.key == pygame.K_EQUALS:
                visible_volume = True
                volume += 0.05
                volume = max(0.0, min(1.0, volume))
                pygame.mixer.music.set_volume(volume)
                volume_timer = pygame.time.get_ticks()

            if event.key == pygame.K_q:
                onda = True
                onda_x = player_rect.centerx
                onda_y = player_rect.centery
                onda_radius = 0   

    #volume desaparecendo hehehe--------
    if visible_volume:
        if pygame.time.get_ticks() - volume_timer > 2000:
            visible_volume = False
    if visible_volume:
        pygame.draw.rect(screen, (80, 80, 80), (20, 20, 200, 20))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, volume * 200, 20))

        #ondas somem tbm po
    if onda:
        onda_radius += onda_speed
    if onda_radius >= onda_max:
                onda = False

    for i, parede in enumerate(paredes):
        distancia = pygame.math.Vector2(parede.centerx - onda_x,parede.centery - onda_y).length()
        
        if abs(distancia - onda_radius) < 20:  # "borda" da onda
            paredes_visibilidade[i] = 120
    
    #mov do player
    old_x = player_rect.x
    old_y = player_rect.y
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_rect.y -= player_speed
        player_direction = "up"

    if keys[pygame.K_s]:
        player_rect.y += player_speed
        player_direction = "down"

    if keys[pygame.K_a]:
        player_rect.x -= player_speed
        player_direction = "left"

    if keys[pygame.K_d]:
        player_rect.x += player_speed
        player_direction = "right"
    for parede in paredes:
        if player_rect.colliderect(parede):
            player_rect.y = old_y
            break
    for parede in paredes:
        if player_rect.colliderect(parede):
            player_rect.x = old_x
            break

    for i, parede in enumerate(paredes):
        if i in paredes_visibilidade:
            pygame.draw.rect(screen, (255, 255, 255), parede)
            paredes_visibilidade[i] -= 1
            if paredes_visibilidade[i] <= 0:
                del paredes_visibilidade[i]

    pygame.draw.rect(
    screen,
    (255,255,255),
    player_rect
    )

    pygame.display.update()
    clock.tick(60)