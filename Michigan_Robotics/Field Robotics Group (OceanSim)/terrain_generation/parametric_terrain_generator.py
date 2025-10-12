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
    
    # Generate preset terrains
    for preset_name in ["rolling_hills", "rough_mountains"]:
        preset_params = param_gen.get_preset_parameters(preset_name)
        preset_heightmap = generate_parametric_heightmap(preset_params)
        
        np.save(os.path.join(output_dir, f"{preset_name}.npy"), preset_heightmap)
        param_gen.save_parameters(preset_params, os.path.join(output_dir, f"{preset_name}_params.json"))
        
        print(f"Generated {preset_name} terrain")