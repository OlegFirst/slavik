#!/bin/bash

echo "🎛️ BCM Platform Setup & Launch"
echo "=============================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker and try again."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18 or higher. Current: $(node -v)"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Show available options
echo "🚀 Choose what to launch:"
echo ""
echo "1. 👤 User Platform Only (port 5173)"
echo "2. 🎛️ Admin Panel Only (port 3001)"  
echo "3. 🔗 Both Platforms"
echo "4. 🐳 Start Backend Services"
echo "5. 📊 Full Stack (Backend + Frontend)"
echo "6. ❌ Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting User Platform..."
        cd /Users/MD/ISO-22301/frontend/web_portal_enhanced
        chmod +x start-user-platform.sh
        ./start-user-platform.sh
        ;;
    2)  
        echo ""
        echo "🚀 Starting Admin Panel..."
        cd /Users/MD/ISO-22301/frontend/admin_panel
        chmod +x start-admin.sh 2>/dev/null || echo "Creating admin start script..."
        
        # Create admin start script if it doesn't exist
        cat > start-admin.sh << 'EOF'
#!/bin/bash
echo "🎛️ Starting BCM Admin Panel..."
echo "=============================="

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🌐 Admin Panel will be available at:"
echo "   http://localhost:3001"
echo ""

npm run dev
EOF
        chmod +x start-admin.sh
        ./start-admin.sh
        ;;
    3)
        echo ""
        echo "🚀 Starting Both Platforms..."
        
        # Start admin panel in background
        echo "Starting Admin Panel..."
        cd /Users/MD/ISO-22301/frontend/admin_panel
        chmod +x start-admin.sh 2>/dev/null || {
            cat > start-admin.sh << 'EOF'
#!/bin/bash
if [ ! -d "node_modules" ]; then npm install; fi
npm run dev
EOF
            chmod +x start-admin.sh
        }
        nohup ./start-admin.sh > admin.log 2>&1 &
        ADMIN_PID=$!
        
        sleep 3
        echo "✅ Admin Panel started (PID: $ADMIN_PID)"
        
        # Start user platform
        echo "Starting User Platform..."
        cd /Users/MD/ISO-22301/frontend/web_portal_enhanced
        chmod +x start-user-platform.sh
        
        # Function to cleanup background processes
        cleanup() {
            echo ""
            echo "🛑 Shutting down platforms..."
            kill $ADMIN_PID 2>/dev/null
            exit 0
        }
        trap cleanup INT
        
        ./start-user-platform.sh
        ;;
    4)
        echo ""
        echo "🐳 Starting Backend Services..."
        cd /Users/MD/ISO-22301
        
        if [ -f "docker-compose.yml" ]; then
            echo "📦 Starting Docker services..."
            docker-compose up -d
            
            echo ""
            echo "⏳ Waiting for services to be ready..."
            sleep 10
            
            echo ""
            echo "✅ Backend services started!"
            echo ""
            echo "🌐 Available services:"
            echo "   • BCM Core (Odoo):    http://localhost:8069"
            echo "   • AI Orchestrator:    http://localhost:8000" 
            echo "   • BIA Engine:         http://localhost:8082"
            echo "   • Document Processor: http://localhost:8083"
            echo "   • EventBus:           http://localhost:8001"
            echo "   • Grafana:            http://localhost:3000"
            echo "   • Prometheus:         http://localhost:9090"
            echo ""
            echo "💡 Use docker-compose logs -f to view logs"
            echo "💡 Use docker-compose down to stop services"
        else
            echo "❌ docker-compose.yml not found in /Users/MD/ISO-22301"
            echo "💡 Please check if you're in the correct directory"
        fi
        ;;
    5)
        echo ""
        echo "🚀 Starting Full Stack..."
        cd /Users/MD/ISO-22301
        
        if [ -f "docker-compose.yml" ]; then
            echo "🐳 Starting backend services..."
            docker-compose up -d
            
            echo "⏳ Waiting for services to be ready..."
            sleep 15
            
            echo "✅ Backend services ready!"
            
            # Start admin panel in background
            echo "🎛️ Starting Admin Panel..."
            cd /Users/MD/ISO-22301/frontend/admin_panel
            chmod +x start-admin.sh 2>/dev/null || {
                cat > start-admin.sh << 'EOF'
#!/bin/bash
if [ ! -d "node_modules" ]; then npm install; fi
npm run dev
EOF
                chmod +x start-admin.sh
            }
            nohup ./start-admin.sh > admin.log 2>&1 &
            ADMIN_PID=$!
            
            sleep 3
            echo "✅ Admin Panel started (PID: $ADMIN_PID)"
            
            # Start user platform
            echo "👤 Starting User Platform..."
            cd /Users/MD/ISO-22301/frontend/web_portal_enhanced
            chmod +x start-user-platform.sh
            
            # Cleanup function
            cleanup() {
                echo ""
                echo "🛑 Shutting down full stack..."
                kill $ADMIN_PID 2>/dev/null
                cd /Users/MD/ISO-22301
                docker-compose down
                exit 0
            }
            trap cleanup INT
            
            echo ""
            echo "🌐 Full Stack URLs:"
            echo "   • User Platform:   http://localhost:5173"
            echo "   • Admin Panel:     http://localhost:3001"
            echo "   • BCM Core:        http://localhost:8069"
            echo "   • AI Orchestrator: http://localhost:8000"
            echo "   • Grafana:         http://localhost:3000"
            echo ""
            
            ./start-user-platform.sh
        else
            echo "❌ docker-compose.yml not found in /Users/MD/ISO-22301"
            exit 1
        fi
        ;;
    6)
        echo "👋 Exiting..."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
