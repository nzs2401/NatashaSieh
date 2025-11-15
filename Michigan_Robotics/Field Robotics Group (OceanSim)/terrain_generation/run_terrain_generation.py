import numpy as np
import omni.usd
from pxr import Gf, Usd, UsdGeom, Vt
import os
import omni.replicator.core as rep

# Get the path of the directory this script is in
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_usd_terrain_from_heightmap(stage, heightmap_path, terrain_name="ProceduralTerrain", scale=(100.0, 100.0, 10.0)):
    """
    Creates a 3D terrain mesh in a USD stage from a NumPy heightmap file.
    """
    try:
        # Step 1: Load the heightmap data from the .npy file
        print(f"Loading heightmap from: {heightmap_path}")
        heightmap = np.load(heightmap_path)
        size = heightmap.shape[0]
        print(f"✓ Heightmap loaded successfully. Shape: {heightmap.shape}")
        
        # Step 2: Calculate vertices
        print("Generating vertices...")
        vertices = []
        for y in range(size):
            for x in range(size):
                pos_x = (x / size - 0.5) * scale[0]
                pos_y = (y / size - 0.5) * scale[1]
                pos_z = heightmap[y, x] * scale[2]
                vertices.append(Gf.Vec3f(pos_x, pos_y, pos_z))

        print(f"✓ Generated {len(vertices)} vertices")

        # Step 3: Define faces (triangles)
        print("Generating faces...")
        face_vertex_counts = []
        face_vertex_indices = []
        for y in range(size - 1):
            for x in range(size - 1):
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

        print(f"✓ Generated {len(face_vertex_counts)} faces")

        # Step 4: Create the USD mesh primitive
        print(f"Creating USD mesh at path: /World/{terrain_name}")
        terrain_prim = UsdGeom.Mesh.Define(stage, f'/World/{terrain_name}')
        
        # Apply the vertices, face counts, and indices to the mesh
        terrain_prim.GetPointsAttr().Set(Vt.Vec3fArray(vertices))
        terrain_prim.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_vertex_counts))
        terrain_prim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_vertex_indices))

        print(f"✓ Successfully created terrain mesh at: {terrain_prim.GetPath()}")
        return True

    except FileNotFoundError:
        print(f"✗ Error: Heightmap file not found at {heightmap_path}")
        return False
    except Exception as e:
        print(f"✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_stage_multiple_methods(stage, save_path):
    """Try multiple methods to save the USD stage."""
    methods_tried = []
    
    # Method 1: Isaac Sim's save_stage_as
    try:
        omni.usd.get_context().save_stage_as(save_path)
        print("✓ Used omni.usd save_stage_as method")
        return True
    except Exception as e:
        methods_tried.append(f"save_stage_as: {e}")
    
    # Method 2: Isaac Sim's save_as
    try:
        omni.usd.get_context().save_as(save_path)
        print("✓ Used omni.usd save_as method")
        return True
    except Exception as e:
        methods_tried.append(f"save_as: {e}")
    
    # Method 3: Direct USD stage export
    try:
        stage.Export(save_path)
        print("✓ Used direct USD stage.Export method")
        return True
    except Exception as e:
        methods_tried.append(f"stage.Export: {e}")
    
    # Method 4: USD root layer export
    try:
        stage.GetRootLayer().Export(save_path)
        print("✓ Used USD root layer Export method")
        return True
    except Exception as e:
        methods_tried.append(f"root_layer.Export: {e}")
    
    # Method 5: Create a new stage and copy content
    try:
        new_stage = Usd.Stage.CreateNew(save_path)
        UsdGeom.Xform.Define(new_stage, "/World")
        
        # Copy the terrain prim to the new stage
        terrain_prim_path = "/World/ProceduralTerrain"
        if stage.GetPrimAtPath(terrain_prim_path):
            new_stage.DefinePrim(terrain_prim_path, "Mesh")
            source_prim = stage.GetPrimAtPath(terrain_prim_path)
            dest_prim = new_stage.GetPrimAtPath(terrain_prim_path)
            
            # Copy attributes
            for attr in source_prim.GetAttributes():
                dest_attr = dest_prim.CreateAttribute(attr.GetName(), attr.GetTypeName())
                dest_attr.Set(attr.Get())
        
        new_stage.GetRootLayer().Save()
        print("✓ Used create new stage and copy method")
        return True
    except Exception as e:
        methods_tried.append(f"create_new_stage: {e}")
    
    print("✗ All save methods failed:")
    for i, method in enumerate(methods_tried, 1):
        print(f"  {i}. {method}")
    return False

if __name__ == "__main__":
    print("=== Isaac Sim Terrain Generation (Robust) ===")
    TERRAIN_TYPE = "sand_ripples"  # Options: "volcanic_boulder_field", "sand_ripples"
    
    try:
        # Get the current stage or create a new one
        print("Initializing USD context...")
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        print("✓ USD stage created")

        # Define the path to your heightmap file
        # heightmap_file = "/home/nsieh/code/isaacsim-5.0/_build/linux-x86_64/release/ROB490/parametric_heightmaps/volcanic_boulder_field.npy"
        heightmap_file = f"/home/nsieh/code/isaacsim-5.0/_build/linux-x86_64/release/ROB490/parametric_heightmaps/{TERRAIN_TYPE}.npy"

        # from parametric_terrain_generator import TerrainParameterGenerator, generate_parametric_heightmap
        # param_gen = TerrainParameterGenerator()
        # random_params = param_gen.generate_random_parameters(seed=12345)
        # heightmap = generate_parametric_heightmap(random_params)
        print(f"Loading heightmap from: {heightmap_file}")
        
        # Run the terrain generation function
        success = generate_usd_terrain_from_heightmap(stage, heightmap_file)
        
        if success:
            # Save the stage using multiple methods
            save_path = os.path.join(SCRIPT_DIR, "procedural_terrain.usd")
            print(f"Attempting to save scene to: {save_path}")
            
            save_success = save_stage_multiple_methods(stage, save_path)
            
            if save_success and os.path.exists(save_path):
                print(f"✓ Scene saved successfully!")
                print(f"USD file: {save_path}")
                print(f"File size: {os.path.getsize(save_path)} bytes")
                
                # List all USD files in the directory
                print("\nUSD files in ROB490 directory:")
                for f in os.listdir(SCRIPT_DIR):
                    if f.endswith('.usd') or f.endswith('.usda'):
                        file_path = os.path.join(SCRIPT_DIR, f)
                        print(f"  {f} ({os.path.getsize(file_path)} bytes)")
                        
            else:
                print(f"✗ Save operation may have failed - checking for file...")
                if os.path.exists(save_path):
                    print(f"✓ File exists despite error: {save_path}")
                else:
                    print(f"✗ No file found at: {save_path}")
        else:
            print("✗ Terrain generation failed")
            
    except Exception as e:
        print(f"✗ Main execution error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== Generation Complete ===")