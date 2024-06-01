import pygame
from PIL import Image
import random
import math
import os
from Drone import Drone
import time
# Coin class
class Coin:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.radius = 5  # Coin radius in pixels

    def draw(self, screen):
        pygame.draw.circle(screen, (128, 0, 128), self.pos, self.radius)  # purple  color

# DroneSimulation class
class DroneSimulation:
    def __init__(self):
        pygame.init()
        self.screen_width = 1366
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Drone Simulation")

        # Load map
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_dir)
        input_filepath = os.path.join(parent_directory, 'maps', 'p13.png')
        self.load_map(input_filepath)

        self.sensor_texts = {
            "Distance_Sensors": "Distance Sensors",
            "forward": "Forward: 0 cm",
            "backward": "Backward: 0 cm",
            "leftward": "Left: 0 cm",
            "rightward": "Right: 0 cm",
            "IMU": "IMU: 0",
            "Coins": "Coins Collected: 0",
            "Drone's battery": "0 %",
            "Drone's speed": "0",
            "P":"0",
            "I":"0",
            "D":"0",
            "is_hugging_right": "True"
        }

        # Initialize drone
        self.drone_radius = int(10 / 2.5)  # Convert cm to pixels
        self.drone = Drone()
        self.respawn_drone()

        self.clock = pygame.time.Clock()
        self.game_over = False

        # List to store drone positions for leaving a trail
        self.drone_positions = []

        # Array to remember painted pixels
        self.detected_pixels = set()

        # Coins
        self.number_of_spawned_coins = 150 # the number of coins to spawn
        self.coins = [] #store all coin instances
        self.spawn_coins(self.number_of_spawned_coins) # generates "number_of_spawned_coins" coins randomly on the map
        self.coins_collected = 0 # counter keeps track of collected coins

    def load_map(self, filename):
        map_img = Image.open(filename)
        map_img = map_img.resize((self.screen_width, self.screen_height))
        self.map_img = pygame.image.fromstring(map_img.tobytes(), map_img.size, map_img.mode)
        self.map_matrix = self.convert_to_matrix(map_img)

    def convert_to_matrix(self, img):
        bw_img = img.convert("L")  # Convert to grayscale
        threshold = 128  # Threshold value for black/white
        bw_matrix = []
        for y in range(self.screen_height):
            row = []
            for x in range(self.screen_width):
                pixel = bw_img.getpixel((x, y))
                if pixel < threshold:
                    row.append(1)  # Black pixel
                else:
                    row.append(0)  # White pixel
            bw_matrix.append(row)
        return bw_matrix

    def respawn_drone(self):
        while True:
            x = random.randint(self.drone_radius, self.screen_width - self.drone_radius - 1)
            y = random.randint(self.drone_radius, self.screen_height - self.drone_radius - 1)
            if not self.check_collision(x, y):
                self.drone_pos = [x, y]
                break

    def check_collision(self, x, y):
        for i in range(int(x - self.drone_radius), int(x + self.drone_radius)):
            for j in range(int(y - self.drone_radius), int(y + self.drone_radius)):
                if 0 <= i < self.screen_width and 0 <= j < self.screen_height:
                    if self.map_matrix[j][i] == 1:
                        return True
        return False

    # def move_drone_by_pressing(self, dx, dy):
    #     new_pos = [self.drone_pos[0] + dx, self.drone_pos[1] + dy]
    #     if (self.drone_radius <= new_pos[0] < self.screen_width - self.drone_radius and
    #             self.drone_radius <= new_pos[1] < self.screen_height - self.drone_radius):
    #         if not self.check_collision(new_pos[0], new_pos[1]):
    #             self.drone_pos = new_pos
    #             self.drone_positions.append(self.drone_pos[:])  # Add position to the trail
    #         else:
    #             self.reset_simulation()
    #     else:
    #         self.reset_simulation()

    # checks if the drone is inside the map and also is not collided, if it did reset the game
    def check_move_legality(self , new_pos):
        if (self.drone_radius <= new_pos[0] < self.screen_width - self.drone_radius and
                self.drone_radius <= new_pos[1] < self.screen_height - self.drone_radius):
            if not self.check_collision(new_pos[0], new_pos[1]):
                self.drone_pos = new_pos
                self.drone_positions.append(self.drone_pos[:])  # Add position to the trail
            else:
                self.reset_simulation()
        else:
            self.reset_simulation()

    def move_drone_by_direction(self, direction = "forward"):
        # Calculate new position
        new_pos = self.drone.move_drone(self.drone_pos , direction)
        self.check_move_legality(new_pos)
                
    def update_drone_angle(self, angle_delta):
        self.drone.update_drone_angle(angle_delta)

    def update_sensors(self):
        self.drone.update_sensors(self.map_matrix, self.drone_pos, self.drone_radius, self.drone.orientation_sensor.drone_orientation)

    def paint_detected_points(self):
        def get_detected_points(sensor_distance, angle_offset):
            angle_rad = math.radians((self.drone.orientation_sensor.drone_orientation + angle_offset) % 360)
            points = []
            for dist in range(1, int(min(sensor_distance, 300) / 2.5) + 1):
                x = self.drone_pos[0] + dist * math.cos(angle_rad)
                y = self.drone_pos[1] + dist * math.sin(angle_rad)
                if 0 <= x < self.screen_width and 0 <= y < self.screen_height:
                    if self.map_matrix[int(y)][int(x)] == 0:  # Check if the point is in the white area
                        points.append((int(x), int(y)))
            return points

        # Get detected points for left and right sensors
        left_points = get_detected_points(self.drone.leftward_distance_sensor.distance, -90)
        right_points = get_detected_points(self.drone.rightward_distance_sensor.distance, 90)

        # Calculate the new points to be added
        new_detected_points = set(left_points + right_points)
        points_to_paint = new_detected_points - self.detected_pixels

        # Update the main set of detected pixels
        self.detected_pixels.update(new_detected_points)

        # Create a surface for detected points if not exists
        if not hasattr(self, 'detected_surface'):
            self.detected_surface = pygame.Surface((self.screen_width, self.screen_height))
            self.detected_surface.set_colorkey((0, 0, 0))  # Set transparent color

        # Paint only the new points on the detected surface
        for x, y in points_to_paint:
            self.detected_surface.set_at((x, y), (255, 255, 0))

        # Blit the detected surface onto the main screen
        self.screen.blit(self.detected_surface, (0, 0))

    def reset_simulation(self):
        self.detected_pixels.clear()  # Clear detected points
        self.respawn_drone()  # Respawn the drone
        self.drone_positions.clear()  # Clear trail
        # empty the surface, ensuring that no previously detected points are displayed on the screen.
        if hasattr(self, 'detected_surface'):
            self.detected_surface.fill((0, 0, 0))  # Fill the detected surface with black color
        #restarting the coins
        self.coins.clear()
        self.coins_collected = 0
        self.sensor_texts["Coins"] = f"Coins Collected: {self.coins_collected} / {self.number_of_spawned_coins}"
        self.spawn_coins(self.number_of_spawned_coins)
        self.drone.optical_flow_sensor.reset_sensor()
        self.drone.battery_sensor.reset_battrey()
        
        
    def spawn_coins(self, num_coins):
        self.coins = []
        while len(self.coins) < num_coins:
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
            if self.map_matrix[y][x] == 0:  # Ensure coin is not inside a wall
                self.coins.append(Coin(x, y))

    def check_coin_collection(self):
        for coin in self.coins[:]:
            distance = math.sqrt((coin.pos[0] - self.drone_pos[0]) ** 2 + (coin.pos[1] - self.drone_pos[1]) ** 2)
            if distance <= 80:  # 80 pixels is equivalent to 2 meter
                self.coins.remove(coin)
                self.coins_collected += 1
                self.sensor_texts["Coins"] = f"Coins Collected: {self.coins_collected} / {self.number_of_spawned_coins}"


    # def check_coin_collection(self):
    #     for coin in self.coins[:]:
    #         # Calculate vector from drone to coin
    #         dx = coin.pos[0] - self.drone_pos[0]
    #         dy = coin.pos[1] - self.drone_pos[1]
            
    #         # Calculate angle between drone orientation and vector to coin
    #         angle_to_coin = math.degrees(math.atan2(dy, dx))
    #         angle_difference = abs(angle_to_coin - self.drone.orientation_sensor.drone_orientation)
    #         angle_difference = min(angle_difference, 360 - angle_difference)  # Take the smallest angle
            
    #         # Check if the angle difference is within the acceptable range for either side (e.g., 10 degrees)
    #         if abs(angle_difference - 90) < 10 or abs(angle_difference - 270) < 10:
    #             distance = math.sqrt(dx ** 2 + dy ** 2)
    #             if distance <= 80:  # 80 pixels is equivalent to 2 meters
    #                 self.coins.remove(coin)
    #                 self.coins_collected += 1
    #                 self.sensor_texts["Coins"] = f"Coins Collected: {self.coins_collected} / {self.number_of_spawned_coins}"


    def run_simulation(self):
        
        # Define the desired frequency (10 times per second)
        frequency = 10  # Hz
        interval = 1000 // frequency  # Convert frequency to milliseconds
        sensors_update_timer = pygame.time.get_ticks()  # Initialize timer for sensors update
        last_time = time.time()

        PID_value_change = 0.005
        while not self.game_over:

            current_time_test = time.time()
            dt = current_time_test - last_time
            last_time = current_time_test

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.move_drone_by_direction("backward")
            if keys[pygame.K_RIGHT]:
                self.move_drone_by_direction("forward")
            if keys[pygame.K_UP]:
                self.move_drone_by_direction("leftward")
            if keys[pygame.K_DOWN]:
                self.move_drone_by_direction("rightward")
            if keys[pygame.K_a]:
                self.update_drone_angle(-10)
            if keys[pygame.K_d]:
                self.update_drone_angle(10)
            #FOR UPDATING P
            if keys[pygame.K_1]:
                self.drone.pid_controller.update_P_value(PID_value_change)
            if keys[pygame.K_2]:
                self.drone.pid_controller.update_P_value(-PID_value_change)
            #FOR UPDATING I    
            if keys[pygame.K_3]:
                self.drone.pid_controller.update_I_value(PID_value_change)
            if keys[pygame.K_4]:
                self.drone.pid_controller.update_I_value(-PID_value_change)
            #FOR UPDATING D
            if keys[pygame.K_5]:
                self.drone.pid_controller.update_D_value(PID_value_change)
            if keys[pygame.K_6]:
                self.drone.pid_controller.update_D_value(-PID_value_change)
            if keys[pygame.K_q]:
                self.drone.switch_wall(True)
            if keys[pygame.K_e]:
                self.drone.switch_wall(False)    
                


            # Check if the right arrow key is pressed to update the speed
            if keys[pygame.K_w]:
                self.drone.optical_flow_sensor.update_speed_acceleration()
                        
            if keys[pygame.K_s]:
                self.drone.optical_flow_sensor.update_speed_deceleration()   


            # Check if it's time to update the sensors , we want to update 10 times per second
            current_time = pygame.time.get_ticks()
            if current_time - sensors_update_timer >= interval:
                # Update sensors
                self.update_sensors()
                sensors_update_timer = current_time  # Reset the timer
            

            # Update drone position by algorithm
            self.drone_pos = self.drone.update_position_by_algorithm(self.drone_pos, len(self.coins), dt)
            self.check_move_legality(self.drone_pos)
            # Check coin collection
            self.check_coin_collection()

            # Blit the map image onto the screen
            self.screen.blit(self.map_img, (0, 0))

            # Paint detected points (yellow markers)
            self.paint_detected_points()

            # Blit the drone trail onto the screen
            for pos in self.drone_positions:
                pygame.draw.circle(self.screen, (0, 0, 255), pos, 2)

            # Draw arrow on the drone indicating its direction
            angle_rad = math.radians(self.drone.orientation_sensor.drone_orientation)
            end_x = self.drone_pos[0] + 15 * math.cos(angle_rad)
            end_y = self.drone_pos[1] + 15 * math.sin(angle_rad)
            pygame.draw.line(self.screen, (0, 0, 0), self.drone_pos, (end_x, end_y), 2)

            # Blit the drone onto the screen
            pygame.draw.circle(self.screen, (255, 0, 0), self.drone_pos, self.drone_radius)

            # Draw coins
            for coin in self.coins:
                coin.draw(self.screen)

            # Update sensor texts
            self.sensor_texts["forward"] = f"Forward: {self.drone.forward_distance_sensor.distance:.1f} cm"
            self.sensor_texts["backward"] = f"Backward: {self.drone.backward_distance_sensor.distance:.1f} cm"
            self.sensor_texts["leftward"] = f"Left: {self.drone.leftward_distance_sensor.distance:.1f} cm"
            self.sensor_texts["rightward"] = f"Right: {self.drone.rightward_distance_sensor.distance:.1f} cm"
            self.sensor_texts["IMU"] = f"IMU: {(360 - self.drone.orientation_sensor.drone_orientation) % 360:.1f}"
            self.sensor_texts["Drone's battery"] = f"Drone's battery: {self.drone.battery_sensor.get_battrey_precentage():.1f} %"
            self.sensor_texts["Drone's speed"] = f"Drone's speed: {self.drone.optical_flow_sensor.get_current_speed():.1f}"
            self.sensor_texts["P"] = f"P: {self.drone.pid_controller.P:.3f}"
            self.sensor_texts["I"] = f"I: {self.drone.pid_controller.I:.3f}"
            self.sensor_texts["D"] = f"D: {self.drone.pid_controller.D:.3f}"
            self.sensor_texts["is_hugging_right"] = f"is_hugging_right: {self.drone.is_hugging_right}"

            # Display sensor texts
            font = pygame.font.Font(None, 36)
            for i, (key, text) in enumerate(self.sensor_texts.items()):
                text_surface = font.render(text, True, (100, 100, 50))
                self.screen.blit(text_surface, (10, self.screen_height - 40 - i * 30))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


def main():
    simulation = DroneSimulation()
    simulation.run_simulation()

if __name__ == "__main__":
    main()
