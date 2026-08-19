# Natasha Sieh

[![LinkedIn](https://img.shields.org/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nsieh/)
**Robotics Engineering Student | University of Michigan**

I'm a Robotics Engineering student at the University of Michigan focused on the intersection of simulation, reinforcement learning, biomechanics, and physical robot behavior.

Most of my work lives in the gap between simulation and reality. At UMich's Field Robotics Group, I built a GPU-accelerated side-scan sonar simulator in NVIDIA Isaac Sim, modeling complex physics and validating them against real-world datasets (co-authored paper submitted to OCEANS 2026).

Now, I bring these principles to legged robotics and biomedical hardware. As RL Subteam Lead for Wolverbot Kickers, I'm working on humanoid fall-recovery policies in Isaac Lab and rebuilding our simulation stack toward competing at RoboCup.

**Core Tools:** Isaac Sim/Lab · CUDA · ROS2 · PyTorch · C++ · Python · MuJoCo  
**Recognition:** CRA Outstanding Undergraduate Researcher Honorable Mention (2026, National)  
*Open to Late Spring/Summer 2027 internships in robotics, legged locomotion, control, and medical devices.*

---

## Research & Technical Experience

### Humanoid Robotics | Michigan Wolverbots (RoboCup)
*RL Subteam Lead | Jan 2026 – Present*
* Re-engineered humanoid URDF to stabilize simulation dynamics in MuJoCo, enabling policy training in Isaac Lab.
* Implemented fall-recovery RL policies in Isaac Lab across diverse orientations; developing evaluation frameworks for velocity and postural stability.
* Engineered sim-to-real transfer logic bridging Isaac Lab physics and physical hardware using Pypot for motor control.
* **Tech Stack:** Isaac Lab, Isaac Sim, MuJoCo, Python, URDF, ROS2, Pypot

### GPU-Accelerated Sonar Simulation | Field Robotics Group (FRoG Lab)
*Undergraduate Researcher | May 2025 – April 2026* | [[Video Demos]](https://drive.google.com/drive/folders/1zUd_xFvGQYKB1XT0i2nqObynq0LG5asB?usp=sharing)
* Built GPU-accelerated acoustic imaging pipeline with CUDA/Warp kernels for real-time performance in NVIDIA Isaac Sim.
* Designed terrain-aware echo modeling and beam pattern generation using PhysX.
* Created procedural underwater terrain generator with PyTorch and VGG-19 Neural Style Transfer for synthetic dataset creation.
* Co-authored publication submitted to OCEANS 2026.
* **Tech Stack:** NVIDIA Isaac Sim, CUDA, Warp, Python, PhysX, ROS2, OpenUSD, PyTorch

### Biomedical Robotics | Extracorporeal Life Support Lab
*Undergraduate Researcher | Sept 2024 – April 2025*
* Implemented a C++ embedded temperature control system (thermistors + PID feedback) for Roll-to-Roll fabrication of wearable artificial lung prototypes for end-stage COPD patients.
* Resolved critical hardware-software integration issues, doubling fabricated lung membrane thickness while reducing defect rates.
* Contributed to the design and testing of 3D-printed microfluidic artificial lungs; attended medical lectures and observed live animal transplant surgeries.
* **Tech Stack:** C++, Arduino, Embedded Systems, PID Control, Sensor Integration, Microfluidics

### Autonomous Navigation | UMARV Robotics Team
*Navigation Engineer | Sept 2024 – April 2025*
* Implemented A* and BFS path planning in C++, improving pathfinding efficiency by 50%.
* Achieved finalist status at 32nd IGVC competition; co-authored IGVC Design Report.
* **Tech Stack:** ROS2, C++, LiDAR, OpenCV, SLAM

---

## Biomedical & Clinical Foundations

* **UCSD Biomechanics & Mechanobiology Program (Summer 2022):** Investigated structural biomechanics of healthy, injured, and diseased knee joints (bone, cartilage, tendons, and ligaments) using mechanical load testing and biomedical data analysis.
* **UH Manoa Medical Diagnostics & Treatment Program (Summer 2022):** Completed clinical skills coursework and cadaver dissections focusing on human anatomical structure and medical device applications.
* **Relevant Coursework:** Anatomy & Physiology, Intro to Clinical Data, Fundamentals of ML for Healthcare.

---

## Technical Skills

| Category | Technologies |
| :--- | :--- |
| **Simulation & GPU** | Isaac Sim/Lab, CUDA, PhysX, Warp, MuJoCo, Gazebo, OpenUSD |
| **Planning & Control** | RL, A*/BFS, RTD, FK/IK, PID, Bang-bang, ROS/ROS2 |
| **Perception & ML** | PyTorch, VGG-19, OpenCV, SLAM (Cartographer/RTAB-Map), Sensor Fusion |
| **Languages & Embedded**| C/C++, Python, Julia, Linux, Git, Docker, ESP32, Arduino, Raspberry Pi, Microfluidics |
| **Fabrication & Hardware** | SolidWorks, OnShape, 3D Printing, Soldering, Roll-to-Roll Manufacturing, Motor Controllers |
