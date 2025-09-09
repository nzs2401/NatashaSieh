# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# Omniverse import
import numpy as np
import omni.timeline
import omni.ui as ui
from omni.usd import StageEventType
from pxr import Sdf, UsdLux, Gf, Usd, UsdGeom, UsdPhysics, PhysxSchema
import omni.replicator.core as rep
import Semantics

# Isaac sim import
from isaacsim.core.api.objects import DynamicCuboid, DynamicSphere
from isaacsim.core.prims import SingleXFormPrim, SingleRigidPrim, SingleGeometryPrim
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.stage import get_current_stage, add_reference_to_stage, create_new_stage, open_stage
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.utils.semantics import add_update_semantics
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.gui.components import CollapsableFrame, Frame, StateButton, get_style
from isaacsim.examples.extension.core_connectors import LoadButton, ResetButton


# Custom import
# from .scenario import ImagingSonarScenario
from isaacsim.oceansim.sensors.ImagingSonarSensor import ImagingSonarSensor
from .scenario import SideScanSonarScenario
from isaacsim.oceansim.sensors.SideScanSonarSensor import SideScanSonarSensor

class UIBuilder:
    def __init__(self):
        # Frames are sub-windows that can contain multiple UI elements
        self.frames = []
        # UI elements created using a UIElementWrapper instance
        self.wrapped_ui_elements = []

        # Get access to the timeline to control stop/pause/play programmatically
        self._timeline = omni.timeline.get_timeline_interface()

        # Run initialization for the provided example
        self._on_init()

    ###################################################################################
    #           The Functions Below Are Called Automatically By extension.py
    ###################################################################################

    def on_menu_callback(self):
        """Callback for when the UI is opened from the toolbar.
        This is called directly after build_ui().
        """
        pass

    def on_timeline_event(self, event):
        """Callback for Timeline events (Play, Pause, Stop)

        Args:
            event (omni.timeline.TimelineEventType): Event Type
        """
        if event.type == int(omni.timeline.TimelineEventType.STOP):
            # When the user hits the stop button through the UI, they will inevitably discover edge cases where things break
            # For complete robustness, the user should resolve those edge cases here
            # In general, for extensions based off this template, there is no value to having the user click the play/stop
            # button instead of using the Load/Reset/Run buttons provided.
            self._scenario_state_btn.reset()
            self._scenario_state_btn.enabled = False

    def on_physics_step(self, step: float):
        """Callback for Physics Step.
        Physics steps only occur when the timeline is playing

        Args:
            step (float): Size of physics step
        """
        pass

    def on_stage_event(self, event):
        """Callback for Stage Events

        Args:
            event (omni.usd.StageEventType): Event Type
        """
        if event.type == int(StageEventType.OPENED):
            # If the user opens a new stage, the extension should completely reset
            self._reset_extension()

    def cleanup(self):
        """
        Called when the stage is closed or the extension is hot reloaded.
        Perform any necessary cleanup such as removing active callback functions
        Buttons imported from omni.isaac.ui.element_wrappers implement a cleanup function that should be called
        """
        for ui_elem in self.wrapped_ui_elements:
            ui_elem.cleanup()

    def build_ui(self):
        """
        Build a custom UI tool to run your extension.
        This function will be called any time the UI window is closed and reopened.
        """
        world_controls_frame = CollapsableFrame("World Controls", collapsed=False)

        with world_controls_frame:
            with ui.VStack(style=get_style(), spacing=5, height=0):
                
                self._load_btn = LoadButton(
                    "Load Button", "LOAD", setup_scene_fn=self._setup_scene, setup_post_load_fn=self._setup_scenario
                )
                self._load_btn.set_world_settings(physics_dt=1 / 60.0, rendering_dt=1 / 60.0)
                self.wrapped_ui_elements.append(self._load_btn)

                self._reset_btn = ResetButton(
                    "Reset Button", "RESET", pre_reset_fn=None, post_reset_fn=self._on_post_reset_btn
                )
                self._reset_btn.enabled = False
                self.wrapped_ui_elements.append(self._reset_btn)

        run_scenario_frame = CollapsableFrame("Run Scenario", collapsed=False)

        with run_scenario_frame:
            with ui.VStack(style=get_style(), spacing=5, height=0):
                self._scenario_state_btn = StateButton(
                    "Run Scenario",
                    "RUN",
                    "STOP",
                    on_a_click_fn=self._on_run_scenario_a_text,
                    on_b_click_fn=self._on_run_scenario_b_text,
                    physics_callback_fn=self._update_scenario,
                )
                self._scenario_state_btn.enabled = False
                self.wrapped_ui_elements.append(self._scenario_state_btn)

        self._outputs_frame = CollapsableFrame("Outputs", collapsed=False)



    ######################################################################################
    # Functions Below This Point Related to Scene Setup (USD\PhysX..)
    ######################################################################################

    def _on_init(self):
        self._rob = None
        self._right_side_sonar = None
        self._left_side_sonar = None
        self._right_sensor_location = [-0.00757, -0.09933, -0.10222] # CHANGE THIS!
        self._left_sensor_location = [-0.00757, 0.09933, -0.10222] # CHANGE THIS!
        # self._init_rob_pos = np.array([-1.76533, 1.21862, 0.50175])
        # self._init_rob_pos = np.array([-7.65574, 5.26742, 9.50]) # CHANGE THIS! 09/07 for shipwreck

        # self._init_rob_pos = np.array([-6.08768, 4.35035, 6.55124])
        self._init_rob_pos = np.array([5.2596, 5.76701, 6.46096])
        self._init_rob_orien = euler_angles_to_quat(np.array([0, 0, 0]), degrees=True)
        self._rob_mass = 10 #kg Need this value to supress a warning given by automatic mass computation from collider assignment
        self._rob_angular_damping = 10.0
        self._rob_linear_damping = 10.0
        self._scenario = SideScanSonarScenario()

    def _add_light_to_stage(self):
        """
        A new stage does not have a light by default.  This function creates a spherical light
        """
        sphereLight = UsdLux.SphereLight.Define(get_current_stage(), Sdf.Path("/World/SphereLight"))
        sphereLight.CreateRadiusAttr(2)
        sphereLight.CreateIntensityAttr(100000)
        SingleXFormPrim(str(sphereLight.GetPath())).set_world_pose(position=np.array([6.5, 0, 12]))
       
    @staticmethod
    def _add_semantic_entry(prim, instance_name, new_type="", new_data=""):
        import random
        import string
        def id_generator(size=4, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
            return "".join(random.choice(chars) for _ in range(size))
        

        sem = Semantics.SemanticsAPI.Apply(prim, instance_name + f"_{id_generator()}")

        sem.CreateSemanticTypeAttr()
        sem.CreateSemanticDataAttr()

        typeAttr = sem.GetSemanticTypeAttr()
        dataAttr = sem.GetSemanticDataAttr()
        typeAttr.Set(new_type)
        dataAttr.Set(new_data)

        return sem
    
    # def _setup_scene(self):
    #     """
    #     This function is attached to the Load Button as the setup_scene_fn callback.
    #     On pressing the Load Button, a new instance of World() is created and then this function is called.
    #     The user should now load their assets onto the stage and add them to the World Scene.

    #     In this example, a new stage is loaded explicitly, and all assets are reloaded.
    #     If the user is relying on hot-reloading and does not want to reload assets every time,
    #     they may perform a check here to see if their desired assets are already on the stage,
    #     and avoid loading anything if they are.  In this case, the user would still need to add
    #     their assets to the World (which has low overhead).  See commented code section in this function.
    #     """
    #     # you can create a new stage. Or comment out this line to load on current stage
    #     create_new_stage()
    #     world_prim_path = '/World'
    #     SingleXFormPrim(name='World',prim_path=world_prim_path)
    #     add_reference_to_stage(usd_path='https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Environments/Simple_Room/simple_room.usd',
    #                            prim_path= world_prim_path + '/room')
    #     # Load the robot
    #     robot_prim_path = world_prim_path + "/rob" 
    #     DynamicCuboid(prim_path=robot_prim_path, size=0.2, color=np.array([0.1,0.5,1]))
    #     self._rob = get_prim_at_path(robot_prim_path)
    #     SingleXFormPrim(robot_prim_path).set_world_pose(position=self._init_rob_pos, orientation=self._init_rob_orien)
    #     set_camera_view(eye=self._init_rob_pos + np.array([2,2,2]), target=self._init_rob_pos)
    #     # Toggle rigid body and apply zero gravity and zero damping
    #     rob_rigidBody_API = PhysxSchema.PhysxRigidBodyAPI.Apply(self._rob)
    #     rob_rigidBody_API.CreateDisableGravityAttr(True)
    #     rob_rigidBody_API.GetLinearDampingAttr().Set(self._rob_linear_damping)
    #     rob_rigidBody_API.GetAngularDampingAttr().Set(self._rob_angular_damping)
    #     rob_rigid_prim = SingleRigidPrim(robot_prim_path, mass=self._rob_mass)



    #     self._right_side_sonar = SideScanSonarSensor(prim_path=robot_prim_path + '/right_side_sonar',
    #                             translation=self._right_sensor_location,
    #                             orientation=euler_angles_to_quat(np.array([0.0, 45.0, -90.0]),  degrees=True),
    #                             range_res=0.005,
    #                             angular_res=0.2,
    #                             hori_res=50,
    #                             )
    #     self._left_side_sonar = None
    


    #     # self._right_side_sonar.side_sonar_initialize()
    #     # self._left_side_sonar.side_sonar_initialize()
    #     # self._left_side_sonar.make_side_sonar_data()
        
    #     # add testing objects
    #     # cube_position =  [(-0.3, 0.3, 0.3), (-0.3, -0.3, 0.3), (0.3, -0.3, 0.3), (0.3, 0, 0.3)]
    #     sphere_position = [(-0.3, 0.6, 0.6), (0, 0.8, 0.3), (0.3, 0.3, 0.3)]


    #     # for i in range(len(cube_position)):
    #     #     cube_path = world_prim_path + f"/cube_{i}"
    #     #     cube = DynamicCuboid(prim_path=cube_path,
    #     #                   position=cube_position[i],
    #     #                   scale=[0.1]*3)
    #     #     self._add_semantic_entry(cube.prim,
    #     #                               "sonar_ref",
    #     #                               "reflectivity",
    #     #                               "1.5")
    #     #     self._add_semantic_entry(cube.prim,
    #     #                               "semantics",
    #     #                               "class",
    #     #                               f"cube_{i}")
    #     #     PhysxSchema.PhysxRigidBodyAPI.Apply(get_prim_at_path(cube_path))

    #     for i in range(len(sphere_position)):
    #         sphere_path = world_prim_path + f"/sphere_{i}"
    #         sphere = DynamicSphere(prim_path=sphere_path,
    #                       position=sphere_position[i],
    #                       scale=[0.1]*3)
    #         self._add_semantic_entry(sphere.prim,
    #                                   "sonar_ref",
    #                                   "reflectivity",
    #                                   "1.0")
    #         self._add_semantic_entry(sphere.prim,
    #                                   "semantics",
    #                                   "class",
    #                                   f"sphere_{i}")
            
    #         PhysxSchema.PhysxRigidBodyAPI.Apply(get_prim_at_path(sphere_path))

    def _setup_scene(self):
        """
        This function is attached to the Load Button as the setup_scene_fn callback.
        On pressing the Load Button, a new instance of World() is created and then this function is called.
        The user should now load their assets onto the stage and add them to the World Scene.

        In this example, a new stage is loaded explicitly, and all assets are reloaded.
        If the user is relying on hot-reloading and does not want to reload assets every time,
        they may perform a check here to see if their desired assets are already on the stage,
        and avoid loading anything if they are.  In this case, the user would still need to add
        their assets to the World (which has low overhead).  See commented code section in this function.
        """
        # you can create a new stage. Or comment out this line to load on current stage
        create_new_stage()
        world_prim_path = '/World'
        SingleXFormPrim(name='World',prim_path=world_prim_path)

        # --- ADD THIS LINE TO ADD A LIGHT TO THE SCENE ---
        self._add_light_to_stage()

        domeLight = UsdLux.DomeLight.Define(get_current_stage(), Sdf.Path("/World/DomeLight"))
        # You can set the intensity
        domeLight.CreateIntensityAttr(1000) # Adjust as needed
        # Background is a simple sky color
        domeLight.CreateColorAttr(Gf.Vec3f(0.5, 0.7, 1.0))

        from omni.isaac.core.utils.prims import add_reference_to_stage

        eenv_usd_path = "https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac/Environments/Grid/gridroom_black.usd"
        env_prim_path = "/World/BlackGridEnvironment"
        add_reference_to_stage(usd_path=eenv_usd_path, prim_path=env_prim_path)


        ship_prim_path = world_prim_path + '/ship_scene' # Define this once for clarity

        # Load your ship.usd file instead of simple_room.usd
        add_reference_to_stage(usd_path='/home/nsieh/Downloads/ship/ship.usd', # **CHANGE THIS LINE**
                            prim_path= world_prim_path + '/ship_scene') # **You might want to change the prim_path name as well**

        # Rotate usd
        ship_xform_prim = SingleXFormPrim(prim_path=ship_prim_path)
        rotation_degrees = np.array([90.0, 0.0, 0.0]) # Example: Rotate 90 degrees around Z-axis
        ship_orientation = euler_angles_to_quat(rotation_degrees, degrees=True)
        ship_xform_prim.set_world_pose(orientation=ship_orientation)

        # Load the robot
        robot_prim_path = world_prim_path + "/rob" 
        DynamicCuboid(prim_path=robot_prim_path, size=0.2, color=np.array([0.1,0.5,1]))
        self._rob = get_prim_at_path(robot_prim_path)
        SingleXFormPrim(robot_prim_path).set_world_pose(position=self._init_rob_pos, orientation=self._init_rob_orien)
        set_camera_view(eye=self._init_rob_pos + np.array([2,2,2]), target=self._init_rob_pos)
        # Toggle rigid body and apply zero gravity and zero damping
        rob_rigidBody_API = PhysxSchema.PhysxRigidBodyAPI.Apply(self._rob)
        rob_rigidBody_API.CreateDisableGravityAttr(True)
        rob_rigidBody_API.GetLinearDampingAttr().Set(self._rob_linear_damping)
        rob_rigidBody_API.GetAngularDampingAttr().Set(self._rob_angular_damping)
        rob_rigid_prim = SingleRigidPrim(robot_prim_path, mass=self._rob_mass)

        self._right_side_sonar = SideScanSonarSensor(prim_path=robot_prim_path + '/right_side_sonar',
                                translation=self._right_sensor_location,
                                orientation=euler_angles_to_quat(np.array([0.0, 45.0, -90.0]),  degrees=True),
                                # range_res=0.01,
                                # angular_res=0.2,
                                # hori_res=50,
                                )
        self._left_side_sonar = None
        # self._left_side_sonar = SideScanSonarSensor(prim_path=robot_prim_path + '/left_side_sonar',
        #                         translation=self._left_sensor_location,
        #                         orientation=euler_angles_to_quat(np.array([0.0, 45.0, 90.0]),  degrees=True),
        #                         range_res=0.005,
        #                         angular_res=0.2,
        #                         hori_res=50,
        #                         )

    # def _setup_scene(self):
    #     """
    #     This function is attached to the Load Button as the setup_scene_fn callback.
    #     On pressing the Load Button, a new instance of World() is created and then this function is called.
    #     The user should now load their assets onto the stage and add them to the World Scene.
    #     """
    #     create_new_stage()
    #     world_prim_path = '/World'
    #     SingleXFormPrim(name='World',prim_path=world_prim_path)

    #     self._add_light_to_stage()

    #     domeLight = UsdLux.DomeLight.Define(get_current_stage(), Sdf.Path("/World/DomeLight"))
    #     domeLight.CreateIntensityAttr(1000)
    #     domeLight.CreateColorAttr(Gf.Vec3f(0.5, 0.7, 1.0))

    #     # # --- ADDING THE GROUND PLANE HERE ---
    #     # # The PhysicsGroundPlane creates a large, static plane at Z=0 by default.
    #     # # It's already configured for collisions.
    #     # PhysicsGroundPlane(prim_path=world_prim_path + "/groundPlane",
    #     #                    color=np.array([0.2, 0.3, 0.2])) # Optional: set a color
    #     # print(f"Added ground plane at {world_prim_path}/groundPlane")
    #     # # --- END GROUND PLANE ADDITION ---

    #     ship_prim_path = world_prim_path + '/ship_scene'

    #     add_reference_to_stage(usd_path='/home/nsieh/Downloads/ship/ship.usd',
    #                         prim_path=ship_prim_path)
        
    #     ship_xform_prim = SingleXFormPrim(prim_path=ship_prim_path)
        
    #     # Make sure this rotation is the one you finalized for your ship's orientation
    #     # rotation_degrees = np.array([0.0, -90.0, 90.0]) # Replace with your finalized ship rotation
    #     rotation_degrees = np.array([90.0, 0.0, 0.0])
    #     ship_orientation = euler_angles_to_quat(rotation_degrees, degrees=True)
    #     ship_xform_prim.set_world_pose(orientation=ship_orientation)

    #     # Load the robot
    #     robot_prim_path = world_prim_path + "/rob" 
    #     DynamicCuboid(prim_path=robot_prim_path, size=0.2, color=np.array([0.1,0.5,1]))
    #     self._rob = get_prim_at_path(robot_prim_path)
    #     SingleXFormPrim(robot_prim_path).set_world_pose(position=self._init_rob_pos, orientation=self._init_rob_orien)
    #     set_camera_view(eye=self._init_rob_pos + np.array([2,2,2]), target=self._init_rob_pos)
    #     # Toggle rigid body and apply zero gravity and zero damping
    #     rob_rigidBody_API = PhysxSchema.PhysxRigidBodyAPI.Apply(self._rob)
    #     rob_rigidBody_API.CreateDisableGravityAttr(True)
    #     rob_rigidBody_API.GetLinearDampingAttr().Set(self._rob_linear_damping)
    #     rob_rigidBody_API.GetAngularDampingAttr().Set(self._rob_angular_damping)
    #     rob_rigid_prim = SingleRigidPrim(robot_prim_path, mass=self._rob_mass) # Ensure this is assigned to self._rob_rigid_prim if you control it programmatically


    #     self._right_side_sonar = SideScanSonarSensor(prim_path=robot_prim_path + '/right_side_sonar',
    #                             translation=self._right_sensor_location,
    #                             orientation=euler_angles_to_quat(np.array([0.0, 45.0, -90.0]),  degrees=True),
    #                             range_res=0.005,
    #                             angular_res=0.2,
    #                             hori_res=50,
    #                             )
    #     self._left_side_sonar = SideScanSonarSensor(prim_path=robot_prim_path + '/left_side_sonar',
    #                             translation=self._left_sensor_location,
    #                             orientation=euler_angles_to_quat(np.array([0.0, 45.0, 90.0]),  degrees=True),
    #                             range_res=0.005,
    #                             angular_res=0.2,
    #                             hori_res=50,
    #                             )

    #     # add testing objects
    #     sphere_position = [(-0.3, 0.6, 0.6), (0, 0.8, 0.3), (0.3, 0.3, 0.3)]

    #     for i in range(len(sphere_position)):
    #         sphere_path = world_prim_path + f"/sphere_{i}"
    #         sphere = DynamicSphere(prim_path=sphere_path,
    #                     position=sphere_position[i],
    #                     scale=[0.1]*3)
    #         self._add_semantic_entry(sphere.prim,
    #                                 "sonar_ref",
    #                                 "reflectivity",
    #                                 "1.0")
    #         self._add_semantic_entry(sphere.prim,
    #                                 "semantics",
    #                                 "class",
    #                                 f"sphere_{i}")

    #         PhysxSchema.PhysxRigidBodyAPI.Apply(get_prim_at_path(sphere_path))




    def _setup_scenario(self):
        """
        This function is attached to the Load Button as the setup_post_load_fn callback.
        The user may assume that their assets have been loaded by their setup_scene_fn callback, that
        their objects are properly initialized, and that the timeline is paused on timestep 0.
        """
        self._reset_scenario()

        # UI management
        self._scenario_state_btn.reset()
        self._scenario_state_btn.enabled = True
        self._reset_btn.enabled = True

    def _reset_scenario(self):
        self._scenario.teardown_scenario()
        self._scenario.setup_scenario(self._rob, self._right_side_sonar, self._left_side_sonar)

    def _on_post_reset_btn(self):
        """
        This function is attached to the Reset Button as the post_reset_fn callback.
        The user may assume that their objects are properly initialized, and that the timeline is paused on timestep 0.

        They may also assume that objects that were added to the World.Scene have been moved to their default positions.
        I.e. the cube prim will move back to the position it was in when it was created in self._setup_scene().
        """
        self._reset_scenario()

        # UI management
        self._scenario_state_btn.reset()
        self._scenario_state_btn.enabled = True

    def _update_scenario(self, step: float):
        """This function is attached to the Run Scenario StateButton.
        This function was passed in as the physics_callback_fn argument.
        This means that when the a_text "RUN" is pressed, a subscription is made to call this function on every physics step.
        When the b_text "STOP" is pressed, the physics callback is removed.

        Args:
            step (float): The dt of the current physics step
        """
        self._right_side_sonar.make_side_sonar_data()
        # self._left_side_sonar.make_side_sonar_data()
        self._scenario.update_scenario(step)

    def _on_run_scenario_a_text(self):
        """
        This function is attached to the Run Scenario StateButton.
        This function was passed in as the on_a_click_fn argument.
        It is called when the StateButton is clicked while saying a_text "RUN".

        This function simply plays the timeline, which means that physics steps will start happening.  After the world is loaded or reset,
        the timeline is paused, which means that no physics steps will occur until the user makes it play either programmatically or
        through the left-hand UI toolbar.
        """
        self._timeline.play()

    def _on_run_scenario_b_text(self):
        """
        This function is attached to the Run Scenario StateButton.
        This function was passed in as the on_b_click_fn argument.
        It is called when the StateButton is clicked while saying a_text "STOP"

        Pausing the timeline on b_text is not strictly necessary for this example to run.
        Clicking "STOP" will cancel the physics subscription that updates the scenario, which means that
        the robot will stop getting new commands and the cube will stop updating without needing to
        pause at all.  The reason that the timeline is paused here is to prevent the robot being carried
        forward by momentum for a few frames after the physics subscription is canceled.  Pausing here makes
        this example prettier, but if curious, the user should observe what happens when this line is removed.
        """
        self._timeline.pause()

    def _reset_extension(self):
        """This is called when the user opens a new stage from self.on_stage_event().
        All state should be reset.
        """
        self._on_init()
        self._reset_ui()

    def _reset_ui(self):
        self._scenario_state_btn.reset()
        self._scenario_state_btn.enabled = False
        self._reset_btn.enabled = False