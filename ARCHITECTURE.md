# Healthcare Chatbot Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │   Next.js    │         │  Streamlit   │                     │
│  │   Frontend   │         │  Chat App    │                     │
│  │  (Your App)  │         │  (Existing)  │                     │
│  └──────┬───────┘         └──────┬───────┘                     │
│         │                        │                              │
└─────────┼────────────────────────┼──────────────────────────────┘
          │                        │
          │ HTTP/REST              │ Local
          │                        │
┌─────────▼────────────────────────▼──────────────────────────────┐
│                         API LAYER                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (NEW)                        │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Endpoints:                                         │  │  │
│  │  │  • POST /chat          - Main chat endpoint        │  │  │
│  │  │  • GET  /health        - Health check              │  │  │
│  │  │  • GET  /patient/:id   - Patient context           │  │  │
│  │  │  • GET  /docs          - API documentation         │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Middleware:                                        │  │  │
│  │  │  • CORS Handler                                     │  │  │
│  │  │  • Error Handler                                    │  │  │
│  │  │  • Request Validator (Pydantic)                     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      AGENT LAYER                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            LangGraph Agent Workflow                        │ │
│  │                                                            │ │
│  │  ┌──────────────┐      ┌──────────────┐                  │ │
│  │  │   Node 1:    │      │   Node 2:    │                  │ │
│  │  │   Fetch      │─────▶│   Generate   │                  │ │
│  │  │   Context    │      │   Response   │                  │ │
│  │  └──────┬───────┘      └──────┬───────┘                  │ │
│  │         │                     │                           │ │
│  │         │                     │                           │ │
│  └─────────┼─────────────────────┼───────────────────────────┘ │
│            │                     │                             │
└────────────┼─────────────────────┼─────────────────────────────┘
             │                     │
             │                     │
        ┌────┴─────┐          ┌───┴────┐
        │          │          │        │
        ▼          ▼          ▼        │
┌────────────┬────────────┐  ┌────────┴──────┐
│            │            │  │               │
│  Supabase  │  Ethereum  │  │  OpenAI GPT-4 │
│  Database  │ Blockchain │  │      LLM      │
│            │            │  │               │
└────────────┴────────────┘  └───────────────┘
     DATA SOURCES                  AI MODEL
```

## Request Flow

```
1. User Input
   │
   ├─▶ Frontend (Next.js)
   │   └─▶ HTTP POST /chat
   │       └─▶ { user_id, message, thread_id }
   │
2. API Layer (FastAPI)
   │
   ├─▶ Request Validation (Pydantic)
   │   └─▶ Validate user_id, message
   │
   ├─▶ Invoke LangGraph Agent
   │   └─▶ Pass state: { messages, user_id, patient_context }
   │
3. Agent Workflow (LangGraph)
   │
   ├─▶ Node 1: Fetch Patient Context
   │   ├─▶ Query Supabase (Name, Age, Email)
   │   ├─▶ Query Ethereum (Medical History, Medications)
   │   └─▶ Merge data into patient_context
   │
   ├─▶ Node 2: Generate Response
   │   ├─▶ Build dynamic system prompt
   │   │   └─▶ Include patient context
   │   ├─▶ Invoke GPT-4 with prompt + user message
   │   └─▶ Receive personalized response
   │
4. Response Flow
   │
   ├─▶ Agent returns final state
   │   └─▶ { response, user_id, thread_id, patient_context }
   │
   ├─▶ FastAPI formats response
   │   └─▶ JSON with ChatResponse model
   │
   └─▶ Return to Frontend
       └─▶ Display to user
```

## Data Flow Diagram

```
┌─────────────┐
│    User     │
│   Message   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌───────────────────────────────┐  │
│  │  1. Validate Request          │  │
│  │  2. Extract user_id & message │  │
│  │  3. Generate thread_id        │  │
│  └───────────┬───────────────────┘  │
└──────────────┼──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      LangGraph State Machine         │
│                                      │
│  State = {                           │
│    messages: [],                     │
│    user_id: "...",                   │
│    patient_context: {},              │
│    response: ""                      │
│  }                                   │
└───────────┬──────────────────────────┘
            │
            ▼
     ┌──────────────┐
     │  Node 1:     │
     │  Context     │
     │  Fetcher     │
     └──────┬───────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌──────────┐
│Supabase │    │Ethereum  │
│  Query  │    │  Query   │
└────┬────┘    └────┬─────┘
     │              │
     └──────┬───────┘
            │
            ▼
    patient_context = {
      name: "Jane Doe",
      age: 45,
      medical_history: "...",
      medications: [...],
      diagnoses: [...]
    }
            │
            ▼
     ┌──────────────┐
     │  Node 2:     │
     │  Response    │
     │  Generator   │
     └──────┬───────┘
            │
            ▼
    system_prompt = """
    You are a medical assistant.
    Patient: {name}, Age: {age}
    History: {medical_history}
    ...
    """
            │
            ▼
      ┌─────────┐
      │ GPT-4   │
      │ OpenAI  │
      └────┬────┘
           │
           ▼
    AI Response:
    "Based on your Type 2 Diabetes..."
           │
           ▼
┌──────────────────────┐
│   Final State        │
│  {                   │
│    response: "...",  │
│    user_id: "...",   │
│    patient_context   │
│  }                   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Format as JSON      │
│  ChatResponse Model  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Return to Frontend  │
└──────────────────────┘
```

## Component Responsibilities

### Frontend (Next.js)
- User interface
- Authentication (Supabase Auth)
- Session management
- API calls to backend

### Backend (FastAPI)
- REST API endpoints
- Request validation
- CORS handling
- Error management
- Agent orchestration

### Agent (LangGraph)
- Workflow orchestration
- State management
- Context aggregation
- Response generation

### Data Sources
- **Supabase**: Patient demographics, contact info
- **Ethereum**: Medical records, prescriptions, lab results

### AI Model
- **GPT-4**: Natural language understanding and generation
- Personalized medical advice
- Context-aware responses

## Security Flow

```
┌──────────────┐
│   Frontend   │
│   (Next.js)  │
└──────┬───────┘
       │
       │ JWT Token (from Supabase Auth)
       │
       ▼
┌──────────────────────┐
│  Backend API         │
│  ┌────────────────┐  │
│  │ Verify JWT     │  │  ← Check Supabase token
│  └────────┬───────┘  │
│           │          │
│  ┌────────▼───────┐  │
│  │ Extract        │  │
│  │ user_id        │  │
│  └────────┬───────┘  │
└───────────┼──────────┘
            │
            ▼
     Proceed with request
```

## Error Handling Flow

```
Error Occurs
    │
    ├─▶ Validation Error (Pydantic)
    │   └─▶ Return 400 Bad Request
    │
    ├─▶ Authentication Error
    │   └─▶ Return 401 Unauthorized
    │
    ├─▶ Data Fetch Error (Supabase/Web3)
    │   └─▶ Use fallback/mock data
    │   └─▶ Log warning
    │   └─▶ Continue with available data
    │
    ├─▶ LLM Error (OpenAI)
    │   └─▶ Return generic error message
    │   └─▶ Log error details
    │   └─▶ Return 500 Internal Server Error
    │
    └─▶ Unexpected Error
        └─▶ Global exception handler
        └─▶ Return 500 with safe error message
        └─▶ Log full stack trace
```

## Caching Strategy

```
Request arrives
    │
    ▼
Check Cache (user_id + endpoint)
    │
    ├─▶ Cache Hit (< 5 minutes old)
    │   └─▶ Return cached data
    │
    └─▶ Cache Miss
        ├─▶ Fetch from Supabase/Ethereum
        ├─▶ Store in cache (TTL: 5 minutes)
        └─▶ Return fresh data
```

## Deployment Architecture

```
┌────────────────────────────────────────┐
│           Load Balancer                │
│        (Cloud Provider)                │
└───────────┬────────────────────────────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌─────────┐
│ API     │    │ API     │
│ Instance│    │ Instance│
│ 1       │    │ 2       │
└────┬────┘    └────┬────┘
     │              │
     └──────┬───────┘
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
┌─────────┐    ┌──────────┐
│ Redis   │    │PostgreSQL│
│ Cache   │    │ History  │
└─────────┘    └──────────┘
```

---

This architecture ensures:
- ✅ Scalability (horizontal scaling)
- ✅ Performance (caching, efficient queries)
- ✅ Reliability (error handling, fallbacks)
- ✅ Security (validation, authentication)
- ✅ Maintainability (modular design)
