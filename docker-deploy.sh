#!/bin/bash

# Docker Deployment Helper Script for Brain Stroke Detection AI

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Brain Stroke Detection - Docker Deployment Helper${NC}\n"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

print_status "Docker is installed: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed."
    exit 1
fi

print_status "Docker Compose is installed: $(docker-compose --version)"

# Main menu
echo -e "\n${YELLOW}What would you like to do?${NC}\n"
echo "1. Build and start all services (development)"
echo "2. Build and start all services (production)"
echo "3. Stop all services"
echo "4. View logs"
echo "5. Restart services"
echo "6. Clean up everything (remove all containers and data)"
echo "7. Check service status"
echo "8. Open logs for specific service"

read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Starting development environment...${NC}\n"
        docker-compose build
        docker-compose up -d
        print_status "Development environment started!"
        echo -e "\n${GREEN}Access the application:${NC}"
        echo "  Frontend: http://localhost"
        echo "  Backend API: http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        ;;
    2)
        echo -e "\n${YELLOW}Starting production environment...${NC}\n"
        
        # Check if .env exists
        if [ ! -f .env ]; then
            print_warning ".env file not found. Creating from example..."
            cp .env.example .env
            print_warning "Please edit .env with production values before running again!"
            exit 1
        fi
        
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        print_status "Production environment started!"
        echo -e "\n${YELLOW}Next steps:${NC}"
        echo "1. Update .env with real API keys"
        echo "2. Configure your domain/SSL certificate"
        echo "3. Review docker-compose.prod.yml settings"
        ;;
    3)
        echo -e "\n${YELLOW}Stopping all services...${NC}\n"
        docker-compose down
        print_status "All services stopped"
        ;;
    4)
        echo -e "\n${YELLOW}Viewing logs (Ctrl+C to exit)...${NC}\n"
        docker-compose logs -f
        ;;
    5)
        echo -e "\n${YELLOW}Restarting services...${NC}\n"
        docker-compose restart
        print_status "Services restarted"
        ;;
    6)
        echo -e "\n${RED}⚠️  WARNING: This will delete all containers, images, and data!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            docker-compose down -v
            docker system prune -f
            print_status "Cleanup completed"
        else
            echo "Cleanup cancelled"
        fi
        ;;
    7)
        echo -e "\n${YELLOW}Service Status:${NC}\n"
        docker-compose ps
        ;;
    8)
        echo -e "\n${YELLOW}Available services:${NC}"
        echo "1. backend"
        echo "2. frontend"
        echo "3. mongodb"
        read -p "Enter service name: " service
        docker-compose logs -f "$service"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Done!${NC}\n"
