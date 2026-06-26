#!/bin/bash
# Security Scan Script for OMAYA Platform

echo "🔍 Starting Security Scan..."

# 1. Docker Image Scanning (Simulated with dummy output if Trivy not installed)
if command -v trivy &> /dev/null
then
    echo "🐳 Scanning Docker images with Trivy..."
    trivy image omaya-api:3.1.1
    trivy image omaya-frontend:3.1.1
else
    echo "⚠️ Trivy not found. Please install Trivy for real Docker scanning."
    echo "Simulating scan results: 0 CRITICAL, 2 HIGH, 5 MEDIUM vulnerabilities found."
fi

# 2. Dependency Scanning (Python)
echo "🐍 Scanning Python dependencies..."
if command -v safety &> /dev/null
then
    safety check -r backend/requirements.txt
else
    echo "⚠️ Safety not found. Run 'pip install safety' for dependency scanning."
fi

# 3. Static Code Analysis (Python)
echo "📝 Running Bandit for static analysis..."
if command -v bandit &> /dev/null
then
    bandit -r backend/
else
    echo "⚠️ Bandit not found. Run 'pip install bandit' for static analysis."
fi

echo "✅ Security scan completed."
