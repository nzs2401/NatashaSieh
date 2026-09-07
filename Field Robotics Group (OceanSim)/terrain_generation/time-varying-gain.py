import numpy as np
import cv2

def apply_tvg_correction(sonar_image, alpha=2.0, beta=0.0001):
    """
    Apply Time-Varying Gain to sonar waterfall image
    
    Args:
        sonar_image: 2D array (rows=pings, cols=range bins)
        alpha: Spreading loss exponent (1=cylindrical, 2=spherical)
        beta: Absorption coefficient
    
    Returns:
        TVG-corrected sonar image
    """
    height, width = sonar_image.shape
    
    # Create range array (assuming range increases along columns)
    range_bins = np.arange(width)
    max_range = width
    
    # Normalize range to [0, 1]
    normalized_range = range_bins / max_range
    
    # Calculate TVG correction: r^alpha * exp(beta*r)
    tvg_gain = np.power(normalized_range + 0.01, alpha) * np.exp(beta * normalized_range * max_range)
    
    # Apply gain to each row (ping)
    corrected = sonar_image.astype(np.float32) * tvg_gain[np.newaxis, :]
    
    # Clip to valid range
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    
    return corrected


def demonstrate_tvg():
    """Show before/after TVG on your terrain heightmap"""
    
    # Load a heightmap and convert to sonar-like intensity
    heightmap = np.load("parametric_heightmaps/sand_ripples.npy")
    
    # Simulate sonar intensity (gradient-based)
    gy, gx = np.gradient(heightmap)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    sonar_image = (gradient_mag * 255).astype(np.uint8)
    
    # Apply TVG
    tvg_corrected = apply_tvg_correction(sonar_image, alpha=2.0, beta=0.0001)
    
    # Save comparison
    comparison = np.hstack([sonar_image, tvg_corrected])
    cv2.imwrite("tvg_comparison.png", comparison)
    
    # Also save separately
    cv2.imwrite("sonar_before_tvg.png", sonar_image)
    cv2.imwrite("sonar_after_tvg.png", tvg_corrected)
    
    print("✓ TVG demonstration complete!")
    print("  Before: sonar_before_tvg.png")
    print("  After: sonar_after_tvg.png")
    print("  Comparison: tvg_comparison.png")


if __name__ == "__main__":
    demonstrate_tvg()