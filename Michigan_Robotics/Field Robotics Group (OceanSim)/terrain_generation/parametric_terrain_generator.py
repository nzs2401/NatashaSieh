import numpy as np
from perlin_noise import PerlinNoise
import random
import os
from scipy import ndimage
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
import json

@dataclass
class TerrainParameters:
    """Class to hold all terrain generation parameters"""
    # Heightmap generation
    map_size: int = 512
    noise_scale: float = 8.0
    octaves: int = 4
    amplitude_decay: float = 0.6
    frequency_multiplier: float = 1.8
    
    # Smoothing
    smoothing_method: str = "gaussian"  # "gaussian", "median", "uniform", "none"
    smoothing_strength: float = 1.5
    
    # Noise
    random_noise_strength: float = 0.005
    
    # Elevation adjustments
    elevation_curve: str = "none"  # "smooth", "valleys", "plateau", "none"
    
    # 3D scaling
    scale_x: float = 100.0
    scale_y: float = 100.0
    scale_z: float = 10.0
    
    # Seed for reproducibility
    seed: int = None

class TerrainParameterGenerator:
    """Generate randomized terrain parameters within specified ranges"""
    
    def __init__(self):
        self.parameter_ranges = {
            'map_size': [256, 512, 1024],  # Discrete choices
            'noise_scale': (4.0, 15.0),   # Continuous range
            'octaves': (2, 6),            # Integer range
            'amplitude_decay': (0.4, 0.8),
            'frequency_multiplier': (1.5, 2.5),
            'smoothing_method': ["gaussian", "median", "uniform", "none"],
            'smoothing_strength': (0.5, 3.0),
            'random_noise_strength': (0.001, 0.01),
            'elevation_curve': ["smooth", "valleys", "plateau", "none"],
            'scale_x': (50.0, 200.0),
            'scale_y': (50.0, 200.0),
            'scale_z': (5.0, 20.0)
        }
        
        # Predefined parameter sets for specific terrain types
        self.terrain_presets = {
            ### NEW Nov 14, 3:52pm ###
            'sand_ripples': TerrainParameters(
                map_size=1024,
                noise_scale=90.0,          # LARGE scale for ripple wavelength
                octaves=3,                 # LOW octaves for smooth, regular features
                amplitude_decay=0.7,       # Gentle decay
                frequency_multiplier=2.0,
                smoothing_method="gaussian", # SMOOTH for sand
                smoothing_strength=4.0,    # High smoothing
                random_noise_strength=0.001, # Very low noise (sand is smooth)
                elevation_curve="smooth",  # Gentle curves
                scale_x=100.0,
                scale_y=100.0,
                scale_z=0.03,              # VERY FLAT - ripples are only ~0.5m tall
            ),
            ### NEW Nov 14, 3:52pm ###
            'rolling_hills': TerrainParameters(
                noise_scale=12.0, octaves=3, smoothing_method="gaussian",
                smoothing_strength=2.0, elevation_curve="smooth"
            ),
            'rough_mountains': TerrainParameters(
                noise_scale=6.0, octaves=6, smoothing_method="none",
                smoothing_strength=3.5, elevation_curve="none", scale_z=25.0
            ),
            'gentle_valleys': TerrainParameters(
                noise_scale=10.0, octaves=4, smoothing_method="gaussian",
                smoothing_strength=2.8, elevation_curve="valleys"
            ),
            'plateau_landscape': TerrainParameters(
                noise_scale=8.0, octaves=5, smoothing_method="median",
                smoothing_strength=2.2, elevation_curve="plateau"
            ),
            # ADDED 11/2 12:25
            'volcanic_boulder_field': TerrainParameters(  # ADD THIS
                map_size=1024,
                noise_scale=4.0,
                octaves=10,
                amplitude_decay=0.55,
                frequency_multiplier=2.3,
                smoothing_method="none",
                smoothing_strength=0.0,
                random_noise_strength=0.025,
                elevation_curve="none",
                scale_x=100.0,
                scale_y=100.0,
                scale_z=2.0
            )
            
        }
    
    def generate_random_parameters(self, seed: int = None) -> TerrainParameters:
        """Generate a random set of terrain parameters"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        params = TerrainParameters()
        
        for param_name, param_range in self.parameter_ranges.items():
            if isinstance(param_range, list):
                # Discrete choices
                setattr(params, param_name, random.choice(param_range))
            elif isinstance(param_range, tuple) and len(param_range) == 2:
                min_val, max_val = param_range
                if param_name == 'octaves':
                    # Integer range
                    setattr(params, param_name, random.randint(min_val, max_val))
                else:
                    # Continuous range
                    setattr(params, param_name, random.uniform(min_val, max_val))
        
        params.seed = seed if seed is not None else random.randint(0, 100000)
        return params
    
    def get_preset_parameters(self, preset_name: str) -> TerrainParameters:
        """Get predefined parameter set"""
        if preset_name not in self.terrain_presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(self.terrain_presets.keys())}")
        return self.terrain_presets[preset_name]
    
    def save_parameters(self, params: TerrainParameters, filepath: str):
        """Save parameters to JSON file"""
        param_dict = {
            'map_size': params.map_size,
            'noise_scale': params.noise_scale,
            'octaves': params.octaves,
            'amplitude_decay': params.amplitude_decay,
            'frequency_multiplier': params.frequency_multiplier,
            'smoothing_method': params.smoothing_method,
            'smoothing_strength': params.smoothing_strength,
            'random_noise_strength': params.random_noise_strength,
            'elevation_curve': params.elevation_curve,
            'scale_x': params.scale_x,
            'scale_y': params.scale_y,
            'scale_z': params.scale_z,
            'seed': params.seed
        }
        
        with open(filepath, 'w') as f:
            json.dump(param_dict, f, indent=2)
    
    def load_parameters(self, filepath: str) -> TerrainParameters:
        """Load parameters from JSON file"""
        with open(filepath, 'r') as f:
            param_dict = json.load(f)
        
        return TerrainParameters(**param_dict)

def generate_parametric_heightmap(params: TerrainParameters) -> np.ndarray:
    """Generate heightmap using the provided parameters"""
    if params.seed is not None:
        random.seed(params.seed)
        np.random.seed(params.seed)
    
    heightmap = np.zeros((params.map_size, params.map_size))
    
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    
    # Generate noise layers
    for i in range(params.octaves):
        noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
        
        current_scale = params.noise_scale * frequency
        
        x_offset = random.uniform(-0.1, 0.1)
        y_offset = random.uniform(-0.1, 0.1)
        
        x_coords, y_coords = np.meshgrid(np.arange(params.map_size), np.arange(params.map_size))
        
        sample_x = (x_coords / params.map_size * current_scale) + x_offset
        sample_y = (y_coords / params.map_size * current_scale) + y_offset
        
        noise_layer = np.array([noise([x, y]) for x, y in zip(sample_x.flatten(), sample_y.flatten())]).reshape(params.map_size, params.map_size)
        
        heightmap += noise_layer * amplitude
        
        max_value += amplitude
        amplitude *= params.amplitude_decay
        frequency *= params.frequency_multiplier
    
    # Normalize
    heightmap /= max_value
    
    # Add random noise
    if params.random_noise_strength > 0:
        random_noise = np.random.normal(0, params.random_noise_strength, (params.map_size, params.map_size))
        heightmap += random_noise
    
    # Apply smoothing
    if params.smoothing_method == "gaussian":
        heightmap = ndimage.gaussian_filter(heightmap, sigma=params.smoothing_strength)
    elif params.smoothing_method == "median":
        heightmap = ndimage.median_filter(heightmap, size=int(params.smoothing_strength * 2 + 1))
    elif params.smoothing_method == "uniform":
        heightmap = ndimage.uniform_filter(heightmap, size=int(params.smoothing_strength * 2 + 1))
    
    # Apply elevation curve
    if params.elevation_curve == "smooth":
        heightmap = np.power(heightmap, 0.7)
    elif params.elevation_curve == "valleys":
        heightmap = 1.0 - np.power(1.0 - heightmap, 1.5)
    elif params.elevation_curve == "plateau":
        heightmap = np.where(heightmap > 0.6, 0.6 + (heightmap - 0.6) * 0.3, heightmap)
    
    # Final normalization
    heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
    
    return heightmap

def generate_volcanic_boulder_heightmap(params: TerrainParameters) -> np.ndarray:
    """Generate volcanic boulder field terrain matching SSS reference"""
    if params.seed is not None:
        random.seed(params.seed)
        np.random.seed(params.seed)
    
    heightmap = np.zeros((params.map_size, params.map_size))
    
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    
    # Layer 1: Base terrain with ridging for angular features
    for i in range(params.octaves):
        noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
        
        current_scale = params.noise_scale * frequency
        x_offset = random.uniform(-0.1, 0.1)
        y_offset = random.uniform(-0.1, 0.1)
        
        x_coords, y_coords = np.meshgrid(np.arange(params.map_size), np.arange(params.map_size))
        sample_x = (x_coords / params.map_size * current_scale) + x_offset
        sample_y = (y_coords / params.map_size * current_scale) + y_offset
        
        noise_layer = np.array([noise([x, y]) for x, y in zip(sample_x.flatten(), sample_y.flatten())]).reshape(params.map_size, params.map_size)
        
        # Apply ridging to create sharp features
        if i < params.octaves * 0.4:  # First 40% of octaves
            noise_layer = 1.0 - 2.0 * np.abs(noise_layer)
        
        heightmap += noise_layer * amplitude
        
        max_value += amplitude
        amplitude *= params.amplitude_decay
        frequency *= params.frequency_multiplier
    
    # Normalize base terrain
    heightmap /= max_value
    
    # Layer 2: Add "boulders" - small bumps scattered around
    num_boulders = int(params.map_size * params.map_size * 0.02)  # 2% coverage
    for _ in range(num_boulders):
        x_center = random.randint(0, params.map_size - 1)
        y_center = random.randint(0, params.map_size - 1)
        boulder_size = random.uniform(3, 10)  # pixels
        boulder_height = random.uniform(0.05, 0.15)  # height contribution
        
        # Create boulder using Gaussian
        y_grid, x_grid = np.ogrid[:params.map_size, :params.map_size]
        distance = np.sqrt((x_grid - x_center)**2 + (y_grid - y_center)**2)
        boulder = boulder_height * np.exp(-(distance**2) / (2 * boulder_size**2))
        heightmap += boulder
    
    # Layer 3: High-frequency noise for surface roughness
    high_freq_noise = np.random.uniform(-0.1, 0.1, (params.map_size, params.map_size))
    
    # Apply noise at multiple scales to create granular texture
    for scale in [2, 4, 8]:
        noise_layer = np.random.uniform(-1, 1, (params.map_size // scale, params.map_size // scale))
        noise_layer = ndimage.zoom(noise_layer, scale, order=1)
        # Crop or pad to exact size
        if noise_layer.shape[0] > params.map_size:
            noise_layer = noise_layer[:params.map_size, :params.map_size]
        high_freq_noise += noise_layer * 0.02
    
    heightmap += high_freq_noise * params.random_noise_strength * 3
    
    # Final normalization
    heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
    
    return heightmap

### NEW Nov 14, 3:54pm ###
# def generate_sand_ripples_heightmap(params: TerrainParameters) -> np.ndarray:
#     """Generate sand ripples using physical ripple equations"""
#     if params.seed is not None:
#         random.seed(params.seed)
#         np.random.seed(params.seed)
    
#     heightmap = np.zeros((params.map_size, params.map_size))
#     x_coords, y_coords = np.meshgrid(np.arange(params.map_size), np.arange(params.map_size))
    
#     # Base ripple direction with MINIMAL variation
#     base_angle = random.uniform(0, np.pi)
    
#     # Very gentle direction variation (only at large scales)
#     direction_noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
#     direction_scale = 0.8  # Large-scale gentle curves only
    
#     dir_samples = np.array([direction_noise([x/params.map_size * direction_scale, 
#                                              y/params.map_size * direction_scale]) 
#                            for x, y in zip(x_coords.flatten(), y_coords.flatten())])
#     direction_field = dir_samples.reshape(params.map_size, params.map_size)
    
#     # Minimal angle variation (0.1 radians ≈ 5.7 degrees max deviation)
#     angle_variation = direction_field * 0.1
#     local_angles = base_angle + angle_variation
    
#     # Rotate coordinates
#     x_rot = x_coords * np.cos(local_angles) + y_coords * np.sin(local_angles)
    
#     # PHYSICALLY BASED RIPPLE PARAMETERS
#     # Ripple Index RI = λ/(2A) typically 10-15 for current ripples
#     ripple_index = 12.0  # Mid-range value
#     wavelength = params.map_size / (params.noise_scale * 1.2)  # λ in pixels
#     amplitude = wavelength / (2.0 * ripple_index)  # A calculated from RI
    
#     # Create base sinusoidal ripple: z(x) = A*sin(2πx/λ)
#     base_ripples = amplitude * np.sin(2 * np.pi * x_rot / wavelength)
    
#     # Add asymmetry using Fourier harmonics (for stoss/lee asymmetry)
#     # This creates the gentle upstream side and steeper downstream side
#     asymmetry = 0.15 * amplitude * np.sin(4 * np.pi * x_rot / wavelength + np.pi/2)
#     asymmetry += 0.08 * amplitude * np.sin(6 * np.pi * x_rot / wavelength + np.pi/3)
    
#     # Combine base ripples with asymmetry
#     ripples = base_ripples + asymmetry
    
#     # Normalize ripples to [0, 1] range initially
#     ripples = (ripples - ripples.min()) / (ripples.max() - ripples.min())
    
#     # Apply gentle power function to round peaks slightly
#     ripples = np.power(ripples, 0.8)
    
#     heightmap = ripples
    
#     # Add MINIMAL quasi-periodic variation (not random chaos)
#     # This represents natural variation in ripple spacing
#     large_scale_var = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
#     var_scale = 3.0
    
#     var_samples = np.array([large_scale_var([x/params.map_size * var_scale, 
#                                              y/params.map_size * var_scale]) 
#                            for x, y in zip(x_coords.flatten(), y_coords.flatten())])
#     variation = var_samples.reshape(params.map_size, params.map_size)
    
#     heightmap += variation * 0.08  # Very subtle variation
    
#     # Smooth to remove mesh artifacts and create natural sand texture
#     heightmap = ndimage.gaussian_filter(heightmap, sigma=params.smoothing_strength)
    
#     # Add fine-scale sand grain texture
#     grain_texture = np.random.normal(0, params.random_noise_strength, heightmap.shape)
#     grain_texture = ndimage.gaussian_filter(grain_texture, sigma=0.5)
#     heightmap += grain_texture * 0.3
    
#     # Final normalization
#     heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
    
#     return heightmap

# NEW Nov 24, 12:07pm ###
# def generate_sand_ripples_heightmap(params: TerrainParameters) -> np.ndarray:
#     """Generate sand ripples with GUARANTEED flat base using offset"""
#     if params.seed is not None:
#         random.seed(params.seed)
#         np.random.seed(params.seed)
    
#     x_coords, y_coords = np.meshgrid(np.arange(params.map_size), np.arange(params.map_size))
    
#     # Ripple direction
#     base_angle = random.uniform(0, np.pi)
    
#     direction_noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
#     direction_scale = 0.4
    
#     dir_samples = np.array([direction_noise([x/params.map_size * direction_scale, 
#                                              y/params.map_size * direction_scale]) 
#                            for x, y in zip(x_coords.flatten(), y_coords.flatten())])
#     direction_field = dir_samples.reshape(params.map_size, params.map_size)
    
#     angle_variation = direction_field * 0.06
#     local_angles = base_angle + angle_variation
    
#     # Rotate coordinates
#     x_rot = x_coords * np.cos(local_angles) + y_coords * np.sin(local_angles)
    
#     # Ripple wavelength
#     wavelength = params.map_size / (params.noise_scale * 1.0)
    
#     # Create sine wave
#     ripple_wave = np.sin(2 * np.pi * x_rot / wavelength)
    
#     # Map to [0, 1]
#     ripple_wave = (ripple_wave + 1.0) / 2.0
    
#     # Threshold: only keep peaks
#     threshold = 0.6
#     ripple_bumps = np.where(ripple_wave > threshold,
#                            (ripple_wave - threshold) / (1.0 - threshold),
#                            0.0)
    
#     # Smooth the bumps heavily
#     ripple_bumps = ndimage.gaussian_filter(ripple_bumps, sigma=4.0)
    
#     # CRITICAL FIX: Start with a RAISED baseline (not zero!)
#     BASE_HEIGHT = 0.5  # This is the flat seafloor level
#     heightmap = np.full((params.map_size, params.map_size), BASE_HEIGHT)
    
#     # Add ripples ON TOP of the base (they can only increase height)
#     RIPPLE_HEIGHT = 0.3  # Maximum additional height from ripples
#     heightmap += ripple_bumps * RIPPLE_HEIGHT
    
#     # Add subtle large-scale undulation
#     large_var = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
#     var_samples = np.array([large_var([x/params.map_size * 1.5, 
#                                        y/params.map_size * 1.5]) 
#                            for x, y in zip(x_coords.flatten(), y_coords.flatten())])
#     variation = var_samples.reshape(params.map_size, params.map_size)
    
#     # Normalize variation to small positive values
#     variation = (variation - variation.min()) / (variation.max() - variation.min())
#     heightmap += variation * 0.03
    
#     # Add fine sand texture
#     grain = np.random.normal(0, 0.001, heightmap.shape)
#     grain = ndimage.gaussian_filter(grain, sigma=0.3)
#     heightmap += grain
    
#     # Final smoothing
#     heightmap = ndimage.gaussian_filter(heightmap, sigma=2.0)
    
#     # NO NORMALIZATION! Keep the absolute values
#     # The base is at 0.5, ripples extend up to ~0.8
#     # This preserves the flat regions at exactly 0.5
    
#     return heightmap
def generate_sand_ripples_heightmap(params: TerrainParameters) -> np.ndarray:
    """Generate sand ripples with natural discontinuities and pattern breaks"""
    if params.seed is not None:
        random.seed(params.seed)
        np.random.seed(params.seed)
    
    x_coords, y_coords = np.meshgrid(np.arange(params.map_size), np.arange(params.map_size))
    
    # === STEP 1: Generate base ripple pattern (as before) ===
    base_angle = random.uniform(0, np.pi)
    
    direction_noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
    direction_scale = 0.4
    
    dir_samples = np.array([direction_noise([x/params.map_size * direction_scale, 
                                             y/params.map_size * direction_scale]) 
                           for x, y in zip(x_coords.flatten(), y_coords.flatten())])
    direction_field = dir_samples.reshape(params.map_size, params.map_size)
    
    angle_variation = direction_field * 0.06
    local_angles = base_angle + angle_variation
    
    x_rot = x_coords * np.cos(local_angles) + y_coords * np.sin(local_angles)
    
    wavelength = params.map_size / (params.noise_scale * 1.0)
    
    ripple_wave = np.sin(2 * np.pi * x_rot / wavelength)
    ripple_wave = (ripple_wave + 1.0) / 2.0
    
    threshold = 0.6
    ripple_bumps = np.where(ripple_wave > threshold,
                           (ripple_wave - threshold) / (1.0 - threshold),
                           0.0)
    
    ripple_bumps = ndimage.gaussian_filter(ripple_bumps, sigma=4.0)
    
    # === STEP 2: CREATE DISCONTINUITIES ===
    
    # A. Generate "dead zones" - areas where ripples fade out
    dead_zone_noise = PerlinNoise(octaves=2, seed=random.randint(0, 100000))
    dead_zone_samples = np.array([dead_zone_noise([x/params.map_size * 3.0, 
                                                   y/params.map_size * 3.0]) 
                                 for x, y in zip(x_coords.flatten(), y_coords.flatten())])
    dead_zone_mask = dead_zone_samples.reshape(params.map_size, params.map_size)
    
    # Normalize to [0, 1] and create patches where ripples are suppressed
    dead_zone_mask = (dead_zone_mask - dead_zone_mask.min()) / (dead_zone_mask.max() - dead_zone_mask.min())
    dead_zone_mask = np.where(dead_zone_mask < 0.3, dead_zone_mask / 0.3, 1.0)  # 30% of area has reduced ripples
    
    # Apply dead zones
    ripple_bumps = ripple_bumps * dead_zone_mask
    
    # B. Create bifurcations - ripples split into two
    num_bifurcations = random.randint(2, 5)
    for _ in range(num_bifurcations):
        # Random location and direction for bifurcation
        bif_x = random.randint(int(params.map_size * 0.2), int(params.map_size * 0.8))
        bif_y = random.randint(int(params.map_size * 0.2), int(params.map_size * 0.8))
        bif_angle = random.uniform(0, 2 * np.pi)
        bif_width = random.uniform(15, 40)  # pixels
        
        # Create a wedge-shaped mask for bifurcation
        y_grid, x_grid = np.ogrid[:params.map_size, :params.map_size]
        
        # Distance from bifurcation point
        dx = x_grid - bif_x
        dy = y_grid - bif_y
        
        # Rotate to bifurcation angle
        dx_rot = dx * np.cos(bif_angle) + dy * np.sin(bif_angle)
        dy_rot = -dx * np.sin(bif_angle) + dy * np.cos(bif_angle)
        
        # Create wedge: affects area ahead of point
        wedge_mask = np.where((dx_rot > 0) & (np.abs(dy_rot) < bif_width * (1 + dx_rot / 100.0)),
                             0.3,  # Suppress ripples in wedge
                             1.0)
        
        # Smooth the wedge edges
        wedge_mask = ndimage.gaussian_filter(wedge_mask, sigma=10.0)
        ripple_bumps = ripple_bumps * wedge_mask
    
    # C. Create pattern disruptions - abrupt breaks
    num_breaks = random.randint(3, 7)
    for _ in range(num_breaks):
        break_x = random.randint(0, params.map_size - 1)
        break_y = random.randint(0, params.map_size - 1)
        break_size = random.uniform(20, 60)
        break_strength = random.uniform(0.0, 0.4)  # How much to suppress
        
        # Create local disruption using Gaussian
        y_grid, x_grid = np.ogrid[:params.map_size, :params.map_size]
        distance = np.sqrt((x_grid - break_x)**2 + (y_grid - break_y)**2)
        break_mask = 1.0 - (1.0 - break_strength) * np.exp(-(distance**2) / (2 * break_size**2))
        
        ripple_bumps = ripple_bumps * break_mask
    
    # D. Add secondary ripple train at different angle (creates Y-junctions)
    if random.random() > 0.5:  # 50% chance
        secondary_angle = base_angle + random.uniform(np.pi/6, np.pi/3)  # 30-60 degree offset
        x_rot_2 = x_coords * np.cos(secondary_angle) + y_coords * np.sin(secondary_angle)
        
        wavelength_2 = wavelength * random.uniform(0.8, 1.2)
        ripple_wave_2 = np.sin(2 * np.pi * x_rot_2 / wavelength_2)
        ripple_wave_2 = (ripple_wave_2 + 1.0) / 2.0
        
        ripple_bumps_2 = np.where(ripple_wave_2 > threshold,
                                  (ripple_wave_2 - threshold) / (1.0 - threshold),
                                  0.0)
        ripple_bumps_2 = ndimage.gaussian_filter(ripple_bumps_2, sigma=4.0)
        
        # Blend secondary ripples in only some regions
        blend_noise = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
        blend_samples = np.array([blend_noise([x/params.map_size * 2.0, 
                                              y/params.map_size * 2.0]) 
                                 for x, y in zip(x_coords.flatten(), y_coords.flatten())])
        blend_mask = blend_samples.reshape(params.map_size, params.map_size)
        blend_mask = (blend_mask - blend_mask.min()) / (blend_mask.max() - blend_mask.min())
        blend_mask = np.where(blend_mask > 0.6, (blend_mask - 0.6) / 0.4, 0.0)
        
        # Add secondary ripples where mask is active
        ripple_bumps = ripple_bumps + ripple_bumps_2 * blend_mask * 0.5
    
    # === STEP 3: Assemble final heightmap ===
    BASE_HEIGHT = 0.5
    heightmap = np.full((params.map_size, params.map_size), BASE_HEIGHT)

    RIPPLE_HEIGHT = 0.3
    heightmap += ripple_bumps * RIPPLE_HEIGHT
    
    # Add subtle large-scale undulation
    large_var = PerlinNoise(octaves=1, seed=random.randint(0, 100000))
    var_samples = np.array([large_var([x/params.map_size * 1.5, 
                                       y/params.map_size * 1.5]) 
                           for x, y in zip(x_coords.flatten(), y_coords.flatten())])
    variation = var_samples.reshape(params.map_size, params.map_size)
    variation = (variation - variation.min()) / (variation.max() - variation.min())
    heightmap += variation * 0.03
    
    # Add fine sand texture
    grain = np.random.normal(0, 0.001, heightmap.shape)
    grain = ndimage.gaussian_filter(grain, sigma=0.3)
    heightmap += grain
    
    # Final smoothing
    heightmap = ndimage.gaussian_filter(heightmap, sigma=2.0)
    
    return heightmap


def generate_terrain_by_preset(preset_name: str, params: TerrainParameters) -> np.ndarray:
    """Route to the correct generation function based on preset name"""
    
    terrain_generators = {
        'volcanic_boulder_field': generate_volcanic_boulder_heightmap,
        'sand_ripples': generate_sand_ripples_heightmap,
        # All other presets use the default generator
    }
    
    # Use specialized generator if available, otherwise use default
    generator = terrain_generators.get(preset_name, generate_parametric_heightmap)
    return generator(params)
### NEW Nov 14, 3:54pm ###

# Example usage and testing
if __name__ == "__main__":
    # Create parameter generator
    param_gen = TerrainParameterGenerator()
    
    # Test 1: Generate random parameters
    print("=== Random Parameter Generation ===")
    for i in range(3):
        random_params = param_gen.generate_random_parameters(seed=i*100)
        print(f"Random Set {i+1}:")
        print(f"  Scale: {random_params.noise_scale:.1f}, Octaves: {random_params.octaves}")
        print(f"  Smoothing: {random_params.smoothing_method} ({random_params.smoothing_strength:.1f})")
        print(f"  3D Scale: ({random_params.scale_x:.0f}, {random_params.scale_y:.0f}, {random_params.scale_z:.0f})")
        print()
    
    # Test 2: Use presets
    print("=== Preset Parameter Sets ===")
    for preset_name in param_gen.terrain_presets.keys():
        preset_params = param_gen.get_preset_parameters(preset_name)
        print(f"{preset_name.replace('_', ' ').title()}:")
        print(f"  Scale: {preset_params.noise_scale}, Octaves: {preset_params.octaves}")
        print(f"  Smoothing: {preset_params.smoothing_method}")
        print()
    
    # Test 3: Generate and save sample heightmaps
    print("=== Generating Sample Heightmaps ===")
    output_dir = "parametric_heightmaps"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a random terrain
    random_params = param_gen.generate_random_parameters(seed=12345)
    random_heightmap = generate_parametric_heightmap(random_params)
    
    # Save heightmap and parameters
    np.save(os.path.join(output_dir, "random_terrain.npy"), random_heightmap)
    param_gen.save_parameters(random_params, os.path.join(output_dir, "random_terrain_params.json"))
    
    print(f"Saved random terrain to {output_dir}/")
    print("Parameters saved to JSON for reproducibility!")
    
    # # Generate preset terrains using the router function
    # for preset_name in ["rolling_hills", "rough_mountains", "volcanic_boulder_field", "sand_ripples"]:  # ADDED sand_ripples
    #     preset_params = param_gen.get_preset_parameters(preset_name)
        
    #     # USE THE ROUTER - it automatically picks the right function!
    #     preset_heightmap = generate_terrain_by_preset(preset_name, preset_params)
        
    #     np.save(os.path.join(output_dir, f"{preset_name}.npy"), preset_heightmap)
    #     param_gen.save_parameters(preset_params, os.path.join(output_dir, f"{preset_name}_params.json"))
        
    #     print(f"Generated {preset_name} terrain")

    # Generate preset terrains using the router function
    # for preset_name in ["rolling_hills", "rough_mountains", "volcanic_boulder_field", "sand_ripples"]:
    for preset_name in ["sand_ripples"]:
        try:
            print(f"Generating {preset_name}...")
            preset_params = param_gen.get_preset_parameters(preset_name)
            
            # USE THE ROUTER - it automatically picks the right function!
            preset_heightmap = generate_terrain_by_preset(preset_name, preset_params)
            
            np.save(os.path.join(output_dir, f"{preset_name}.npy"), preset_heightmap)
            param_gen.save_parameters(preset_params, os.path.join(output_dir, f"{preset_name}_params.json"))
            
            print(f"✓ Generated {preset_name} terrain")
        except Exception as e:
            print(f"✗ ERROR generating {preset_name}: {e}")
            import traceback
            traceback.print_exc()
            continue  # Continue to next terrain even if one fails

        # run: cd /home/nsieh/code/isaacsim-5.0/_build/linux-x86_64/release/ROB490
        # run: python parametric_terrain_generator.py
        # check: ls -lh parametric_heightmaps/


