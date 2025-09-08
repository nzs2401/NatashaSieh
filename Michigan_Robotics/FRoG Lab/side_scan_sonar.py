from isaacsim.sensors.camera import Camera
import omni.replicator.core as rep
import omni.ui as ui
import numpy as np
import matplotlib.pyplot as plt
from omni.replicator.core.scripts.functional import write_np, write_image
import warp as wp
from isaacsim.oceansim.utils.ImagingSonar_kernels import *
from isaacsim.oceansim.sensors.ImagingSonarSensor import ImagingSonarSensor
from scipy.spatial.transform import Rotation as R

# TODO: 1. look into time varying and gain for filtering output to have less intensity in the near range
# TODO: 2. Decrease the horizontal FOV to scan the smaller window
# TODO: 3. Check out Advaith's code if still have problem implementing the SSS
class SideScanSonarSensor(Camera):     
   def __init__(self,
               prim_path,
               name = "SSS",
               frequency = None,
               dt = None,
               position = None,
               orientation = None,
               translation = None,
               render_product_path = None,
               physics_sim_view = None,
               min_range: float = 8.0, # was 6 m
               max_range: float = 10.0, # m
               range_res: float = 0.001,
               hori_fov: float = 0.5, # 0.5 angled  (was 2.0)
               vert_fov: float = 90.0, # thin vertical FOV for side scan
               angular_res: float = 0.25, # deg
               hori_res: int = 300 # (# of raycast) isaac camera render product only accepts square pixel,
                                   # for now vertical res is automatically set with ratio of hori_fov vs.vert_fov
               ):
  
  
       self._supported_annotators = []


       self._name = name
       self.max_range = max_range
       self.min_range = min_range
       self.range_res = range_res
       self.hori_fov = hori_fov
       self.vert_fov = vert_fov
       self.angular_res = np.deg2rad(angular_res)
       self.hori_res = hori_res


       # Create a 1D grid in range to represent sonar bins
       # This models side-scan sonar behavior where echoes are stored per angle.
       r_vals = np.arange(self.min_range, self.max_range, self.range_res)


       self.num_range_bins = len(r_vals)


       # Creating meshgrid & Arrays for accumulating sonar return data.
       # Each bin collects total intensity and hit count to build a normalized sonar map.
       self.r = wp.array(r_vals, dtype=wp.float32)


       self.bin_sum = wp.empty(shape=(self.num_range_bins), dtype=wp.float32)
       self.bin_count = wp.empty(shape=(self.num_range_bins), dtype=wp.int32)
       self.side_sonar_data = wp.empty(shape=self.r.shape, dtype=wp.vec3)
       self.side_sonar_image = wp.empty(shape=(self.num_range_bins, 4), dtype=wp.uint8)
       self.gau_noise = wp.empty(shape=(self.num_range_bins), dtype=wp.float32)
       self.range_dependent_ray_noise = wp.empty(shape=(self.num_range_bins), dtype=wp.float32)


       # Define sonar bin grid geometry for Warp-based binning kernels.
       self.sonar_grid = sonarGrid()
       self.sonar_grid.x_offset = self.min_range
       self.sonar_grid.x_res = self.range_res
       self.sonar_grid.y_res = self.angular_res
       self.sonar_grid.x_num = self.num_range_bins # Use calculated num_range_bins


       # Maintain accurate aspect ratio between horizontal and vertical resolution to match sonar's physical beam shape.
       self.AR = self.hori_fov / self.vert_fov
       self.vert_res = min(int(self.hori_res / self.AR), 4096)


       # Define dimensions of sonar "waterfall" display
       self.right_scan_width = self.num_range_bins # full width of the sonar image
       self.channel_count = 4 # width of waterfall display
       self.waterfall_height = 720

     # Create a buffer to store the last few sonar scans for visualizing the waterfall effect
       self.waterfall = wp.empty(shape=(self.waterfall_height, self.num_range_bins, 4), dtype=wp.uint8)
       self.waterfall_buffer = wp.empty_like(self.waterfall)


       # Init base class
       super().__init__(prim_path=prim_path,
                       name=name,
                       frequency=frequency,
                       dt=dt,
                       resolution=[self.hori_res, self.vert_res],
                       position=position,
                       orientation=orientation,
                       translation=translation,
                       render_product_path=render_product_path)
       self.set_clipping_range(
           near_distance=self.min_range,
           far_distance=self.max_range
       )


       # Required camera init workaround
       super().initialize(physics_sim_view)


       # Compute and set horizontal aperture
       self.focal_length = self.get_focal_length()
       horizontal_aper = 2 * self.focal_length * np.tan(np.deg2rad(self.hori_fov) / 2)
       self.set_horizontal_aperture(horizontal_aper)


   # Function to extract a right-side row for updating waterfall display
   def get_right_scan_waterfall_row(self):
       # Extract the last row of the right side sonar image
       return self.side_sonar_image.numpy()
  
   # # Function to extract a left-side row for updating waterfall display
   # def get_left_scan_waterfall_row(self):
   #     # Extract the last row of the left side sonar image
   #     return self.left_side_sonar_image.numpy()


   # combined = np.hstack([self.left_waterfall_img, self.right_waterfall_img])
   '''
   The get_right_scan_waterfall_row function extracts data from the "bottom" (last row) of its source.
   However, the update_waterfall function then uses np.roll to move all existing data down and places this newly extracted "bottom" row at the top of the waterfall_buffer.
   This is the standard way to create a waterfall display where new data appears at the top and pushes older data down.
   '''
   # Function to update the waterfall display with the latest sonar scan
   def update_waterfall(self):
      
       # # extract latest sonar row
       # right_row = self.get_right_scan_waterfall_row()
       # # left_row = self.get_left_scan_waterfall_row()


       # # new_row = np.concatenate([left_row, right_row], axis=0)


       # # remove oldest row and add new one to the top
       # self.waterfall_buffer = np.roll(self.waterfall_buffer, 1, axis=0)
       # self.waterfall_buffer[0, :, :] = new_row


       # extract latest sonar row
       new_row = self.get_right_scan_waterfall_row()


       # remove oldest row and add new one to the top
       self.waterfall_buffer = np.roll(self.waterfall_buffer, 1, axis=0)
       self.waterfall_buffer[0, :, :] = new_row




   def side_sonar_initialize(self,
                        normalizing_method: str = "range",
                        viewport: bool = True,
                        privileged_bbox: bool = False,
                        include_unlabelled = False,
                        if_array_copy: bool = True):
       """Initialize sonar data processing pipeline and annotators.
  
       Args:
           normalizing_method (str, optional): Choose between "range" for normalization per range (r) or "all" for the normalization from the whole map
           viewport (bool, optional): Enable viewport visualization. Defaults to True.
                                       Set to False for Sonar running without visualization.
           include_unlabelled (bool, optional): Include unlabelled objects to be scanned into sonar view. Defaults to False.
           if_array_copy (bool, optional): If True, retrieve a copy of the data array.
                                           This is recommended for workflows using asynchronous backends to manage the data lifetime.
                                           Can be set to False to gain performance if the data is expected to be used immediately within the writer.
                                           Defaults to True.
                                          
       Note:
           - Attaches pointcloud, camera params, and semantic segmentation annotators
           - Sets up Warp arrays for sonar image processing
           - Can optionally write data to disk if output_dir specified
       """
       self._viewport = viewport
       self._privileged_bbox = privileged_bbox
       self._device = str(wp.get_preferred_device())
       self.scan_data = {}
       self.id = 0


       self.pointcloud_annot = rep.AnnotatorRegistry.get_annotator(
           name="pointcloud",
           init_params={"includeUnlabelled": include_unlabelled},
           do_array_copy=if_array_copy,
           device=self._device
           )
      
       self.cameraParams_annot = rep.AnnotatorRegistry.get_annotator(
           name="CameraParams",
           do_array_copy=if_array_copy,
           device=self._device
           )
      
       self.semanticSeg_annot = rep.AnnotatorRegistry.get_annotator(
           name="semantic_segmentation",
           init_params={"colorize": False},
           do_array_copy=if_array_copy,
           device=self._device
       )


       print(f'[{self._name}] Render query res: {self.hori_res} x {self.vert_res}. Num Range Bins: {self.num_range_bins}')


       self.pointcloud_annot.attach(self._render_product_path)
       self.cameraParams_annot.attach(self._render_product_path)
       self.semanticSeg_annot.attach(self._render_product_path)


      
       if self._viewport:
           self.make_sonar_viewport()
      
       if self._privileged_bbox:
           self.bbox_annot = rep.AnnotatorRegistry.get_annotator(
               name='bounding_box_3d_fast',
               do_array_copy=if_array_copy,
           )
           self.bbox_annot.attach(self._render_product_path)


       if normalizing_method == "all":
           self._max_intensity = wp.zeros(shape=(1,), dtype=wp.float32)
           self._left_max_intensity = wp.zeros(shape=(1,), dtype=wp.float32)
           self._compute_max_intensity = side_compute_max_intensity_all
           self._make_sonar_map = side_make_sonar_map_all
       elif normalizing_method == "range":
           self._max_intensity = wp.zeros(shape=(self.r.shape[0],), dtype=wp.float32)
           self._left_max_intensity = wp.zeros(shape=(self.r.shape[0],), dtype=wp.float32)
           self._compute_max_intensity = side_compute_max_intensity_range
           self._make_sonar_map = side_make_sonar_map_range
      




   def scan(self):


       self.scan_data = {
       "pcl": None,
       "normals": None,
       "semantics": None,
       "viewTransform": None,
       "idToLabels": None,
       }


       """Capture a single sonar scan frame and store the raw data.
  
       Returns:
           bool: True if scan was successful (valid data received), False otherwise
  
       Note:
           - Stores pointcloud, normals, semantics, and camera transform in scan_data dict
           - First few frames may be empty due to CUDA initialization
           - Automatically skips frames with no detected objects
       """
       # Due to the time to load annotator to cuda, the first few simulation tick gives no annotation in memory.
       # This would also reult error when no mesh within the sonar fov
       # Ignore scan that gives empty data stream
       if len(self.semanticSeg_annot.get_data()['info']['idToLabels']) !=0:
           pointcloud_data = self.pointcloud_annot.get_data(device=self._device)
           self.scan_data['pcl'] = self.pointcloud_annot.get_data(device=self._device)['data']  # shape :(1,N,3) <class 'warp.types.array'>
           self.scan_data['normals'] = self.pointcloud_annot.get_data(device=self._device)['info']['pointNormals'] # shape :(1,N,4) <class 'warp.types.array'>
           self.scan_data['semantics'] = self.pointcloud_annot.get_data(device=self._device)['info']['pointSemantic'] # shape: (1, N) <class 'warp.types.array'>
           self.scan_data['viewTransform'] = self.cameraParams_annot.get_data()['cameraViewTransform'].reshape(4,4).T # 4 by 4 np.ndarray extrinsic matrix
           self.scan_data['idToLabels'] = self.semanticSeg_annot.get_data()['info']['idToLabels'] # dict
       else:
           pass


       if self.scan_data['pcl'] is not None and self.scan_data['pcl'].shape[0] > 0:
           # print(f"[{self._name}] Sample PCL data (first 3 points): {self.scan_data['pcl'].numpy()[:3]}")
           self.id += 1
           return True
       else:
           # print(f"[{self._name}] PCL data is empty or None.")
           self.id += 1
           return False
          


   @staticmethod
   def make_indexToProp_array(idToLabels: dict, query_property: str) -> np.ndarray:
       """ A utility function helps to convert idToLabels into indexToProp array
       This manipulation facilitates warp computation framework
       indexToProp is an 1-dim array where the values associated with the query property
       are placed at the index corresponding to the key
       First two entry are always zero because {'0': {'class': 'BACKGROUND'}, '1': {'class': 'UNLABELLED'}}
       eg: indexToProp = [0, 0, 0.1, 1 .....]
       """
       max_id = max(idToLabels.keys(), default=-1)
       indexToProp_array = np.ones((int(max_id)+1,))
       for id in idToLabels.keys():
           for property in idToLabels.get(id):
               if property == query_property:
                   indexToProp_array[int(id)] = idToLabels.get(id).get(property)
       return indexToProp_array
      


   def make_side_sonar_data(self,
                       query_prop: str ='reflectivity', # Do not modify this if not developing the sensor.
                       attenuation: float = 1.0, # Control the attentuation along distance when computing attenuation
                       gau_noise_param: float = 0.05, # multiplicative noise coefficient
                       ray_noise_param: float = 0.05, # additive noise parameter
                       intensity_offset: float = 0.0, # offset intensity after normalization
                       intensity_gain: float = 1.0, # scale intensity after normalization
                       central_peak: float = 0.0, # control the strength of the streak
                       central_std: float = 0.001, # control the spread of the streak
                       ):
       """Process raw scan data into a sonar image with configurable parameters.


       Args:
           query_prop (str): Material property to query (default 'reflectivity')
                           Don't modify this if not for development.
           attenuation (float): Distance attenuation coefficient (0-1)
           gau_noise_param (float): Gaussian noise multiplier
           ray_noise_param (float): Rayleigh noise scale factor
           intensity_offset (float): Post-normalization intensity offset
           intensity_gain (float): Post-normalization intensity multiplier
           central_peak (float): Central beam streak intensity
           central_std (float): Central beam streak width
  
       """


       if not self.scan():
           return


       num_points = self.scan_data['pcl'].shape[0]
       # Load these small numpy arrays to cuda
       indexToRefl_np = self.make_indexToProp_array(idToLabels=self.scan_data['idToLabels'],
                                                       query_property=query_prop)
       indexToRefl = wp.array(data=indexToRefl_np, dtype=wp.float32)
       viewTransform = wp.mat44(self.scan_data['viewTransform'])




       # Compute intensity for each ray query
       intensity = wp.empty(shape=(num_points,), dtype=wp.float32)


       wp.launch(kernel=compute_intensity,
               dim=num_points,
               inputs=[
                   self.scan_data['pcl'],
                   self.scan_data['normals'],
                   viewTransform,
                   self.scan_data['semantics'],
                   indexToRefl,
                   attenuation,
               ],
               outputs=[intensity]
               )


       # print("BEFORE intensity first 100:", intensity.numpy()[:100])       


              
       # Transform pointcloud from world cooridates to sonar local and convert to spherical coord
       pcl_bin_idx = wp.empty(shape=(num_points, ), dtype=wp.vec2ui)
       pcl_range = wp.empty(shape=(num_points, ), dtype=wp.float32)


       # Inject Gaussian and Rayleigh noise to mimic real sonar distortions.
       # Central streak simulates typical strong beamline artifacts.
  
       wp.launch(kernel=side_world2local,
               dim=num_points,
               inputs=[
                   viewTransform,
                   self.scan_data['pcl']
               ],
                   outputs=[
                   pcl_range
                   ]
               )
      
       # Collapse three dimensional intensity data to 2D
       # Simply sum intensity return and compute number of return that falls into the same bin
       # Zero out intensity in each bin (do not omit this, this is necessary)
       self.bin_sum.zero_()
       self.bin_count.zero_()


       # self.left_bin_sum.zero_()
       # self.left_bin_count.zero_()


       # self.side_bin_semantics.zero_()
       # self.left_side_bin_semantics.zero_()


       wp.launch(kernel=side_bin_process,
                 dim=pcl_range.shape[0],
               # dim=num_points,
               inputs=[
                   pcl_range,
                   intensity,
                   self.sonar_grid
               ],
               outputs=[
                   self.bin_sum,
                   self.bin_count,
                   # pcl_bin_idx,
               ]
               )
      
       # print("x_offset:", self.sonar_grid.x_offset)
       # print("x_res:", self.sonar_grid.x_res)
       # print("x_num:", self.sonar_grid.x_num)
    #    print("bin_count:", self.bin_count.size())
       # print("Total bins span:", self.sonar_grid.x_offset + self.sonar_grid.x_res * self.sonar_grid.x_num)
       # print("pcl_range min:", pcl_range.numpy().min())
       # print("pcl_range max:", pcl_range.numpy().max())
       # print("intensity min:", intensity.numpy().min())
       # print("intensity max:", intensity.numpy().max())
      
       wp.launch(
           kernel=side_normal_1d,
           dim=self.bin_sum.shape,
           inputs=[
               self.id,   # use frame num for RNG seed increment
               0.0,
               gau_noise_param
           ],
           outputs=[
               self.gau_noise
           ]
       )


       wp.launch(
           kernel=side_range_dependent_rayleigh_1d,
           dim=self.bin_sum.shape,
           inputs=[
               self.id,   # use frame num for RNG seed increment
               self.r,
               # self.azi,
               self.max_range,
               ray_noise_param,
               central_peak,
               central_std,
           ],
           outputs=[
               self.range_dependent_ray_noise


           ]
       )


       # pre-normalization intensity for one row of the sonar image
    #    print("[DEBUG] bin_sum row before normalization:", bin_sum_np[row_idx])


       self._max_intensity.fill_(-wp.inf)
       # Normalizing intensity at each bin either by global maximum or rangewise maximum
       wp.launch(
           # dim=self.bin_sum.shape,
           dim=self.bin_sum.shape[0],
           kernel=self._compute_max_intensity,
           inputs=[
               self.bin_sum,
           ],
           outputs=[
               self._max_intensity
           ]
       )
      
       wp.synchronize()


       # print("Max intensity array sample:", self._max_intensity.numpy()[:])
       # print("Max intensity array min/max:", self._max_intensity.numpy().min(), self._max_intensity.numpy().max())


       wp.launch(
           kernel=self._make_sonar_map, # Convert binned (range, azimuth) sonar data into a flat intensity map.
                                        # This is the classic sonar swath image representation.
           dim=self.side_sonar_data.shape,
           inputs=[
               self.r,
               # self.azi,
               self.bin_sum,
               self._max_intensity,
               self.gau_noise,
               self.range_dependent_ray_noise,
               intensity_offset,
               intensity_gain,
               # num_intensity
               # attenuation
           ],
           outputs=[
               self.side_sonar_data
           ]
           )
       
       np.save("/home/nsieh/Desktop/before_bin_sum.npy",arr=self.bin_sum.numpy())
       
       # Create output array with same shape as bin_sum
       self.out_array = wp.empty(self.bin_count.shape[0], dtype=wp.float32)

       wp.launch(kernel=normalize_bin,
                dim=self.bin_sum.shape[0],
                inputs=[self.bin_sum, self.bin_count,self.out_array])

      
       # print("Intensity min/max:", intensity.numpy().min(), intensity.numpy().max())
       # print("Max intensity min/max:", self._max_intensity.numpy().min(), self._max_intensity.numpy().max())
       # print("Gau noise min/max:", self.gau_noise.numpy().min(), self.gau_noise.numpy().max())
       # print("Ray noise min/max:", self.range_dependent_ray_noise.numpy().min(), self.range_dependent_ray_noise.numpy().max())


       # side_sonar_data_np = self.side_sonar_data.numpy()
       # print("AFTER normalization (actual intensity values):", side_sonar_data_np[:, 2])   
       # print("AFTER intensity first 100:", self.side_sonar_data.numpy()[:100])    
      
       if self._viewport:
           self.get_side_sonar_image()
           # self.get_left_side_sonar_image()
           # self.get_side_semantics_image()


       # print("[SSS] bin_sum total:", self.bin_sum.numpy().sum())
    #    print("[SSS] bin_count total:", self.bin_count.numpy().sum())
       np.save("/home/nsieh/Desktop/bin_sum.npy",arr=self.out_array.numpy())
       # print("[SSS] Max intensity after normalization:", self._max_intensity.numpy().max())
       # print("[SSS] Sample sonar data [0,0]:", self.side_sonar_data.numpy()[0, 0])


   def get_sonar_data(self) -> wp.array:
       """Get GPU array of sonar data


       Returns:
           sonar_data (wp.array(dtype=wp.vec3)): shaped (num_r_bin, num_azi_bin), with each entry a wp.vec3 containing [x, y, bin_intensity]
       with (x, y) are cartesian coordinates of the (r, azi) of the bin.
       """
       return self.side_sonar_data
  
   # def get_left_sonar_data(self) -> wp.array:
   #     """Get GPU array of sonar data


   #     Returns:
   #         sonar_data (wp.array(dtype=wp.vec3)): shaped (num_r_bin, num_azi_bin), with each entry a wp.vec3 containing [x, y, bin_intensity]
   #     with (x, y) are cartesian coordinates of the (r, azi) of the bin.
   #     """
   #     return self.left_side_sonar_data
  
   def get_side_sonar_image(self) -> wp.array:
        """Convert processed sonar data to a viewable grayscale image.
    
        Returns:
            sonar_image (wp.array(dtype=wp.uint8)): GPU array containing the sonar image (RGBA format) 
    
        Note:
            - Used internally for viewport display
            - Image dimensions match the sonar's polar binning resolution
        """

        wp.launch(
            dim=(self.side_sonar_image.shape[0],),  # <-- positional `dim`
            # dim=(self.num_range_bins,),
            kernel=make_side_sonar_image,  # <-- positional `kernel`
            inputs=[self.side_sonar_data],  # <-- keyword
            outputs=[self.side_sonar_image],  # <-- keyword
        )
        # Synchronize to ensure all GPU operations are complete before accessing the image
        wp.synchronize()


        wp.launch(
                  dim=(self.waterfall_height-1, self.num_range_bins, 4),
                  kernel=update_waterfall,
                  inputs=[
                      self.waterfall,
                      self.waterfall_buffer,
                  ])
        
        wp.launch(
            dim=(self.num_range_bins, 4),
            kernel=update_first_row,
            inputs=[
                self.side_sonar_image,
                self.waterfall,
            ]
        )
        wp.copy(self.waterfall_buffer, self.waterfall)

        self._sonar_provider.set_bytes_data_from_gpu(self.waterfall.ptr, [self.num_range_bins, self.waterfall_height])


        return self.side_sonar_image

   @staticmethod
   def get_bbox_3d_corners(bbox_data):
       """Return transformed points in the following order: [LDB, RDB, LUB, RUB, LDF, RDF, LUF, RUF]
       where R=Right, L=Left, D=Down, U=Up, B=Back, F=Front and LR: x-axis, UD: y-axis, FB: z-axis.


       Args:
           bbox_data (numpy.ndarray): A structured numpy array containing the fields: [`x_min`, `y_min`,
               `x_max`, `y_max`, `transform`.


       Returns:
           corners_world (numpy.ndarray): Transformed corner homogeneous coordinates at world frame with shape `(N, 8, 4)`.
           N: number of bbox, 8: eight corners, 4: homogeneous coordinates [x,y,z,1]
       """


       # extend the demension of input data to fit the format of helper method parameter"""
       rdb = [bbox_data["x_max"], bbox_data["y_min"], bbox_data["z_min"]]
       ldb = [bbox_data["x_min"], bbox_data["y_min"], bbox_data["z_min"]]
       lub = [bbox_data["x_min"], bbox_data["y_max"], bbox_data["z_min"]]
       rub = [bbox_data["x_max"], bbox_data["y_max"], bbox_data["z_min"]]
       ldf = [bbox_data["x_min"], bbox_data["y_min"], bbox_data["z_max"]]
       rdf = [bbox_data["x_max"], bbox_data["y_min"], bbox_data["z_max"]]
       luf = [bbox_data["x_min"], bbox_data["y_max"], bbox_data["z_max"]]
       ruf = [bbox_data["x_max"], bbox_data["y_max"], bbox_data["z_max"]]
       tfs = bbox_data["transform"]
       corners = np.stack((ldb, rdb, lub, rub, ldf, rdf, luf, ruf), 0)
       # Homogenize the coordinate
       corners_homo = np.pad(corners, ((0, 0), (0, 1), (0, 0)), constant_values=1.0)
       # local object frame to world frame
       corners_world = np.einsum("jki,ikl->ijl", corners_homo, tfs)
     
       return corners_world
  
   def process_bbox_corners(self, bbox_3d_corners):
       """Process the bbox3d data directly from annotator
       Returns:
           corners_min, corners_max : np.ndarray((N,2)), np.ndarray((N,2))
           corners_min is the [(x_min, y_min), ...] that defines all the detected bboxes in the image frame
           corners_max is the [(x_max, y_max), ...] that defines all the detected bboxes in the image frame
       """
       N = bbox_3d_corners.shape[0]
       # world frame to camera frame
       corners_local = np.einsum('ijk,lk->ijl', bbox_3d_corners, self.scan_data['viewTransform'])
       # Rotate axis such that y axis pointing forward for sonar data plotting
       corners_local = np.einsum('ijk,lk->ijl', corners_local, np.array([[1,0,0,0],
                                                                         [0,0,-1,0],
                                                                         [0,1,0,0],
                                                                         [0,0,0,1]]))
       # collapse to 2d sonar grid
       corners_min = np.zeros(shape=(N, 2), dtype=np.int32)
       corners_max = np.zeros(shape=(N, 2), dtype=np.int32)
       corners_local = corners_local[..., :3] # shape: [N,8,3]
       r = np.linalg.norm(corners_local, axis=-1) # shape: [N, 8]
       # azi = np.arctan2(corners_local[..., 1], corners_local[..., 0]) # shape: [N, 8]
       x_pix = np.int32((r - self.min_range) / self.range_res) # shape: [N, 8]
       # y_pix = np.int32((azi - self.min_azi) / self.angular_res) # shape: [N, 8]
       x_pix = np.clip(x_pix, 0, self.r.shape[0]-1)
       y_pix = np.clip(y_pix, 0, self.r.shape[1]-1)
       corners_min[..., 0] = np.min(x_pix, axis=1)
       corners_min[..., 1] = np.min(y_pix, axis=1)
       corners_max[..., 0] = np.max(x_pix, axis=1)
       corners_max[..., 1] = np.max(y_pix, axis=1)


       return corners_min, corners_max


  
  
   def get_priviledged_bbox(self):
       """Priviledged bbox means the bbox computed from the scene, not from the sensor view. It's called priviledged because observer
       itself won't be able to access this information. For regular bbox, simply use cv2.findCentroid() on semantics information.


       Returns:
           bbox_id: bbox's id
           bbox_min: is the [(x_min, y_min), ...] that defines all the detected bboxes in the image frame
           bbox_max: is the [(x_max, y_max), ...] that defines all the detected bboxes in the image frame
       """
       if self._privileged_bbox and len(self.semanticSeg_annot.get_data()['info']['idToLabels']) !=0:
           self.scan_data['bbox'] = self.bbox_annot.get_data()['data']
           self.scan_data['bbox_ids'] = self.bbox_annot.get_data()['info']['bboxIds']
           # Compute the privileged bbox
           bbox_corners = self.get_bbox_3d_corners(self.scan_data['bbox'])
           bbox_min, bbox_max = self.process_bbox_corners(bbox_corners)
           return self.scan_data['bbox_ids'], bbox_min, bbox_max
       else:
           # print(f'[{self._name}] Initialize with priviledged_bbox to true before calling this.')
           return
  
  
   @staticmethod
   def draw_bbox_on_image(bboxes_min : np.ndarray,
                 bboxes_max : np.ndarray,
                 image : wp.array,
                 colormap : str = 'turbo'):
       """
       Args:
           bbox_min: is the [(x_min, y_min), ...] that defines all the detected bboxes in the image frame
           bbox_max: is the [(x_max, y_max), ...] that defines all the detected bboxes in the image frame         
           image: GPU array containing the image (RGBA) wp.array(dtype=wp.uint8)
           colormap: (str) following plt's cmap standard
       """
      
       num_bboxes = bboxes_min.shape[0]
       cmap = plt.get_cmap(colormap)
       side_colors = cmap(np.linspace(0, 1, num_bboxes)) * 255  # Get n colors from the colormap


      
       for i in range(num_bboxes): 
           wp.launch(
               kernel = draw_bbox,
               dim=(bboxes_max[i,0]-bboxes_min[i,0],
                   bboxes_max[i,1]-bboxes_min[i,1]),
               inputs=[
                   i,
                   wp.array(data=bboxes_min, ndim=2, dtype=wp.int32),
                   wp.array(data=bboxes_max, ndim=2, dtype=wp.int32),
                   wp.array(data=side_colors, ndim=2, dtype=wp.uint8),
                   image
               ]
           )






   def make_sonar_viewport(self):
       """Create an interactive viewport window for real-time sonar visualization.
  
       Note:
           - Displays live sonar images when simulation is running
           - Includes range and azimuth tick marks
           - Window size is fixed at 1440x760 pixels
       """
       self.wrapped_ui_elements = []


       self._sonar_provider = ui.ByteImageProvider()
       self._sonar_segmentation_provider = ui.ByteImageProvider()
       self._window = ui.Window(self._name, width=1440, height=720+40, visible=True)
      
       with self._window.frame:
           with ui.ZStack(height=1440, width = 1440):
               ui.Rectangle(widthstyle={"background_color": 0xFF000000})
               ui.Label('Run the scenario for image to be received',
                        style={'font_size': 55,'alignment': ui.Alignment.CENTER},
                        word_wrap=True)
               with ui.HStack(height=1440, width = 1440):
                   sonar_image_provider = ui.ImageWithProvider(self._sonar_provider,
                                       style={"width": 1440,
                                           "height": 1440,
                                           "fill_policy" : ui.FillPolicy.STRETCH,
                                           'alignment': ui.Alignment.CENTER})
                   # segmentation_image_provider = ui.ImageWithProvider(self._sonar_segmentation_provider,
                   #                                                    style={"width": 720,
                   #                                                    "height": 720,
                   #                                                    "fill_policy" : ui.FillPolicy.STRETCH,
                   #                                                    'alignment': ui.Alignment.CENTER})
      
       self.wrapped_ui_elements.append(sonar_image_provider)
       # self.wrapped_ui_elements.append(segmentation_image_provider)
       self.wrapped_ui_elements.append(self._sonar_provider)
       self.wrapped_ui_elements.append(self._sonar_segmentation_provider)
       self.wrapped_ui_elements.append(self._window)


   def update_viewport_img(self):
       # Get latest sonar image as a np array
       # img_np = np.flipud(self.waterfall_buffer)
       img_np = (self.waterfall_buffer)


        # Ensure img_np is C-contiguous for tobytes()
       if not img_np.flags['C_CONTIGUOUS']:
           img_np = np.ascontiguousarray(img_np)


       # Update UI
       # self._sonar_provider.set_data(img_np.flatten(), list(img_np.shape))
       # self._sonar_provider.set_bytes_data(img_np.flatten(), list(img_np.shape))
       explicit_stride = img_np.shape[1] * img_np.shape[2] * img_np.itemsize
       self._sonar_provider.set_bytes_data(
           bytearray(img_np.tobytes()),
           [img_np.shape[1], img_np.shape[0]], # Correct order: [width, height]
           ui.TextureFormat.RGBA8_UNORM,             # Still assuming 4-channel, uint8, RGBA
           explicit_stride                       # Pass the calculated stride explicitly
       )
      




   def get_range(self) -> list[float]:
       """Get the configured operating range of the sonar.
  
       Returns:
           list[float]: [min_range, max_range] in meters
       """
       return [self.min_range, self.max_range]
  
   def get_fov(self) -> list[float]:
       """Get the configured field of view angles.
  
       Returns:
           list[float]: [horizontal_fov, vertical_fov] in degrees
       """
       return [self.hori_fov, self.vert_fov]
  


  
   def close(self):
       """Clean up resources by detaching annotators and clearing caches.
  
       Note:
           - Required for proper shutdown when done using the sensor
           - Also closes viewport window if one was created
       """
       self.pointcloud_annot.detach(self._render_product_path)
       self.cameraParams_annot.detach(self._render_product_path)
       self.semanticSeg_annot.detach(self._render_product_path)


       rep.AnnotatorCache.clear(self.pointcloud_annot)
       rep.AnnotatorCache.clear(self.cameraParams_annot)
       rep.AnnotatorCache.clear(self.semanticSeg_annot)


       print(f'[{self._name}] Annotator detached. AnnotatorCache cleaned.')


       if self._viewport:
           self.ui_destroy()


       if self._privileged_bbox:
           self.bbox_annot.detach(self._render_product_path)
           rep.AnnotatorCache.clearn(self.bbox_annot)






   def ui_destroy(self):
       """Explicitly destroy viewport UI elements.
  
       Note:
           - Called automatically by close()
           - Only needed if manually managing UI lifecycle
       """
       for elem in self.wrapped_ui_elements:
           elem.destroy()