import sys
import signal
import time
from joblib import dump, load  # To get the model to the robot


import os
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.neural_network import MLPClassifier




from mbot_bridge.api import MBot
from utils.camera import CameraHandler
from utils.robot import plan_to_pose, turn_to_theta
from waypoint_writer import read_labels_and_waypoints




# TODO: Update PATH_TO_MODEL.
PATH_TO_MODEL = "/home/mbot/robot-tour-guide-f23/model.joblib"


robot = MBot()  # This initializes communication with your robot.


def signal_handler(sig, frame):
   print("Stopping...")
   robot.stop()
   sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def main():
   ch = CameraHandler()  # Initialize the camera


   # NOTE: This code will fail if you have not updated PATH_TO_MODEL above.
   assert os.path.exists(PATH_TO_MODEL), f"Model file {PATH_TO_MODEL} does not exist."
   model = load(PATH_TO_MODEL)
  
   # TODO: Either uncomment and modify the hard coded definitions for
   # waypoints and labels below or run waypoint_writer.py to write
   # waypoints and labels for your current map to output/waypoints.txt.
   #
   # You must handle the case where your model detects a label which is not part of the
   # given course.


   labels, waypoints = read_labels_and_waypoints()  # Load from waypoints.txt
  
   # labels = [0, 1, 2, ...]
   # waypoints = [[0, 0, 0], [9, 2, 8], [3, 6, 4], ...]


   # NOTE: To get the cropped image of a post-it from the camera, do:
   #
   # frame = ch.get_processed_image()
   #
   # If a post-it is not detected, frame will be None. Make sure you check for this
   # case. To save the image to the folder "output", pass `save=True` to this
   # function. It will be the last image labeled 08_bordered_frame_X.jpg. Check out
   # the previous images to understand how the preprocessing step works. This might
   # slow down execution slightly.
  
   # NOTE: To plan a path to a goal position (x and y, in meters), do:
   #
   # plan_to_pose(x, y, robot)
   #
   # To turn to a given angle (theta, in radians), do:
   #
   # turn_to_theta(theta, robot)
   #
   # You must turn to the theta after x, y location is reached.


   # TODO: Your code here!
   # Write your code to detect the label on a poster at a given waypoint, and use
   # the result to determine which waypoint to visit next. You will need to use the
   # "labels" and "waypoints" variables! When the robot reads a poster with label "0",
   # it should return to the start position (0, 0, 0) and the program should exit.
   x, y, theta = 0, 0, 0


   while True:
       frame = ch.get_processed_image()  # Get the image of a digit from the camera.


       if frame is None:
           print("No frame detected. Skipping...")
           continue


       y_pred = model.predict([frame])[0]


       if y_pred == "0":
           print("Detected '0'")
           plan_to_pose(0, 0, robot) # Original position
           turn_to_theta(0, robot) # Original angle
           robot.stop()
           break


       # Update to the next waypoint based on the label
       if y_pred in labels:
           x, y, theta = waypoints[labels.index(y_pred)]
           plan_to_pose(x, y, robot)  # Use this to drive to a goal location.
           time.sleep(1)  # Time to drive to next location
           turn_to_theta(theta, robot)  # Use this to turn to a goal angle.
       else:
           print(f"Unknown label {y_pred}. Unable to proceed.")
           break


if __name__ == '__main__':
   main()



