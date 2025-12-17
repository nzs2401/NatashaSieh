import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_all_heightmaps(heightmap_dir="parametric_heightmaps", output_dir="visualized_heightmaps"):
    """
    Convert all .npy heightmaps to viewable PNG images
    So you can finally SEE your parametric terrains!
    """
    heightmap_dir = Path(heightmap_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    heightmap_files = list(heightmap_dir.glob("*.npy"))
    
    print(f"=== Visualizing {len(heightmap_files)} Heightmaps ===\n")
    
    for hmap_file in heightmap_files:
        print(f"Visualizing: {hmap_file.name}")
        
        # Load heightmap (values 0.0 to 1.0)
        heightmap = np.load(hmap_file)
        
        # Convert to image (0-255)
        image = (heightmap * 255).astype(np.uint8)
        
        # Save as PNG
        output_path = output_dir / f"{hmap_file.stem}_original.png"
        cv2.imwrite(str(output_path), image)
        
        print(f"  ✓ Saved: {output_path}")
    
    print(f"\n✓ All heightmaps visualized in: {output_dir}/")
    print("  You can now open these PNG files to see your terrains!")


def convert_enhanced_back_to_heightmap(enhanced_dir="style_enhanced_terrains", 
                                       output_dir="parametric_heightmaps"):
    """
    Convert style-transferred PNG images back to .npy heightmaps
    So you can use them in Isaac Sim!
    """
    enhanced_dir = Path(enhanced_dir)
    output_dir = Path(output_dir)
    
    enhanced_files = list(enhanced_dir.glob("*_realistic.png"))
    
    print(f"\n=== Converting {len(enhanced_files)} Enhanced Images Back to Heightmaps ===\n")
    
    for enhanced_file in enhanced_files:
        print(f"Converting: {enhanced_file.name}")
        
        # Load enhanced PNG (0-255)
        image = cv2.imread(str(enhanced_file), cv2.IMREAD_GRAYSCALE)
        
        # Convert back to heightmap (0.0-1.0)
        heightmap = image.astype(np.float32) / 255.0
        
        # Save with _enhanced suffix
        terrain_name = enhanced_file.stem.replace("_realistic", "")
        output_path = output_dir / f"{terrain_name}_enhanced.npy"
        
        np.save(output_path, heightmap)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"     Shape: {heightmap.shape}, Range: [{heightmap.min():.3f}, {heightmap.max():.3f}]")
    
    print(f"\n✓ Enhanced heightmaps ready for Isaac Sim in: {output_dir}/")
    print("  Use these .npy files with your run_terrain_generation.py script!")


def create_side_by_side_comparisons(original_dir="visualized_heightmaps",
                                     enhanced_dir="style_enhanced_terrains",
                                     output_dir="comparisons"):
    """
    Create before/after comparison images for your report
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    original_dir = Path(original_dir)
    enhanced_dir = Path(enhanced_dir)
    
    # Get matching pairs
    original_files = {f.stem.replace("_original", ""): f 
                     for f in original_dir.glob("*_original.png")}
    enhanced_files = {f.stem.replace("_realistic", ""): f 
                     for f in enhanced_dir.glob("*_realistic.png")}
    
    # Find common terrains
    common_terrains = set(original_files.keys()) & set(enhanced_files.keys())
    
    print(f"\n=== Creating {len(common_terrains)} Before/After Comparisons ===\n")
    
    for terrain_name in common_terrains:
        print(f"Creating comparison: {terrain_name}")
        
        # Load images
        original = cv2.imread(str(original_files[terrain_name]), cv2.IMREAD_GRAYSCALE)
        enhanced = cv2.imread(str(enhanced_files[terrain_name]), cv2.IMREAD_GRAYSCALE)
        
        # Resize enhanced to match original if needed
        if original.shape != enhanced.shape:
            enhanced = cv2.resize(enhanced, (original.shape[1], original.shape[0]))
        
        # Create side-by-side comparison
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        
        axes[0].imshow(original, cmap='gray')
        axes[0].set_title('Before: Parametric Generation\n(Pure mathematics)', fontsize=12, pad=10)
        axes[0].axis('off')
        
        axes[1].imshow(enhanced, cmap='gray')
        axes[1].set_title('After: Neural Style Transfer\n(Real sonar texture)', fontsize=12, pad=10)
        axes[1].axis('off')
        
        plt.suptitle(f'{terrain_name.replace("_", " ").title()}', fontsize=14, y=0.98)
        plt.tight_layout()
        
        # Save
        output_path = output_dir / f"{terrain_name}_comparison.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Saved: {output_path}")
    
    print(f"\n✓ Comparison images saved to: {output_dir}/")
    print("  Use these in your report!")


def create_summary_figure(comparison_dir="comparisons", output_file="summary_figure.png"):
    """
    Create a single figure showing all terrain comparisons
    Perfect for your report!
    """
    comparison_dir = Path(comparison_dir)
    comparison_files = sorted(list(comparison_dir.glob("*_comparison.png")))
    
    if not comparison_files:
        print("No comparison files found! Run create_side_by_side_comparisons() first.")
        return
    
    print(f"\n=== Creating Summary Figure with {len(comparison_files)} Terrains ===\n")
    
    # Load all comparisons
    images = []
    titles = []
    for comp_file in comparison_files:
        img = cv2.imread(str(comp_file))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        images.append(img)
        
        terrain_name = comp_file.stem.replace("_comparison", "").replace("_", " ").title()
        titles.append(terrain_name)
    
    # Create grid
    n_images = len(images)
    n_cols = 2
    n_rows = (n_images + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6 * n_rows))
    axes = axes.flatten() if n_images > 1 else [axes]
    
    for i, (img, title) in enumerate(zip(images, titles)):
        axes[i].imshow(img)
        axes[i].set_title(title, fontsize=12, pad=5)
        axes[i].axis('off')
    
    # Hide unused subplots
    for i in range(n_images, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle('Synthetic Terrain Enhancement: Parametric Generation + Neural Style Transfer',
                fontsize=16, y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"✓ Saved summary figure: {output_file}")
    print("  This is perfect for your report presentation!")


def print_usage_instructions():
    """Print how to use enhanced heightmaps in Isaac Sim"""
    print("\n" + "="*70)
    print("HOW TO USE ENHANCED HEIGHTMAPS IN ISAAC SIM")
    print("="*70)
    print("""
1. Your enhanced heightmaps are saved in: parametric_heightmaps/
   - sand_ripples_enhanced.npy
   - volcanic_boulder_field_enhanced.npy
   - etc.

2. To use in Isaac Sim, edit run_terrain_generation.py:

   # Change TERRAIN_TYPE to the enhanced version
   TERRAIN_TYPE = "sand_ripples_enhanced"  # Add "_enhanced" suffix
   
   # The heightmap file path will be:
   heightmap_file = f"parametric_heightmaps/{TERRAIN_TYPE}.npy"

3. Run Isaac Sim script as usual:
   ~/.local/share/ov/pkg/isaac-sim-*/python.sh run_terrain_generation.py

4. Your terrain will now have REALISTIC sonar texture!
""")
    print("="*70 + "\n")


# ====================
# MAIN WORKFLOW
# ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TERRAIN VISUALIZATION & CONVERSION PIPELINE")
    print("="*70 + "\n")
    
    # Step 1: Visualize original heightmaps
    print("STEP 1: Visualizing original parametric terrains...")
    visualize_all_heightmaps()
    
    # Step 2: Convert enhanced images back to heightmaps
    print("\nSTEP 2: Converting enhanced images back to heightmaps...")
    convert_enhanced_back_to_heightmap()
    
    # Step 3: Create comparison images
    print("\nSTEP 3: Creating before/after comparisons...")
    create_side_by_side_comparisons()
    
    # Step 4: Create summary figure
    print("\nSTEP 4: Creating summary figure for report...")
    create_summary_figure()
    
    # Step 5: Print usage instructions
    print_usage_instructions()
    
    print("✓ Complete! You now have:")
    print("  - visualized_heightmaps/     : Your original terrains as images")
    print("  - style_enhanced_terrains/   : Style-transferred images")
    print("  - parametric_heightmaps/*_enhanced.npy : Ready for Isaac Sim")
    print("  - comparisons/               : Before/after images for report")
    print("  - summary_figure.png         : All comparisons in one figure")