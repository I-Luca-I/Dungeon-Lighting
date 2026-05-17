import pygame
from source.game import Game
from source.menu import Menu

def main():
    menu = Menu()
    data = menu.run()
    if not(data["load_dungeon"]):
        return

    time = 0  # placeholders
    turns = 0
    num_executed_turns = 0
    while data != None:
        pygame.init()
        game = Game(id=data["id"], save=data["save"], entrance=data["entrance"], turns=turns, time=time, num_executed_turns=num_executed_turns)
        data, turns, time, num_executed_turns = game.run()

main()
