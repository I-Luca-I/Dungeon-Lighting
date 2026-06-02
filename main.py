import pygame
from source.game import Game
from source.menu import Menu

def main():
    menu = Menu()
    data = menu.run()
    if not(data["load_dungeon"]):
        return

    time = data["time"]
    turns = data["turn"]
    num_executed_turns = data["turn"]
    while data != None:
        pygame.init()
        game = Game(id=data["id"], save=data["save"], entrance=data["entrance"], turns=turns, time=time, num_executed_turns=num_executed_turns)
        data, turns, time, num_executed_turns = game.run()

main()
