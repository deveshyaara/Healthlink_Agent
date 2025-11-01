# Health Agent Chat - AI-Powered Healthcare Communication System

A LangGraph-based AI agent designed to interact with patients, provide healthcare suggestions, and escalate critical cases to healthcare providers. Built with Google's Gemini AI and Streamlit for an intuitive chat interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Future Integration: Blockchain Data via API](#future-integration-blockchain-data-via-api)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements an intelligent healthcare communication agent that:
- Understands patient queries and recognizes intent
- Fetches patient context (currently mocked, ready for blockchain integration)
- Generates empathetic, context-aware responses using Google Gemini AI
- Automatically escalates critical cases to healthcare providers
- Maintains conversation history for better context

## ✨ Features

- **Intent Recognition**: Automatically classifies user queries (suggestions, information requests, general chat)
- **Context-Aware Responses**: Uses patient data to provide personalized suggestions
- **Smart Escalation**: Detects critical keywords and escalates to healthcare providers
- **Chat History**: Maintains conversation context across interactions
- **User-Friendly Interface**: Built with Streamlit for easy deployment
- **Extensible Architecture**: Ready for blockchain and external API integration

## 🏗️ Architecture

The agent follows a multi-node workflow using LangGraph:

```
User Input → Intent Recognition → Context Fetching → LLM Processing → 
Escalation Check → Response Generation → END
```

### Node Description

1. **receive_query**: Ingests user input and recognizes intent
2. **fetch_context**: Retrieves patient context (currently mocked)
3. **llm_suggest**: Generates AI-powered suggestions using Gemini
4. **escalate_if_needed**: Checks for critical conditions requiring provider attention
5. **save_and_respond**: Saves interaction and returns response

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Agent
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install langchain-google-genai langchain-core langgraph streamlit python-dotenv
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Get your Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create or select a project
   - Generate an API key
   - Add it to your `.env` file

## 💻 Usage

### Running the Chat Interface

```bash
streamlit run chat_app.py
```

The application will open in your default browser at `http://localhost:8501`

### Running the Agent Standalone

```bash
python agent.py
```

This runs the agent with a test query for debugging purposes.

### Example Interactions

**Patient Query:**
```
User: "Can you give me a suggestion for my diet?"
Agent: "Based on your Type 2 Diabetes diagnosis and HbA1c level of 7.2%, 
        I recommend focusing on low-glycemic foods..."
```

**Escalation Scenario:**
```
User: "I'm experiencing severe pain in my chest"
Agent: [Provides immediate guidance while escalating to healthcare provider]
System: !!! ESCALATION TRIGGERED !!!
```

## 📁 Project Structure

```
Agent/
│
├── agent.py              # Core LangGraph agent implementation
├── chat_app.py           # Streamlit web interface
├── .env                  # Environment variables (create this)
├── README.md             # This file
└── __pycache__/          # Python cache directory
```

## ⚙️ Configuration

### Model Configuration

Edit `agent.py` to modify the LLM settings:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Model version
    temperature=0.2,            # Creativity level (0-1)
)
```

### Escalation Keywords

Modify the escalation triggers in `agent.py`:

```python
escalation_keywords = ["medication change", "severe pain", "urgent", "dosage"]
```

## 🔗 Future Integration: Blockchain Data via API

### Architecture for Blockchain Integration

This section outlines how to efficiently integrate blockchain data from your blockchain server via API.

#### 1. API Client Module

Create `api/blockchain_client.py`:

```python
import requests
from typing import Dict, Optional
import os
from datetime import datetime, timedelta
from cachetools import TTLCache

class BlockchainAPIClient:
    """
    Efficient client for fetching patient data from blockchain server.
    Implements caching, rate limiting, and error handling.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("BLOCKCHAIN_API_URL")
        self.api_key = api_key or os.getenv("BLOCKCHAIN_API_KEY")
        
        # Cache data for 5 minutes to reduce API calls
        self.cache = TTLCache(maxsize=100, ttl=300)
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def get_patient_context(self, patient_id: str) -> Optional[Dict]:
        """
        Fetch patient data from blockchain with caching.
        """
        # Check cache first
        if patient_id in self.cache:
            print(f"Cache hit for patient: {patient_id}")
            return self.cache[patient_id]
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/patients/{patient_id}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self.cache[patient_id] = data
            return data
            
        except requests.RequestException as e:
            print(f"Error fetching patient data: {e}")
            return None
    
    def get_medical_history(self, patient_id: str, days: int = 30) -> Optional[Dict]:
        """
        Fetch patient's medical history from blockchain.
        """
        cache_key = f"{patient_id}_history_{days}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/patients/{patient_id}/history",
                params={"days": days},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            self.cache[cache_key] = data
            return data
            
        except requests.RequestException as e:
            print(f"Error fetching medical history: {e}")
            return None
    
    def get_lab_results(self, patient_id: str) -> Optional[Dict]:
        """
        Fetch latest lab results from blockchain.
        """
        cache_key = f"{patient_id}_labs"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/patients/{patient_id}/lab-results",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            self.cache[cache_key] = data
            return data
            
        except requests.RequestException as e:
            print(f"Error fetching lab results: {e}")
            return None
    
    def verify_data_integrity(self, patient_id: str, data_hash: str) -> bool:
        """
        Verify data integrity using blockchain hash.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/verify",
                json={
                    "patient_id": patient_id,
                    "data_hash": data_hash
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("verified", False)
            
        except requests.RequestException as e:
            print(f"Error verifying data: {e}")
            return False
```

#### 2. Update Environment Variables

Add to `.env`:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Blockchain API Configuration
BLOCKCHAIN_API_URL=https://your-blockchain-server.com
BLOCKCHAIN_API_KEY=your_blockchain_api_key_here

# Optional: Cache settings
CACHE_TTL=300  # seconds
CACHE_MAX_SIZE=100  # number of entries
```

#### 3. Modified Context Fetching

Update `fetch_context` function in `agent.py`:

```python
from api.blockchain_client import BlockchainAPIClient

# Initialize blockchain client (singleton pattern recommended)
blockchain_client = BlockchainAPIClient()

def fetch_context(state: AgentState):
    """
    Node 2: Context Builder - Now fetches from blockchain
    """
    print(f"--- Node: fetch_context ---")
    
    # Extract patient ID from state or session
    patient_id = state.get("patient_id", "patient-123")
    intent = state["intent"]
    
    print(f"Fetching context for Patient ID: {patient_id} (Intent: {intent})")
    
    # Fetch data from blockchain API
    context = blockchain_client.get_patient_context(patient_id)
    
    if context is None:
        # Fallback to mock data if API fails
        print("WARNING: Blockchain API unavailable, using mock data")
        context = mock_load_context(patient_id, intent)
    else:
        # Enrich with additional data based on intent
        if intent == "suggestion_request":
            lab_results = blockchain_client.get_lab_results(patient_id)
            if lab_results:
                context["lab_results"] = lab_results
        
        if intent == "info_request":
            history = blockchain_client.get_medical_history(patient_id)
            if history:
                context["medical_history"] = history
    
    return {"context": context}
```

#### 4. Efficient Data Fetching Strategies

**Strategy 1: Parallel Fetching**

```python
import asyncio
import aiohttp

async def fetch_all_patient_data(patient_id: str):
    """
    Fetch multiple endpoints concurrently for better performance.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_patient_info(session, patient_id),
            fetch_lab_results(session, patient_id),
            fetch_medical_history(session, patient_id),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "patient_info": results[0],
            "lab_results": results[1],
            "medical_history": results[2]
        }
```

**Strategy 2: Lazy Loading**

```python
def fetch_context(state: AgentState):
    """
    Only fetch data needed for the specific intent.
    """
    patient_id = state.get("patient_id")
    intent = state["intent"]
    
    # Always fetch basic info
    context = blockchain_client.get_patient_context(patient_id)
    
    # Conditionally fetch additional data
    if intent == "suggestion_request":
        context["lab_results"] = blockchain_client.get_lab_results(patient_id)
    
    elif intent == "medication_query":
        context["prescriptions"] = blockchain_client.get_prescriptions(patient_id)
    
    return {"context": context}
```

**Strategy 3: WebSocket for Real-Time Updates**

```python
import asyncio
import websockets

class BlockchainWebSocketClient:
    """
    Subscribe to real-time blockchain updates.
    """
    
    async def subscribe_to_patient_updates(self, patient_id: str, callback):
        uri = f"wss://{self.base_url}/ws/patients/{patient_id}"
        
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({
                "action": "subscribe",
                "patient_id": patient_id
            }))
            
            async for message in websocket:
                data = json.loads(message)
                await callback(data)
```

#### 5. Installation for Blockchain Integration

Add these dependencies:

```bash
pip install requests aiohttp cachetools websockets
```

Update `requirements.txt`:

```txt
langchain-google-genai>=0.0.6
langchain-core>=0.1.0
langgraph>=0.0.20
streamlit>=1.28.0
python-dotenv>=1.0.0
requests>=2.31.0
aiohttp>=3.9.0
cachetools>=5.3.0
websockets>=12.0
```

#### 6. API Endpoint Expectations

Your blockchain server should provide these endpoints:

```
GET  /api/v1/patients/{patient_id}
GET  /api/v1/patients/{patient_id}/history?days={days}
GET  /api/v1/patients/{patient_id}/lab-results
GET  /api/v1/patients/{patient_id}/prescriptions
POST /api/v1/verify
WS   /ws/patients/{patient_id}  (optional, for real-time updates)
```

**Expected Response Format:**

```json
{
  "patient_id": "patient-123",
  "name": "Jane Doe",
  "dob": "1985-03-15",
  "diagnosis": "Type 2 Diabetes",
  "medication": "Metformin 500mg",
  "recent_visit": "2025-10-28",
  "lab_results": {
    "hba1c": "7.2%",
    "glucose": "145 mg/dL"
  },
  "blockchain_hash": "0x1234567890abcdef...",
  "last_updated": "2025-11-01T10:30:00Z"
}
```

#### 7. Testing the Integration

Create `tests/test_blockchain_integration.py`:

```python
import unittest
from unittest.mock import Mock, patch
from api.blockchain_client import BlockchainAPIClient

class TestBlockchainIntegration(unittest.TestCase):
    
    def setUp(self):
        self.client = BlockchainAPIClient(
            base_url="https://test-blockchain.com",
            api_key="test-key"
        )
    
    @patch('requests.Session.get')
    def test_get_patient_context(self, mock_get):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "patient_id": "test-123",
            "name": "Test Patient"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Test the method
        result = self.client.get_patient_context("test-123")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["patient_id"], "test-123")
    
    def test_caching(self):
        # First call
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            self.client.get_patient_context("test-123")
            self.assertEqual(mock_get.call_count, 1)
            
            # Second call should use cache
            self.client.get_patient_context("test-123")
            self.assertEqual(mock_get.call_count, 1)  # Still 1, not 2

if __name__ == '__main__':
    unittest.run()
```

#### 8. Performance Optimization Tips

1. **Implement Connection Pooling**: Reuse HTTP connections
2. **Use CDN/Edge Caching**: Cache frequently accessed blockchain data
3. **Batch Requests**: Fetch multiple patients' data in one API call if supported
4. **Implement Circuit Breaker**: Prevent cascading failures
5. **Monitor API Metrics**: Track latency, error rates, cache hit rates
6. **Use GraphQL**: If your blockchain API supports it, fetch only needed fields

#### 9. Security Considerations

```python
# Add authentication middleware
class SecureBlockchainClient(BlockchainAPIClient):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.token_expiry = None
    
    def refresh_token(self):
        """Refresh JWT token if expired"""
        if self.token_expiry and datetime.now() < self.token_expiry:
            return
        
        response = self.session.post(
            f"{self.base_url}/auth/token",
            json={"api_key": self.api_key}
        )
        data = response.json()
        self.token = data["access_token"]
        self.token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })
```

## 🗺️ Development Roadmap

- [ ] Implement blockchain API integration
- [ ] Add user authentication and session management
- [ ] Implement PostgreSQL/MongoDB for conversation history
- [ ] Add multi-language support
- [ ] Implement voice interface
- [ ] Create admin dashboard for healthcare providers
- [ ] Add analytics and reporting features
- [ ] Implement HIPAA compliance measures
- [ ] Deploy to cloud (AWS/Azure/GCP)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for the LLM capabilities
- LangChain team for the excellent framework
- Streamlit for the easy-to-use UI framework

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Note**: This project is currently in development. Patient data is mocked for demonstration purposes. In production, ensure compliance with healthcare data regulations (HIPAA, GDPR, etc.) and implement proper security measures.
