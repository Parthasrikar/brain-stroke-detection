# 🔍 Comprehensive Integration Analysis: mega-project → m-project/apps

## 📊 PROJECT COMPARISON

### **mega-project** (Source - Standalone)
| Component | Tech | Location |
|-----------|------|----------|
| **Backend API** | Flask + CORS | `app.py` |
| **ML Model** | TensorFlow/Keras ResNet50 Ensemble | `stroke_model_resnet50_ensemble.h5` |
| **Frontend** | React 19 + Vite | `frontend/src/` |
| **Database** | None (Stateless) | — |
| **Auth** | None | — |
| **Model Input** | Disk-based path loading | `MODEL_PATH` env var |
| **Dependencies** | Flask, TensorFlow, Pillow, numpy | See `requirements.txt` |
| **Endpoints** | `/health`, `/predict`, `/validate-mri` | Simple route-based |

### **m-project/apps** (Target - Modular)
| Component | Tech | Location |
|-----------|------|----------|
| **Backend API** | FastAPI + AsyncIO | `api/main.py` |
| **ML Engine** | Custom wrapper (TensorFlow) | `api/ml_engine.py` |
| **Frontend** | React 19 + Vite + Router | `web/src/` |
| **Database** | MongoDB + Beanie ORM | Configured in `main.py` |
| **Auth** | JWT tokens + PassLib | `api/routers/auth.py` |
| **Model Input** | Loaded via ML engine module | `ml_engine.predict()` |
| **Dependencies** | FastAPI, Motor, Beanie, TensorFlow | Already compatible |
| **Endpoints** | Router-based modular | `/predict/`, `/auth/`, `/chatbot/`, etc |

---

## 🎯 BEST INTEGRATION METHOD

### **Recommended Approach: HYBRID INTEGRATION**

#### **Why Not Direct Copy-Paste?**
❌ Flask → FastAPI: Different async patterns, will cause conflicts  
❌ Stateless Flask → MongoDB integration: Architectural mismatch  
❌ Model loading differences: Path-based vs module-based  
❌ CORS setup: Already configured in FastAPI  

#### **Why Hybrid?**
✅ Leverages existing m-project architecture  
✅ Maintains MongoDB persistence  
✅ Keeps authentication intact  
✅ Migrates only ML logic (safe extraction)  

---

## 📋 STEP-BY-STEP INTEGRATION PLAN

### **PHASE 1: MODEL & PREPROCESSING EXTRACTION**

**What to Copy:**
1. **Model file**: `stroke_model_resnet50_ensemble.h5` → `apps/api/models/`
2. **Preprocessing logic** from `app.py`:
   - `preprocess_image()` function
   - `validate_mri()` function
   - Image validation heuristics
3. **Training scripts** (optional, for reference): `train_*.py`, `preprocess_*.py`

**Destination:**
```
apps/ai/
├── models/
│   └── stroke_model_resnet50_ensemble.h5
├── preprocessing.py          (← NEW: extracted functions)
└── model_loader.py           (← NEW: centralized loading)
```

**File Size Impact:**
- Model file: ~200MB
- Code: ~15KB

---

### **PHASE 2: ML ENGINE INTEGRATION**

**Current State** (`apps/api/ml_engine.py`):
- Likely has placeholder or basic logic
- Needs enhanced with mega-project's stroke detection

**What to Update:**
```python
# Before (current m-project)
result = ml_engine.predict(contents)

# After (with mega-project logic)
result = ml_engine.predict_stroke(contents)
# Includes:
# - MRI validation
# - ResNet50 ensemble prediction
# - Confidence threshold checking (0.65)
# - OOD (Out-of-Distribution) detection
# - Confidence scores for all 3 classes
```

**Implementation:**
- Merge `preprocess_image()` → `ml_engine.preprocess()`
- Merge `validate_mri()` → `ml_engine.is_brain_ct()`
- Load model in `ml_engine.__init__()` (async-safe)
- Keep existing prediction endpoint interface

---

### **PHASE 3: API ENDPOINT MIGRATION**

**mega-project Endpoints → m-project/apps:**

| mega-project | m-project/apps | Changes |
|--------------|----------------|---------|
| `POST /predict` (Flask) | `POST /predict/` (FastAPI) | ✅ Already exists |
| Returns: `status, advice, predictions` | Returns: `prediction, confidence, error` | ⚠️ Map response format |
| Health check: `/health` | Health check: `/` | ✅ Different path |
| Manual payload → Automatic Gemini | Uses Gemini if `GEMINI_API_KEY` set | ✅ Same logic |

**Response Format Alignment:**
```python
# mega-project
{
    "prediction": "Haemorrhagic",
    "confidence": 0.92,
    "probabilities": {"Haemorrhagic": 0.92, "Ischemic": 0.07, "Normal": 0.01},
    "status": "Stroke detected",
    "advice": "Seek immediate medical attention"
}

# m-project/apps (current)
{
    "error": "...", OR
    "status": "...",
    "advice": "...",
    "is_brain": true/false
}

# → Merge into one format for both
```

---

### **PHASE 4: DEPENDENCIES & REQUIREMENTS**

**mega-project `requirements.txt`:**
```
Flask==3.1.2
flask-cors==6.0.2
tensorflow==2.20.0
TensorFlow-Hub==0.16.1
tensorflow-datasets==4.9.7
numpy==2.2.6
Pillow==12.0.0
python-dotenv==1.0.1
gunicorn==23.0.0
requests==2.32.5
scikit-learn==1.7.2
monai==1.3.0
matplotlib==3.8.2
```

**m-project/apps `requirements.txt`:**
```
fastapi
uvicorn
motor
beanie
tensorflow
numpy
pillow
...
```

**Action:**
- ✅ TensorFlow, numpy, Pillow already in m-project
- ✅ scikit-learn, requests already compatible
- 🔄 Add to m-project: `monai==1.3.0` (for augmentation scripts)
- ✅ Remove Flask, flask-cors (not needed in FastAPI)

---

### **PHASE 5: FRONTEND COMPARISON**

#### **mega-project Frontend**
- Single-file focus: `App.jsx` handles all views
- No routing infrastructure
- API calls to `http://localhost:5000`
- Components: Hero, Upload, Result, RehabDashboard, ExerciseLibrary, RecoveryTracker

#### **m-project/apps Frontend**
- Router-based: `/`, `/auth`, `/dashboard`
- Authentication layer
- API calls to FastAPI backend
- Navbar + Pages structure

#### **Integration Strategy:**
```
Option A: Keep m-project/apps structure (Recommended)
├── Map mega-project components into existing pages
├── Reuse authentication
├── Update API URLs (localhost:5173 → localhost:8000)

Option B: Merge UIs
├── More complex
├── Risk of breaking current functionality
└── Not recommended for production

RECOMMENDATION: Option A
```

---

## 🚀 RECOMMENDED INTEGRATION STEPS (IN ORDER)

### **STEP 1: Setup Directory Structure**
```bash
# Create AI module directory
mkdir -p apps/ai/models

# Copy model file
cp mega-project/stroke_model_resnet50_ensemble.h5 apps/ai/models/

# Verify file integrity
ls -lh apps/ai/models/stroke_model_resnet50_ensemble.h5
```

### **STEP 2: Extract & Create Preprocessing Module**
```bash
# Create preprocessing.py
# Extract from mega-project/app.py:
#   - preprocess_image()
#   - validate_mri()
#   - CONFIDENCE_THRESHOLD constant
#   - Image validation logic
```

### **STEP 3: Update ml_engine.py**
```bash
# Modify apps/api/ml_engine.py:
#   - Import preprocessing functions
#   - Load model with error handling
#   - Implement predict() method
#   - Add MRI validation
#   - Return standardized response
```

### **STEP 4: Update prediction router**
```bash
# Modify apps/api/routers/prediction.py:
#   - Use updated ml_engine.predict()
#   - Keep Gemini integration
#   - Map response to expected format
#   - Handle errors consistently
```

### **STEP 5: Update requirements.txt**
```bash
# Add missing dependencies:
#   - monai (for future dataset augmentation)
#   - scikit-learn (for class weights)
#   - Add version pins for TensorFlow consistency
```

### **STEP 6: Test Integration**
```bash
# 1. Start FastAPI backend
cd apps/api
python -m uvicorn main:app --reload

# 2. Test prediction endpoint
curl -X POST http://localhost:8000/predict -F "file=@test_image.jpg"

# 3. Verify model loading
curl http://localhost:8000/health
```

### **STEP 7: Frontend Updates**
```bash
# Update API_URL in apps/web/src/App.jsx
# Map mega-project components to existing UI
# Test upload workflow end-to-end
```

---

## 📊 COMPARISON TABLE: Integration Methods

| Method | Effort | Risk | Result | Recommendation |
|--------|--------|------|--------|---|
| **Copy-Paste All** | Low (2-3 hrs) | ⚠️ HIGH | Creates duplicate/conflicting code | ❌ Not Recommended |
| **Flask Wrapper** | Medium (4-5 hrs) | ⚠️ MEDIUM | Two backends running | ❌ Inefficient |
| **Hybrid (ML Extract)** | Medium (3-4 hrs) | ✅ LOW | Clean, modular, tested | ✅ **RECOMMENDED** |
| **Complete Rewrite** | High (8-10 hrs) | 🔴 CRITICAL | Start from scratch | ❌ Overkill |

---

## 🎯 HYBRID INTEGRATION: DETAILED WORKFLOW

```
MEGA-PROJECT          EXTRACTION          M-PROJECT/APPS
============================================================
app.py                           ┌──────── ml_engine.py
├─ preprocess_image()       ─────┤─ predict()
├─ validate_mri()           ─────┤─ preprocess_image()
├─ CONFIDENCE_THRESHOLD     ─────┤─ validate_mri()
└─ Model loading logic      ─────┤─ load_model()

MODEL FILE                       │
└─ stroke_model_*.h5        ─────┴──── apps/ai/models/

PREDICTION ROUTER                │
└─ /predict endpoint        ─────┴──── routers/prediction.py
                                       (wrapped in FastAPI)

TRAINING SCRIPTS
├─ train_ensemble_models.py ──── Reference only (optional copy)
├─ preprocess_monai.py      ──── Reference only (optional copy)
└─ train_*.py               ──── Reference only (optional copy)
```

---

## ⚙️ TECHNICAL CONSIDERATIONS

### **Async Compatibility**
- ✅ FastAPI supports background tasks
- ✅ TensorFlow inference is CPU-bound (not I/O)
- ✅ Use `asyncio` for non-blocking uploads
- ⚠️ Model prediction must run in thread pool (TensorFlow is not async-safe)

### **Model Loading Performance**
- ⏱️ ResNet50 ensemble: ~200MB file → ~1-2 sec load time
- 💾 Consider lazy loading (load on first request)
- 🔄 Cache model in memory after first load
- 🔐 Implement thread-safe model access

### **Dependencies Conflicts**
- ✅ TensorFlow versions compatible
- ✅ Both use numpy, Pillow
- ✅ CORS already configured in FastAPI
- 🔄 Verify MONAI compatibility with existing packages

### **Database Integration**
- ✅ ScanRecord model already defined
- ✅ Can store predictions with metadata
- ✅ User association via auth system
- 🔄 Add fields: model_version, confidence_scores

---

## 📈 MIGRATION SUCCESS CRITERIA

✅ Model loads without errors  
✅ Prediction endpoint returns correct format  
✅ Confidence threshold working (0.65)  
✅ MRI validation active  
✅ Gemini integration (if API key present)  
✅ Database stores predictions  
✅ Frontend displays results correctly  
✅ No Flask process running  

---

## 🎬 EXECUTION TIMELINE

| Phase | Task | Duration | Dependency |
|-------|------|----------|-----------|
| 1 | Setup directories + Copy model file | 15 min | None |
| 2 | Extract preprocessing module | 30 min | Phase 1 |
| 3 | Update ml_engine.py | 45 min | Phase 2 |
| 4 | Update prediction router | 30 min | Phase 3 |
| 5 | Update requirements.txt + Test | 20 min | Phase 4 |
| 6 | Frontend integration | 30 min | Phase 5 |
| 7 | End-to-end testing | 20 min | Phase 6 |

**Total Estimated Time: 3-4 hours**

---

## 🚨 RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Model file corruption | Low | Critical | Verify checksum, keep backup |
| Async loading issues | Medium | High | Use ThreadPoolExecutor |
| Dependency conflicts | Medium | Medium | Pin versions in requirements.txt |
| CORS issues | Low | Medium | Test with frontend locally |
| Memory overflow (large files) | Low | Medium | Implement upload size limits |

---

## ✅ NEXT STEPS

1. **Read this analysis** (5 min)
2. **Backup mega-project** (5 min)
3. **Create directory structure** (Phase 1)
4. **Extract preprocessing** (Phase 2)
5. **Test with simple POST request** (Phase 3)
6. **Integrate frontend** (Phase 4)
7. **Full end-to-end testing** (Phase 5)

---

## 📞 QUICK REFERENCE

**Model File:** `stroke_model_resnet50_ensemble.h5` (200MB)  
**Key Functions:** `preprocess_image()`, `validate_mri()`  
**Confidence Threshold:** 0.65 (65% minimum)  
**Classes:** Haemorrhagic, Ischemic, Normal  
**API Framework:** FastAPI (async) + TensorFlow (sync inference)  
**Database:** MongoDB via Beanie ORM  

