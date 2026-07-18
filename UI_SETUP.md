# ANITA Travel Assistant - UI Setup & Launch Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

#### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 2. **Configure Environment Variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# GOOGLE_API_KEY=your_key
# PINECONE_API_KEY=your_key
# etc.
```

#### 3. **Launch the Application**

**Option A: Modern UI (Recommended)**
```bash
streamlit run streamlit_ui.py
```

**Option B: Original UI**
```bash
streamlit run main.py
```

The application will open in your browser at: `http://localhost:8501`

---

## 📋 UI Features

### Left Sidebar - Configuration Panel
- **Mode Selection**: Choose between Demo (simulated data) or Online (real APIs)
- **Trip Details**: Set origin, destination, and travel dates
- **Traveler Profile**: Select your travel type (Solo, Family, Adventure, etc.)
- **Budget Level**: Set your budget preferences (Economy to Luxury)
- **Quick Actions**: Refresh itinerary or save trip

### Main Tabs

#### 1. 🗺️ Overview
- Trip summary with duration and details
- Interactive Google Maps link
- AI-generated trip recommendations

#### 2. ✈️ Flights
- Flight options with pricing and ratings
- Departure/arrival details
- Quick selection buttons

#### 3. 🏨 Hotels
- Hotel recommendations by location
- Ratings and price ranges
- One-click booking capability

#### 4. 🚖 Transport
- Local transportation options (Taxi, Bus, Metro, etc.)
- Duration and pricing information
- Real-time availability

#### 5. 🎯 Activities & Tours
- Curated activities and tours
- Location-based recommendations
- Pricing and popularity metrics

#### 6. 🍽️ Dining
- Restaurant recommendations
- Cuisine filtering options
- Distance and dining experience ratings

#### 7. ⚠️ Travel Alerts
- Real-time weather alerts
- Risk assessments
- Health and safety advisories
- Accessibility information

#### 8. 📊 Impact Analysis
- Sustainability metrics
- Budget analysis with alternatives
- Wellbeing recommendations
- Cultural fit suggestions

---

## 🎨 UI Components

### Cards
Professional card components with:
- Hover effects
- Icons and badges
- Organized information display
- Call-to-action buttons

### Badges
- **Price Badge** (Green) - Cost information
- **Rating Badge** (Yellow) - Star ratings
- **Status Badges** - Success/Warning/Error states

### Responsive Layout
- Adapts to different screen sizes
- Multi-column grids for options
- Mobile-friendly design

---

## 🔧 Configuration

### Streamlit Settings (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#0066cc"          # Main brand color
backgroundColor = "#ffffff"       # Page background
textColor = "#1f2937"            # Text color

[server]
port = 8501                       # Application port
headless = true                   # Run without browser popup
enableXsrfProtection = true       # Security feature
```

### Environment Variables (.env)
```
GOOGLE_API_KEY=...               # For Gemini API
GOOGLE_MAPS_API_KEY=...          # For Maps integration
PINECONE_API_KEY=...             # For RAG vector database
AVIATIONSTACK_API_KEY=...        # For flight data
```

---

## 🎯 Usage Scenarios

### Demo Mode (No API Keys Required)
Perfect for testing and demonstration:
```bash
# Set environment
export APP_MODE=demo

# Run application
streamlit run streamlit_ui.py

# All data is simulated
```

### Online Mode (Requires API Keys)
Connect to real data sources:
```bash
# Set API keys first
export GOOGLE_API_KEY=your_key
export PINECONE_API_KEY=your_key

# Run application
streamlit run streamlit_ui.py

# Live data from real APIs
```

---

## 📱 Mobile Responsiveness

The UI is fully responsive and works on:
- ✅ Desktop browsers (Chrome, Firefox, Safari, Edge)
- ✅ Tablets (iPad, Android tablets)
- ✅ Mobile phones (iPhone, Android)

---

## 🔐 Security Notes

### API Keys
- Never commit `.env` files to version control
- Use `.env.example` as template
- Rotate keys regularly
- Use environment variables in production

### Data Privacy
- All user data is stored locally
- No analytics by default
- XSRF protection enabled
- Secure session management

---

## 🐛 Troubleshooting

### Issue: Port 8501 already in use
```bash
streamlit run streamlit_ui.py --server.port 8502
```

### Issue: Module not found errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Slow performance in Online mode
- This is normal on first run (caching builds)
- Subsequent runs will be faster
- Enable caching for better performance

### Issue: API key errors
- Verify `.env` file is in project root
- Check API keys are valid and active
- Ensure APIs are enabled in cloud console

---

## 📊 Performance

### Caching Strategy
The application uses Streamlit's caching to improve performance:
- Trip configurations cached for 1 hour
- Results cached between refreshes
- User preferences stored locally

### Expected Load Times
- **Demo Mode**: < 1 second
- **Online Mode (first load)**: 3-5 seconds
- **Online Mode (cached)**: < 1 second

---

## 🛠️ Advanced Usage

### Custom Styling
Edit `streamlit_ui.py` CSS section to customize:
- Color scheme
- Fonts and sizing
- Spacing and layout
- Animation effects

### Adding New Features
The UI is modular and extensible:
1. Add new tab to the tabs list
2. Implement content in corresponding `with` block
3. Use existing card components for consistency

### Integrating Additional APIs
To add more data sources:
1. Add API key to `.env`
2. Create new agent class
3. Integrate with ANITA orchestrator
4. Display results in appropriate tab

---

## 📚 Additional Resources

### Documentation Files
- `ARCHITECTURE_ISSUES_REPORT.md` - Technical architecture
- `CRITICAL_FIXES_REQUIRED.md` - Bug fixes documentation
- `FIXES_COMPLETED.md` - Implementation details

### Project Structure
```
anita-travel-assistant-fixed/
├── streamlit_ui.py          # Main UI file
├── main.py                  # Alternative UI
├── orchestrator/            # Core orchestration
│   ├── anita.py
│   ├── state_manager.py
│   └── routes.py
├── agents/                  # Specialized agents
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── tour_agent.py
│   └── ...
├── rag/                     # RAG knowledge base
├── prompts/                 # AI prompts
├── utils/                   # Utilities
├── requirements.txt         # Dependencies
└── .streamlit/              # Streamlit config
```

---

## 🚢 Deployment

### Local Development
```bash
streamlit run streamlit_ui.py --logger.level=debug
```

### Production Deployment
```bash
streamlit run streamlit_ui.py --server.headless true --client.toolbarMode minimal
```

### Docker Deployment (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_ui.py", "--server.headless", "true"]
```

---

## 📞 Support

### Common Issues Checklist
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Port 8501 is available
- [ ] No firewall blocking localhost:8501

### Getting Help
1. Check `.env.example` for required keys
2. Review error messages in console
3. Consult `CRITICAL_FIXES_REQUIRED.md` for known issues
4. Check Streamlit documentation: https://docs.streamlit.io

---

## ✨ Features Highlight

### 🎯 Intelligent Routing
- Automatically routes requests to specialized agents
- Adapts based on traveler type and preferences
- Learns from user feedback

### 🔄 Real-time Updates
- Live weather alerts
- Dynamic pricing updates
- Real-time availability checks

### 💡 Smart Recommendations
- AI-powered suggestions based on preferences
- Impact analysis on sustainability, budget, health
- Alternative options for risk mitigation

### 📈 Analytics
- Trip impact dashboard
- Budget tracking
- Travel insights and patterns

---

## 🎉 Ready to Explore!

Your ANITA Travel Assistant is now configured and ready to help you plan amazing trips!

```bash
# Launch the application
streamlit run streamlit_ui.py

# Your browser will open automatically
# Start planning your next adventure! ✈️
```

Enjoy your travels! 🌍✈️🏨
