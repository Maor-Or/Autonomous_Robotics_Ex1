#from IMU import IMU
#from BatterySensor import BatterySensor
from DistanceSensor import DistanceSensor
import math
#from OpticalFlow import OpticalFlow

# Drone class
class Drone:
    def __init__(self):
        # self.battery_sensor = BatterySensor()
        # self.optical_flow_sensor = OpticalFlow()
        #self.orientation_sensor = IMU()
        self.forward_distance_sensor = DistanceSensor("forward")
        self.backward_distance_sensor = DistanceSensor("backward")
        self.leftward_distance_sensor = DistanceSensor("leftward")
        self.rightward_distance_sensor = DistanceSensor("rightward")
        self.drone_angle_forward=0 #the drone's angle, the drone is looking rightward
        self.drone_speed = 4 # drone's speed per sec , 10 cm per second 10 / 0.025

    def update_sensors(self, map_matrix, position, drone_radius, orientation):
        self.forward_distance_sensor.update_values(map_matrix, position, drone_radius, orientation)
        self.backward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        self.leftward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        self.rightward_distance_sensor.update_values(map_matrix, position, drone_radius,orientation)
        

    def move_drone(self,drone_pos):
        # Calculate new position
        dx = math.cos(math.radians(self.drone_angle_forward)) * self.drone_speed  # moves in the x axis in a speed relatively to the drone's angle 
        dy = math.sin(math.radians(self.drone_angle_forward)) * self.drone_speed  # moves in the y axis in a speed relatively to the drone's angle 
        new_pos = [drone_pos[0] + dx, drone_pos[1] + dy]
        return new_pos,dx,dy

    def update_drone_angle(self,angle_delta):
        self.drone_angle_forward = (self.drone_angle_forward + angle_delta) % 360
        




    #         self.autonomous_algorithm_func = autonomous_algorithm_func

#     def update_postion_by_algorithm(self):    
