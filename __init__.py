"""
ComfyLlama Package

A ComfyUI custom node package for integrating llama.cpp servers into ComfyUI workflows.

This package provides:
- LlamaLiteClient: A client for communicating with llama.cpp servers
- LlamaLiteNode: A ComfyUI custom node that wraps the client

Installation:
1. Place this package in your ComfyUI custom_nodes directory
2. Ensure dependencies are installed: openai, httpx, pillow
3. Restart ComfyUI

Usage:
The LlamaLiteNode will appear in the "LlamaLite" category in ComfyUI.
Connect it to your workflow and configure the server URL and prompts.

Author: AI Assistant
Version: 1.0.0
License: MIT
"""

from .llamalite import LlamaLiteClient
from .comfy_llama_node import LlamaLiteNode, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Package metadata
__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "ComfyUI custom node package for llama.cpp integration"

# Export main components
__all__ = [
    "LlamaLiteClient",
    "LlamaLiteNode", 
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS"
]

# ComfyUI will look for these mappings when loading the package
# Re-export them at package level for convenience
WEB_DIRECTORY = "./web"  # Directory for any web assets (if needed)

# Print loading message
print(f"ComfyLlama v{__version__} loaded successfully!")
print("LlamaLite nodes are now available in the 'LlamaLite' category.")
