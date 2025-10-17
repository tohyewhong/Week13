
import sys
import os

# Add the project root to Python path for IDE compatibility
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.controller import Controller
    from app.schemas import Turn
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory.")
    print("Try: python app/main.py or python -m app.main")
    sys.exit(1)

def main():
    ctrl=Controller()
    print("🤖 AI Assistant (CLI Mode). Type your question. Ctrl+C to exit.\n")
    try:
        while True:
            user=input("🧑 You: ").strip()
            if not user: continue
            result=ctrl.handle(Turn(user_text=user))
            print("\n🤖 Assistant:\n", result.response_text)
            if result.image_path:
                print(f"[🖼️ Image saved at: {result.image_path}]\n")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__=="__main__":
    main()
