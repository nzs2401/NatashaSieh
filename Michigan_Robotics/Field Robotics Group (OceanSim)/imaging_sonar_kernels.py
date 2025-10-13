import warp as wp
from typing import Any

@wp.struct
class sonarGrid:
    x_offset: float
    y_offset: float
    x_res: float
    y_res: float
    x_num: wp.uint32
    y_num: wp.uint32

@wp.func
def cartesian_to_spherical(cart: wp.vec3) -> wp.vec3:
    r = wp.sqrt(cart[0]*cart[0] + cart[1]*cart[1] + cart[2]*cart[2])
    return wp.vec3(r,
                wp.atan2(cart[1], cart[0]),
                wp.acos(cart[2] / r)
                )
                                    

@wp.kernel
def compute_intensity(pcl: wp.array(ndim=2, dtype=wp.float32),
                    normals: wp.array(ndim=2, dtype=wp.float32),
                    viewTransform: wp.mat44,
                    semantics: wp.array(ndim=1, dtype=wp.uint32),
                    indexToRefl: wp.array(dtype=wp.float32),
                    attenuation: float,
                    intensity: wp.array(dtype=wp.float32)
                    ):
    tid = wp.tid() # index of current point 
    pcl_vec = wp.vec3(pcl[tid,0], pcl[tid,1], pcl[tid,2]) # 3D position for current point
    normal_vec = wp.vec3(normals[tid,0], normals[tid,1],normals[tid,2]) # 3D position for normal of current point
    R = wp.mat33(viewTransform[0,0], viewTransform[0,1], viewTransform[0,2],
                 viewTransform[1,0], viewTransform[1,1], viewTransform[1,2],
                 viewTransform[2,0], viewTransform[2,1], viewTransform[2,2]) # rotation matrix from world frame to sensor frame
    T = wp.vec3(viewTransform[0,3], viewTransform[1,3], viewTransform[2,3]) # translation vector from world frame to sensor frame
    sensor_loc = - (wp.transpose(R) @ T) # computes the location of the sensor (origin of sensor frame) in world coordinates
    incidence = pcl_vec - sensor_loc # incidence vector is the direction from the sensor to the surface point
    # Will use warp.math.norm_l2() in future release
    dist = wp.sqrt(incidence[0]*incidence[0] + incidence[1]*incidence[1] + incidence[2]*incidence[2]) # distance equation
    unit_directs = wp.normalize(pcl_vec - sensor_loc) # normalized direction from sensor to the point
    cos_theta = wp.dot(-unit_directs, normal_vec) # cos between view direction and normal because flatter surfaces reflect more
    reflectivity = indexToRefl[semantics[tid]] # value based on indexToRefl table
    intensity[tid] = reflectivity * cos_theta * wp.exp(-attenuation * dist) # compute intensity of each point based on these parameters

@wp.kernel
def world2local(viewTransform: wp.mat44,
                pcl_world: wp.array(ndim=2, dtype=wp.float32),
                pcl_local_spher: wp.array(dtype=wp.vec3)):
    tid = wp.tid()
    pcl_world_homogeneous = wp.vec4(pcl_world[tid,0],
                          pcl_world[tid,1],
                          pcl_world[tid,2],
                          wp.float32(1.0)
                          )
    pcl_local_homogeneous = viewTransform @ pcl_world_homogeneous
    # Rotate axis such that y axis pointing forward for sonar data plotting
    pcl_local = wp.vec3(pcl_local_homogeneous[0], -pcl_local_homogeneous[2], pcl_local_homogeneous[1])
    pcl_local_spher[tid] = cartesian_to_spherical(pcl_local)

@wp.kernel
def side_world2local(viewTransform: wp.mat44,
                     pcl_world: wp.array(ndim=2, dtype=wp.float32),
                     pcl_range: wp.array(dtype=wp.float32)):
    tid = wp.tid()

    # Read world point
    x = pcl_world[tid, 0]
    y = pcl_world[tid, 1]
    z = pcl_world[tid, 2]

    # Skip if nan
    if wp.isnan(x) or wp.isnan(y) or wp.isnan(z):
        pcl_range[tid] = 0.0
        return

    # Homogeneous vector
    px = x
    py = y
    pz = z
    pw = 1.0

    # Transform into local frame manually
    lx = viewTransform[0, 0]*px + viewTransform[0, 1]*py + viewTransform[0, 2]*pz + viewTransform[0, 3]*pw
    ly = viewTransform[1, 0]*px + viewTransform[1, 1]*py + viewTransform[1, 2]*pz + viewTransform[1, 3]*pw
    lz = viewTransform[2, 0]*px + viewTransform[2, 1]*py + viewTransform[2, 2]*pz + viewTransform[2, 3]*pw
    lx = -lx

    # Compute range
    r = wp.sqrt(lx*lx + ly*ly + lz*lz)

    # Avoid NaNs or very small numbers
    if wp.isnan(r) or wp.isinf(r) or r < 1e-3:
        pcl_range[tid] = 0.0
        return

    pcl_range[tid] = r


@wp.kernel
def bin_process(pcl: wp.array(dtype=wp.vec3),
                  intensity: wp.array(dtype=wp.float32),
                  semantics: wp.array(dtype=wp.uint32),
                  sonar_grid: sonarGrid,
                  bin_sum: wp.array(ndim=2, dtype=wp.float32),
                  bin_count: wp.array(ndim=2, dtype=wp.int32),
                  pcl_bin_idx: wp.array(dtype=wp.vec2ui),
                  bin_min_zenith: wp.array(ndim=2, dtype=wp.float32)
                  ):
    tid = wp.tid()

    # Get the range, azimuth of the point
    x = pcl[tid][0]
    y = pcl[tid][1]
    # Calculate the bin indices for range and azimuth
    x_bin_idx = wp.uint32((x - sonar_grid.x_offset) / sonar_grid.x_res)
    y_bin_idx = wp.uint32((y - sonar_grid.y_offset) / sonar_grid.y_res)
    wp.atomic_add(bin_sum, x_bin_idx, y_bin_idx, intensity[tid])
    wp.atomic_add(bin_count, x_bin_idx, y_bin_idx, 1)
    # Store the bin idx that corresponding to this pcl
    pcl_bin_idx[tid] = wp.vec2ui(x_bin_idx, y_bin_idx)
    # Store the minimum zenith value recorded for all the pcl 
    # that falls into this bin and is not background or unlabelled
    # if semantics[tid] != 0 or 1:
    #     wp.atomic_min(bin_min_zenith, x_bin_idx, y_bin_idx, pcl[tid][2])
    if semantics[tid] != 0 and semantics[tid] != 1:
        wp.atomic_min(bin_min_zenith, x_bin_idx, y_bin_idx, pcl[tid][2])

@wp.kernel
# For one sonar ping, it processes a 1D array of point ranges.
# It bins those points by range using x_offset and x_res.
# It collapses the data into a 1D array of intensity sums per bin: bin_sum.
def side_bin_process(
    pcl_range: wp.array(dtype=wp.float32),
    intensity: wp.array(dtype=wp.float32),
    sonar_grid: sonarGrid,                       # Must define x_offset and x_res
    bin_sum: wp.array(dtype=wp.float32),         # Shape: (num_range_bins,)
    bin_count: wp.array(dtype=wp.int32),         # Shape: (num_range_bins,)
):
    tid = wp.tid()

    r = pcl_range[tid]

    # Manual unpacking
    x_offset = sonar_grid.x_offset
    x_res = sonar_grid.x_res
    x_num = sonar_grid.x_num

    # Early exits to avoid out-of-bounds indexing
    if r < x_offset:
        return

    if r >= x_offset + x_res * float(x_num):
        return

    # Safe to compute bin index now
    r_bin_idx = wp.uint32((r - x_offset) / x_res)

    # NEW: safeguard
    if r_bin_idx >= x_num:
        return  # Or optionally, write to a debug counter

    wp.atomic_add(bin_sum, r_bin_idx, intensity[tid])
    wp.atomic_add(bin_count, r_bin_idx, 1)

@wp.kernel
def bin_semantics_process(pcl: wp.array(dtype=wp.vec3),
                          semantics: wp.array(dtype=wp.uint32),
                          pcl_bin_idx: wp.array(dtype=wp.vec2ui),
                          bin_min_zenith: wp.array(ndim=2, dtype=wp.float32),
                          bin_semantics: wp.array(ndim=2, dtype=wp.uint32)
                          ):
    tid = wp.tid()

    # Get the zenith of this pcl
    z = pcl[tid][2]

    # Get the index of the bin in which this pcl falls in
    x_bin_idx = pcl_bin_idx[tid][0]
    y_bin_idx = pcl_bin_idx[tid][1]
    # This ensures the semantics of this cell only belongs to the pcl semantics with the smallest zenith value
    if (z <= bin_min_zenith[x_bin_idx, y_bin_idx]):
        bin_semantics[x_bin_idx, y_bin_idx] = semantics[tid]


@wp.kernel
def side_bin_semantics_process(pcl: wp.array(dtype=wp.float32),
                          semantics: wp.array(dtype=wp.uint32),
                          pcl_bin_idx: wp.array(dtype=wp.vec2ui),
                        #   bin_min_zenith: wp.array(ndim=2, dtype=wp.float32),
                          bin_semantics: wp.array(ndim=2, dtype=wp.uint32)
                          ):
    tid = wp.tid()

    # Get the index of the bin in which this pcl falls in
    x_bin_idx = pcl_bin_idx[tid][0]
    y_bin_idx = pcl_bin_idx[tid][1]

    # Directly assign semantics for the bin of this point
    bin_semantics[x_bin_idx, y_bin_idx] = semantics[tid]


@wp.kernel
def draw_bbox(n : int,
              aligned_bbox_min: wp.array(ndim=2, dtype=wp.int32),
              aligned_bbox_max: wp.array(ndim=2, dtype=wp.int32),
              bbox_colors: wp.array(ndim=2, dtype=wp.uint8),
              image: wp.array(ndim=3, dtype=wp.uint8),
              ):
    # loop through the horizontal and vertical length, respectively
    i, j = wp.tid()
    width = image.shape[1]
    
    x_min = aligned_bbox_min[n,0]
    y_min = aligned_bbox_min[n,1]
    x_max = aligned_bbox_max[n,0]
    y_max = aligned_bbox_max[n,1]

    for c in range(4):
        image[x_min + i, width - y_min, c] = bbox_colors[n, c]
        image[x_min + i, width - y_max, c] = bbox_colors[n, c]
        image[x_min, width - (y_min + j), c] = bbox_colors[n, c]
        image[x_max, width - (y_min + j), c] = bbox_colors[n, c]

## This kernel is not used
@wp.kernel 
def average(sum: wp.array(ndim=2, dtype=wp.float32),
            count: wp.array(ndim=2, dtype=wp.int32),
            avg: wp.array(ndim=2, dtype=wp.float32)):
    i, j = wp.tid()
    if count[i, j] > 0:
        avg[i, j] = sum[i, j] / wp.float32(count[i, j])




@wp.kernel
def compute_max_intensity_all(array: wp.array(ndim=2, dtype=wp.float32), 
              max_value: wp.array(shape=(1,), dtype=wp.float32)):
    i,j = wp.tid()  
    wp.atomic_max(max_value, 0, array[i, j])

@wp.kernel
def side_compute_max_intensity_all(array: wp.array(dtype=wp.float32), 
              max_value: wp.array(shape=(1,), dtype=wp.float32)):
    i = wp.tid()
    wp.atomic_max(max_value, 0, array[i])

@wp.kernel
def compute_max_intensity_range(array: wp.array(ndim=2, dtype=wp.float32), 
              max_value: wp.array(dtype=wp.float32)):
    i, j = wp.tid()
    wp.atomic_max(max_value, i, array[i,j])

@wp.kernel
def side_compute_max_intensity_range(array: wp.array(dtype=wp.float32), 
              max_value: wp.array(dtype=wp.float32)):
    i = wp.tid()
    wp.atomic_max(max_value, 0, array[i])


@wp.kernel
def normalize_bin(bin_sum: wp.array(dtype=wp.float32),
                      bin_count: wp.array(dtype=wp.int32),
                      out_array: wp.array(dtype=wp.float32)):
    i = wp.tid()
    count = bin_count[i]

    if count > 0:
        out_array[i] = bin_sum[i] / float(count)
    else:
        out_array[i] = 0.0


@wp.kernel
def normal_2d(seed: int,
              mean: float,
              std: float,
              output: wp.array(ndim=2, dtype=wp.float32),

):
    i, j = wp.tid()
    state = wp.rand_init(seed, i * output.shape[1] + j)  
    
    # Generate normal random variable
    output[i,j] = mean + std * wp.randn(state)

@wp.kernel
def side_normal_1d(seed: int,
              mean: float,
              std: float,
              output: wp.array(dtype=wp.float32),

):
    i = wp.tid()
    # state = wp.rand_init(seed, i * output.shape[1])  
    state = wp.rand_init(seed, i)


    # Generate normal random variable
    output[i] = mean + std * wp.randn(state)


@wp.kernel
def range_dependent_rayleigh_2d(seed: int,
                                r: wp.array(ndim=2, dtype=wp.float32),
                                azi: wp.array(ndim=2, dtype=wp.float32),
                                max_range: float,
                                rayleigh_scale: float,
                                central_peak: float,
                                central_std: float,
                                output: wp.array(ndim=2, dtype = wp.float32)
):
    i, j = wp.tid()
    state = wp.rand_init(seed, i * output.shape[1] + j)
    
    # Generate two uniform random numbers
    n1 = wp.randn(state)
    n2 = wp.randn(state)  # Offset for independence
    
    # Transform to Rayleigh distribution
    rayleigh = rayleigh_scale * wp.sqrt(n1*n1 + n2*n2)
    # Apply range dependency
    output[i,j] = wp.pow(r[i,j]/max_range, 2.0) * (1.0 + central_peak * wp.exp(-wp.pow(azi[i,j] - wp.PI/2.0, 2.0) / central_std)) * rayleigh

# @wp.kernel
# def side_range_dependent_rayleigh_1d(seed: int,
#                                 r: wp.array(dtype=wp.float32),
#                                 # azi: wp.array(ndim=2, dtype=wp.float32),
#                                 max_range: float,
#                                 rayleigh_scale: float,
#                                 central_peak: float,
#                                 central_std: float,
#                                 output: wp.array(dtype = wp.float32)
# ):
#     i = wp.tid()
#     # state = wp.rand_init(seed, i * output.shape[1])
#     state = wp.rand_init(seed, i)

    
#     # Generate two uniform random numbers
#     n1 = wp.randn(state)
#     n2 = wp.randn(state)  # Offset for independence
    
#     # Transform to Rayleigh distribution
#     rayleigh = rayleigh_scale * wp.sqrt(n1*n1 + n2*n2)
#     # Apply range dependency
#     output[i] = wp.pow(r[i] / max_range, 2.0) * rayleigh

@wp.kernel
def side_range_dependent_rayleigh_1d(seed: int,
                                r: wp.array(dtype=wp.float32),
                                max_range: float,
                                rayleigh_scale: float,
                                central_peak: float,
                                central_std: float,
                                output: wp.array(dtype=wp.float32)
):
    i = wp.tid()
    state = wp.rand_init(seed, i)

    n1 = wp.randn(state)
    n2 = wp.randn(state)
    rayleigh = rayleigh_scale * wp.sqrt(n1*n1 + n2*n2)

    # Slightly softer exponent
    # range_factor = wp.pow(r[i] / max_range, 1.0)
    range_factor = wp.pow(r[i] / max_range, 0.3) # changed Oct 13
    output[i] = range_factor * rayleigh



@wp.kernel
def make_sonar_map_all(r: wp.array(ndim=2, dtype=wp.float32),
                       azi: wp.array(ndim=2, dtype=wp.float32),
                       intensity: wp.array(ndim=2, dtype=wp.float32), 
                       max_intensity: wp.array(shape=(1,), dtype=wp.float32), 
                       gau_noise: wp.array(ndim=2, dtype=wp.float32),
                       range_ray_noise: wp.array(ndim=2, dtype=wp.float32),
                       offset: wp.float32,
                       gain: wp.float32,
                       result: wp.array(ndim=2, dtype=wp.vec3)):
    i, j = wp.tid()
    intensity[i,j] = intensity[i,j] / (max_intensity[0] + 1e-10)
    intensity[i,j] *= (0.5 + gau_noise[i,j])
    intensity[i,j] += range_ray_noise[i,j]
    intensity[i,j] += offset
    intensity[i,j] *= gain
    intensity[i,j] = wp.clamp(intensity[i,j], wp.float32(0.0), wp.float32(1.0))

    result[i,j] = wp.vec3(r[i,j] * wp.cos(azi[i,j]),
                          r[i,j] * wp.sin(azi[i,j]),
                          intensity[i,j])
    
@wp.kernel
def side_make_sonar_map_all(r: wp.array(ndim=2, dtype=wp.float32),
                       azi: wp.array(ndim=2, dtype=wp.float32),
                       intensity: wp.array(ndim=2, dtype=wp.float32), 
                       max_intensity: wp.array(shape=(1,), dtype=wp.float32), 
                       gau_noise: wp.array(ndim=2, dtype=wp.float32),
                       range_ray_noise: wp.array(ndim=2, dtype=wp.float32),
                       offset: wp.float32,
                       gain: wp.float32,
                       result: wp.array(ndim=2, dtype=wp.vec3)):
    i, j = wp.tid()
    intensity[i,j] = intensity[i,j] / (max_intensity[0] + 1e-10)
    intensity[i,j] *= (0.5 + gau_noise[i,j])
    intensity[i,j] += range_ray_noise[i,j]
    intensity[i,j] += offset
    intensity[i,j] *= gain
    intensity[i,j] = wp.clamp(intensity[i,j], wp.float32(0.0), wp.float32(1.0))

    result[i,j] = wp.vec3(r[i,j] * wp.cos(azi[i,j]),
                          r[i,j] * wp.sin(azi[i,j]),
                          intensity[i,j])

@wp.kernel
def make_sonar_map_range(r: wp.array(ndim=2, dtype=wp.float32),
                       azi: wp.array(ndim=2, dtype=wp.float32),
                       intensity: wp.array(ndim=2, dtype=wp.float32),
                       max_intensity: wp.array(dtype=wp.float32), 
                       gau_noise: wp.array(ndim=2, dtype=wp.float32),
                       range_ray_noise: wp.array(ndim=2, dtype=wp.float32),
                       offset: wp.float32,
                       gain: wp.float32,
                       result: wp.array(ndim=2, dtype=wp.vec3)):
    i, j = wp.tid()

    intensity[i,j] = intensity[i,j] / (max_intensity[i] + 1e-10)
    intensity[i,j] *= (0.5 + gau_noise[i,j])
    intensity[i,j] += range_ray_noise[i,j]
    intensity[i,j] += offset
    intensity[i,j] *= gain
    intensity[i,j] = wp.clamp(intensity[i,j], wp.float32(0.0), wp.float32(1.0))

    result[i,j] = wp.vec3(r[i,j] * wp.cos(azi[i,j]),
                          r[i,j] * wp.sin(azi[i,j]),
                          intensity[i,j])

### FIXING NORMALIZATION ##################################################################
# Aug25th 13:30
@wp.kernel
def side_make_sonar_map_range(r: wp.array(dtype=wp.float32),
                    #    azi: wp.array(ndim=2, dtype=wp.float32),
                       intensity: wp.array(dtype=wp.float32),
                       max_intensity: wp.array(dtype=wp.float32), 
                       gau_noise: wp.array(dtype=wp.float32),
                       range_ray_noise: wp.array(dtype=wp.float32),
                       offset: wp.float32,
                       gain: wp.float32,
                       result: wp.array(dtype=wp.vec3)):
    i = wp.tid()

    # intensity[i] = intensity[i] / (max_intensity[0] + 1e-10)
    # intensity[i] *= (0.5 + gau_noise[i])
    # intensity[i] += range_ray_noise[i]

    intensity[i] = intensity[i] / (max_intensity[0] + 1e-6)
    intensity[i] *= (0.9 + 0.1 + gau_noise[i])
    # intensity[i] +=  range_ray_noise[i]
    intensity[i] += 0.3 * range_ray_noise[i]
    intensity[i] += offset
    intensity[i] *= gain
    intensity[i] = wp.clamp(intensity[i], wp.float32(0.0), wp.float32(1.0))

    result[i] = wp.vec3(r[i], 0.0, intensity[i])


# # Testing
# @wp.kernel
# def side_make_sonar_map_range(r: wp.array(dtype=wp.float32),
#                               intensity: wp.array(dtype=wp.float32),
#                               max_intensity: wp.array(dtype=wp.float32),
#                               gau_noise: wp.array(dtype=wp.float32),
#                               range_ray_noise: wp.array(dtype=wp.float32),
#                               offset: wp.float32,
#                               gain: wp.float32,
#                               result: wp.array(dtype=wp.vec3)):
#     i = wp.tid()
    
#     # More stable normalization - prevent extreme max values from dominating
#     # Use a combination of current max and a stabilizing factor
#     stable_max = wp.max(max_intensity[0], wp.float32(100.0))  # Ensure minimum threshold
#     clamped_max = wp.min(stable_max, wp.float32(10000.0))     # Cap maximum to prevent over-normalization
    
#     # Alternative: Use logarithmic scaling for high dynamic range
#     if intensity[i] > wp.float32(1e-6):
#         # Log normalization helps compress high values and enhance low values
#         intensity[i] = wp.log(intensity[i] + wp.float32(1.0)) / wp.log(clamped_max + wp.float32(1.0))
#     else:
#         intensity[i] = wp.float32(0.0)
    
#     # Apply a smoothing factor to reduce sharp transitions
#     # This helps eliminate banding by creating more gradual intensity changes
#     smoothed_intensity = wp.pow(intensity[i], wp.float32(0.7))  # Gamma correction
    
#     # Reduce noise impact (excessive noise can create artifacts)
#     smoothed_intensity *= (wp.float32(0.8) + wp.float32(0.2) * gau_noise[i])
#     smoothed_intensity += wp.float32(0.3) * range_ray_noise[i]
    
#     # Apply offset and gain
#     smoothed_intensity += offset
#     smoothed_intensity *= gain
    
#     # Final clamp
#     smoothed_intensity = wp.clamp(smoothed_intensity, wp.float32(0.0), wp.float32(1.0))
    
#     result[i] = wp.vec3(r[i], wp.float32(0.0), smoothed_intensity)

### FIXING NORMALIZATION ##################################################################

@wp.kernel
def make_sonar_image(sonar_data: wp.array(ndim=2, dtype=wp.vec3),
                     sonar_image: wp.array(ndim=3, dtype=wp.uint8)):
    i, j = wp.tid()
    width = sonar_data.shape[1]
    sonar_rgb = wp.uint8(sonar_data[i,j][2] * wp.float32(255))
    sonar_image[i,width-j,0] = sonar_rgb
    sonar_image[i,width-j,1] = sonar_rgb
    sonar_image[i,width-j,2] = sonar_rgb
    sonar_image[i,width-j,3] = wp.uint8(255)

@wp.kernel
def make_side_sonar_image(side_sonar_data: wp.array(dtype=wp.vec3),
                     side_sonar_image: wp.array(ndim=2, dtype=wp.uint8)):
    i = wp.tid()
    # width = side_sonar_data.shape[1]
    sonar_rgb = wp.uint8(side_sonar_data[i][2] * wp.float32(255))
    # sonar_rgb = wp.uint8(side_sonar_data[i][2] * wp.float32(400))
    side_sonar_image[i,0] = sonar_rgb
    side_sonar_image[i,1] = sonar_rgb
    side_sonar_image[i,2] = sonar_rgb
    side_sonar_image[i,3] = wp.uint8(255)

@wp.kernel
def update_waterfall(waterfall: wp.array(ndim=3,dtype=wp.uint8),
                     waterfall_buffer: wp.array(ndim=3, dtype=wp.uint8)):
    i, j, k = wp.tid()
    waterfall[i+1, j, k] = waterfall_buffer[i, j, k]

@wp.kernel
def update_first_row(sonar_image: wp.array(ndim = 2, dtype = wp.uint8),
                 waterfall: wp.array(ndim=3, dtype=wp.uint8)):
    i, j = wp.tid()
    waterfall[0, i, j] = sonar_image[i,j]

@wp.kernel
def make_semantics_image(bin_semantics: wp.array(ndim=2, dtype=wp.uint32),
                         semantics_color: wp.array(ndim=2, dtype=wp.uint8),
                         semantics_image: wp.array(ndim=3, dtype=wp.uint8),
                         ):
    i, j = wp.tid()
    width = bin_semantics.shape[1]
    semantics_image[i,width-j,0] = semantics_color[bin_semantics[i,j], 0]
    semantics_image[i,width-j,1] = semantics_color[bin_semantics[i,j], 1]
    semantics_image[i,width-j,2] = semantics_color[bin_semantics[i,j], 2]
    semantics_image[i,width-j,3] = semantics_color[bin_semantics[i,j], 3]


# @wp.kernel
# def make_side_semantics_image(side_bin_semantics: wp.array(dtype=wp.uint32),
#                          semantics_color: wp.array(ndim=2, dtype=wp.uint8),
#                          semantics_image: wp.array(ndim=3, dtype=wp.uint8),
#                          ):
#     i, j = wp.tid()
#     width = side_bin_semantics.shape[1]
#     semantics_image[i,width-j,0] = semantics_color[side_bin_semantics[i,j], 0]
#     semantics_image[i,width-j,1] = semantics_color[side_bin_semantics[i,j], 1]
#     semantics_image[i,width-j,2] = semantics_color[side_bin_semantics[i,j], 2]
#     semantics_image[i,width-j,3] = semantics_color[side_bin_semantics[i,j], 3]


## THis kernel not used ##

# ImagingSonarSensor.py
#######################################
# bbox_corners = wp.array(bbox_corners, ndim=3, dtype=wp.float32)
# aligned_bbox_min = wp.empty(shape=(bbox_corners.shape[0], 2), dtype=wp.int32)
# aligned_bbox_max = wp.empty(shape=(bbox_corners.shape[0], 2), dtype=wp.int32)
# aligned_bbox_min.fill_(10000)
# aligned_bbox_max.fill_(0)
# wp.launch(kernel=bin_bbox_process,
#             dim=bbox_corners.shape[0:2],
#             inputs=[
#                 bbox_corners,
#                 self.sonar_grid,
#             ],
#             outputs=[
#                 aligned_bbox_min,
#                 aligned_bbox_max
#             ])

# ImagingSonar_kernels.py
##########################################
# @wp.kernel
# def bin_bbox_process(bbox_corners: wp.array(ndim=3, dtype=wp.float32),
#                      sonar_grid: sonarGrid,
#                      aligned_bbox_min: wp.array(ndim=2, dtype=wp.int32),
#                      aligned_bbox_max: wp.array(ndim=2, dtype=wp.int32)
#                     ):
#     i, j = wp.tid()
#     # Convert 8 corners local frame carteisan to local frame spherical
#     bbox_corner_spher = cartesian_to_spherical(wp.vec3(bbox_corners[i,j,0],
#                                                        bbox_corners[i,j,1],
#                                                        bbox_corners[i,j,2]))
#     # collapse 8 corners to the sonar grid
#     x_bin_idx = wp.int32((bbox_corner_spher[0] - sonar_grid.x_offset) / sonar_grid.x_res)
#     y_bin_idx = wp.int32((bbox_corner_spher[1] - sonar_grid.y_offset) / sonar_grid.y_res)

#     x_bin_idx = wp.clamp(x_bin_idx, 0, sonar_grid.x_num-1)
#     y_bin_idx = wp.clamp(y_bin_idx, 0, sonar_grid.y_num-1)
#     # Compute an axis-aligned minimum-area bbox 
#     # that contains all 8 corners of the 3d bbox
#     # x_min
#     wp.atomic_min(aligned_bbox_min, i, 0, x_bin_idx)
#     # y_min
#     wp.atomic_min(aligned_bbox_min, i, 1, y_bin_idx)
#     # x_max
#     wp.atomic_max(aligned_bbox_max, i, 0, x_bin_idx)
#     # y_max
#     wp.atomic_max(aligned_bbox_max, i, 1, y_bin_idx)