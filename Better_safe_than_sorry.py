Import math
from utils.geometry import normalize_angle


class ObstacleAvoidance:
   def __init__(self, safety_distance=1.0, free_distance=1.5, forward_fov=60):
       self.safety_distance = safety_distance 
       self.free_distance = free_distance     
       self.forward_fov = forward_fov         


   def is_obstacle_ahead(self, lidar_readings):
       for angle, distance in lidar_readings:
           if angle > 180:
               angle -= 360
           if abs(angle) <= self.forward_fov / 2:
               if distance < self.safety_distance:
                   return True
       return False


   def get_best_gap_direction(self, lidar_readings, goal_angle):
       """
       Find the free beam whose angle is closest to goal_angle
       goal_angle: direction toward the lookahead point (radians)
       """
       best_angle = None
       best_diff = float('inf')


       for angle, distance in lidar_readings:
           if angle > 180:
               angle -= 360
           if distance >= self.free_distance:
               angle_rad = math.radians(angle)
               diff = abs(normalize_angle(angle_rad - goal_angle))
               if diff < best_diff:
                   best_diff = diff
                   best_angle = angle_rad


       return best_angle 


   def compute_controls(self, rover_x, rover_y, rover_theta,
                        lidar_readings, v_planned, omega_planned,
                        goal_x, goal_y):
       """
       Main function — call this every simulation step
       Returns (v, omega)
       """


       goal_angle = math.atan2(goal_y - rover_y, goal_x - rover_x)


       if not self.is_obstacle_ahead(lidar_readings):
           return v_planned, omega_planned


       best_direction = self.get_best_gap_direction(lidar_readings, goal_angle)


       if best_direction is None:
           print("Completely blocked - stopping!")
           return 0.0, 0.0




       steering_error = normalize_angle(best_direction - rover_theta)
       v = 0.5                     
       omega = 2.0 * steering_error


       print(f"Avoiding obstacle - steering to {math.degrees(best_direction):.1f}°")
       return v, omega
