import os
import re
from dotenv import load_dotenv
import requests
import argparse
import time


def extract_code_from_file(file_path):
    """
    Extract code from a file to be sent to Groq API.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        The code content to be analyzed
    """
    print(f"[INFO] Reading code from file: {file_path}")
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(f"[INFO] Successfully read file (size: {len(content)} bytes)")
            return content
    except FileNotFoundError:
        print(f"[ERROR] File {file_path} not found.")
        return None
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return None


def save_sustainable_code(file_path, sustainable_code):
    """
    Save the sustainable code received from Groq API to a file.
    
    Args:
        file_path: Path to save the sustainable code
        sustainable_code: The sustainable code received from Groq API
    
    Returns:
        True if successful, False otherwise
    """
    print(f"[INFO] Saving sustainable code to: {file_path}")
    try:
        with open(file_path, 'w') as file:
            file.write(sustainable_code)
            print(f"[SUCCESS] Sustainable code saved successfully (size: {len(sustainable_code)} bytes)")
            return True
    except Exception as e:
        print(f"[ERROR] Error saving sustainable code: {e}")
        return False


def send_to_groq_api(code_content, api_key):
    """
    Send code to Groq API for sustainability analysis.
    
    Args:
        code_content: The code to analyze
        api_key: The Groq API key
    
    Returns:
        The sustainable code received from Groq API
    """
    print("[INFO] Preparing to send code to Groq API")
    
    # Define the prompt for sustainability analysis
    prompt = f"""
    Role: You are a highly experienced software engineer specializing in sustainable and efficient coding practices.
    
    Task: Analyze the following code snippet and identify potential areas where it could be improved to reduce resource consumption (CPU, memory, energy), and minimize environmental impact.
    
    CODE:
    python
    {code_content}
    
    
    Please provide ONLY the revised code without any explanations or comments. The output should directly replace the original code snippet.
    """
    
    print(f"[INFO] Created analysis prompt of {len(prompt)} characters")
    
    # Send request to Groq API
    try:
        print("[INFO] Sending code to Groq API for sustainability analysis...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are a sustainable coding expert that optimizes code to reduce environmental impact."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
        )
        
        # Check for errors
        if response.status_code != 200:
            print(f"[ERROR] Error from Groq API: Status code {response.status_code}")
            print(f"[ERROR] Response text: {response.text}")
            return None
        
        # Extract the response
        print("[INFO] Successfully received response from Groq API")
        sustainable_code = response.json()["choices"][0]["message"]["content"]
        
        # Remove Markdown code block markers if present
        print("[INFO] Processing sustainable code...")
        if "python" in sustainable_code or "" in sustainable_code:
            print("[INFO] Removing markdown code block markers")
            sustainable_code = re.sub(r'python', '', sustainable_code)
            sustainable_code = re.sub(r'', '', sustainable_code)
        
        sustainable_code = sustainable_code.strip()
        print(f"[INFO] Processed sustainable code: {len(sustainable_code)} bytes")
        
        return sustainable_code
        
    except Exception as e:
        print(f"[ERROR] Error using Groq API: {e}")
        return None


def analyze_external_file(input_file_path, output_file_path=None):
    """
    Analyze an external file for sustainability using Groq API.
    
    Args:
        input_file_path: Path to the input file
        output_file_path: Path to save the sustainable code (optional)
    
    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    
    # Load environment variables for API key
    load_dotenv()
    print("[INFO] Loaded environment variables")
    
    # Get API key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[ERROR] No API key found in environment variables")
        print("[INFO] Please set the GROQ_API_KEY environment variable")
        return False
    
    # Extract code from the input file
    code_content = extract_code_from_file(input_file_path)
    if not code_content:
        print("[ERROR] Failed to extract code from input file")
        return False
    
    # Send code to Groq API
    sustainable_code = send_to_groq_api(code_content, api_key)
    if not sustainable_code:
        print("[ERROR] Failed to get sustainable code from Groq API")
        return False
    
    # Determine output file path
    if not output_file_path:
        # If no output file specified, use input file name with '_sustainable' suffix
        input_file_name = os.path.basename(input_file_path)
        input_file_dir = os.path.dirname(input_file_path)
        file_name, file_ext = os.path.splitext(input_file_name)
        output_file_path = os.path.join(input_file_dir, f"{file_name}_sustainable{file_ext}")
    
    # Save sustainable code to output file
    success = save_sustainable_code(output_file_path, sustainable_code)
    if not success:
        print("[ERROR] Failed to save sustainable code")
        return False
    
    elapsed_time = time.time() - start_time
    print(f"[INFO] Process completed in {elapsed_time:.2f} seconds")
    print(f"[SUCCESS] Sustainable code saved to: {output_file_path}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze external file for sustainability using Groq API")
    parser.add_argument("input_file", help="Path to the input file to analyze")
    parser.add_argument("--output", help="Path to save the sustainable code (optional)")
    
    args = parser.parse_args()
    print(f"\n[START] Sustainable code analyzer for: {args.input_file}")
    
    success = analyze_external_file(args.input_file, args.output)
    
    # Return appropriate exit code
    if not success:
        print("[ERROR] Process failed. Exiting with error code 1.")
        exit(1)
    else:
        print("[SUCCESS] Process completed successfully!")