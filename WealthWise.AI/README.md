# 🤖 FinGPT Financial AI Services - FastAPI Application

A production-ready **FastAPI application** that provides AI-powered financial advisory services using **real FinGPT models** from AI4Finance Foundation. This application exposes three main categories of financial AI APIs with comprehensive features for financial analysis, recommendations, and goal planning.

## 🎯 **Three Main API Categories**

### 📊 **Category 1: AI Financial Advisor**
- **Personal Financial Advice**: Comprehensive financial recommendations based on user profiles
- **Portfolio Analysis**: Investment portfolio optimization and risk analysis  
- **Risk Assessment**: Financial risk evaluation and mitigation strategies

### 💡 **Category 2: AI Recommendations**
- **Market Insights**: AI-powered market trend analysis and insights
- **News Analysis**: Financial news sentiment analysis and market impact assessment
- **Sector Analysis**: Sector-wise investment recommendations and analysis

### 🎯 **Category 3: AI Finance Goal Planner**
- **Goal Strategy Creation**: Comprehensive financial planning for multiple goals
- **Progress Tracking**: Goal progress monitoring and adjustment recommendations
- **Savings Optimization**: Optimal savings allocation and investment strategies

## 🚀 **Key Features**

✅ **Real FinGPT Integration**: Authentic AI4Finance Foundation models from HuggingFace  
✅ **FastAPI Framework**: Modern, fast, and async web framework  
✅ **Live Market Data**: Yahoo Finance integration with real-time financial data  
✅ **Comprehensive Validation**: Input validation for all data models  
✅ **Rate Limiting**: Built-in rate limiting with sliding window algorithm  
✅ **Authentication**: JWT-based authentication and authorization  
✅ **Structured Logging**: JSON-formatted logging for production monitoring  
✅ **Error Handling**: Graceful error handling with fallback modes  
✅ **Interactive Documentation**: Auto-generated OpenAPI docs  
✅ **Production Ready**: Docker support, health checks, monitoring  

## 📋 **Prerequisites**

- **Python 3.8+** (Python 3.10+ recommended)
- **8GB+ RAM** (16GB+ recommended for full FinGPT models)
- **GPU with 6GB+ VRAM** (optional, for faster AI inference)
- **Internet connection** (for initial model downloads)

## 🛠️ **Installation & Setup**

### 1. **Clone and Setup**
```bash
git clone <repository-url>
cd fingpt-financial-ai-services #Folder Name

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 2. **Install Dependencies**
```bash
# Install all requirements
pip install -r requirements.txt

# For CUDA GPU support (optional)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 3. **Environment Configuration**
```bash
# Copy environment template
cp .env .env

# Edit .env file with your configuration
# Required: Set SECRET_KEY for production
# Optional: Add API keys for enhanced functionality
```

### 4. **Run the Application**
```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at: **http://localhost:8000**

## 📚 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **Homepage**: http://localhost:8000

### **Health Checks**
```bash
# Overall health
GET /health

# Category-specific health
GET /api/v1/advisor/health
GET /api/v1/recommendations/health  
GET /api/v1/planner/health
```

## 🔧 **API Usage Examples**

### **1. Financial Advice API**
```bash
curl -X POST "http://localhost:8000/api/v1/advisor/personal-advice" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "user_id": "user123",
    "age": 35,
    "annual_income": 75000,
    "monthly_expenses": 4000,
    "current_savings": 50000,
    "current_investments": 25000,
    "monthly_savings_capacity": 2000,
    "risk_tolerance": "moderate",
    "employment_status": "employed",
    "investment_experience": 5,
    "family_dependents": 1,
    "has_emergency_fund": true,
    "total_debt": 15000,
    "monthly_debt_payments": 500
  }'
```

### **2. Market Recommendations API**
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/market-insights" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "user_id": "user123",
    "age": 35,
    "annual_income": 75000,
    "risk_tolerance": "moderate",
    "preferred_sectors": ["technology", "healthcare"]
  }' \
  -G -d "symbols=AAPL,MSFT,GOOGL" \
  -G -d "timeframe=1M"
```

### **3. Goal Planning API**
```bash
curl -X POST "http://localhost:8000/api/v1/planner/create-strategy" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "user_id": "user123",
    "age": 35,
    "annual_income": 75000,
    "monthly_savings_capacity": 2000,
    "risk_tolerance": "moderate",
    "goals": [
      {
        "goal_id": "retirement",
        "goal_type": "retirement",
        "goal_name": "Retirement Fund",
        "target_amount": 1000000,
        "current_amount": 25000,
        "target_date": "2055-01-01",
        "priority": 1
      }
    ],
    "total_goal_amount": 1000000
  }'
```

## 🤖 **FinGPT Models Used**

This application integrates with real FinGPT models from AI4Finance Foundation:

### **Primary Models**
- **`FinGPT/fingpt-mt_llama2-7b_lora`**: Multi-task financial analysis and advisory
- **`FinGPT/fingpt-sentiment_llama2-13b_lora`**: Financial sentiment analysis
- **`FinGPT/fingpt-forecaster_dow30_llama2-7b_lora`**: Financial forecasting and planning

### **Model Features**
- **Automatic Download**: Models downloaded from HuggingFace on first run
- **GPU Acceleration**: CUDA support for faster inference
- **Model Caching**: Local caching to avoid re-downloads
- **Fallback Modes**: Graceful degradation when models unavailable

## 🐳 **Docker Deployment**

### **Build and Run**
```bash
# Build image
docker build -t fingpt-financial-ai .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=false \
  -e SECRET_KEY=your-production-key \
  fingpt-financial-ai

# With GPU support
docker run --gpus all -p 8000:8000 fingpt-financial-ai
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  fingpt-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - SECRET_KEY=your-production-key
      - HUGGINGFACE_TOKEN=your-token
    volumes:
      - ./models_cache:/app/models_cache
      - ./logs:/app/logs
```

## 🏗️ **Project Structure**

```
fingpt-financial-ai-services/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
│
├── api/v1/                # API route handlers
│   ├── advisor.py         # Financial advisor endpoints
│   ├── recommendations.py # Recommendations endpoints
│   └── planner.py         # Goal planner endpoints
│
├── models/                # Pydantic data models
│   ├── user_models.py     # User profile and goal models
│   └── response_models.py # API response models
│
├── services/              # Business logic services
│   ├── fingpt_service.py  # FinGPT integration service
│   └── market_data_service.py # Market data integration
│
├── middleware/            # FastAPI middleware
│   └── auth_middleware.py # Authentication middleware
│
├── utils/                 # Utility functions
│   ├── validation.py      # Input validation
│   ├── rate_limiting.py   # Rate limiting utilities
│   └── logging_config.py  # Logging configuration
│
├── config/                # Configuration
│   └── settings.py        # Application settings
│
└── logs/                  # Application logs
    └── fingpt_app.log
```

## ⚡ **Performance & Scaling**

### **Hardware Recommendations**
- **Development**: 8GB RAM, CPU-only inference
- **Production**: 16GB+ RAM, GPU with 8GB+ VRAM
- **High-Traffic**: 32GB+ RAM, multiple GPUs, load balancer

### **Optimization Tips**
- **Enable GPU**: Set CUDA_VISIBLE_DEVICES for GPU acceleration
- **Model Caching**: Models cached after first load (~2-5min initial startup)
- **Rate Limiting**: Prevent abuse with built-in rate limiting
- **Async Operations**: All endpoints use async/await for better concurrency

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Core Settings
DEBUG=false                    # Production: false
SECRET_KEY=256-bit-secret     # Required for production
PORT=8000                     # Server port
WORKERS=4                     # Production workers

# FinGPT Models  
HUGGINGFACE_TOKEN=token       # Optional: for gated models
HF_CACHE_DIR=./models_cache   # Model cache directory

# API Keys (Optional)
ALPHA_VANTAGE_API_KEY=key     # Enhanced market data
FINNHUB_API_KEY=key           # Professional market data  
NEWS_API_KEY=key              # News analysis

# Security & Performance
RATE_LIMIT_ENABLED=true       # Enable rate limiting
RATE_LIMIT_REQUESTS=1000      # Requests per hour
MAX_CONCURRENT_REQUESTS=10    # Concurrent request limit
```

## 🧪 **Testing**

### **Manual Testing**
Visit the interactive documentation at http://localhost:8000/docs to test all endpoints.

### **Automated Testing**
```bash
# Install testing dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 📊 **Monitoring & Observability**

### **Built-in Monitoring**
- **Health Checks**: `/health` endpoint with service status
- **Structured Logging**: JSON-formatted logs for analysis
- **Request Analytics**: Background analytics for usage patterns
- **Performance Metrics**: Response times and success rates

### **Log Analysis**
```bash
# View logs
tail -f fingpt_app.log

# Parse JSON logs
cat fingpt_app.log | jq '.message'

# Filter by level
cat fingpt_app.log | jq 'select(.level == "ERROR")'
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Models Not Loading**
   ```bash
   # Check internet connection and HuggingFace access
   # Verify available RAM/VRAM
   # Review logs: tail -f fingpt_app.log
   ```

2. **Memory Issues**  
   ```bash
   # Use CPU-only mode
   export CUDA_VISIBLE_DEVICES=""

   # Reduce concurrent requests
   export MAX_CONCURRENT_REQUESTS=2
   ```

3. **API Authentication Errors**
   ```bash
   # In development, DEBUG=true enables mock authentication
   # In production, implement proper JWT token validation
   ```

4. **Rate Limiting**
   ```bash
   # Disable for testing
   export RATE_LIMIT_ENABLED=false

   # Adjust limits
   export RATE_LIMIT_REQUESTS=5000
   ```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 **Acknowledgments**

- **AI4Finance Foundation** for FinGPT models
- **HuggingFace** for model hosting and transformers library
- **Meta** for LLaMA base models  
- **Yahoo Finance** for financial data APIs
- **FastAPI** for the excellent web framework

## 📧 **Support**

- **Documentation**: Visit `/docs` for interactive API documentation
- **Issues**: Create GitHub issues for bugs and feature requests  
- **Logs**: Check `fingpt_app.log` for detailed error information

---

**Built with ❤️ using FinGPT, FastAPI, and modern AI technologies**

🚀 **Ready for production deployment with real FinGPT AI capabilities!**
