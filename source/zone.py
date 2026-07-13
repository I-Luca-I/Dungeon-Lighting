import numpy as np
import pygame, csv
import random
from . import triggerables


class Zone:
    def __init__(self, turns:int, time:int, num_executed_turns:int, path_to_file:str, frequenza_encounters:int, mask:pygame.Mask):
        self.mask = mask
        self.turns = turns
        self.time = time
        # with open(path_to_file, "r") as file:
        #     self.reader = csv.reader(file)
        #     self.sheet = []
        #     for i in self.reader:
        #         self.sheet.append(str(_) for _ in i)
        self.sheet = np.loadtxt(path_to_file, delimiter=",", dtype=str)
        self.num_executed_turns = num_executed_turns
        self.frequenza_encounters = frequenza_encounters
        self.rimanenti = []
        self.rcheck = []
        for i in range(len(self.sheet)):
            self.rimanenti.append(float(self.sheet[i][2]))
            self.rcheck.append(0.0)
        self.totali = self.rimanenti

    def turn_change(self):
        self.turns += 1
        self.time += 10
        rand = random.randrange(1, self.frequenza_encounters)
        text = None
        if (rand == 1 and self.rimanenti != self.rcheck):
            rand = random.randrange(len(self.sheet))
            while (self.rimanenti[rand] <= 0.0):
                rand = random.randrange(len(self.sheet))
            row = self.sheet[rand]
            if self.rimanenti[rand] >= float(row[4]):
                n_apparsi = random.randrange(int(float(row[3])), int(float(row[4])) + 1)
            elif self.rimanenti[rand] >= float(row[3]):
                n_apparsi = random.randrange(int(float(row[3])), int(self.rimanenti[rand]) + 1)
            else:
                n_apparsi = int(self.rimanenti[rand])
            self.rimanenti[rand] -= n_apparsi
            text = row[0] + ") " + str(n_apparsi) + " " + row[1]
        print("turno:" + str(self.turns) + " tempo:" + (str((self.time // 60) % 24)) + ":" + str(self.time - (self.time // 60) * 60))
        if text:
            print(text)

    @staticmethod
    def get_zones(number_of_zones:int, frequencies:list[int], consumati_per_zona, turns:int, time:int, num_executed_turns:int, dungeon_id:str) -> list:
        zone_color_by_id = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 0), (128, 0, 128), (0, 128, 128)]
        zones = []
        for i in range(number_of_zones):
            zones.append(Zone(turns, time, num_executed_turns, f"saves/dungeon_{dungeon_id}/random_table_zona_{i+1}.csv", frequencies[i], triggerables.Triggerable.get_big_mask(pygame.image.load(f"saves/dungeon_{dungeon_id}/zones_{dungeon_id}.png"), zone_color_by_id[i])))
            rimanenti = zones[i].rimanenti
            zones[i].rimanenti = []
            for j in range(len(consumati_per_zona[i])):
                zones[i].rimanenti.append(rimanenti[j] - consumati_per_zona[i][j])
        return zones