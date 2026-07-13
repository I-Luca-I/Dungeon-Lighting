import numpy as np
from numba import njit

"""
self deve essere sotituito da una struttura che comprenda:
    - texture (shape array)
    - position (array)
    - moving (bool)
    - max_rays (int)
    - prev_position (array)
    
# event deve essere sotituito da una struttura che comprenda:
#     - type (da capire con cosa sostituirlo e che tipo di dato è)
#     - button (idem con patate)

i seguenti attributi di self vengono invece definiti qui all'inerno di move, quindi ricordarsi di ritornarli (non tutti 
sono effettivamente necessari però per adesso questa lista comprende tutto):
    - self.overlap_vector (array)
    - self.mouse_endpoints (array)
    - self.mouse_startpoints (array)
    - self.interrupt_points (array)
    - self.start_interrupt_points (array)
    - self.min_dist_index (int)
    
la nuova "architettura" per come pensavo di fare move sarebbe:

fuori dalla classe:
@njit
def move_redo(self: struttura di cui parlo sopra, event: idem con patate, mouse_coords: np.array, collision_mask: np.ndarray):

dentro pawn:
def move(parametri come adesso):
    qui convertiamo i dati nelle strutture appropriate per numba
    dati = move_redo(con qui i parametri de-oggettificati)
    qui andiamo a modificare self con i dati raccolti dalla chiamata di move_redo
    
"""
TEXTURE_SIZE = 0
POSITION = 1 # MODIFIED
PREV_POSITION = 2 # UNUSED
MOVING = 3
MAX_RAYS = 4

def move(pawn:np.ndarray, mouse_coords:np.ndarray, collision_mask:np.ndarray) -> None:
    x = (mouse_coords[0] - pawn[POSITION][0])
    y = (mouse_coords[1] - pawn[POSITION][1])

    self.mouse_endpoints = []
    self.mouse_startpoints = []
    for i in range(0, pawn[MAX_RAYS], pawn[MAX_RAYS] // 500):
        end = (max(0, min(mouse_coords[0], collision_mask.shape[0] - 1)),
               (max(0, min(mouse_coords[1], collision_mask.shape[1] - 1))))
        start = (
            max(0,
                min(int(end[0] - ((np.sqrt(x ** 2 + y ** 2) + 0) * np.cos(i * (2 * np.pi) / pawn[MAX_RAYS]))), collision_mask.shape[0] - 1)),
            max(0,
                min(int(end[1] - ((np.sqrt(x ** 2 + y ** 2) + 0) * np.sin(i * (2 * np.pi) / pawn[MAX_RAYS]))), collision_mask.shape[1] - 1))
        )
        self.mouse_startpoints.append(start)

        m = float(start[1] - end[1]) / float(start[0] - end[0]) if (start[0] != end[0]) else collision_mask.shape[
            1]
        q = start[1] - m * start[0]
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])

        interrupt = False

        if (dx > dy):
            for j in range(int(start[0]), int(end[0]), 1 if end[0] > start[0] else -1):
                if (collision_mask[j][int(m * j + q)] == 1):
                    prev_j = j - (1 if end[0] > start[0] else -1)
                    self.mouse_endpoints.append([prev_j, int(m * (prev_j) + q)])
                    interrupt = True
                    break
        else:
            for j in range(int(start[1]), int(end[1]), 1 if end[1] > start[1] else -1):
                if (collision_mask[int((j - q) / m)][j] == 1):
                    prev_j = j - (1 if end[1] > start[1] else -1)
                    self.mouse_endpoints.append([int(((prev_j) - q) / m), prev_j])
                    interrupt = True
                    break

        if (not (interrupt)):
            self.mouse_endpoints.append([end[0], end[1]])

    i = 0
    self.interrupt_points = []
    self.start_interrupt_points = []
    while (i < len(self.mouse_endpoints)):
        start = pawn[POSITION]
        end = self.mouse_endpoints[i]

        m = float(start[1] - end[1]) / float(start[0] - end[0]) if (start[0] != end[0]) else collision_mask.shape[
            1]
        q = start[1] - m * start[0]
        dx = abs(start[0] - end[0])
        dy = abs(start[1] - end[1])

        interrupt = False
        if (dx > dy):
            for j in range(int(start[0]), int(end[0]), 1 if end[0] > start[0] else -1):
                if (collision_mask[j][int(m * j + q)] == 1):
                    self.interrupt_points.append((j, int(m * j + q)))
                    interrupt = True
                    break
        else:
            for j in range(int(start[1]), int(end[1]), 1 if end[1] > start[1] else -1):
                if (collision_mask[int((j - q) / m)][j] == 1):
                    self.interrupt_points.append((int((j - q) / m), j))
                    interrupt = True
                    break

        if (interrupt):
            self.mouse_startpoints.pop(i)
            self.mouse_endpoints.pop(i)
            self.start_interrupt_points.append(start)
        else:
            i += 1

    self.min_dist_index = 0
    for i in range(len(self.mouse_endpoints)):
        dist = abs(mouse_coords[0] - self.mouse_endpoints[i][0]) + abs(mouse_coords[1] - self.mouse_endpoints[i][1])
        min_dist = abs(mouse_coords[0] - self.mouse_endpoints[self.min_dist_index][0]) + abs(
            mouse_coords[1] - self.mouse_endpoints[self.min_dist_index][1])
        if (dist < min_dist):
            self.min_dist_index = i

    if (pawn[MOVING] and len(self.mouse_endpoints) > 0):
        pawn[POSITION] = pygame.Vector2(
            self.mouse_endpoints[self.min_dist_index][0],
            self.mouse_endpoints[self.min_dist_index][1]
        )
