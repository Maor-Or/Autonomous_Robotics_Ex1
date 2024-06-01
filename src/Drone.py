from IMU import IMU
from BatterySensor import BatterySensor
from DistanceSensor import DistanceSensor
import math
from OpticalFlow import OpticalFlow
from PIDController import PIDController

class Drone:
    def __init__(self):
        self.battery_sensor = BatterySensor() #battery is initialing with 100%
        self.optical_flow_sensor = OpticalFlow()
        self.forward_distance_sensor = DistanceSensor("forward")
        self.backward_distance_sensor = DistanceSensor("backward")
        self.leftward_distance_sensor = DistanceSensor("leftward")
        self.rightward_distance_sensor = DistanceSensor("rightward")
        self.orientation_sensor = IMU() #the drone's angle, the drone is looking rightward, beginning at 0
        self.pid_controller = PIDController(0.085, 0, 0.05, 5)  
        self.forward_pid_controller = PIDController(1.6,0, 0.03, 5)
        self.narrow_pid_controller = PIDController(0.03,0, 0.03, 5)
        self.desired_wall_distance = 20 # Desired distance from the wall in cm
        # Initialize variables for path tracking
        self.current_path = []
        self.previous_paths = []
        # Variables for wall following
        self.is_hugging_right = True  # Start by hugging the right wall

    def update_sensors(self, map_matrix, position, drone_radius, orientation):
        self.forward_distance_sensor.update_values(map_matrix, position, drone_radius, orientation)
        self.backward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        self.leftward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        self.rightward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        self.battery_sensor.update_battrey_precentage()
        
    def move_drone(self,drone_pos , direction):
        directions = {
            "forward": 0,
            "backward": 180,
            "leftward": 270,
            "rightward": 90
        }
          
        dx = math.cos(math.radians(self.orientation_sensor.drone_orientation + directions[direction])) * self.optical_flow_sensor.current_speed  # moves in the x axis in a speed relatively to the drone's angle 
        dy = math.sin(math.radians(self.orientation_sensor.drone_orientation + directions[direction])) * self.optical_flow_sensor.current_speed  # moves in the y axis in a speed relatively to the drone's angle
        new_pos = [drone_pos[0] + dx, drone_pos[1] + dy]

        return new_pos
    
    def update_drone_angle(self,angle_delta):
        self.orientation_sensor.update_orientation ((self.orientation_sensor.drone_orientation + angle_delta) % 360) 

    def update_path(self, new_position):
        # Update the current path with the new position
        self.current_path.append(new_position)

    def update_previous_paths(self):
        # Update the previous paths array with the current path
        self.previous_paths = self.current_path

    def check_for_repeated_path(self):
        # Compare the current path with previous paths
        for path in self.previous_paths:
            if len(path) == len(self.current_path) and path == self.current_path:
                return True  # Current path is too similar to a previous path
        return False

    def switch_wall(self , flag):
        # Switch to hug the opposite wall
        self.is_hugging_right = flag
        # Clear the current path to start tracking a new path
        #self.current_path = []

    def wall_following(self, drone_pos, dt):

        # Calculate the error from the desired wall distance
        if not self.is_hugging_right: #self.leftward_distance_sensor.distance < 35:  # Detect the wall on the left side
            error = -1 *(self.leftward_distance_sensor.distance - self.desired_wall_distance)
        else:
            error = self.rightward_distance_sensor.distance - self.desired_wall_distance

        turnning_direction = -1 if self.is_hugging_right else 1
        # Calculate the left / right wall hugging correction using the PID controller
        overall_correction = self.pid_controller.update(error, dt)

        # Calculate the correction for case the drone's front is getting too close to a wall
        front_danger_distance = 65
        if(self.forward_distance_sensor.distance >= front_danger_distance):
            forward_distance_error = 0
        else:
            forward_distance_error = front_danger_distance - self.forward_distance_sensor.distance 

        forward_correction = self.forward_pid_controller.update(forward_distance_error, dt)
        
        
        narrow_path_error = 0
        if self.is_hugging_right and self.leftward_distance_sensor.distance < self.rightward_distance_sensor.distance :
            narrow_path_error = self.rightward_distance_sensor.distance - self.leftward_distance_sensor.distance
        elif not self.is_hugging_right and self.leftward_distance_sensor.distance > self.rightward_distance_sensor.distance :
            narrow_path_error = self.rightward_distance_sensor.distance - self.leftward_distance_sensor.distance 

        narrow_correction = self.narrow_pid_controller.update(narrow_path_error , dt)

        #Sum up the corrections for the wall hugging and the drone's front error correction
        overall_correction +=  (forward_correction * turnning_direction) + narrow_correction

        # Limit the correction to prevent aggressive maneuvers
        max_correction = 10  # Define a maximum correction angle
        overall_correction = max(-max_correction, min(overall_correction, max_correction))

        # Adjust the drone's angle based on the correction
        self.update_drone_angle(overall_correction)

        # Move the drone forward
        new_pos = self.move_drone(drone_pos, "forward")

        # Update the path with the current position
        self.update_path(new_pos)

        # # Check if the current path is too similar to a previous path
        # if self.check_for_repeated_path():
        #     # Switch to hug the opposite wall
        #     self.switch_wall()

        # Update previous paths
        self.update_previous_paths()

        return new_pos

    def update_position_by_algorithm(self, drone_pos, coins_left, dt):

        # Then perform wall-following
        new_pos = self.wall_following(drone_pos,dt)

        return new_pos
        

