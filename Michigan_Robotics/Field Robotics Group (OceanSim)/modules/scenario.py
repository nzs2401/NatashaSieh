import numpy as np
from omni.replicator.core.scripts.functional import write_np
import omni.replicator.core as rep
from pxr import Gf, PhysxSchema

from isaacsim.oceansim.utils.keyboard_cmd import keyboard_cmd
# from isaacsim.oceansim.sensors.ImagingSonarSensor import ImagingSonarSensor
from isaacsim.oceansim.sensors.SideScanSonarSensor import SideScanSonarSensor


class SideScanSonarScenario():
    def __init__(self):
        self._rob = None
        self._right_side_sonar = None
        self._left_side_sonar = None

        self._running_scenario = False
        self._time = 0.0
        # self._output_dir = '/home/haoyu/Desktop/viz'
        self._force_cmd = None
        self._torque_cmd = None
        
    def setup_scenario(self, rob, right_side_sonar : SideScanSonarSensor, left_side_sonar : SideScanSonarSensor):
        self._rob = rob
        self._right_side_sonar = right_side_sonar 
        self._left_side_sonar = left_side_sonar  

        self._right_side_sonar.side_sonar_initialize(include_unlabelled=True, 
                                    #  output_dir=self._output_dir
                                    normalizing_method="range"
                                     )
        
        # self._left_side_sonar.side_sonar_initialize(include_unlabelled=True, 
        #                             #  output_dir=self._output_dir
        #                             normalizing_method="range"
        #                              )
   
        self._running_scenario = True
        # self.backend = rep.BackendDispatch({"paths": {"out_dir": self._output_dir}})

        self._rob_forceAPI = PhysxSchema.PhysxForceAPI.Apply(self._rob)
        self._force_cmd = keyboard_cmd(base_command=np.array([0.0, 0.0, 0.0]),
                                    input_keyboard_mapping={
                                    # forward command
                                    "W": [5.0, 0.0, 0.0],
                                    # backward command
                                    "S": [-5.0, 0.0, 0.0],
                                    # leftward command
                                    "A": [0.0, 5.0, 0.0],
                                    # rightward command
                                    "D": [0.0, -5.0, 0.0],
                                        # rise command
                                    "UP": [0.0, 0.0, 5.0],
                                    # sink command
                                    "DOWN": [0.0, 0.0, -5.0],
                                    })
        # self._force_cmd = keyboard_cmd(base_command=np.array([2.0, 0.0, 0.0]))
        self._torque_cmd = keyboard_cmd(base_command=np.array([0.0, 0.0, 0.0]),
                                    input_keyboard_mapping={
                                    # yaw command (left)
                                    "J": [0.0, 0.0, 10.0],
                                    # yaw command (right)
                                    "L": [0.0, 0.0, -10.0],
                                    # pitch command (up)
                                    "I": [0.0, -10.0, 0.0],
                                    # pitch command (down)
                                    "K": [0.0, 10.0, 0.0],
                                    # row command (left)
                                    "LEFT": [-10.0, 0.0, 0.0],
                                    # row command (negative)
                                    "RIGHT": [10.0, 0.0, 0.0],
                                    })

    def teardown_scenario(self):

        self._rob = None
        self._right_side_sonar = None
        self._left_side_sonar = None

        self._running_scenario = False
        self._time = 0.0

        if self._force_cmd is not None:
            self._force_cmd.cleanup()
            self._torque_cmd.cleanup()
        if self._right_side_sonar is not None:
            self._right_side_sonar.close()
        # if self._left_side_sonar is not None:
        #     self._left_side_sonar.close()



    def update_scenario(self, step: float):
        if not self._running_scenario:
            return
        self._time += step


        self._right_side_sonar.make_side_sonar_data()
        # self._left_side_sonar.make_left_side_sonar_data()
        force_cmd = Gf.Vec3f(*self._force_cmd._base_command)
        torque_cmd = Gf.Vec3f(*self._torque_cmd._base_command)
        self._rob_forceAPI.CreateForceAttr().Set(force_cmd)
        self._rob_forceAPI.CreateTorqueAttr().Set(torque_cmd)