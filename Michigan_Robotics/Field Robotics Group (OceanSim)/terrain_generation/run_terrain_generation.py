# CRITICAL: SimulationApp MUST be imported and initialized FIRST
from omni.isaac.kit import SimulationApp

# Initialize the simulation app - this MUST come before any other Isaac Sim imports
simulation_app = SimulationApp({"headless": False})  # Set to True for headless mode

# Now we can import other Isaac Sim modules
import numpy as np
import omni.usd
from pxr import Gf, Usd, UsdGeom, Vt
import os

print("=== STARTING TERRAIN GENERATION ===")

# Get the absolute path of the directory containing this script.
# This ensures the script can find its files regardless of the working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {SCRIPT_DIR}")

def generate_usd_terrain_from_heightmap(stage, heightmap_path, terrain_name="ProceduralTerrain", scale=(100.0, 100.0, 10.0)):
    """
    Creates a 3D terrain mesh in a USD stage from a NumPy heightmap file.

    Args:
        stage (Usd.Stage): The USD stage to create the mesh on.
        heightmap_path (str): The file path to the .npy heightmap file.
        terrain_name (str): The name of the terrain prim.
        scale (tuple): A tuple (x, y, z) for scaling the terrain dimensions.
    """
    if not os.path.exists(heightmap_path):
        print(f"Error: Heightmap file not found at {heightmap_path}")
        print("Please ensure your file structure looks like this:")
        print("my_isaac_project/")
        print("├── run_terrain_generation.py")
        print("└── src/")
        print("    └── heightmaps/")
        print("        └── improved_heightmap.npy")
        return False

    try:
        # Step 1: Load the heightmap data from the .npy file
        print(f"Loading heightmap from: {heightmap_path}")
        heightmap = np.load(heightmap_path)
        print(f"Heightmap loaded successfully, shape: {heightmap.shape}")
        size = heightmap.shape[0]
        
        # Step 2: Calculate vertices
        print("Generating vertices...")
        vertices = []
        for y in range(size):
            for x in range(size):
                # Map the (x, y) coordinates to a normalized range and then scale them
                pos_x = (x / size - 0.5) * scale[0]
                pos_y = (y / size - 0.5) * scale[1]
                pos_z = heightmap[y, x] * scale[2]
                vertices.append(Gf.Vec3f(pos_x, pos_y, pos_z))

        # Step 3: Define faces (triangles)
        print("Generating faces...")
        face_vertex_counts = []
        face_vertex_indices = []
        for y in range(size - 1):
            for x in range(size - 1):
                # The indices of the four corners of the current square
                v1_idx = y * size + x
                v2_idx = y * size + (x + 1)
                v3_idx = (y + 1) * size + (x + 1)
                v4_idx = (y + 1) * size + x

                # First triangle
                face_vertex_counts.append(3)
                face_vertex_indices.append(v1_idx)
                face_vertex_indices.append(v2_idx)
                face_vertex_indices.append(v3_idx)

                # Second triangle
                face_vertex_counts.append(3)
                face_vertex_indices.append(v1_idx)
                face_vertex_indices.append(v3_idx)
                face_vertex_indices.append(v4_idx)

        # Step 4: Create the USD mesh primitive
        print("Creating USD mesh...")
        terrain_prim = UsdGeom.Mesh.Define(stage, f'/World/{terrain_name}')
        
        # Apply the vertices, face counts, and indices to the mesh
        terrain_prim.GetPointsAttr().Set(Vt.Vec3fArray(vertices))
        terrain_prim.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_vertex_counts))
        terrain_prim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_vertex_indices))

        # Add a simple material (optional but good for visibility)
        print("Adding material...")
        try:
            # Create a simple displayColor attribute for visibility
            prim = stage.GetPrimAtPath(f'/World/{terrain_name}')
            prim.CreateAttribute("primvars:displayColor", Vt.Vec3fArray).Set(Vt.Vec3fArray([(0.6, 0.4, 0.2)]))  # Brown terrain color
        except Exception as material_error:
            print(f"Warning: Could not add material: {material_error}")
        
        print(f"Successfully created terrain mesh at: {terrain_prim.GetPath()}")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("Initializing USD stage...")
        # Get the current stage or create a new one
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        print("USD stage initialized successfully")

        # Define the path to your heightmap file
        # This assumes the heightmap is in the 'src/heightmaps/' folder relative to this script.
        heightmap_file = os.path.join(SCRIPT_DIR, "src", "heightmaps", "improved_heightmap.npy")
        
        # Check if the directory structure exists
        heightmap_dir = os.path.dirname(heightmap_file)
        if not os.path.exists(heightmap_dir):
            print(f"Creating directory: {heightmap_dir}")
            os.makedirs(heightmap_dir, exist_ok=True)
            print("Directory created. Please place your heightmap file there and run again.")
        
        # Fallback: look for heightmap in script directory
        if not os.path.exists(heightmap_file):
            fallback_file = os.path.join(SCRIPT_DIR, "basic_heightmap.npy")
            if os.path.exists(fallback_file):
                print(f"Using fallback heightmap: {fallback_file}")
                heightmap_file = fallback_file
            else:
                print("No heightmap found. Creating a simple test heightmap...")
                # Create a simple test heightmap
                test_heightmap = np.random.rand(64, 64) * 0.5 + 0.5  # Random heights between 0.5 and 1.0
                heightmap_file = os.path.join(SCRIPT_DIR, "test_heightmap.npy")
                np.save(heightmap_file, test_heightmap)
                print(f"Test heightmap created: {heightmap_file}")
        
        # Run the terrain generation function
        print("Starting terrain generation...")
        success = generate_usd_terrain_from_heightmap(stage, heightmap_file)
        
        if success:
            # Save the stage
            save_path = os.path.join(SCRIPT_DIR, "procedural_terrain.usd")
            print(f"Saving scene to: {save_path}")
            omni.usd.get_context().save_as(save_path)
            print(f"Scene saved successfully to: {save_path}")
            print("=== TERRAIN GENERATION COMPLETED SUCCESSFULLY ===")
        else:
            print("=== TERRAIN GENERATION FAILED ===")
            
    except Exception as e:
        print(f"Script failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # IMPORTANT: Always close the simulation app
        print("Closing simulation app...")
        simulation_app.close()
        print("Script finished.")