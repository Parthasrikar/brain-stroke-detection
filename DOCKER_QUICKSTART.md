# 🚀 Quick Start: Docker Deployment

## ⚡ 5-Minute Setup

### 1️⃣ Prerequisites Check
```bash
# Verify Docker is installed
docker --version

# Verify Docker Compose is installed
docker-compose --version
```

### 2️⃣ Use the Helper Script (Easiest)
```bash
cd /Users/gparthasrikar/Documents/m-project

# Run the deployment helper
./docker-deploy.sh

# Choose option 1 for development
```

**OR** Manually:

### 2️⃣ Manual Setup

**Copy environment template:**
```bash
cp .env.example .env
```

**Edit your API keys** (optional for testing):
```bash
nano .env
# Update:
# - GEMINI_API_KEY (get from https://aistudio.google.com/apikey)
# - JWT_SECRET (or keep default for testing)
```

**Build and start:**
```bash
docker-compose build
docker-compose up -d
```

### 3️⃣ Access Your Application
```
🌐 Frontend:    http://localhost
📚 API Docs:    http://localhost:8000/docs
🔧 Backend API: http://localhost:8000
```

### 4️⃣ Verify Everything Works
```bash
# Check service status
docker-compose ps

# Should show 3 services all "Up":
# - brain_stroke_backend
# - brain_stroke_frontend
# - brain_stroke_mongodb

# View logs
docker-compose logs -f
```

---

## 📁 What Was Created

| File | Purpose |
|------|---------|
| `Dockerfile.backend` | Python FastAPI container |
| `Dockerfile.frontend` | React Vite + Nginx container |
| `docker-compose.yml` | Multi-container orchestration |
| `docker-compose.prod.yml` | Production overrides |
| `nginx.conf` | Nginx web server config |
| `.env.example` | Environment variables template |
| `.dockerignore` | Exclude large files from build |
| `docker-deploy.sh` | Interactive deployment script |
| `DOCKER_DEPLOYMENT.md` | Complete deployment guide |

---

## 🎯 Common Tasks

### Stop everything
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Restart after code changes
```bash
docker-compose up -d --build
```

### Clean up (⚠️ removes all data)
```bash
docker-compose down -v
```

---

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change port in docker-compose.yml (e.g., 8000 → 8001)
```

**Backend won't connect to MongoDB?**
```bash
# Wait 10 seconds and try again
# MongoDB takes time to initialize

docker-compose logs mongodb
```

**Frontend showing 404?**
```bash
# Ensure backend is running
docker-compose ps

# Check backend is responsive
curl http://localhost:8000/docs
```

---

## 📚 Full Documentation
See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for comprehensive guide including:
- Architecture overview
- All command reference
- Customization options
- Production setup
- Kubernetes deployment
- Troubleshooting

---

## ✅ Next Steps
1. ✓ Docker files created
2. → Run `./docker-deploy.sh` to start
3. → Test at http://localhost
4. → View API docs at http://localhost:8000/docs
5. → Read DOCKER_DEPLOYMENT.md for advanced setup

**Ready?** Run:
```bash
./docker-deploy.sh
```
