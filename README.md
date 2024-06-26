# Autonomous_Robotics_Ex1 - Drone Control System
## Contributors
* Maor Or
* Raz Saad
* Shlomit Ashkenazi

## How to run
* Clone the repo to a local machine
* Download requirements with: pip install -r requirements.txt
* From a terminal window navigate to the src folder and execute: python Main_Pygame.py
* Optional - You can add a custom-made map for the drone to cover: add the image into the maps folder
## Demo
https://github.com/Raz-Saad/Autonomous_Robotics_Ex1/assets/43138073/f54530c8-0b4c-4101-8a18-2469a66a9ed3


![Capture](https://github.com/Raz-Saad/Autonomous_Robotics_Ex1/assets/43138073/cc1cc1e4-19e6-47a4-948d-6dcbc6f00888)

## Overview
Building a basic control system for a drone, allowing it to navigate through a two-dimensional terrain. The objective is to enable the drone to cover as much terrain as possible and return to the take-off point when the battery level reaches 50%.

## Assignment Details
### Infrastructure
The infrastructure consists of a two-dimensional map with white pixels representing flyable areas and black pixels representing obstacles.
Each pixel is assumed to be 2.5 cm.
The drone has a radius of 10 cm and is equipped with various sensors, including four distance meters (right, left, forward, and backward), a speed sensor (optical flow), an orientation sensor (IMU) and a battery sensor. All sensors operate at a rate of 10 times per second.
### Flight Constraints
The drone can adjust its pitch and roll within ±10 degrees with an angular speed of 100 degrees per second.
It can accelerate at a constant rate of 1 meter per second^2 and reach a maximum speed of 3 meters per second.
The maximum flight time is 8 minutes (480 seconds).
## Our Approach to Autonomous Flight
Control Algorithm Design: Designing algorithm to control the drone's movements based on sensor inputs and predefined flight objectives. This approach involves implementing navigation and obstacle avoidance using PID controllers.
