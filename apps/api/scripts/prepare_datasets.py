import os
import csv
import random
from glob import glob

DATASET_PATH = "/Users/gparthasrikar/Documents/m-project/Brain_Stroke_CT_Dataset"
OUTPUT_DIR = "/Users/gparthasrikar/Documents/m-project/apps/api/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_files(category):
    # Recursively find images
    patterns = [
        os.path.join(DATASET_PATH, category, "**", "*.jpg"),
        os.path.join(DATASET_PATH, category, "**", "*.png"),
        os.path.join(DATASET_PATH, category, "**", "*.jpeg")
        # We start with standard images. If 0 found, we might need to handle DICOMs later.
    ]
    files = []
    for p in patterns:
        files.extend(glob(p, recursive=True))
    return files

def split_data(files, train_ratio=0.8, val_ratio=0.1):
    random.shuffle(files)
    n = len(files)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    return {
        'train': files[:train_end],
        'val': files[train_end:val_end],
        'test': files[val_end:]
    }

def main():
    print("Scanning files...")
    normal_files = get_files("Normal")
    ischemia_files = get_files("Ischemia")
    bleeding_files = get_files("Bleeding")
    
    print(f"Found: Normal={len(normal_files)}, Ischemia={len(ischemia_files)}, Bleeding={len(bleeding_files)}")

    if len(normal_files) == 0:
        print("Warning: No standard images found. Checking for DICOM...")
        # Fallback to DICOM if needed, but assuming PNGs exist based on previous analysis
        # If 0, we will halt and ask user/check.
    
    # --- Dataset A (Binary: Normal=0, Stroke=1) ---
    print("Creating Dataset A (Binary)...")
    data_a = []
    for f in normal_files:
        data_a.append((f, 0))
    for f in ischemia_files + bleeding_files:
        data_a.append((f, 1))
    
    random.shuffle(data_a)
    
    # Split
    split_idx_a = int(len(data_a) * 0.8)
    # Simple split for CSV. We can simple save one big CSV with a "split" column
    # or separate CSVs. Let's do separate or one big one. 
    # Let's make one CSV with columns: path, label, split
    
    with open(os.path.join(OUTPUT_DIR, "dataset_a.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "label", "split"])
        
        for i, (path, label) in enumerate(data_a):
            r = random.random()
            if r < 0.8: split = "train"
            elif r < 0.9: split = "val"
            else: split = "test"
            writer.writerow([path, label, split])

    # --- Dataset B (Type: Ischemia=0, Bleeding=1) ---
    print("Creating Dataset B (Type)...")
    data_b = []
    for f in ischemia_files:
        data_b.append((f, 0))
    for f in bleeding_files:
        data_b.append((f, 1))
        
    random.shuffle(data_b)
    
    with open(os.path.join(OUTPUT_DIR, "dataset_b.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["filepath", "label", "split"])
        
        for i, (path, label) in enumerate(data_b):
            r = random.random()
            if r < 0.8: split = "train"
            elif r < 0.9: split = "val"
            else: split = "test"
            writer.writerow([path, label, split])
            
    print("Done. CSVs created at apps/api/data/")

if __name__ == "__main__":
    main()
