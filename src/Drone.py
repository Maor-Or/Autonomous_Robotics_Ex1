from IMU import IMU
from BatterySensor import BatterySensor
from DistanceSensor import DistanceSensor
import math
from OpticalFlow import OpticalFlow
from PIDController import PIDController
import time
   
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
        self.desired_wall_distance = 25 # Desired distance from the wall in cm
        # Variables for wall following
        self.is_hugging_right = True  # Start by hugging the right wall
        self.starting_position = None # starting postion of the drone
        self.trail = []
        self.returning_to_start = False
        self.use_pid = True
        self.cooldown = False
        self.cooldown_start_time = 0

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

    def check_for_repeated_path(self):
        return

    def switch_wall(self ):
        self.use_pid = False
        # Adjust drone to look 10 degrees away from the current wall
        angle_delta = -10 if self.is_hugging_right else 10
        self.update_drone_angle(angle_delta)


    def wall_following(self, drone_pos, dt):
        #if we dont use PID
        if not self.use_pid:
            if self.is_hugging_right:
            #checking if the drone should move without the PID
                if  self.forward_distance_sensor.distance > 40 and self.leftward_distance_sensor.distance > 40:
                    # Move forward without PID control
                    new_pos = self.move_drone(drone_pos, "forward")
                    return new_pos
                else:
                    # Re-enable wall hugging after moving forward
                    self.is_hugging_right = not self.is_hugging_right
                    self.use_pid = True
            else:
                if  self.forward_distance_sensor.distance > 40 and self.rightward_distance_sensor.distance > 40:
                    # Move forward without PID control
                    new_pos = self.move_drone(drone_pos, "forward")
                    return new_pos
                else:
                    # Re-enable wall hugging after moving forward
                    self.is_hugging_right = not self.is_hugging_right
                    self.use_pid = True
            

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

        return new_pos

    def update_position_by_algorithm(self, drone_pos, dt):
        # Check battery level and initiate return if necessary
        if self.battery_sensor.get_battrey_precentage() <= 50 and not self.returning_to_start:
            self.returning_to_start = True

        if self.returning_to_start:
            # Get the next position on the return trail
            new_pos = self.get_next_position_for_trailback()
        else:
            # Then perform wall-following
            new_pos = self.wall_following(drone_pos,dt)
 
            if time.time() - self.cooldown_start_time >= 3:
                self.cooldown = False

            #if there is cooldown is over you can switch wall    
            if not self.cooldown:
                if self.is_in_trail_environment(new_pos):
                    print("should switch walls")
                    self.switch_wall()
                    self.cooldown = True
                    self.cooldown_start_time = time.time()

        return new_pos

    
    def set_starting_position(self, position):
        self.starting_position = position
        self.trail = [position]  # Initialize the trail with the starting position

    def update_position(self, position):
        if not self.returning_to_start:
            self.trail.append(position)
        else:
            self.trail.pop()  # Remove the last position as the drone moves back

    def get_next_position_for_trailback(self):
        if len(self.trail) > 1:
            next_position = self.trail[-2]  # Get the second to last position
            self.update_angle_to_next_position_for_trailback(next_position)
            return next_position
        else:
            self.returning_to_start = False  # Reached the start
            return self.starting_position

    def update_angle_to_next_position_for_trailback(self, next_position):
        # Calculate the angle needed to face the next position
        current_position = self.trail[-1]
        dx = next_position[0] - current_position[0]
        dy = next_position[1] - current_position[1]
        angle_to_next_position = math.degrees(math.atan2(dy, dx))
        
        # Update the drone's angle to face the next position
        self.orientation_sensor.update_orientation(angle_to_next_position)
        
    def is_in_trail_environment(self, point, radius = 0.5):
        for trail_point in self.trail:
            distance = math.sqrt((point[0] - trail_point[0]) ** 2 + (point[1] - trail_point[1]) ** 2)
            if distance <= radius:
                return True
        return False
