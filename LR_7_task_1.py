import math
import random
import matplotlib.pyplot as pl
# дані були запсані у окремий файл, для кращого розуміння
from data import smpl_prblm_dis, smpl_prblm_map, Ukraine_dis, Ukraine_map, graph_dis, graph_map, shop_dis, shop_map

# змінні
vrnt = 13 # номер варіанта за журналом
alpha = 1.0
beta = 5.0
rho = 0.5  # P
Q = 10
iterations = 10000

city_mapping = shop_map  # назви міст
city_count = len(city_mapping)
distances = shop_dis  # матриця відстаней
y = list()  # зміна для графіку відображення найкращого шляху


class Ant:
    def __init__(self, parent):
        self.parent = parent
        self.position = vrnt - 1 # віднімаємо 1, тому що в масиві відрахунок починається з 0
        self.start = self.position
        self.totalDist = 0.0
        self.tList = [self.position]
        self.myPheromone = []

    def travel(self):
        if len(self.tList) == city_count:
            self.tList.remove(self.start)


        p_array = [0 for _ in range(city_count)]
        summa = 0
        # використовуємо формулу для вірогідності відвідування наступних точок
        for i in range(city_count):
            if i not in self.tList:
                summa += (self.parent.pheromones[self.position][i] ** alpha) * (self.parent.visibility[self.position][i] ** beta)
        for i in range(city_count):
            if i not in self.tList:
                try:
                    p_array[i] = (self.parent.pheromones[self.position][i] ** alpha) * (
                            self.parent.visibility[self.position][
                                i] ** beta) / summa
                except:
                    pass
        # перевірка, щоб міста не повторювались
        revers = list(filter(lambda p: p not in self.tList, [i for i in range(city_count)]))
        revers.reverse()
        next_city = revers[0]
        # визначаємо наступну точку за рандомом
        winner_num = random.random() * sum(p_array)
        for i, probability in enumerate(p_array):
            winner_num -= probability
            if winner_num <= 0:
                next_city = i
                break
        # записуємо наступне місце
        newd = distances[self.position][next_city]
        self.totalDist += newd if newd > 0 and next_city not in self.tList else math.inf
        self.tList.append(next_city)
        self.position = next_city

    def update_ways(self):
        # оновлюємо феромон на відвіданих гранях
        self.myPheromone = [[0.0 for _ in range(city_count)] for __ in range(city_count)]
        for i in range(1, len(self.tList)):
            k = self.tList[i - 1]
            j = self.tList[i]
            self.myPheromone[k][j] = Q / self.totalDist


class Colony:
    smallestCost = math.inf
    optimal_way = []
    ants = []
    pheromones = None
    visibility = None

    def __init__(self):
        # початкова кількість феромону та нульове
        self.pheromones = [[1 / (city_count * city_count) for _ in range(city_count)] for __ in range(city_count)]
        # ета - обернена відстань
        self.visibility = [[0 if i == j else 1 / distances[i][j] for i in range(city_count)] for j in range(city_count)]

    def do_main(self):
        self.smallestCost = math.inf
        self.optimal_way = []
        # ГОЛОВНИЙ ЦИКЛ
        for t in range(iterations):
            self.reload_ants()
            self.move_ants()
            self.update_ways()
            # дані для графіка
            y.append(self.smallestCost)
        return self.smallestCost, self.optimal_way

    def move_ants(self):
        for ant in self.ants:
            # подорож по всім містам
            for i in range(city_count):
                ant.travel()
            # визначаємо оптимальний шлях
            if ant.totalDist < self.smallestCost:
                self.smallestCost = ant.totalDist
                self.optimal_way = [ant.tList[-1]] + ant.tList
            ant.update_ways()

    def update_ways(self):
        # випаровуємо і додаємо ферамони
        for i, row in enumerate(self.pheromones):
            for j, col in enumerate(row):
                self.pheromones[i][j] *= rho
                for ant in self.ants:
                    self.pheromones[i][j] += ant.myPheromone[i][j]

    def reload_ants(self):
        # під час оновлення агентів, вважаю що 80% оптимально, тому множимо на 0.8
        self.ants = [Ant(self) for _ in range(round(city_count * 0.8))]


dist, path = Colony().do_main()
print(f"Оптимальний результат: {dist}, шлях: {' -> '.join(city_mapping[i] for i in path)}")
# відображаємо результат на графіку
pl.figure()
pl.plot([x for x in range(city_count + 1)], path, )
for i, txt in enumerate(city_mapping):
    pl.annotate(txt, (path.index(i), i))
pl.show()
