import sys
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

def verify():
    print("Loading environment...")
    load_dotenv("backend_v2/.env")
    
    print("Importing Container...")
    try:
        from src.container import Container
        print("Initializing Container...")
        container = Container.get_instance()
        
        print("Checking services...")
        if container.llm_service:
            print(" - LLM Service: OK")
        if container.vector_store:
            print(" - Vector Store: OK")
            
        print("\n✅ Verification Successful: Backend V2 structure is valid.")
        
    except ImportError as e:
        print(f"\n❌ ImportError: {e}")
        print("Make sure you are running from the project root and dependencies are installed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    verify()
