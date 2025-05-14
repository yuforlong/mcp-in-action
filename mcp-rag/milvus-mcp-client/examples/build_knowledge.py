#!/usr/bin/env python
"""
Example script for building a knowledge base from a text file.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.knowledge_builder import KnowledgeBuilder

async def main():
    """
    Main function to build a knowledge base from a text file.
    """
    # Check if file path is provided
    if len(sys.argv) < 2:
        print("Usage: python build_knowledge.py <file_path> [title] [author]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    # Optional parameters
    title = sys.argv[2] if len(sys.argv) > 2 else None
    author = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Prepare metadata
    metadata = {}
    if title:
        metadata["title"] = title
    if author:
        metadata["author"] = author
        
    # Create knowledge builder
    builder = KnowledgeBuilder()
    
    print(f"Building knowledge base from file: {file_path}")
    print(f"Metadata: {metadata}")
    
    try:
        # Build knowledge base
        result = await builder.build_from_file(file_path, metadata)
        
        # Print result
        print("\nResults:")
        print(f"- Stored {result['stored_chunks']}/{result['total_chunks']} chunks to knowledge base")
        print(f"- Extracted and stored {result['extracted_faqs']} FAQs")
        print("\nDone!")
        
    except Exception as e:
        print(f"Error building knowledge base: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    asyncio.run(main()) 