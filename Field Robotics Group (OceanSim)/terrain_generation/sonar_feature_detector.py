import numpy as np
import cv2
import matplotlib.pyplot as plt

class SonarFeatureDetector:
    """Better feature detection for side-scan sonar"""
    
    def __init__(self, image_path):
        """Load the sonar image"""
        self.img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            raise ValueError(f"Could not load image: {image_path}")
        print(f"Loaded image: {self.img.shape}")
    
    def preprocess(self):
        """Step 1: Clean up the sonar image"""
        print("Preprocessing...")
        
        # Remove noise while keeping edges sharp
        denoised = cv2.bilateralFilter(self.img, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        self.preprocessed = enhanced
        return enhanced
    
    def detect_edges_log(self):
        """Step 2: Detect edges (better than Canny for sonar)"""
        print("Detecting edges with LoG...")
        from scipy import ndimage
        
        # Laplacian of Gaussian - better for noisy images
        log = ndimage.gaussian_laplace(self.preprocessed, sigma=2)
        
        # Threshold
        threshold = np.abs(log).mean() + 2 * np.abs(log).std()
        edges = np.abs(log) > threshold
        
        return (edges * 255).astype(np.uint8)
    
    def detect_texture_gabor(self):
        """Step 3: Detect texture patterns (great for terrain)"""
        print("Detecting texture with Gabor filters...")
        
        responses = []
        # Try 8 different orientations
        for theta in np.arange(0, np.pi, np.pi / 8):
            # Create Gabor filter
            kernel = cv2.getGaborKernel(
                ksize=(21, 21),
                sigma=5.0,
                theta=theta,
                lambd=10.0,
                gamma=0.5,
                psi=0
            )
            
            # Apply filter
            filtered = cv2.filter2D(self.preprocessed, cv2.CV_32F, kernel)
            responses.append(filtered)
        
        # Take maximum response across all orientations
        gabor_response = np.max(np.array(responses), axis=0)
        
        # Normalize to 0-255
        gabor_norm = cv2.normalize(gabor_response, None, 0, 255, cv2.NORM_MINMAX)
        
        return gabor_norm.astype(np.uint8)
    
    def detect_ridges(self):
        """Step 4: Detect linear structures (good for shipwrecks)"""
        print("Detecting ridges...")
        
        # Sobel in X and Y directions
        sobelx = cv2.Sobel(self.preprocessed, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(self.preprocessed, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradient magnitude
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize
        magnitude_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        
        return magnitude_norm.astype(np.uint8)
    
    def analyze_all(self, save_path='sonar_analysis.png'):
        """Run complete analysis and show results"""
        
        # Run all detections
        preprocessed = self.preprocess()
        edges = self.detect_edges_log()
        texture = self.detect_texture_gabor()
        ridges = self.detect_ridges()
        
        # Create comparison figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        
        axes[0, 0].imshow(self.img, cmap='gray')
        axes[0, 0].set_title('1. Original Sonar Image', fontsize=14, fontweight='bold')
        
        axes[0, 1].imshow(preprocessed, cmap='gray')
        axes[0, 1].set_title('2. Preprocessed (Denoised + Enhanced)', fontsize=14, fontweight='bold')
        
        axes[0, 2].imshow(edges, cmap='gray')
        axes[0, 2].set_title('3. Edge Detection (LoG)', fontsize=14, fontweight='bold')
        
        axes[1, 0].imshow(texture, cmap='hot')
        axes[1, 0].set_title('4. Texture/Roughness (Gabor)', fontsize=14, fontweight='bold')
        
        axes[1, 1].imshow(ridges, cmap='hot')
        axes[1, 1].set_title('5. Linear Features (Sobel)', fontsize=14, fontweight='bold')
        
        # Combined result
        combined = cv2.addWeighted(texture, 0.5, ridges, 0.5, 0)
        axes[1, 2].imshow(combined, cmap='hot')
        axes[1, 2].set_title('6. Combined Features', fontsize=14, fontweight='bold')
        
        for ax in axes.flat:
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"\nSaved analysis to: {save_path}")
        plt.show()
        
        return {
            'preprocessed': preprocessed,
            'edges': edges,
            'texture': texture,
            'ridges': ridges,
            'combined': combined
        }

# Main function to use
def analyze_sonar_image(image_path):
    """Simple function to analyze a sonar image"""
    detector = SonarFeatureDetector(image_path)
    results = detector.analyze_all()
    return results

# Example usage
if __name__ == "__main__":
    # Change this to your actual image path
    image_path = "/home/nsieh/Desktop/sonar_output/waterfall/complete_survey_waterfall_20251013_151842.png"
    
    print("="*60)
    print("SONAR FEATURE ANALYSIS")
    print("="*60)
    
    try:
        results = analyze_sonar_image(image_path)
        print("\n✓ Analysis complete!")
        print("  Check 'sonar_analysis.png' for results")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("  1. The image path is correct")
        print("  2. You have these packages: opencv-python, numpy, matplotlib, scipy")