import os
from PIL import Image
from collections import Counter

DATASET_PATH = "/Users/gparthasrikar/Documents/m-project/Brain_Stroke_CT_Dataset"
CATEGORIES = ["Normal", "Ischemia", "Bleeding"]

def analyze_dataset():
    print(f"Analyzing dataset at: {DATASET_PATH}")
    stats = {}
    dimensions = []
    
    for category in CATEGORIES:
        path = os.path.join(DATASET_PATH, category)
        if not os.path.exists(path):
            print(f"Warning: Category {category} not found at {path}")
            continue
            
        files = []
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.dcm')):
                    files.append(os.path.join(root, f))
        
        count = len(files)
        stats[category] = count
        
        # Check first 10 images for dimensions
        for img_path in files[:10]:
            try:
                if img_path.endswith('.dcm'):
                    # Skip DICOM for dimension check in this simple script if pydicom not installed
                    # But we can try treating as binary or use basic check if convertible
                    pass 
                else:
                    with Image.open(img_path) as img:
                        dimensions.append(img.size)
            except Exception as e:
                pass

    print("\n--- Class Distribution ---")
    for cat, count in stats.items():
        print(f"{cat}: {count} images")
    
    if dimensions:
        most_common_dims = Counter(dimensions).most_common(3)
        print("\n--- Common Dimensions ---")
        for dim, count in most_common_dims:
            print(f"{dim}: {count} files")
    else:
        print("\nNo standard image formats (PNG/JPG) checked for dimensions (mostly DICOM?).")

if __name__ == "__main__":
    analyze_dataset()
