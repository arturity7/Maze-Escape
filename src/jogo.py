import pygame
from sys import exit
pygame.init()
pygame.mixer.init()


#tamanho da tela--------
fullscreen = False
WIDTH = 1200
HEIGHT = 600

screen = pygame.display.set_mode(( WIDTH, HEIGHT ))

#area da musica fml-----------
pygame.mixer_music.load("assets\sons\soundtrack.mp3")
volume = max(0.0, min(1.0, 0.5))
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1, fade_ms=(3000))
visible_volume = False
volume_timer = 0

pygame.display.set_caption('Labirinto')
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
        
    pygame.display.update()
    clock.tick(60)