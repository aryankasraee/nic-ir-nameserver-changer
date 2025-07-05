#!/bin/bash

echo "Cleaning up Docker containers and images..."

# Stop and remove containers
docker compose down

# Remove images (optional)
read -p "Do you want to remove Docker images? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi $(docker images "nic-ir-changer*" -q) 2>/dev/null || true
    docker system prune -f
fi

echo "Cleanup completed!"
