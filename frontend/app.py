# rag_agent_app/frontend/streamlit_app.py

import streamlit as st
import requests
import json
import os
import uuid
from dotenv import load_dotenv

# --- Configuration Loading ---
def load_config():
    """
    Loads environment variables from the .env file.
    Assumes .env is in the project root (one level up from frontend/).
    """
    load_dotenv()
    return {
        "FASTAPI_BASE_URL": os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
    }

# --- Session State Management ---
def init_session_state():
    """
    Initializes necessary variables in Streamlit's session state.
    This ensures data persists across reruns.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "session_id" not in st.session_state:
        # Generate a unique session ID for LangGraph checkpointing and conversation tracking
        st.session_state.session_id = str(uuid.uuid4())
        # Add an initial greeting from the assistant for a fresh conversation
        st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you today?"})

    if "web_search_enabled" not in st.session_state:
        # Default web search to enabled
        st.session_state.web_search_enabled = True 

# --- UI Rendering Functions ---
def display_header():
    """Renders the main title and introductory markdown."""
    st.title("🤖 AI Agent Chatbot")
    st.markdown("Ask me anything! I can answer questions using my internal knowledge (RAG) or by searching the web.")
    st.markdown("---")

def render_document_upload_section(fastapi_base_url: str):
    """
    Renders the UI for uploading PDF documents to the knowledge base.
    Handles file upload and API call to the backend.
    """
    st.header("Upload Document to Knowledge Base")
    with st.expander("Upload New Document (PDF Only)"):
        # File uploader widget, accepts only PDF types
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="pdf_uploader")
        
        # Button to trigger the upload process
        if st.button("Upload PDF", key="upload_pdf_button"):
            if uploaded_file is not None:
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    try:
                        # Prepare the file content for a multipart/form-data request
                        # requests.post expects a tuple: (filename, file_content, content_type)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        # Make a POST request to the backend's upload endpoint
                        upload_response = requests.post(f"{fastapi_base_url}/upload-document/", files=files)
                        upload_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                        
                        # Parse the JSON response from the backend
                        upload_data = upload_response.json()
                        st.success(f"PDF '{upload_data.get('filename')}' uploaded successfully! Processed {upload_data.get('processed_chunks')} pages.")
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the FastAPI backend. Please ensure it's running.")
                    except requests.exceptions.RequestException as e:
                        # Catch specific request errors and display backend's response if available
                        st.error(f"Error uploading document: {e}. Response: {e.response.text if e.response else 'No response from backend.'}")
                    except Exception as e:
                        # Catch any other unexpected errors during the upload process
                        st.error(f"An unexpected error occurred during upload: {e}")
            else:
                st.warning("Please upload a PDF file before clicking 'Upload PDF'.")
    st.markdown("---")

def render_agent_settings_section():
    """
    Renders the section for agent settings, including the web search toggle.
    Updates the 'web_search_enabled' flag in session state.
    """
    st.header("Agent Settings")
    # Checkbox to enable/disable web search, linked to session state
    st.session_state.web_search_enabled = st.checkbox(
        "Enable Web Search (🌐)", 
        value=st.session_state.web_search_enabled,
        help="If enabled, the agent can use web search when its knowledge base is insufficient. If disabled, it will only use uploaded documents."
    )
    st.markdown("---")

def display_chat_history():
    """Displays all messages currently in the session state chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def call_backend_chat_api(fastapi_base_url: str, session_id: str, query: str, enable_web_search: bool):
    """
    Makes a POST request to the FastAPI backend's chat endpoint.
    Returns the agent's response and trace events.
    """
    payload = {
        "session_id": session_id,
        "query": query,
        "enable_web_search": enable_web_search
    }
    
    response = requests.post(f"{fastapi_base_url}/chat/", json=payload, stream=False)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    
    data = response.json()
    agent_response = data.get("response", "Sorry, I couldn't get a response from the agent.")
    trace_events = data.get("trace_events", [])
    
    return agent_response, trace_events

def display_trace_events(trace_events: list):
    """
    Renders the detailed agent workflow trace in an expandable section.
    Uses icons and conditional styling for better readability.
    """
    if trace_events:
        with st.expander("🔬 Agent Workflow Trace"):
            for event in trace_events:
                # Determine icon based on node name
                icon_map = {
                    'router': "➡️",
                    'rag_lookup': "📚",
                    'web_search': "🌐",
                    'answer': "💡",
                    '__end__': "✅"
                }
                icon = icon_map.get(event['node_name'], "⚙️") # Default to gear icon

                st.subheader(f"{icon} Step {event['step']}: {event['node_name']}")
                st.write(f"**Description:** {event['description']}")
                
                # Special handling for RAG verdict
                if event['node_name'] == 'rag_lookup' and 'sufficiency_verdict' in event['details']:
                    verdict = event['details']['sufficiency_verdict']
                    if verdict == "Sufficient":
                        st.success(f"**RAG Verdict:** {verdict} - Relevant info found in Knowledge Base.")
                    else:
                        st.warning(f"**RAG Verdict:** {verdict} - No sufficient info in Knowledge Base. Diverting to Web Search.")
                    
                    if 'retrieved_content_summary' in event['details']:
                        st.markdown(f"**Retrieved Content Summary:** `{event['details']['retrieved_content_summary']}`")
                # Special handling for web search content summary
                elif event['node_name'] == 'web_search' and 'retrieved_content_summary' in event['details']:
                    st.markdown(f"**Web Search Content Summary:** `{event['details']['retrieved_content_summary']}`")
                # Display other event details as JSON
                elif event['details']:
                    st.json(event['details'])
                
                st.markdown("---") # Separator for each step in the trace

def render_chat_interface(fastapi_base_url: str):
    """
    Renders the main chat input and handles interaction with the backend.
    Displays user and assistant messages, and the agent trace.
    """
    st.header("Chat with the Agent")
    display_chat_history()

    # User input field. This automatically updates st.session_state.messages
    if prompt := st.chat_input("Your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant's response and trace
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."): # Show a spinner while waiting for the response
                try:
                    # Call the backend API
                    agent_response, trace_events = call_backend_chat_api(
                        fastapi_base_url,
                        st.session_state.session_id,
                        prompt,
                        st.session_state.web_search_enabled
                    )
                    
                    # Display the agent's final response
                    st.markdown(agent_response)
                    # Add the agent's response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": agent_response})

                    # Display the workflow trace
                    display_trace_events(trace_events)
                    
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the FastAPI backend. Please ensure it's running.")
                    st.session_state.messages.append({"role": "assistant", "content": "Error: Could not connect to the backend."})
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred with the request: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
                except json.JSONDecodeError:
                    st.error("Received an invalid response from the backend.")
                    st.session_state.messages.append({"role": "assistant", "content": "Error: Invalid response from backend."})
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Unexpected Error: {e}"})

# --- Main Application Entry Point ---
def main():
    """Main function to run the Streamlit application."""
    config = load_config()
    init_session_state()
    display_header()
    render_document_upload_section(config["FASTAPI_BASE_URL"])
    render_agent_settings_section()
    render_chat_interface(config["FASTAPI_BASE_URL"])

if __name__ == "__main__":
    main()