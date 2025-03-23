import os
import re
import streamlit as st
import requests
from dotenv import load_dotenv
import tempfile

st.set_page_config(
    page_title="Sustainable Code Analyzer",
    page_icon="🌱",
    layout="wide"
)
# Load environment variables
load_dotenv()

# Page config

# App title and description
st.title("🌱 Sustainable Code Analyzer")
st.markdown("""
This application analyzes your code and suggests optimizations to reduce resource consumption
(CPU, memory, energy) and minimize environmental impact. Simply upload your code file or paste your code,
and the AI will generate a more sustainable version.
""")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar for API key
with st.sidebar:
    st.header("API Configuration")
    
    # Get API key
    saved_api_key = os.getenv("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key", value=saved_api_key, type="password")
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
    )
    
    # Temperature setting
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
    
    # History section
    st.header("Analysis History")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"Analysis #{i+1}: {item['filename']}"):
                st.code(item['original_code'], language="python")
                st.markdown("**Sustainable Version:**")
                st.code(item['sustainable_code'], language="python")
    else:
        st.info("No analyses yet. Upload a file to get started.")

# Function to analyze code
def analyze_code_for_sustainability(code_content, filename):
    """
    Analyze code using Groq API for sustainability improvements
    """
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar")
        return None
    
    # Define the prompt for sustainability analysis
    prompt = f"""
    Role: You are a highly experienced software engineer specializing in sustainable and efficient coding practices.
    
    Task: Analyze the following code snippet and identify potential areas where it could be improved to reduce resource consumption (CPU, memory, energy), and minimize environmental impact.
    
    CODE:
    ```python
    {code_content}
    ```
    
    Please provide ONLY the revised code without any explanations or comments. The output should be in a format ready to directly replace the original code file.
    """
    
    # Progress bar and status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update status
        status_text.text("Sending code to Groq for sustainability analysis...")
        progress_bar.progress(30)
        
        # Send request to Groq API
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a sustainable coding expert that optimizes code to reduce environmental impact."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
        )
        
        progress_bar.progress(70)
        
        # Check for errors
        if response.status_code != 200:
            st.error(f"Error from Groq API: {response.text}")
            return None
        
        # Extract the response
        sustainable_code = response.json()["choices"][0]["message"]["content"]
        
        # Remove Markdown code block markers
        sustainable_code = re.sub(r'```python\s*', '', sustainable_code)
        sustainable_code = re.sub(r'```\s*', '', sustainable_code)
        
        # Update progress
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Add to history
        st.session_state.history.append({
            'filename': filename,
            'original_code': code_content,
            'sustainable_code': sustainable_code
        })
        
        return sustainable_code
        
    except Exception as e:
        st.error(f"Error: {e}")
        return None
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()

# Main interface - tabs for different input methods
tab1, tab2 = st.tabs(["Upload File", "Paste Code"])

with tab1:
    uploaded_file = st.file_uploader("Choose a Python file", type=['py'])
    
    if uploaded_file is not None:
        # Read the file
        file_contents = uploaded_file.getvalue().decode("utf-8")
        
        # Display the original code
        with st.expander("Original Code"):
            st.code(file_contents, language="python")
        
        # Analyze button
        if st.button("Analyze & Optimize", key="analyze_file"):
            sustainable_code = analyze_code_for_sustainability(file_contents, uploaded_file.name)
            
            if sustainable_code:
                # Display comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Code")
                    st.code(file_contents, language="python")
                
                with col2:
                    st.subheader("Sustainable Code")
                    st.code(sustainable_code, language="python")
                
                # Download button
                st.download_button(
                    label="Download Sustainable Code",
                    data=sustainable_code,
                    file_name=f"sustainable_{uploaded_file.name}",
                    mime="text/plain"
                )

with tab2:
    # Text area for pasting code
    code_input = st.text_area("Paste your Python code here:", height=300)
    filename = st.text_input("Filename (for reference):", "code_snippet.py")
    
    if st.button("Analyze & Optimize", key="analyze_pasted"):
        if code_input:
            sustainable_code = analyze_code_for_sustainability(code_input, filename)
            
            if sustainable_code:
                # Display comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Original Code")
                    st.code(code_input, language="python")
                
                with col2:
                    st.subheader("Sustainable Code")
                    st.code(sustainable_code, language="python")
                
                # Download button
                st.download_button(
                    label="Download Sustainable Code",
                    data=sustainable_code,
                    file_name=f"sustainable_{filename}",
                    mime="text/plain"
                )
        else:
            st.warning("Please paste some code first.")

# Footer
st.markdown("---")
st.markdown("🌿 Sustainable Code Analyzer - Making software environmentally friendly")