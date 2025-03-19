import streamlit as st
import anthropic
import os
from typing import List, Dict
import time
import json
from pathlib import Path

# Initialize Claude client
claude = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

class ConversationManager:
    def __init__(self):
        self.history: List[Dict] = []
        self.total_cost = 0.0
        self.token_price = 0.0001  # $0.0001 per token (example rate)

    def add_message(self, role: str, content: str, tokens: int = 0):
        self.history.append({"role": role, "content": content})
        self.total_cost += tokens * self.token_price

def init_session_state():
    if 'conversation' not in st.session_state:
        st.session_state.conversation = ConversationManager()

def call_claude(prompt: str, conversation: ConversationManager):
    try:
        response = claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1500,
            messages=[
                {"role": msg["role"], "content": msg["content"]} 
                for msg in conversation.history
            ] + [{"role": "user", "content": prompt}],
            system="You are a helpful AI assistant with computer use capabilities. You can perform file operations, browse the web, and execute system commands safely."
        )
        
        # Extract response and token usage
        content = response.content[0].text
        tokens = response.usage.output_tokens
        
        conversation.add_message("assistant", content, tokens)
        return content
    except Exception as e:
        return f"Error: {str(e)}"

def handle_audio_input(audio_file) -> str:
    # Placeholder for audio transcription
    # In a real implementation, you'd use a transcription service
    return "[Transcribed audio would appear here]"

def main():
    st.title("Claude Computer Use Interface")
    init_session_state()
    
    # Input section
    user_input = st.text_area("Enter your instruction for Claude:")
    audio_file = st.file_uploader("Or upload audio message", type=['wav', 'mp3'])
    
    if st.button("Send"):
        if user_input or audio_file:
            # Handle audio if provided
            if audio_file:
                transcription = handle_audio_input(audio_file)
                user_input = f"{user_input}\n[Audio Input]: {transcription}"
            
            # Get Claude's response
            response = call_claude(user_input, st.session_state.conversation)
            
            # Display response
            st.markdown("### Claude's Response:")
            st.write(response)
            
            # Show cost
            st.markdown("### Session Cost:")
            st.write(f"${st.session_state.conversation.total_cost:.4f}")
    
    # Display conversation history
    st.markdown("### Conversation History:")
    for msg in st.session_state.conversation.history:
        st.text(f"{msg['role'].title()}: {msg['content']}")

if __name__ == "__main__":
    main()
