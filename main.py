import pygame
from source.game import Game

def main():
    pygame.init()
    game = Game(id="palle")
    game.run()

main()
