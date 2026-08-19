# Natasha Sieh

[![LinkedIn](https://img.shields.org/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nsieh/)
**Robotics Engineering Student | University of Michigan**

I'm a Robotics Engineering student at the University of Michigan focused on the intersection of simulation, reinforcement learning, biomechanics, and physical robot behavior.

Most of my work lives in the gap between simulation and reality. At UMich's Field Robotics Group, I built a GPU-accelerated side-scan sonar simulator in NVIDIA Isaac Sim, modeling complex physics and validating them against real-world datasets (co-authored paper submitted to OCEANS 2026).

Now, I bring these principles to legged robotics and biomedical hardware. As RL Subteam Lead for Wolverbot Kickers, I'm working on humanoid fall-recovery policies in Isaac Lab and rebuilding our simulation stack toward competing at RoboCup.

**Core Tools:** Isaac Sim/Lab · CUDA (Custom Kernels) · C++17 · Python · ROS2 · PyTorch · MuJoCo  
**Recognition:** CRA Outstanding Undergraduate Researcher Honorable Mention (2026, National)  
*Open to Late Spring/Summer 2027 internships in robotics, legged locomotion, control, and medical devices.*

---

## Research & Technical Experience

### Humanoid Robotics | Michigan Wolverbots (RoboCup)
*RL Subteam Lead | Jan 2026 – Present*
* Re-engineered humanoid URDF to stabilize simulation dynamics in MuJoCo, enabling policy training in Isaac Lab.
* Implemented fall-recovery RL policies in Isaac Lab across diverse orientations; developing evaluation frameworks for velocity and postural stability.
* Engineered sim-to-real transfer logic bridging Isaac Lab physics and physical hardware using motor controllers and Pypot.
* **Tech Stack:** Isaac Lab, Isaac Sim, MuJoCo, Python, URDF, ROS2, RViz, Pypot, Motor Controllers

### GPU-Accelerated Sonar Simulation | Field Robotics Group (FRoG Lab)
*Undergraduate Researcher | May 2025 – April 2026* | [[Video Demos]](https://drive.google.com/drive/folders/1zUd_xFvGQYKB1XT0i2nqObynq0LG5asB?usp=sharing)
* Built GPU-accelerated acoustic imaging pipeline with custom CUDA/Warp kernels for real-time ray-tracing performance in NVIDIA Isaac Sim.
* Designed terrain-aware echo modeling and beam pattern generation using PhysX and OpenUSD.
* Created procedural underwater terrain generator with PyTorch, VGG-19 Neural Style Transfer, and SDG for synthetic dataset creation.
* Co-authored publication submitted to OCEANS 2026; set up Docker containerized environments and collaborative Git workflows (PRs).
* **Tech Stack:** NVIDIA Isaac Sim, CUDA, Warp, PhysX, OpenUSD, PyTorch, VGG-19, SDG, Docker, Git

### Biomedical Robotics | Extracorporeal Life Support Lab
*Undergraduate Researcher | Sept 2024 – April 2025*
* Implemented a C++ embedded temperature control system (thermistors + PID feedback) for Roll-to-Roll fabrication of wearable artificial lung prototypes for end-stage COPD patients.
* Resolved critical hardware-software integration issues, doubling fabricated lung membrane thickness while reducing defect rates.
* Contributed to CAD design, soldering, 3D printing, and testing of microfluidic artificial lungs; attended medical lectures and observed live animal transplant surgeries.
* **Tech Stack:** C++, Arduino, Embedded Systems, PID Control, CAD, 3D Printing, Soldering, Thermistors, Microfluidics

### Autonomous Navigation | UMARV Robotics Team
*Navigation Engineer | Sept 2024 – April 2025*
* Implemented A* and BFS path planning in C++, improving pathfinding efficiency by 50%.
* Integrated LiDAR, RGB-D sensors, and SLAM (Cartographer/RTAB-Map) for real-time localization and obstacle avoidance.
* Achieved finalist status at 32nd IGVC competition; co-authored IGVC Design Report.
* **Tech Stack:** ROS2, RViz, C++, LiDAR, RGB-D, OpenCV, SLAM (Cartographer/RTAB-Map), Sensor Fusion

---

## Biomedical & Clinical Foundations

* **UCSD Biomechanics & Mechanobiology Program (Summer 2022):** Investigated structural biomechanics of healthy, injured, and diseased knee joints using mechanical load testing and data analysis (NumPy/Matplotlib).
* **UH Manoa Medical Diagnostics & Treatment Program (Summer 2022):** Completed clinical skills coursework and cadaver dissections focusing on human anatomical structure and medical device applications.
* **Relevant Coursework:** Anatomy & Physiology, Intro to Clinical Data, Fundamentals of ML for Healthcare.

---

## Technical Skills

| Category | Technologies |
| :--- | :--- |
| **Simulation & GPU** | NVIDIA Isaac Sim, IsaacLab, CUDA (custom kernel development), PhysX, Warp, OpenUSD, MuJoCo, Gazebo |
| **Perception & ML** | PyTorch, VGG-19, OpenCV, SLAM (Cartographer/RTAB-Map), SDG (Synthetic Data Generation), Sensor Fusion |
| **Planning & Control** | A*/BFS, RL (Reinforcement Learning), FK/IK, PID, ROS/ROS2, RViz |
| **Languages & Systems** | C/C++/C++17, Python, Linux, Git (collaborative workflows, PRs), Docker |
| **Embedded & Hardware** | ESP32, Arduino, Raspberry Pi, LiDAR, RGB-D, CAD, 3D printing, Soldering, Motor Controllers |
| **Data & Analysis** | NumPy, Matplotlib, Monte Carlo simulation, Worst-case safety analysis, Unit testing |
