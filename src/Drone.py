#from IMU import IMU
#from BatterySensor import BatterySensor
from DistanceSensor import DistanceSensor
#from OpticalFlow import OpticalFlow

# class Drone:
#     def __init__(self, autonomous_algorithm_func):
#         self.battery_sensor = BatterySensor()
#         self.optical_flow_sensor = OpticalFlow()
#         self.orientation_sensor = IMU()
#         self.forward_distance_sensor = DistanceSensor ("forward")
#         self.backward_distance_sensor = DistanceSensor ("backward")
#         self.leftward_distance_sensor = DistanceSensor ("leftward")
#         self.rightward_distance_sensor = DistanceSensor ("rightward")
#         self.autonomous_algorithm_func = autonomous_algorithm_func

#     def update_postion_by_algorithm(self):

# Drone class
class Drone:
    def __init__(self):
        self.forward_distance_sensor = DistanceSensor("forward")
        self.backward_distance_sensor = DistanceSensor("backward")
        self.leftward_distance_sensor = DistanceSensor("leftward")
        self.rightward_distance_sensor = DistanceSensor("rightward")

    def update_sensors(self, map_matrix, position, orientation):
        self.forward_distance_sensor.update_values(map_matrix, position, orientation)
        self.backward_distance_sensor.update_values(map_matrix, position, orientation)
        self.leftward_distance_sensor.update_values(map_matrix, position, orientation)
        self.rightward_distance_sensor.update_values(map_matrix, position, orientation)
