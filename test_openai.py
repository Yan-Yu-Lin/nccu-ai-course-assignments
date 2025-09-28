#!/usr/bin/env python3
"""
Test script to demonstrate that uv run doesn't auto-install dependencies
"""

try:
    import openai
    print("✅ OpenAI library is installed!")
    print(f"OpenAI version: {openai.__version__}")

    # Try to create a client (won't actually work without API key)
    client = openai.OpenAI(api_key="dummy-key-for-testing")
    print("✅ Successfully created OpenAI client")

except ImportError as e:
    print("❌ OpenAI library is NOT installed!")
    print(f"Error: {e}")
    print("\nThis proves that 'uv run' doesn't automatically install missing packages.")
    print("You need to manually install with: uv pip install openai")