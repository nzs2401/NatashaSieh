import numpy as np
import cv2
import matplotlib.pyplot as plt

# Step 1: Create a simple test image
def create_simple_test():
    # Make a gray image with some lines
    img = np.ones((400, 400), dtype=np.uint8) * 128  # Gray background
    # Draw 2 clear lines
    cv2.line(img, (50, 100), (350, 150), 255, 3)  # White line
    cv2.line(img, (100, 250), (300, 300), 255, 3)  # White line
    return img

# Step 3: Detect edges
def detect_edges_simple(img):
    edges = cv2.Canny(img, 50, 150)
    return edges

# Step 4: Find lines
def find_lines_simple(edges):
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=50,
        maxLineGap=10
    )
    return lines

# NEW: Step 4.5: Merge nearby parallel lines
def merge_nearby_lines(lines, distance_threshold=10, angle_threshold=10):
    """Merge lines that are close and parallel"""
    if lines is None or len(lines) <= 1:
        return lines
    
    merged = []
    used = set()
    
    for i, line1 in enumerate(lines):
        if i in used:
            continue
        
        x1, y1, x2, y2 = line1[0]
        
        # Calculate angle of line1
        angle1 = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        mid1 = ((x1 + x2) / 2, (y1 + y2) / 2)
        
        # Start a group with this line
        group = [line1[0]]
        used.add(i)
        
        # Find similar nearby lines
        for j, line2 in enumerate(lines):
            if j in used:
                continue
                
            x3, y3, x4, y4 = line2[0]
            angle2 = np.arctan2(y4 - y3, x4 - x3) * 180 / np.pi
            mid2 = ((x3 + x4) / 2, (y3 + y4) / 2)
            
            # Check if angles are similar
            angle_diff = abs(angle1 - angle2)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            # Check if midpoints are close
            mid_dist = np.sqrt((mid1[0] - mid2[0])**2 + (mid1[1] - mid2[1])**2)
            
            if mid_dist < distance_threshold and angle_diff < angle_threshold:
                group.append(line2[0])
                used.add(j)
        
        # Average all lines in the group
        if len(group) > 0:
            avg_x1 = int(np.mean([l[0] for l in group]))
            avg_y1 = int(np.mean([l[1] for l in group]))
            avg_x2 = int(np.mean([l[2] for l in group]))
            avg_y2 = int(np.mean([l[3] for l in group]))
            merged.append([[avg_x1, avg_y1, avg_x2, avg_y2]])
    
    return np.array(merged) if merged else None

# Step 5: Draw the detected lines
def draw_lines(img, lines):
    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green
    return result

# Now run the whole pipeline
test_image = create_simple_test()
edges = detect_edges_simple(test_image)
lines = find_lines_simple(edges)

# Print raw detections
print(f"Raw detections: {len(lines) if lines is not None else 0} lines")

# Merge nearby lines
lines_merged = merge_nearby_lines(lines, distance_threshold=10, angle_threshold=10)

# Print merged result
print(f"After merging: {len(lines_merged) if lines_merged is not None else 0} lines")

result_raw = draw_lines(test_image, lines)
result_merged = draw_lines(test_image, lines_merged)

# Show everything - now with 4 panels
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].imshow(test_image, cmap='gray')
axes[0, 0].set_title('Original')
axes[0, 1].imshow(edges, cmap='gray')
axes[0, 1].set_title('Edges')
axes[1, 0].imshow(cv2.cvtColor(result_raw, cv2.COLOR_BGR2RGB))
axes[1, 0].set_title(f'Raw: {len(lines) if lines is not None else 0} lines')
axes[1, 1].imshow(cv2.cvtColor(result_merged, cv2.COLOR_BGR2RGB))
axes[1, 1].set_title(f'Merged: {len(lines_merged) if lines_merged is not None else 0} lines')
plt.tight_layout()
plt.show()



# Load your sonar image
# Replace 'your_sonar_image.png' with your actual file path
sonar_image = cv2.imread('your_sonar_image.png', cv2.IMREAD_GRAYSCALE)

# Check if it loaded
if sonar_image is None:
    print("ERROR: Could not load image. Check your file path!")
else:
    print(f"Loaded sonar image: {sonar_image.shape}")
    
    # Run the same pipeline
    edges_sonar = detect_edges_simple(sonar_image)
    lines_sonar = find_lines_simple(edges_sonar)
    lines_sonar_merged = merge_nearby_lines(lines_sonar, distance_threshold=15, angle_threshold=10)
    
    print(f"Raw detections: {len(lines_sonar) if lines_sonar is not None else 0} lines")
    print(f"After merging: {len(lines_sonar_merged) if lines_sonar_merged is not None else 0} lines")
    
    result_sonar = draw_lines(sonar_image, lines_sonar_merged)
    
    # Show results
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(sonar_image, cmap='gray')
    axes[0].set_title('Your Sonar Scan')
    axes[1].imshow(edges_sonar, cmap='gray')
    axes[1].set_title('Edges Detected')
    axes[2].imshow(cv2.cvtColor(result_sonar, cv2.COLOR_BGR2RGB))
    axes[2].set_title(f'Detected Lines: {len(lines_sonar_merged) if lines_sonar_merged is not None else 0}')
    plt.tight_layout()
    plt.show()