import pygame
from source.game import Game

def main():
    pygame.init()
    game = Game(id=0)
    game.run()

main()
