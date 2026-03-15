import tensorflow as tf
import numpy as np
from PIL import Image
import io

MODEL_A_PATH = "apps/api/models/model_a.h5"
MODEL_B_PATH = "apps/api/models/model_b.h5"

class MLEngine:
    def __init__(self):
        self.model_a = None
        self.model_b = None
        self.load_models()

    def load_models(self):
        print("Loading Model A...")
        try:
            self.model_a = tf.keras.models.load_model(MODEL_A_PATH)
            print("Model A loaded.")
        except Exception as e:
            print(f"Error loading Model A: {e}")

        print("Loading Model B...")
        try:
            self.model_b = tf.keras.models.load_model(MODEL_B_PATH)
            print("Model B loaded.")
        except Exception as e:
            print(f"Error loading Model B: {e}")

    def preprocess_image(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = img_array / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dim
        return img_array

    def is_brain_ct(self, image_bytes):
        try:
            # 1. Open and Resize
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # Resize for faster processing
            img_small = img.resize((224, 224)) 
            img_array = np.array(img_small) # Shape (224, 224, 3)

            # 2. Check for Color (Saturation)
            # CT scans are grayscale. High saturation -> Not a CT.
            # Even B/W photos might have 3 channels equal.
            img_hsv = img_small.convert('HSV')
            saturation = np.array(img_hsv)[:, :, 1]
            if np.mean(saturation) > 20: 
                print("Rejected: Image has color saturation")
                return False
            
            # 3. Check for RGB deviation (for 'grayscale' JPGs that are actually colored)
            img_float = img_array.astype(float)
            r, g, b = img_float[:,:,0], img_float[:,:,1], img_float[:,:,2]
            channel_diff = (np.abs(r - g) + np.abs(g - b) + np.abs(b - r)) / 3.0
            if np.mean(channel_diff) > 5:
                print("Rejected: Image channels deviate (not grayscale)")
                return False

            # 4. Structure Checks (Grayscale)
            gray = img_small.convert('L')
            gray_array = np.array(gray)
            
            # A. Border Check
            # CT scans usually have a black background.
            # Check the average intensity of the outer 5% (approx 10px for 224 size)
            border_size = 15
            top = gray_array[0:border_size, :]
            bottom = gray_array[-border_size:, :]
            left = gray_array[:, 0:border_size]
            right = gray_array[:, -border_size:]
            
            # Combine borders
            borders = np.concatenate((
                top.flatten(), 
                bottom.flatten(), 
                left.flatten(), 
                right.flatten()
            ))
            
            border_mean = np.mean(borders)
            
            # Threshold: Scans have black borders (~0-10). 
            # Real world photos/selfies usually fill the frame or are brighter > 40-50.
            # We use a conservative threshold of 45 to allow for some noise/artifacts.
            if border_mean > 45:
                print(f"Rejected: Borders are too bright ({border_mean:.2f})")
                return False

            # B. Dark Pixel Ratio
            # CT scans have a large percentage of black background.
            # Selfies usually occupy the full histogram.
            # Check percentage of pixels < 30 intensity.
            dark_pixels = np.sum(gray_array < 30)
            total_pixels = gray_array.size
            dark_ratio = dark_pixels / total_pixels
            
            if dark_ratio < 0.15: # Expect at least 15% dark background
                print(f"Rejected: Not enough dark background ({dark_ratio:.2f})")
                return False

            # 5. Shape/Morphology Check
            # Filter out long bones/limbs by checking the Aspect Ratio of the non-black region.
            # Brains (axial slices) are roughly 1:1 circular/oval.
            # Limbs/Knees are often elongated.
            
            # Threshold to find the object (bone/tissue > 40)
            mask = gray_array > 40
            coords = np.argwhere(mask)
            
            if coords.size > 0:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0) + 1
                
                height = y1 - y0
                width = x1 - x0
                
                # Protect against divide by zero (though width > 0 if coords > 0)
                if height > 0:
                    aspect_ratio = width / height
                    
                    # Brain slice is usually 0.7 to 1.4
                    # Knee/Leg/Arm is often < 0.6 or > 1.6
                    if aspect_ratio < 0.60 or aspect_ratio > 1.65:
                        print(f"Rejected: Sshape aspect ratio {aspect_ratio:.2f} is not brain-like (approx 1.0)")
                        return False

            return True

        except Exception as e:
            print(f"Error checking is_brain_ct: {e}")
            return False

    def predict(self, image_bytes):
        if not self.model_a:
            return {"error": "Models not loaded"}

        processed_img = self.preprocess_image(image_bytes)
        
        # --- Stage 1: Normal vs Stroke ---
        # Model A: 0 = Normal, 1 = Stroke
        # Sigmoid output: < 0.5 -> Normal, >= 0.5 -> Stroke
        pred_a = self.model_a.predict(processed_img)[0][0]
        
        if pred_a < 0.5:
            confidence = (1 - pred_a) * 100
            return {
                "status": "Normal",
                "confidence": f"{confidence:.2f}%",
                "stage": "Stage 1 (Screening)",
                "advice": "No signs of stroke detected. Maintain a healthy lifestyle."
            }
        
        # --- Stage 2: Stroke Type ---
        if not self.model_b:
             return {
                "status": "Stroke Detected",
                "type": "Unknown (Model B missing)",
                "confidence_stage1": f"{pred_a * 100:.2f}%",
                 "advice": "Stroke signs detected. Please consult a doctor immediately."
            }

        # Model B: 0 = Ischemia, 1 = Bleeding
        pred_b = self.model_b.predict(processed_img)[0][0]
        
        if pred_b < 0.5:
            result = "Ischemic Stroke"
            confidence = (1 - pred_b) * 100
            advice = "Signs of Ischemic Stroke (Clot). Immediate medical attention required. Thrombolytic therapy may be considered."
        else:
            result = "Haemorrhagic Stroke"
            confidence = pred_b * 100
            advice = "Signs of Haemorrhagic Stroke (Bleeding). Immediate medical attention required. Surgery may be needed. AVOID blood thinners."
            
        return {
            "status": result,
            "confidence": f"{confidence:.2f}%",
            "stage": "Stage 2 (Type Classification)",
            "advice": advice
        }

ml_engine = MLEngine()
