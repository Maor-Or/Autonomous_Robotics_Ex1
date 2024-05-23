import tkinter as tk
from PIL import Image, ImageTk
import random
import math
from Drone import Drone
import sys, os

# DroneSimulation class
class DroneSimulation:
    def __init__(self, master):
        self.master = master
        self.master.title("Drone Simulation")
        self.canvas_width = 1366
        self.canvas_height = 768
        self.canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Load map
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory
        parent_directory = os.path.dirname(script_dir)
        sys.path.insert(0, parent_directory)
        # Get path to sample file in data directory, which is located in the parent directory of this running file
        input_filepath = os.path.join(parent_directory, 'maps', 'p11.png') # change the txt file name to your desired gnss txt log file.
        self.load_map(input_filepath)  # Change "map.png" to your map's file path

        self.sensor_texts = {
            "Distance_Sensors": self.canvas.create_text(100, self.canvas_height -100, text="Distance Sensors", fill="white", font=("Arial", 12, "bold")),
            "forward": self.canvas.create_text(100, self.canvas_height - 20 , text="Forward: 0 cm", fill="white", font=("Arial", 12, "bold")),
            "backward": self.canvas.create_text(100, self.canvas_height - 40, text="Backward: 0 cm", fill="white", font=("Arial", 12, "bold")),
            "leftward": self.canvas.create_text(100, self.canvas_height - 60, text="Left: 0 cm", fill="white", font=("Arial", 12, "bold")),
            "rightward": self.canvas.create_text(100, self.canvas_height - 80, text="Right: 0 cm", fill="white", font=("Arial", 12, "bold")),

            "IMU": self.canvas.create_text(250, self.canvas_height - 80, text="IMU: 0", fill="white", font=("Arial", 12, "bold"))
        }
        # Initialize drone
        self.drone_radius = int(10 / 2.5)  # Convert cm to pixels
        self.drone = Drone()
        self.drone_item = None
        self.arrow_item = None
        self.respawn_drone()

        # Bind arrow key events
        self.master.bind("<Left>", lambda event: self.move_drone_by_pressing(-4, 0))
        self.master.bind("<Right>", lambda event: self.move_drone_automatically())#lambda event: self.move_drone_by_pressing(4, 0))
        self.master.bind("<Up>", lambda event: self.move_drone_by_pressing(0, -4))
        self.master.bind("<Down>", lambda event: self.move_drone_by_pressing(0, 4))
        self.master.bind("<W>", lambda event: self.update_drone_angle(-10))
        self.master.bind("<S>", lambda event: self.update_drone_angle(10))

    def load_map(self, filename):
        self.map_img = Image.open(filename)
        self.map_img = self.map_img.resize((self.canvas_width, self.canvas_height))
        self.map_photo = ImageTk.PhotoImage(self.map_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)

        # Convert map to black and white matrix
        self.map_matrix = self.convert_to_matrix(self.map_img)

    def convert_to_matrix(self, img):
        bw_img = img.convert("L")  # Convert to grayscale
        threshold = 128  # Threshold value for black/white
        bw_matrix = []
        for y in range(self.canvas_height):
            row = []
            for x in range(self.canvas_width):
                pixel = bw_img.getpixel((x, y))
                if pixel < threshold:
                    row.append(1)  # Black pixel
                else:
                    row.append(0)  # White pixel
            bw_matrix.append(row)
        return bw_matrix

    def respawn_drone(self):
        if self.drone_item:
            self.canvas.delete(self.drone_item)
        if self.arrow_item:
            self.canvas.delete(self.arrow_item)
        while True:
            x = random.randint(self.drone_radius, self.canvas_width - self.drone_radius - 1)
            y = random.randint(self.drone_radius, self.canvas_height - self.drone_radius - 1)
            if not self.check_collision(x, y):
                break
        self.drone_pos = [x, y]
        self.drone_item = self.canvas.create_oval(self.drone_pos[0] - self.drone_radius, self.drone_pos[1] - self.drone_radius,
                                                  self.drone_pos[0] + self.drone_radius, self.drone_pos[1] + self.drone_radius,
                                                  fill="red", tags="drone")
        self.arrow_item = self.canvas.create_line(self.drone_pos[0], self.drone_pos[1],
                                                  self.drone_pos[0] + 15, self.drone_pos[1],
                                                  arrow=tk.LAST, fill="black", width=2)
        self.update_sensors()
        self.update_arrow_position()

    def check_collision(self, x, y):
        for i in range(int(x - self.drone_radius), int(x + self.drone_radius)):
            for j in range(int(y - self.drone_radius), int(y + self.drone_radius)):
                if 0 <= i < self.canvas_width and 0 <= j < self.canvas_height:
                    if self.map_matrix[j][i] == 1:
                        return True
        return False

    def move_drone_by_pressing(self, dx, dy):
        # Calculate new position
        new_pos = [self.drone_pos[0] + dx, self.drone_pos[1] + dy]

        # Check if the new position is within bounds
        if (self.drone_radius <= new_pos[0] < self.canvas_width - self.drone_radius and
            self.drone_radius <= new_pos[1] < self.canvas_height - self.drone_radius):
            # Check if the new position is not touching a black pixel
            if not self.check_collision(new_pos[0], new_pos[1]):
                self.drone_pos = new_pos
                self.canvas.move(self.drone_item, dx, dy)
                self.canvas.move(self.arrow_item, dx, dy)
                self.update_sensors()
            else:  # Respawn drone if it touches a black pixel
                self.respawn_drone()


    def move_drone_automatically(self):
        # Calculate new position
        new_pos, dx, dy = self.drone.move_drone(self.drone_pos)

        # Check if the new position is within bounds
        if (self.drone_radius <= new_pos[0] < self.canvas_width - self.drone_radius and
            self.drone_radius <= new_pos[1] < self.canvas_height - self.drone_radius):
            # Check if the new position is not touching a black pixel
            if not self.check_collision(new_pos[0], new_pos[1]):
                self.drone_pos = new_pos
                self.canvas.move(self.drone_item, dx, dy)
                self.canvas.move(self.arrow_item, dx, dy)
                self.update_sensors()
            else:  # Respawn drone if it touches a black pixel
                self.respawn_drone()

    def update_drone_angle(self,angle_delta):
        self.drone.update_drone_angle(angle_delta)
        self.update_arrow_position()
        self.update_sensors()

    def update_arrow_position(self):
        angle_rad = math.radians(self.drone.drone_angle_forward)
        arrow_length = 15
        end_x = self.drone_pos[0] + arrow_length * math.cos(angle_rad)
        end_y = self.drone_pos[1] + arrow_length * math.sin(angle_rad)
        self.canvas.coords(self.arrow_item, self.drone_pos[0], self.drone_pos[1], end_x, end_y)    


    def update_sensors(self):
        self.drone.update_sensors(self.map_matrix, self.drone_pos, self.drone_radius, None)  # Replace None with the actual drone orientation if needed
        self.canvas.itemconfig(self.sensor_texts["forward"], text=f"Forward: {self.drone.forward_distance_sensor.distance:.1f} cm")
        self.canvas.itemconfig(self.sensor_texts["backward"], text=f"Backward: {self.drone.backward_distance_sensor.distance:.1f} cm")
        self.canvas.itemconfig(self.sensor_texts["leftward"], text=f"Left: {self.drone.leftward_distance_sensor.distance:.1f} cm")
        self.canvas.itemconfig(self.sensor_texts["rightward"], text=f"Right: {self.drone.rightward_distance_sensor.distance:.1f} cm")
        self.canvas.itemconfig(self.sensor_texts["IMU"], text=f"IMU: {self.drone.drone_angle_forward:.1f}")

def main():
    root = tk.Tk()
    app = DroneSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()
