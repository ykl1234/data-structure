import csv
from heapq import heappop, heappush
from collections import defaultdict


class Dijkstra:
    def __init__(self, csv_path):
        self.graph = defaultdict(list)
        self.read_csv(csv_path)

    def read_csv(self, csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过标题行
            for start, end, weight in reader:
                self.graph[int(start)].append((int(end), float(weight)))
                self.graph[int(end)].append((int(start), float(weight)))  # 无向图，需要添加反向边

    def find_shortest_path(self, start, end):
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        predecessors = {node: None for node in self.graph}

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            if current_node == end:
                break

            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heappush(priority_queue, (distance, neighbor))

        return distances, predecessors

    def get_shortest_path(self, start, end):
        distances, predecessors = self.find_shortest_path(start, end)
        path = []
        current = end
        while current is not None:
            path.insert(0, current)
            current = predecessors[current]

        return path, distances[end]
