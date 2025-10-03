import asyncio
from app.tools.vector_store import VectorStore

async def test_vector():
    vs = VectorStore()
    
    # Test 1: Add documents
    print("TEST 1: Adding documents...")
    doc1 = await vs.add_document(
        "What is SQL?",
        {"type": "quiz_question", "topic": "sql", "user_id": "test"}
    )
    print(f"Added doc1: {doc1}")
    
    doc2 = await vs.add_document(
        "What does SELECT do?",
        {"type": "quiz_question", "topic": "sql", "user_id": "test"}
    )
    print(f"Added doc2: {doc2}")
    
    doc3 = await vs.add_document(
        "Explain Python functions",
        {"type": "quiz_question", "topic": "python", "user_id": "test"}
    )
    print(f"Added doc3: {doc3}")
    
    # Test 2: Search for SQL questions
    print("\nTEST 2: Searching for SQL questions...")
    results = await vs.search("sql quiz", limit=5)
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  - Text: {r.get('text')[:50]}...")
        print(f"    Type: {r.get('metadata', {}).get('type')}")
        print(f"    Score: {r.get('score')}")
    
    # Test 3: Check if Qdrant is actually storing
    print("\nTEST 3: Direct Qdrant check...")
    try:
        collection_info = vs.client.get_collection(vs.collection_name)
        print(f"Collection has {collection_info.points_count} points")
    except Exception as e:
        print(f"Qdrant error: {e}")
    
    # Test 4: Search for exact match
    print("\nTEST 4: Exact match search...")
    exact_results = await vs.search("What is SQL?", limit=1)
    if exact_results:
        print(f"Found exact match with score: {exact_results[0].get('score')}")
    else:
        print("No exact match found")

asyncio.run(test_vector())