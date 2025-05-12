#!/usr/bin/env python3
import asyncio
import sys
import os
from knowledge_manager import import_knowledge

async def main():
    """
    Main entry point for importing files into the knowledge base
    """
    if len(sys.argv) < 2:
        print("Usage: python import_file.py <file_path>")
        return
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return
    
    print(f"Importing file: {file_path}")
    try:
        await import_knowledge(file_path)
        print(f"Successfully imported {file_path}")
    except Exception as e:
        print(f"Error importing file: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 