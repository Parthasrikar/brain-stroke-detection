# 🐳 Docker Deployment Guide - Brain Stroke Detection AI

## 📋 Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Docker Compose (included with Docker Desktop)
- ML models downloaded in `apps/ai/models/`
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/apikey))

---

## 🚀 Quick Start (5 minutes)

### Step 1: Setup Environment Variables
```bash
cd /Users/gparthasrikar/Documents/m-project

# Copy the example env file
cp .env.example .env

# Edit .env with your actual API keys
nano .env
```

Update these values in `.env`:
```
GEMINI_API_KEY=your_actual_gemini_api_key
JWT_SECRET=set_a_strong_random_secret_key
```

### Step 2: Build & Run with Docker Compose
```bash
# Build all images (backend, frontend, MongoDB)
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 3: Access the Application
- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017 (username: root, password: password123)

---

## 📦 Service Architecture

```
┌─────────────────────────────────────────────┐
│         React Frontend (Port 80)             │
│         Served by Nginx (Production Build)   │
└──────────────────┬──────────────────────────┘
                   │
                   │ HTTP Requests
                   ▼
┌─────────────────────────────────────────────┐
│    FastAPI Backend (Port 8000)              │
│    ├─ /auth - Authentication                │
│    ├─ /predict - Stroke Detection           │
│    └─ /chatbot - AI Rehabilitation          │
└──────────────────┬──────────────────────────┘
                   │
                   │ Database Connections
                   ▼
┌─────────────────────────────────────────────┐
│         MongoDB (Port 27017)                 │
│         Persistent Data Volume               │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Clean up everything (⚠️ removes data)
```bash
docker-compose down -v
```

### Access MongoDB shell
```bash
docker exec -it brain_stroke_mongodb mongosh -u root -p password123
```

---

## 🔧 Customization

### Change Ports
Edit `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "8080:80"    # Access at http://localhost:8080
  backend:
    ports:
      - "9000:8000"  # Access at http://localhost:9000
```

### Change MongoDB Credentials
Edit `docker-compose.yml`:
```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: youruser
  MONGO_INITDB_ROOT_PASSWORD: yourpassword
```

Also update in `.env`:
```
MONGO_URL=mongodb://youruser:yourpassword@mongodb:27017
```

### Enable GPU for ML Model
Add to `docker-compose.yml` backend service:
```yaml
runtime: nvidia
environment:
  NVIDIA_VISIBLE_DEVICES: all
```

---

## 📊 File Structure

```
/Users/gparthasrikar/Documents/m-project/
├── Dockerfile.backend          # Backend Python image
├── Dockerfile.frontend         # Frontend Node image
├── docker-compose.yml          # Multi-container orchestration
├── nginx.conf                  # Nginx configuration
├── .env.example                # Environment variables template
├── .dockerignore                # Files to exclude from images
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── ...
│   ├── web/                    # React frontend
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   └── ...
│   └── ai/
│       └── models/
│           └── stroke_model_resnet50_ensemble.h5   # Large model file
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :80

# If needed, change ports in docker-compose.yml
```

### Container won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild first
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### MongoDB connection failed
```bash
# Wait for MongoDB to be healthy
docker-compose logs mongodb

# Verify it's running
docker exec brain_stroke_mongodb mongosh -u root -p password123 --eval "db.version()"
```

### Frontend not loading (404s)
- Ensure backend is running: `docker-compose ps`
- Check CORS settings in `main.py`
- Verify nginx.conf API proxy settings

---

## 🚢 Production Considerations

### Security
1. **Change default passwords** in `.env`
   ```bash
   JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **Use environment-specific configs**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

3. **Enable HTTPS** with Let's Encrypt (via nginx proxy)

### Performance
1. **Use `.dockerignore`** to reduce image size (already configured)
2. **Build with optimizations**:
   ```bash
   docker build --build-arg NODE_ENV=production -t backend-prod Dockerfile.backend
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats
   ```

### Persistence
- MongoDB data persists in `mongodb_data` volume
- Backup before deploying updates:
  ```bash
  docker exec brain_stroke_mongodb mongodump --out /backup
  ```

---

## 📈 Scaling Options

### Using Kubernetes
For production with high traffic:
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml -o k8s/
kubectl apply -f k8s/
```

### Multiple replicas
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      replicas: 3
```

---

## 🔗 Useful Links
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [React Vite Docker](https://vitejs.dev/guide/build.html)
- [MongoDB Docker](https://hub.docker.com/_/mongo)

---

## ✅ Verification Checklist

After deployment, verify:
- [ ] Frontend loads at http://localhost
- [ ] Backend API responds at http://localhost:8000/docs
- [ ] Hospital Dashboard is accessible
- [ ] Upload and predict works end-to-end
- [ ] MongoDB data persists after container restart
- [ ] Logs show no errors: `docker-compose logs`
