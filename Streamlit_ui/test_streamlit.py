import os
import re
import sys
import json
import streamlit as st
import requests
from dotenv import load_dotenv
import tempfile
import argparse

# Load environment variables
load_dotenv()

def analyze_code_for_sustainability(code_content, filename, api_key=None, model=None, temperature=None, is_cli=False):
    """
    Analyze code using Groq API for sustainability improvements
    
    Parameters:
    - code_content: The code to analyze
    - filename: Name of the file
    - api_key: Groq API key
    - model: Model to use
    - temperature: Temperature setting
    - is_cli: Whether the function is being called from command line
    
    Returns:
    - sustainable_code: The optimized code
    - is_sustainable: Boolean indicating if code meets sustainability standards
    """
    # If no API key provided, try to get from environment
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key and not is_cli:
            st.error("Please enter your Groq API key in the sidebar")
            return None, False
        elif not api_key and is_cli:
            print("Error: No Groq API key found. Set GROQ_API_KEY environment variable.")
            return None, False
    
    # Use default model and temperature if not provided
    model = model or "llama3-70b-8192"
    temperature = temperature if temperature is not None else 0.2
    
    # Define the prompt for sustainability analysis
    prompt = f"""
    Role: You are a highly experienced software engineer specializing in sustainable and efficient coding practices.
    
    Task: Analyze the following code snippet and identify potential areas where it could be improved to reduce resource consumption (CPU, memory, energy), and minimize environmental impact.
    
    CODE:
    python
    {code_content}
    
    
    Please provide:
    1. The revised code without any explanations or comments.
    2. At the end of your response, include a single line with JSON in the format: {{"is_sustainable": true/false}} indicating if the original code already meets high sustainability standards (true) or if it needed significant improvements (false).
    
    The output should be in a format ready to directly replace the original code file.
    """
    
    if not is_cli:
        # Progress bar and status (only in Streamlit UI)
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Sending code to Groq for sustainability analysis...")
        progress_bar.progress(30)
    else:
        print("Analyzing code for sustainability...")
    
    try:
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
        
        if not is_cli:
            progress_bar.progress(70)
        
        # Check for errors
        if response.status_code != 200:
            error_message = f"Error from Groq API: {response.text}"
            if is_cli:
                print(error_message)
            else:
                st.error(error_message)
            return None, False
        
        # Extract the response
        response_content = response.json()["choices"][0]["message"]["content"]
        
        # Try to extract JSON sustainability assessment
        is_sustainable = False
        json_match = re.search(r'{"is_sustainable":\s*(true|false)}', response_content)
        if json_match:
            try:
                assessment = json.loads(json_match.group(0))
                is_sustainable = assessment.get("is_sustainable", False)
                # Remove the JSON from the code
                response_content = re.sub(r'{"is_sustainable":\s*(true|false)}', '', response_content)
            except json.JSONDecodeError:
                pass
        
        # Remove Markdown code block markers
        sustainable_code = re.sub(r'python\s*', '', response_content)
        sustainable_code = re.sub(r'\s*', '', sustainable_code)
        sustainable_code = sustainable_code.strip()
        
        if not is_cli:
            # Update progress (only in Streamlit UI)
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Add to history
            if 'history' in st.session_state:
                st.session_state.history.append({
                    'filename': filename,
                    'original_code': code_content,
                    'sustainable_code': sustainable_code,
                    'is_sustainable': is_sustainable
                })
        else:
            print(f"Analysis complete for {filename}")
            print(f"Sustainability assessment: {'Already sustainable' if is_sustainable else 'Needs improvements'}")
        
        return sustainable_code, is_sustainable
        
    except Exception as e:
        error_msg = f"Error: {e}"
        if is_cli:
            print(error_msg)
        else:
            st.error(error_msg)
        return None, False
    finally:
        if not is_cli:
            # Clean up progress indicators (only in Streamlit UI)
            progress_bar.empty()
            status_text.empty()

def save_optimized_code(original_file_path, sustainable_code):
    """Save the optimized code to a file"""
    directory, filename = os.path.split(original_file_path)
    optimized_filename = f"sustainable_{filename}"
    optimized_file_path = os.path.join(directory, optimized_filename)
    
    with open(optimized_file_path, 'w') as f:
        f.write(sustainable_code)
    
    return optimized_file_path

def run_streamlit_app():
    """Run the Streamlit application"""
    st.set_page_config(
        page_title="Sustainable Code Analyzer",
        page_icon="🌱",
        layout="wide"
    )
    
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
        
        # Husky integration section
        st.header("Husky Integration")
        st.markdown("""
        To use this tool with Git Hooks via Husky:
        
        1. Install Husky: npm install husky --save-dev
        2. Create a hook file: .husky/pre-commit
        3. Make it executable: chmod +x .husky/pre-commit
        
        Copy the following content to the pre-commit file:
        bash
        #!/bin/sh
        # Analyze staged Python files for sustainability
        
        STAGED_FILES=$(git diff --name-only --cached -- "*.py")
        
        if [ -n "$STAGED_FILES" ]; then
          while IFS= read -r file; do
            echo "Analyzing staged file: $file"
            python YOUR_APP_PATH.py --file "$file"
            if [ $? -ne 0 ]; then
              echo "Sustainability analysis failed for: $file"
              exit 1
            fi
          done <<< "$STAGED_FILES"
        else
          echo "No staged Python files to analyze."
        fi
        
        """)
        
        # History section
        st.header("Analysis History")
        if st.session_state.history:
            for i, item in enumerate(st.session_state.history):
                with st.expander(f"Analysis #{i+1}: {item['filename']}"):
                    st.code(item['original_code'], language="python")
                    st.markdown(f"*Sustainable Version:* {'(Already sustainable)' if item.get('is_sustainable', False) else '(Needs improvements)'}")
                    st.code(item['sustainable_code'], language="python")
        else:
            st.info("No analyses yet. Upload a file to get started.")
    
    # Main interface - tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Upload File", "Paste Code", "Analyze File Path"])
    
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
                sustainable_code, is_sustainable = analyze_code_for_sustainability(
                    file_contents, 
                    uploaded_file.name,
                    api_key,
                    model,
                    temperature
                )
                
                if sustainable_code:
                    # Display comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Code")
                        st.code(file_contents, language="python")
                    
                    with col2:
                        st.subheader(f"Sustainable Code {'(Already sustainable)' if is_sustainable else '(Needs improvements)'}")
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
                sustainable_code, is_sustainable = analyze_code_for_sustainability(
                    code_input, 
                    filename,
                    api_key,
                    model,
                    temperature
                )
                
                if sustainable_code:
                    # Display comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Code")
                        st.code(code_input, language="python")
                    
                    with col2:
                        st.subheader(f"Sustainable Code {'(Already sustainable)' if is_sustainable else '(Needs improvements)'}")
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
    
    with tab3:
        # Field for entering a file path
        file_path = st.text_input("Enter the path to a Python file:", "")
        
        if st.button("Analyze & Optimize", key="analyze_path"):
            if file_path and os.path.exists(file_path) and file_path.endswith('.py'):
                try:
                    with open(file_path, 'r') as f:
                        file_contents = f.read()
                    
                    filename = os.path.basename(file_path)
                    
                    sustainable_code, is_sustainable = analyze_code_for_sustainability(
                        file_contents, 
                        filename,
                        api_key,
                        model,
                        temperature
                    )
                    
                    if sustainable_code:
                        # Display comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Original Code")
                            st.code(file_contents, language="python")
                        
                        with col2:
                            st.subheader(f"Sustainable Code {'(Already sustainable)' if is_sustainable else '(Needs improvements)'}")
                            st.code(sustainable_code, language="python")
                        
                        # Save file option
                        if st.button("Save Optimized File", key="save_optimized"):
                            optimized_path = save_optimized_code(file_path, sustainable_code)
                            st.success(f"Saved optimized file to: {optimized_path}")
                        
                        # Download button
                        st.download_button(
                            label="Download Sustainable Code",
                            data=sustainable_code,
                            file_name=f"sustainable_{filename}",
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error reading or processing file: {e}")
            else:
                st.warning("Please enter a valid path to a Python file.")
    
    # Footer
    st.markdown("---")
    st.markdown("🌿 Sustainable Code Analyzer - Making software environmentally friendly")

def run_cli(args):
    """Run in command line interface mode"""
    # Check if file exists
    if not os.path.exists(args.file) or not args.file.endswith('.py'):
        print(f"Error: {args.file} is not a valid Python file")
        return 1
    
    try:
        # Read the file
        with open(args.file, 'r') as f:
            file_contents = f.read()
        
        filename = os.path.basename(args.file)
        
        # Analyze the code
        print(f"Analyzing {filename} for sustainability...")
        sustainable_code, is_sustainable = analyze_code_for_sustainability(
            file_contents,
            filename,
            args.api_key,
            args.model,
            args.temperature,
            is_cli=True
        )
        
        if sustainable_code:
            if args.save:
                # Save the optimized version
                optimized_path = save_optimized_code(args.file, sustainable_code)
                print(f"Saved optimized code to: {optimized_path}")
            
            if not is_sustainable:
                print("⚠ Code needs sustainability improvements.")
                if args.enforce and not args.save:
                    print("Commit rejected due to sustainability issues. Use --save to save the optimized version.")
                    return 1
            else:
                print("✅ Code already meets sustainability standards.")
            
            return 0
        else:
            print("Failed to analyze code")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    # Check if running as CLI or Streamlit app
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        # Running from command line
        parser = argparse.ArgumentParser(description="Sustainable Code Analyzer")
        parser.add_argument("--file", required=True, help="Path to Python file to analyze")
        parser.add_argument("--api-key", help="Groq API key (will use GROQ_API_KEY env var if not provided)")
        parser.add_argument("--model", default="llama3-70b-8192", help="Model to use for analysis")
        parser.add_argument("--temperature", type=float, default=0.2, help="Temperature setting")
        parser.add_argument("--save", action="store_true", help="Save optimized version")
        parser.add_argument("--enforce", action="store_true", help="Enforce sustainability (fail if not sustainable)")
        
        args = parser.parse_args()
        sys.exit(run_cli(args))
    else:
        # Running as Streamlit app
        run_streamlit_app()