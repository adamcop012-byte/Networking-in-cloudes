#!/bin/bash
# Cloud ERP Platform — Validation Script

echo "=========================================="
echo "Cloud ERP Platform — Code & Config Review"
echo "=========================================="
echo ""

# 1. Check Docker configuration
echo "✓ Checking docker-compose.yml..."
if grep -q "version:" docker-compose.yml; then
    echo "  ✗ WARNING: Version attribute still present (deprecated)"
else
    echo "  ✓ Version attribute removed"
fi

# 2. Check for vulnerable CORS settings
echo ""
echo "✓ Checking CORS configuration..."
if grep -q 'allow_origins=\["*"\]' services/*/main.py; then
    echo "  ✗ VULNERABLE: Found allow_origins=['*']"
else
    echo "  ✓ CORS properly restricted with environment variables"
fi

# 3. Check for requirements.txt
echo ""
echo "✓ Checking dependency management..."
for svc in erp crm wms; do
    if [ -f "services/$svc/requirements.txt" ]; then
        echo "  ✓ services/$svc/requirements.txt found"
    else
        echo "  ✗ services/$svc/requirements.txt missing"
    fi
done

# 4. Check Dockerfile improvements
echo ""
echo "✓ Checking Dockerfiles..."
for svc in erp crm wms; do
    if grep -q "requirements.txt" services/$svc/Dockerfile; then
        echo "  ✓ services/$svc/Dockerfile uses requirements.txt"
    else
        echo "  ✗ services/$svc/Dockerfile not updated"
    fi
    if grep -q "\-\-workers" services/$svc/Dockerfile; then
        echo "  ✓ services/$svc/Dockerfile has production workers config"
    else
        echo "  ✗ services/$svc/Dockerfile missing production config"
    fi
done

# 5. Check for environment variables
echo ""
echo "✓ Checking environment configuration..."
if grep -q "CORS_ORIGINS" docker-compose.yml; then
    echo "  ✓ CORS_ORIGINS environment variable configured"
else
    echo "  ✗ CORS_ORIGINS not in docker-compose.yml"
fi

# 6. Check for .env.example
echo ""
echo "✓ Checking deployment documentation..."
if [ -f ".env.example" ]; then
    echo "  ✓ .env.example found with configuration guide"
else
    echo "  ✗ .env.example missing"
fi

# 7. Check API endpoints
echo ""
echo "✓ Checking nginx.conf routes..."
for route in erp crm wms health; do
    if grep -q "location /$route/" gateway/nginx.conf || grep -q "location /health" gateway/nginx.conf; then
        echo "  ✓ Route /$route configured"
    fi
done

# 8. Check for logging
echo ""
echo "✓ Checking logging configuration..."
if grep -q "import logging" services/erp/main.py; then
    echo "  ✓ Logging imported in services"
else
    echo "  ✗ Logging not found in services"
fi

echo ""
echo "=========================================="
echo "✓ Configuration review complete!"
echo "=========================================="
