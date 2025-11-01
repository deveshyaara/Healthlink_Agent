import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Import the compiled LangGraph app from our other file
try:
    from agent import app
except ImportError:
    st.error("Error: Could not import the agent. Please make sure agent.py is in the same directory.")
    st.stop()

st.set_page_config(page_title="Health Agent Chat", page_icon="🤖", layout="centered")
st.title("🤖 Health Agent Chat")
st.caption("A simple chat interface for our LangGraph agent.")

# --- 1. Initialize session state ---
# We use Streamlit's session_state to store the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. Display existing messages ---
# Loop through the history and display each message
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# --- 3. Get new user input ---
# st.chat_input creates a text box at the bottom of the page
if prompt := st.chat_input("Ask for a suggestion..."):

    # Add the user's message to state and display it
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.write(prompt)

    # --- 4. Call the agent ---
    # Show a spinner while the agent is "thinking"
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # We need to pass the history *before* the user's new message
            # because our 'receive_query' node will add the new prompt
            history_for_bot = st.session_state.chat_history[:-1]
            
            # Use a unique thread_id for this session
            config = {"configurable": {"thread_id": "streamlit-chat-session"}}

            # Define the inputs for the agent
            inputs = {"input": prompt, "chat_history": history_for_bot}

            try:
                # 'invoke' runs the full graph and returns the final state
                final_state = app.invoke(inputs, config)
                
                # Get the 'suggestion' from the final state
                response = final_state.get("suggestion", "Sorry, I'm not sure how to respond to that.")
                
                # Display the response
                st.write(response)
                
                # Add the AI's response to the session state
                st.session_state.chat_history.append(AIMessage(content=response))

            except Exception as e:
                st.error(f"An error occurred: {e}")
                # Remove the user's message if the agent fails
                st.session_state.chat_history.pop()
