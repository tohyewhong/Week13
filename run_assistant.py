#!/usr/bin/env python3
"""
Simple launcher script for the AI Assistant.
This should work with IDE play buttons and direct execution.
"""

import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add current directory to Python path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from app.controller import Controller
    from app.schemas import Turn
    
    def main():
        ctrl = Controller()
        print("🤖 AI Assistant (CLI Mode). Type your question. Ctrl+C to exit.\n")
        try:
            while True:
                user = input("🧑 You: ").strip()
                if not user: 
                    continue
                result = ctrl.handle(Turn(user_text=user))
                print("\n🤖 Assistant:\n", result.response_text)
                if result.image_path:
                    print(f"[🖼️ Image saved at: {result.image_path}]\n")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install openai replicate pillow scikit-learn rich duckdb")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
