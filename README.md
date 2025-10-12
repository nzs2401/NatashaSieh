# NatashaSieh

Linkedin: www.linkedin.com/in/nsieh/

Robotics Engineering Student | University of Michigan <br>
-------------------------------------------------------------------------------------

About Me <br>
I'm a second-year Robotics Engineering student at the University of Michigan with research experience in GPU-accelerated robotics simulation, autonomous navigation, and embedded systems. My work spans underwater robot perception, computer vision, and real-time control systems.
Current Focus: GPU-based sonar simulation using NVIDIA Isaac Sim, CUDA, and Warp kernels for underwater robotics research at the Field Robotics Group (FRoG) Lab.

-------------------------------------------------------------------------------------

Research & Technical Experience <br>
GPU-Accelerated Sonar Simulation | Field Robotics Group (FRoG Lab)
University of Michigan | Aug 2025 - Present
Developing high-fidelity side-scan sonar simulation for underwater robotics using NVIDIA Isaac Sim and GPU computing.
(https://drive.google.com/file/d/1naX7FVNVjrl2pK1C0ho7yqw9UuYxW7y8/view) <br>
• Built GPU-accelerated acoustic imaging pipeline with CUDA/Warp kernels for real-time performance <br>
• Designed terrain-aware echo modeling and beam pattern generation using PhysX and Python <br>
• Created procedural underwater terrain generator with NVIDIA SDG Replicator for synthetic dataset creation <br>
• Validated simulation accuracy against real-world shipwreck sonar data <br>
• Engineered ROS-to-ROS2 bridge for cross-platform interoperability <br>

Tech Stack: NVIDIA Isaac Sim, CUDA, Warp, Python, PhysX, ROS2, USD

-------------------------------------------------------------------------------------

Autonomous Navigation | UMARV Robotics Competition Team <br>
University of Michigan | Sept 2024 - Present
Navigation Engineer for autonomous ground vehicle competing in IGVC (Intelligent Ground Vehicle Competition).

Developed ROS2-based perception pipeline using LiDAR and RGB-D cameras for real-time obstacle detection
Implemented A* and BFS path planning algorithms, improving pathfinding efficiency by 50%
Built sensor fusion system combining LiDAR, depth camera, and IMU for robust localization
Achieved finalist status at 32nd IGVC competition

Tech Stack: ROS2, Python, C++, LiDAR, OpenCV, Point Cloud Library, SLAM

-------------------------------------------------------------------------------------

Embedded Systems & Biomedical Robotics | Extracorporeal Life Support Lab <br>
University of Michigan | Sept 2024 - Apr 2025
Contributed to artificial lung development for COPD patients.

Developed embedded temperature control systems using C++ for closed-loop regulation
Integrated sensors and actuators for real-time biomedical prototyping
Supported 3D-printed microfluidic device testing using Roll-to-Roll technology

Tech Stack: C++, Arduino, Embedded Systems, Sensor Integration

-------------------------------------------------------------------------------------

Technical Skills <br>
Programming & GPU Computing
Python, C++, CUDA, NVIDIA Warp, GPU Kernels, Julia, JavaScript, HTML/CSS, Git, Linux
Robotics & Autonomy
ROS/ROS2, SLAM, Path Planning (A*, BFS), LiDAR, Sensor Fusion, Visual Odometry, PID Control, Bang-bang Control
AI & Computer Vision
OpenCV, YOLO, PyTorch, CNNs, TensorFlow, Point Cloud Library, Image Processing, Object Detection
Simulation & Perception
NVIDIA Isaac Sim (Warp, PhysX, Replicator), Gazebo, RViz, Procedural Generation, USD
Embedded Systems & Hardware
Arduino (Uno/Nano/Leonardo), Raspberry Pi, ESP32, Motors (BLDC, Servo, Stepper), Soldering, ESC, Signal Generators, Spectrum Analyzers
CAD & Prototyping
SolidWorks, OnShape, 3D Printing, Laser Cutting, Hardware Integration


<!-- SKILLS: <br>
• Programming: Python (AI/Numpy), OpenCV, Tensorflow, ROS2, C/C++, YOLO, PyTorch, CNNs, Java, Julia, JavaScript, HTML/CSS.  <br>
• Robotics & Controls: LiDAR, SLAM, ROS2, Linux, control algorithms, kinematics, robot odometry, image processing, embedded systems, troubleshooting, point cloud library, breadth for search, Bang-bang control, p-control, Bug Navigation.  <br>
• Electronics & Prototyping: CAD (SolidWorks/OnShape), 3D-printing, soldering, Arduino/Raspberry Pi, centrifuge, Roll-to-Roll machine, motors: BLDC, stepper, & servo, neomotors, Arduino Uno/Nano/Leonardo, ESP32, ESC, Limit switches, Signal Generators, Spectrum Analyzers, Hardware systems integration.  <br>
• Project Mgmt: Version control (Github), scoping, documentation, & cross-functional collaboration.  <br> -->

<!-- ___________________________________________________________________________________________________________
Robotics 1

  Knee Project
  - I made a 3D model of a bending knee joint using a 3D printer to print out my design of a tibia and a femur. The base and side support of the model was a piece of laser cut wood. The servo, controlled by a potentiometer, creates the bending motion. The rubber tube ligaments are used to limit the range of motion.
  - Electronics included: servo motor, potentiometer, and Arduino Uno
![IMG_8928](https://github.com/nzs2401/NatashaSieh/assets/116852829/667d3b5a-b089-4d6b-a870-40098bd894fa)
![IMG_8930](https://github.com/nzs2401/NatashaSieh/assets/116852829/7bf0b93f-4242-43ca-871f-c3b7eb558c68)

____________________________________________________________________________________________________________

Robotics 2

  Hotwheel Carousel
  - Built, designed, and coded a rotating carousel used to transport hotwheel cars to different tracks powered by a brushless motor and other electronics.
  - Electronics included: stepper motor, potentiometer, Arduino Nano, and a Liquid-crystal display (LCD)
![IMG_9991](https://github.com/nzs2401/NatashaSieh/assets/116852829/6af27fbb-3728-4e12-86d9-6606575f77b2)

____________________________________________________________________________________________________________

Robotics 3

  Propeller Design
  - Used Onshape to design the shape, size, and style of the propellers
  - 3D printed the results and kept improving the propellers
![IMG_0088](https://github.com/nzs2401/NatashaSieh/assets/116852829/1f879ac0-b2fa-4c52-9cc8-7111f495ebae)


  Gearbox Design
  - Used to measure torque and efficiency of gearboxes with relation to gear ratios
![IMG_0485](https://github.com/nzs2401/NatashaSieh/assets/116852829/6266e9a2-2dd5-4fa6-a868-54cec421087f)


  ESC, ESP32, & BLDC Motor used to control my Gearbox design
  - Programmed ESP32 to display the speed of the BLDC motor
  - Created a HTML interface with a slider to control and view the speed of the BLDC motor and project it onto an ESP32.
![IMG_D4E57DB13242-1](https://github.com/nzs2401/NatashaSieh/assets/116852829/89320a4b-0e3d-446b-b101-06ccfa04ef2d)

____________________________________________________________________________________________________________

  Lidar & Raspberry Pi
  - Coded in different operating systems, while using Lidar to map out the environemt and work autonomously with a robot dog and a camera.
![IMG_0961 2](https://github.com/nzs2401/NatashaSieh/assets/116852829/0b2b5edc-9c15-4ef7-9992-204816acd9dd)

____________________________________________________________________________________________________________

  Evoydyne Robotics
    - Build and programmed a robot dog to perform tricks like trot, sit, strot and more.
![IMG_9579](https://github.com/nzs2401/NatashaSieh/assets/116852829/be527347-5750-4eff-b451-d75f98652b06)

____________________________________________________________________________________________________________

 -->
