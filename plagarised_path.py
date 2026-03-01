import math
import csv
from utils.geometry import normalize_angle


class PurePursuitController:
   def __init__(self, path_file, lookahead_distance=1.5, max_speed=1.5):
       self.lookahead_distance = lookahead_distance
       self.max_speed = max_speed
       self.path = self.load_path(path_file)
       self.current_index = 0


   def load_path(self, path_file):
       path = []
       with open(path_file, 'r') as f:
           reader = csv.reader(f)
           next(reader)  # skip header if there is one
           for row in reader:
               x, y = float(row[0]), float(row[1])
               path.append((x, y))
       return path


   def find_lookahead_point(self, rover_x, rover_y):
       """Find the point on the path that is lookahead_distance away."""
       for i in range(self.current_index, len(self.path)):
           px, py = self.path[i]
           dist = math.sqrt((px - rover_x)**2 + (py - rover_y)**2)
           if dist >= self.lookahead_distance:
               self.current_index = i 
               return px, py
       return self.path[-1]


   def is_path_complete(self, rover_x, rover_y, threshold=0.5):
       """Check if rover has reached the end of the path."""
       last_x, last_y = self.path[-1]
       dist = math.sqrt((last_x - rover_x)**2 + (last_y - rover_y)**2)
       return dist < threshold


   def compute_controls(self, rover_x, rover_y, rover_theta):
       """Returns (v, omega) to follow the path."""
       if self.is_path_complete(rover_x, rover_y):
           return 0.0, 0.0
       target_x, target_y = self.find_lookahead_point(rover_x, rover_y)


       angle_to_target = math.atan2(target_y - rover_y, target_x - rover_x)


       steering_error = normalize_angle(angle_to_target - rover_theta)


       v = self.max_speed * (1 - 0.5 * abs(steering_error) / math.pi)
       v = max(0.3, min(v, self.max_speed))


       omega = 2.0 * steering_error


       return v, omega
