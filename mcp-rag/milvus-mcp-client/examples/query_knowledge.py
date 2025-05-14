#!/usr/bin/env python
"""
Example script for querying a knowledge base.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.knowledge_retriever import KnowledgeRetriever

async def main():
    """
    Main function to query a knowledge base.
    """
    # Check if question is provided
    if len(sys.argv) < 2:
        print("Usage: python query_knowledge.py <question>")
        sys.exit(1)
        
    question = sys.argv[1]
    
    # Create knowledge retriever
    retriever = KnowledgeRetriever()
    
    print(f"Querying knowledge base with question: {question}")
    print("Please wait, processing your query...")
    
    try:
        # Query knowledge base
        answer = await retriever.query(question)
        
        # Print answer
        print("\n" + "=" * 80)
        print("问题:", question)
        print("-" * 80)
        print("回答:", answer)
        print("=" * 80)
        
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    asyncio.run(main()) 