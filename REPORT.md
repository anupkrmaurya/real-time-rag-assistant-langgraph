# Report – Conversational Concierge

**Name:** Anoop Maurya  
**College:** Galgotias College of Engineering and Technology  

---
## 🎥 Demo Video  

👉 [Watch Demo Video](Video.mp4)  

*(Open the file `Video.mp4` in this repo to view the demo.)*  

---


## 1. Approach  

When I first read the problem statement, I imagined the agent as a **digital salesperson** for a Napa Valley wine business — someone who not only knows the business inside-out but also carries a smartphone to quickly check the weather or search the web.  

I decided to build the project around three main abilities:  
1. **Answer questions from a knowledge document (RAG).**  
2. **Perform web searches in real-time.**  
3. **Give live weather updates.**  

To achieve this, I used **LangGraph** as the “brain” of the system. It allowed me to route user queries smartly: if the question was about the wine business → use the document; if it was about weather → call the weather API; if it needed fresh info → do a web search.  

On top of this, I built:  
- **Backend (FastAPI)** for handling requests.  
- **Frontend (Streamlit)** for an interactive chat interface.  
- **Tools & APIs** like Pinecone (vector DB), HuggingFace (embeddings), Tavily (web search), OpenWeatherMap (weather), and Groq Llama 3 (LLM).  

In short, the system can decide where to look, gather the right info, and present it in a single conversation flow.  

---

## 2. Challenges  

This project wasn’t just coding — it was about **making multiple moving parts work together smoothly**.  

- **Integrating tools**: At first, it was tricky to connect RAG, web search, and weather into one agent without it getting confused.  
- **Weather detection**: People don’t always ask “What is the weather in Delhi?” — sometimes it’s “Is it raining today?” or “How hot is Mumbai?” Handling those variations was a challenge.  
- **API juggling**: With four different APIs (Groq, Pinecone, Tavily, OpenWeather), I had to carefully manage keys, rate limits, and error handling.  
- **Routing decisions**: Making the agent smart enough to pick the right tool at the right time was harder than I expected.  
- **Speed**: Calling multiple services could make the system slow if not optimized.  

---

## 3. Solutions  

To tackle the above, I broke it down step by step:  

- I used a **router node in LangGraph** to classify queries into three buckets: knowledge, web search, or weather.  
- For weather, I wrote a **regex-based location extractor** so the agent can handle natural sentences like “temperature in Paris” or “will it rain today?”. I also added a default city if no location is given.  
- I added **try/except blocks** everywhere to avoid crashes when APIs fail or keys are wrong.  
- To reduce waiting time, I made the FastAPI backend **asynchronous**, so calls run in parallel.  
- Finally, I enabled **trace logging**, which shows users how the agent reached its decision — like a transparent decision map.  

---

## 4. Improvements & Future Work  

If I had more time, I would:  
- Add **streaming responses**, so users see answers being generated live.  
- Improve RAG by adding **query rewriting** and **ranking**, so document answers are sharper.  
- Extend **weather** to include forecasts and alerts.  
- Add **multi-modal input**, like analyzing wine bottle images.  
- Introduce **caching** to avoid repeating the same API calls.  
- Build enterprise features like **user authentication** and **usage analytics**.  

---

## 5. Reflection  

Working on this assignment was a great learning experience. It pushed me to think beyond just “getting the code to run” and focus on **designing a smooth user experience**. The biggest takeaway for me was how important it is to **orchestrate multiple services** — the magic happens not in one API, but in how you make them all talk to each other.  

---
