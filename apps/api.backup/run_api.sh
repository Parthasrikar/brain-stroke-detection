# Navigate to project root (assuming script is in apps/api/)
cd "$(dirname "$0")/../.."
source apps/api/venv/bin/activate
# Run module from root to resolve 'apps.api' imports
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
