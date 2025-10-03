import sys
import os
import asyncio

# Add the backend directory to Python path BEFORE other imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(backend_dir)

# Now import from app after path is set
from app.tools.vector_store import VectorStore

async def clear():
    vs = VectorStore()
    try:
        vs.client.delete_collection(collection_name="education_materials")
        print("Collection cleared")
        vs._ensure_collection()
        print("New collection created")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(clear())