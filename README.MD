# 🧭 WanderMind - A Travel Planner Agent

## 📘 Overview
The **WanderMind** is an AI-powered system designed to generate personalized travel itineraries based on user preferences such as destination, travel dates, budget, and interests.  
It leverages **Agentic AI**, Large Language Models (LLMs) and external APIs (like Amadeus) to integrate real-time flight, hotel, and sightseeing data into a seamless, day-wise itinerary.

This project demonstrates the power of **Generative AI and Agentic Architecture** in creating intelligent, user-driven planning experiences.

---

## 🧩 Problem Statement
Travelers often struggle to plan a complete trip that includes sightseeing, accommodations, and travel options. Travel companies aim to provide a personalized itinerary that meets user preferences and offers a seamless experience.

### 🎯 Goal
Build an AI-driven travel planner that:
- Takes user preferences (destination, travel dates, interests, budget, etc.)
- Retrieves and filters relevant data (flights, hotels, attractions)
- Generates a **personalized, day-wise itinerary** with details for each day
- Outputs the final itinerary as a **structured summary and downloadable PDF**

---

## ⚙️ Key Features
✅ **LLM-powered Recommendations:** Uses Azure OpenAI API (via `openai_llm.py`) to interpret and generate natural language itineraries.  
✅ **Dynamic Data Integration:** Fetches real-time flight and hotel data using the **Amadeus API** (`amadeus_helper.py`).  
✅ **Graph-based Workflow:** Orchestrates interdependent nodes (`attr_nodes`, `flights_nodes`, `hotels_nodes`, `itinerary_nodes`, `user_nodes`) in a **parallelized decision pipeline**, where data fetching for attractions, flights, and hotels occurs **simultaneously** after user input is captured. The results are then merged to generate a complete, optimized itinerary.  
✅ **State Management:** Maintains conversation and decision context through the `state` module.  
✅ **Streamlit UI:** Provides an interactive front-end for user input and itinerary display.  
✅ **Export & Visualization:** Generates a final PDF itinerary (`travel_itinerary.pdf`) and visual graph (`Graph_image.jpg`).

---

## 🗂️ Project Structure
```
src/
├── Data/
│ └── combined.csv # Dataset with attraction data
├── graphs/
│ ├── graph_builder.py # Builds and manages the node graph
├── helper/
│ └── amadeus_helper.py # Handles API calls to Amadeus
├── LLMs/
│ └── openaillm.py # LLM interface using Azure OpenAI API
├── nodes/
│ ├── attr_nodes.py # Handles attractions and sightseeing logic
│ ├── flights_nodes.py # Handles flight-related nodes
│ ├── hotels_nodes.py # Handles hotel recommendation nodes
│ ├── itinerary_nodes.py # Builds final itinerary per day
│ └── user_nodes.py # Manages user preference inputs
├── state/
│ └── state.py # Defines state classes and transitions
├── tools/
│ ├── logger.py # Handles logging and debugging
│ ├── tools_for_attr.py # Helper utilities for attractions
│ ├── tools_for_flights.py # Helper utilities for flights
│ └── tools_for_hotels.py # Helper utilities for hotels
└── ui/
├── streamlitui/
│ └── main.py # Streamlit front-end entry point
│ └── displayresult.py # Displays the generated itinerary
├── uiconfig.py # Streamlit UI configuration
└── uiconfig.ini # UI settings
```
---

### Naming Convention for Functions
- `fetch_`: API or external data calls  
- `parse_`: Parsing user inputted free text to get user_data  
- `summarize_` / `generate_`: LLM-based reasoning or synthesis  
- `create_` / `load_` / `setup_`: Initialization and setup functions  
- `render_`: Output or UI rendering  
- `get_`: Only for simple property accessors

---

## 🧠 Architecture

The project follows a **modular, agentic, and parallelized architecture** that efficiently builds a travel itinerary through coordinated node execution.

1. **Start:** The process begins with `fetch_user_data`, where the system collects user preferences such as destination, dates, and budget from the free text fed in by the user via the Streamlit UI.  
2. **Parallel Data Retrieval:** Once user data is available, three independent branches run **in parallel**:
   - `get_attr_details` → `get_top_attr_details` (for sightseeing and attractions)  
   - `get_flight_details` → `get_top_flight_details` (for flight options)  
   - `get_hotel_details` → `get_top_hotel_details` (for accommodations)  
3. **Itinerary Generation:** The results from all three parallel branches are merged in the `get_itinerary` node, which compiles a **day-wise itinerary** with flights, hotels, and attractions.  
4. **End:** The final output is a **personalized travel itinerary**, available as both a structured summary and a downloadable PDF (`travel_itinerary.pdf`).

A visual representation of the graph can be found in `Graph_image.jpg`.

### Robust Failure Handling
The system now gracefully handles cases where one or more external data sources are unavailable (e.g., Amadeus flight API downtime, missing hotel results, incomplete attraction data). Instead of breaking the itinerary generation flow:

- Each data retrieval module returns structured fallback responses.
- The itinerary generator continues seamlessly using available data.
- The UI displays clear contextual warnings (e.g., “Live flight data unavailable — showing itinerary without flight recommendations.”)
- The final itinerary still remains complete and readable.

This ensures the system is reliable even when external services are partially unavailable.

---

## 🚀 Setup and Installation

### 1️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux
```
### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Set Up Environment Variables
```ini
AZURE_OPENAI_API_KEY = your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT = your_azure_openai_wndpoint
AZURE_OPENAI_API_VERSION = your_azure_openai_api_version
AZURE_EMBD_OPENAI_API_VERSION = your_azure_openai_api_version_for_embeddings
AZURE_DEPLOYMENT_NAME = your_azure_openai_api_deplyoment_name
AZURE_EMBD_DEPLMENT_NAME = your_azure_openai_api_deplyoment_name_for_embeddings
AMADEUS_CLIENT_SECRET = your_amadeus_client_secret
AMADEUS_CLIENT_ID = your_amadeus_client_id # this is the api key
AMADEUS_ENV = your_amadeus_environment # either prod or test
```
### 4️⃣ Run the App
```bash
streamlit run app.py
```
## 🧾 Example Output

- **Graph Visualization:** `Graph_image.jpg`  
- **Generated Itinerary (PDF):** `travel_itinerary.pdf`

---

## 📚 Requirements

Refer to `requirements.txt` for full dependency details.

---

## 🏁 Future Enhancements

- **Voice-Based Trip Requests:**  
  Enable speech-to-text functionality so users can verbally describe their travel plans instead of typing, making the experience more natural and hands-free.

- **Real-Time Availability Checks:**  
  Integrate live APIs to instantly verify flight and hotel availability, ensuring all itinerary options are accurate and up to date before confirmation.

- **Interactive Map Visualization:**  
  Embed dynamic maps within the UI to visualize hotels, attractions, and travel routes, providing users with better spatial awareness and trip context.

- **Collaborative Trip Mode:**  
  Introduce a shared planning mode where multiple users can co-create an itinerary, merge preferences, and finalize trip details together.  

- **Clarity in error messages:**
Add dynamic retry + caching strategy for flight/hotel APIs to further reduce dependency on live responses.

---

## 📜 License

This project is for **educational and demonstration purposes**.  
For production usage, please ensure API compliance and proper data governance.
