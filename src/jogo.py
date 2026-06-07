import pygame
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
volume = max(0.0, min(1.0, 0.5))
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
                volume -= 0.1
                volume = max(0.0, min(1.0, volume))
                pygame.mixer.music.set_volume(volume)
                volume_timer = pygame.time.get_ticks()

            if event.key == pygame.K_EQUALS:
                visible_volume = True
                volume += 0.1
                volume = max(0.0, min(1.0, volume))
                pygame.mixer.music.set_volume(volume)
                volume_timer = pygame.time.get_ticks()

    #volume desaparecendo hehehe--------
    if visible_volume:
        if pygame.time.get_ticks() - volume_timer > 2000:
            visible_volume = False
    if visible_volume:
        pygame.draw.rect(screen, (80, 80, 80), (20, 20, 200, 20))
        pygame.draw.rect(screen, (255, 255, 255), (20, 20, volume * 200, 20))

    #mov do player
    keys = pygame.key.get_pressed()
    pygame.draw.rect(
    screen,
    (255,255,255),
    player_rect
    )
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

    pygame.display.update()
    clock.tick(60)