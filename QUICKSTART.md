# Quick Start Guide - Healthcare Chatbot Backend

This guide will get your production backend up and running in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (for GPT-4)
- Supabase account (optional, for production)
- Ethereum node access (optional, for blockchain features)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install all dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env` and add your API keys:

```env
# Minimum required for testing (FREE!)
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.2

# Optional (use OpenAI instead)
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4-turbo-preview

# Optional (use mock data if not set)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/your-project-id
```

### 3. Start the Backend Server

**Option A: Using PowerShell Script (Recommended)**

```bash
.\run_backend.ps1
```

**Option B: Direct Python**

```bash
python backend_api.py
```

**Option C: Using Uvicorn**

```bash
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "message": "Healthcare Chatbot API is running",
  "version": "1.0.0"
}
```

### 5. Test the API

**Option A: Using the Test Script**

```bash
python test_backend.py
```

**Option B: Using curl**

```bash
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"patient-123\",\"message\":\"What should I eat for diabetes?\"}"
```

**Option C: Using the Interactive Docs**

1. Go to http://localhost:8000/docs
2. Click on `POST /chat`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "user_id": "patient-123",
     "message": "What exercises are good for Type 2 Diabetes?"
   }
   ```
5. Click "Execute"

### 6. Test Response

You should get a response like:

```json
{
  "response": "Based on your Type 2 Diabetes diagnosis, I recommend...",
  "user_id": "patient-123",
  "thread_id": "thread-patient-123-abc123",
  "patient_context": {
    "name": "Jane Doe",
    "age": 45,
    "medical_history": "Type 2 Diabetes diagnosed in 2020",
    "medications": ["Metformin 500mg twice daily"]
  }
}
```

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install fastapi uvicorn
```

### Issue 2: "Google API key not found"

**Solution:**
1. Make sure `.env` file exists in the project root
2. Verify `GOOGLE_API_KEY=your-key-here` is set correctly
3. Get a free API key from https://makersuite.google.com/app/apikey
4. Restart the server after updating `.env`

### Issue 3: "Port 8000 is already in use"

**Solution:**
```bash
# Change port in .env
API_PORT=8001

# Or specify port when running
uvicorn backend_api:app --port 8001
```

### Issue 4: CORS errors when calling from frontend

**Solution:**
Add your frontend URL to `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Next Steps

### For Development
1. Test with `test_backend.py`
2. Customize the system prompt in `agent_graph.py`
3. Add more medical knowledge to the LLM context

### For Production
1. Set up Supabase database (see README)
2. Configure Ethereum blockchain (see README)
3. Deploy to cloud (Railway, Render, or AWS)
4. Set up monitoring and logging
5. Enable rate limiting
6. Add authentication

### For Frontend Integration

**Next.js Example:**

```typescript
// app/api/chat/route.ts
export async function POST(request: Request) {
  const { userId, message } = await request.json();
  
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      message: message
    })
  });
  
  return Response.json(await response.json());
}
```

**React Hook:**

```typescript
// hooks/useHealthChat.ts
export function useHealthChat() {
  const [loading, setLoading] = useState(false);
  
  const sendMessage = async (userId: string, message: string) => {
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, message })
      });
      return await res.json();
    } finally {
      setLoading(false);
    }
  };
  
  return { sendMessage, loading };
}
```

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/chat` | POST | Send message, get response |
| `/patient/{user_id}` | GET | Get patient context |
| `/docs` | GET | Interactive API documentation |
| `/redoc` | GET | Alternative API documentation |

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-4 |
| `OPENAI_MODEL` | No | gpt-4-turbo-preview | Model to use |
| `LLM_TEMPERATURE` | No | 0.3 | Response creativity (0-1) |
| `API_HOST` | No | 0.0.0.0 | Server host |
| `API_PORT` | No | 8000 | Server port |
| `SUPABASE_URL` | No | - | Supabase project URL |
| `SUPABASE_KEY` | No | - | Supabase anon key |
| `WEB3_PROVIDER_URL` | No | - | Ethereum node URL |
| `ALLOWED_ORIGINS` | No | * | CORS allowed origins |

## Support

- Check the main [README.md](README.md) for detailed documentation
- Review API docs at `/docs` when server is running
- Run `test_backend.py` to verify everything works

## Success Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file created with OPENAI_API_KEY
- [ ] Backend server starts without errors
- [ ] /health endpoint returns "healthy"
- [ ] /chat endpoint responds to test messages
- [ ] API documentation accessible at /docs
- [ ] test_backend.py runs successfully

---

**You're all set! 🎉**

The backend is now ready for integration with your Next.js frontend or can be used standalone for testing and development.
