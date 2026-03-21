import pygame
from source.game import Game
from source.menu import Menu

def main():
    menu = Menu()
    data = menu.run()
    if not(data["load_dungeon"]):
        return

    while data != None:
        pygame.init()
        game = Game(id=data["id"], save=data["save"], entrance=data["entrance"])
        data = game.run()

main()
