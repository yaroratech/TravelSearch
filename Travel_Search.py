import heapq, random, pickle, math, time
from math import pi, acos, sin, cos
from tkinter import *
from collections import deque

class PriorityQueue():
   def __init__(self):
      self.queue = []
      current = 0

   def next(self):
      if self.current >= len(self.queue):
         self.current
         raise StopIteration

      out = self.queue[self.current]
      self.current += 1

      return out

   def __iter__(self):
      return self

   __next__ = next

   def isEmpty(self):
      return len(self.queue) == 0

   def remove(self, index):
      del self.queue[index]
      return None

   def pop(self):
      return heapq.heappop(self.queue)

   def push(self, value):
      heapq.heappush(self.queue, value)

   def peek(self):
      return self.queue[0]
   
def calc_edge_cost(y1, x1, y2, x2):
   y1  = float(y1)
   x1  = float(x1)
   y2  = float(y2)
   x2  = float(x2)
   R   = 3958.76 # miles = 6371 km

   y1 *= pi/180.0
   x1 *= pi/180.0
   y2 *= pi/180.0
   x2 *= pi/180.0
   # approximate great circle distance with law of cosines
   return acos( sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(x2-x1) ) * R

def make_graph(nodes = "rrNodes.txt", node_city = "rrNodeCity.txt", edges = "rrEdges.txt"):
   nodeLoc, nodeToCity, cityToNode, neighbors, edgeCost = {}, {}, {}, {}, {}
   map = {}   # have screen coordinate for each node location

   for line in open(nodes, 'r'):
      string = line[0:len(line)-1].split(" ")
      nodeLoc[string[0]] = (string[1], string[2])
   for node in nodeLoc:
      lat = float(nodeLoc[node][0])
      long = float(nodeLoc[node][1])
      modlat = (lat - 10)/60 #scales to 0-1
      modlong = (long+130)/70 #scales to 0-1
      map[node] = [modlat*800, modlong*1200] #scales to fit 800 1200
   for line in open(node_city, 'r'):
      string = line[0:len(line)-1].split(" ")
      if len(string) == 3:
         nodeToCity[string[0]] = string[1] + " " + string[2]
         cityToNode[string[1] + " " + string[2]] = string[0]
      else:
         nodeToCity[string[0]] = string[1]
         cityToNode[string[1]] = string[0]
   for line in open(edges, 'r'):
      string = line[0:len(line) - 1].split(" ")
      edgeCost[(string[0], string[1])] = dist_heuristic(string[0], string[1], [nodeLoc, nodeToCity])
      edgeCost[(string[1], string[0])] = dist_heuristic(string[1], string[0], [nodeLoc, nodeToCity])
      if string[0] in neighbors:
         neighbors[string[0]].append(string[1])
      else:
         neighbors[string[0]] = [string[1]]
      if string[1] in neighbors:
         neighbors[string[1]].append(string[0])
      else:
         neighbors[string[1]] = [string[0]]
   return [nodeLoc, nodeToCity, cityToNode, neighbors, edgeCost, map]

def dist_heuristic(n1, n2, graph):
   return calc_edge_cost(graph[0][n1][0], graph[0][n1][1], graph[0][n2][0], graph[0][n2][1])

def display_path(path, graph):
   #nodetocity, citytonode
   citypath = []
   for state in path:
      if state in graph[1]:
         citypath.append(graph[1][state])
   print(citypath)

def generate_path(state, explored, graph):
   path = [state]
   cost = 0
   while explored[state] != 's':
      cost += graph[4][(state, explored[state])]
      state = explored[state]
      path.append(state)
   return path[::-1], cost

def drawLine(canvas, y1, x1, y2, x2, col):
   x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)   
   canvas.create_line(x1, 800-y1, x2, 800-y2, fill=col)

def draw_final_path(ROOT, canvas, path, graph, col='red'):
   x = 0
   for state in path[:len(path)-1]:
      drawLine(canvas, graph[5][state][0], graph[5][state][1], graph[5][path[x+1]][0], graph[5][path[x+1]][1], col = 'red')
      x+= 1
   ROOT.update()

def draw_all_edges(ROOT, canvas, graph):
   ROOT.geometry("1200x800")
   canvas.pack(fill=BOTH, expand=1)
   for n1, n2 in graph[4]:  #graph[4] keys are edge set
      drawLine(canvas, *graph[5][n1], *graph[5][n2], 'white') #graph[5] is map dict
   ROOT.update()

# Node: (lat, long) or (y, x), node: city, city: node, node: neighbors, (n1, n2): cost
def bfs(start, goal, graph, col):
   ROOT = Tk() #creates new tkinter
   ROOT.title("BFS")
   canvas = Canvas(ROOT, background='black') #sets background
   draw_all_edges(ROOT, canvas, graph)
   counter = 0
   frontier, explored = deque(), {start: "s"}
   frontier.append(start)
   while frontier:
      s = frontier.popleft()
      if s == goal:
         print('The number of explored nodes of BFS: ' + str(len(explored)))
         path, cost = generate_path(s, explored, graph)
         draw_final_path(ROOT, canvas, path, graph)
         return path, cost
      for a in graph[3][s]:  #graph[3] is neighbors
         if a not in explored:
            explored[a] = s
            frontier.append(a)
            drawLine(canvas, *graph[5][s], *graph[5][a], col)
      counter += 1
      if counter % 100 == 0: ROOT.update()
   return None

def bi_bfs(start, goal, graph, col):
   ROOT = Tk()
   ROOT.title("Bi-BFS")
   canvas = Canvas(ROOT, background = 'black')
   draw_all_edges(ROOT, canvas, graph)
   counter = 0
   frontier, explored = [], {start: "s"}
   fback = []
   explored2 = {goal: "s"}
   frontier.append((start, [start]))
   fback.append((goal, [goal]))
   while frontier and fback:
      parent, orig = frontier.pop(0)
      backward, borig = fback.pop(0)
      if parent in explored2:
         path, cost = generate_path(parent, explored, graph)
         path2, cost2 = generate_path(parent, explored2, graph)
         path2real = path2[::-1][1:]
         path3 = path + path2real
         print("The number of nodes explored: " + str(len(explored2) + len(explored) - 1))
         print("The Bi-BFS path: " + str(path3))
         print('The length of the path of Bi-BFS: ' + str(len(path+path2real)))
         draw_final_path(ROOT, canvas, path3, graph)
         return path3, cost + cost2
      elif backward in explored:
         path, cost = generate_path(backward, explored, graph)
         path2, cost2 = generate_path(backward, explored2, graph)
         path2real = path2[::-1][1:]
         path3 = path + path2real
         print("The number of nodes explored: " + str(len(explored2) + len(explored) - 1))
         print("The Bi-BFS path: " + str(path3))
         print('The length of the path of Bi-BFS: ' + str(len(path + path2real)))
         draw_final_path(ROOT, canvas, path3, graph)
         return path3, cost + cost2
      for x in graph[3][parent]:
         if x not in explored:
            explored[x] = parent
            frontier.append((x, orig + [x]))
            drawLine(canvas, *graph[5][parent], *graph[5][x], col)
      for y in graph[3][backward]:
         if y not in explored2:
            explored2[y] = backward
            fback.append((y, borig + [y]))
            drawLine(canvas, *graph[5][backward], *graph[5][y], col)
      counter += 1
      if counter % 100 == 0: ROOT.update()
   return None

def a_star(start, goal, graph, col, heuristic=dist_heuristic):
   ROOT = Tk()
   ROOT.title("A-Star")
   canvas = Canvas(ROOT, background = 'black')
   draw_all_edges(ROOT, canvas, graph)
   counter = 0
   frontier = PriorityQueue()
   if start == goal: return []
   explored = {start: dist_heuristic(start, goal, graph)}
   initial_dist = dist_heuristic(start, goal, graph)
   PriorityQueue.push(frontier, (initial_dist, start, [start]))
   while not frontier.isEmpty():
      parent = PriorityQueue.pop(frontier)
      explored[parent[1]] = parent[0]
      if parent[1] == goal:
         print('The number of explored nodes of A Star: ' + str(len(explored)))
         draw_final_path(ROOT, canvas, parent[2], graph)
         return parent[2], parent[0]
      for x in graph[3][parent[1]]:
         cost = parent[0] - dist_heuristic(parent[1], goal, graph) + graph[4][(parent[1], x)] + dist_heuristic(x, goal, graph)
         if x not in explored or explored[x] > cost:
            PriorityQueue.push(frontier, (cost, x, parent[2] + [x]))
            explored[x] = cost
            drawLine(canvas, *graph[5][parent[1]], *graph[5][x], col)
      counter += 1
      if counter % 100 == 0: ROOT.update()
   return None

def bi_a_star(start, goal, graph, col, heuristic=dist_heuristic):
   ROOT = Tk()
   ROOT.title("Bi-A-Star")
   canvas = Canvas(ROOT, background = 'black')
   draw_all_edges(ROOT, canvas, graph)
   frontier = PriorityQueue()
   fback = PriorityQueue()
   counter = 0
   if start == goal: return []
   explored = {start: (dist_heuristic(start, goal, graph), '')}
   explored2 = {goal: (dist_heuristic(start, goal, graph), '')}
   initial_dist = dist_heuristic(start, goal, graph)
   PriorityQueue.push(frontier, (initial_dist, start, [start], ''))
   PriorityQueue.push(fback, (initial_dist, goal, [goal], ''))
   while not frontier.isEmpty() and not fback.isEmpty():
      parent = PriorityQueue.pop(frontier)
      backward = PriorityQueue.pop(fback)
      explored[parent[1]] = (parent[0], parent[3])
      explored2[backward[1]] = (backward[0], backward[3])
      if parent[1] in explored2:
         print('hi"')
         z = path(explored2, parent[1])
         # z = backward[2][::-1].index(parent[1])
         # return parent[2] + backward[2][::-1][z+1:]
         print("Number of explored nodes: " + str(len(explored) + len(explored2) - 1))
         print("The length of Bi-A-Star is: " + str(len(parent[2] + z[1:])))
         draw_final_path(ROOT, canvas, parent[2] + z[1:], graph)
         print("The Whole path: " + str(parent[2] + z[1:]))
         print(parent[1])
         print(parent[0])
         return parent[2] + z[1:], parent[0]
      elif backward[1] in explored:
         z = path(explored, backward[1])
         # z = parent[2].index(backward[1])
         # return parent[2][:z] + backward[2][::-1]
         print("Number of explored nodes for Bi-A-Star: " + str(len(explored) + len(explored2) - 1))
         print("The length of Bi-A-Star is: " + str(len(z[::-1] + backward[2][::-1][1:])))
         draw_final_path(ROOT, canvas, z[::-1] + backward[2][::-1][1:], graph)
         print("The whole path: " + str(z[::-1] + backward[2][::-1][1:]))
         print(backward[1])
         print(backward[0])
         return z[::-1] + backward[2][::-1][1:], backward[0]
      for x in graph[3][parent[1]]:
         cost = parent[0] - dist_heuristic(parent[1], goal, graph) + graph[4][(parent[1], x)] + dist_heuristic(x, goal,
                                                                                                               graph)
         if x not in explored or explored[x][0] > cost:
            PriorityQueue.push(frontier, (cost, x, parent[2] + [x], parent[1]))  # heuristic(s1, goal) not needed
            explored[x] = (cost, parent[1])
            drawLine(canvas, *graph[5][parent[1]], *graph[5][x], col)
      for y in graph[3][backward[1]]:
         cost = backward[0] - dist_heuristic(backward[1], start, graph) + graph[4][(backward[1], y)] + dist_heuristic(y, start,
                                                                                                               graph)
         if y not in explored2 or explored2[y][0] > cost:
            PriorityQueue.push(fback, (cost, y, backward[2] + [y], backward[1]))
            explored2[y] = (cost, backward[1])
            drawLine(canvas, *graph[5][backward[1]], *graph[5][y], col)
      counter += 1
      if counter % 100 == 0: ROOT.update()
   return None

def path(explored, n):
   l = [] #n is parent[1]
   while explored[n][1] != 'test':
      l.append(n)
      if explored[n][1] == '':
         break
      n = explored[n][1]
   return l

def a_starnodraw(start, goal, graph, col, heuristic=dist_heuristic):
   frontier = PriorityQueue()
   if start == goal: return []
   explored = {start: dist_heuristic(start, goal, graph)}
   initial_dist = dist_heuristic(start, goal, graph)
   PriorityQueue.push(frontier, (initial_dist, start, [start]))
   while not frontier.isEmpty():
      parent = PriorityQueue.pop(frontier)
      explored[parent[1]] = parent[0]
      if parent[1] == goal:
         print('The number of explored nodes of A Star: ' + str(len(explored)))
         return parent[2], parent[0]
      for x in graph[3][parent[1]]:
         cost = parent[0] - dist_heuristic(parent[1], goal, graph) + graph[4][(parent[1], x)] + dist_heuristic(x, goal, graph)
         if x not in explored or explored[x] > cost:
            PriorityQueue.push(frontier, (cost, x, parent[2] + [x]))
            explored[x] = cost
   return None

def tri_directional(city1, city2, city3, graph, col, heuristic=dist_heuristic):
   path1, cost1 = a_starnodraw(city1, city2, graph, col)
   path2, cost2 = a_starnodraw(city2, city3, graph, col)
   path3, cost3 = a_starnodraw(city1, city3, graph, col)
   cit2 = cost1 + cost2
   cit1 = cost1 + cost3
   cit3 = cost2 + cost3
   minimum = min(cit1, cit2, cit3)
   if minimum == cit1:
      path4, cost4 = a_star(city1, city2, graph, col)
      path5, cost5 = a_star(city1, city3, graph, col)
      print("The Whole Path: " + str(path4 + path5[::-1][1:]))
      print("The length: " + str(len(path4 + path5[::-1][1:])))
      print("The cost: " + str(cost4 + cost5))
      return path4 + path5, cost4 + cost5
   elif minimum == cit2:
      path4, cost4 = a_star(city1, city2, graph, col)
      path5, cost5 = a_star(city2, city3, graph, col)
      print("The Whole Path: " + str(path4 + path5[::-1][1:]))
      print("The length: " + str(len(path4 + path5[::-1][1:])))
      print("The cost: " + str(cost4 + cost5))
      return path4 + path5[::-1][1:], cost4 + cost5
   else:
      path4, cost4 = a_star(city2, city3, graph, col)
      path5, cost5 = a_star(city1, city3, graph, col)
      print("The Whole Path: " + str(path4 + path5[::-1][1:]))
      print("The length: " + str(len(path4 + path5[::-1][1:])))
      print("The cost: " + str(cost4 + cost5))
      return path4 + path5[::-1][1:], cost4 + cost5
   return None
   
def main():
   start, goal, third = input("Start city: "), input("Goal city: "), input("Third city for tri-directional: ")
   #graph = make_graph("rrNodes.txt", "rrNodeCity.txt", "rrEdges.txt")
   with open("Travel_Search.pkl", "rb") as infile:
      graph = pickle.load(infile)
   print('neighbers check of 0100004', graph[3]['0100004'])

   print('edge cost from 0100004 to 0100003',
         graph[4][('0100004', '0100003')])
   cur_time = time.time()
   path, cost = bfs(graph[2][start], graph[2][goal], graph, 'yellow') #graph[2] is city to node
   if path != None:
      citypath = display_path(path, graph)
   else: print ("No Path Found.")
   print("The whole path: " + str(path[1:]))
   print("The length of the whole path: " + str(len(path[1:])))
   print(citypath)
   print ('BFS Path Cost:', cost)
   print ('BFS duration:', (time.time() - cur_time))
   print ()

   cur_time = time.time()
   path, cost = bi_bfs(graph[2][start], graph[2][goal], graph, 'green')
   if path != None: display_path(path, graph)
   else: print ("No Path Found.")
   print ('Bi-BFS Path Cost:', cost)
   print ('Bi-BFS duration:', (time.time() - cur_time))
   print ()

   cur_time = time.time()
   path, cost = a_star(graph[2][start], graph[2][goal], graph, 'blue')
   if path != None:
      citypath = display_path(path, graph)
   else: print ("No Path Found.")
   print("The whole path: " + str(path[1:]))
   print("The length of the whole path: " + str(len(path[1:])))
   print(citypath)
   print ('A star Path Cost:', cost)
   print ('A star duration:', (time.time() - cur_time))
   print ()

   cur_time = time.time()
   path, cost = bi_a_star(graph[2][start], graph[2][goal], graph, 'orange')
   if path != None: display_path(path, graph)
   else: print ("No Path Found.")
   print ('Bi-A star Path Cost:', cost)
   print ("Bi-A star duration: ", (time.time() - cur_time))
   print ()

   print ("Tri-Search of ({}, {}, {})".format(start, goal, third))
   cur_time = time.time()
   path, cost = tri_directional(graph[2][start], graph[2][goal], graph[2][third], graph, 'pink')
   if path != None: display_path(path, graph)
   else: print ("No Path Found.")
   print ('Tri-A star Path Cost:', cost)
   print ("Tri-directional search duration:", (time.time() - cur_time))

   mainloop() # Let TK windows stay still
 
if __name__ == '__main__':
   main()



