"""
ComfyUI Custom Node for LlamaLite Integration

This module provides a custom ComfyUI node that wraps around the LlamaLiteClient
to enable easy integration of llama.cpp servers into ComfyUI workflows.

The node allows users to send prompts to a local llama.cpp server and receive
both the response message and the complete chat history for further processing.

Author: AI Assistant
License: MIT
"""

import json
import logging
import numpy
import torch
from PIL import Image
from typing import Dict, Any, Tuple, Optional, List

# Import the LlamaLiteClient from the local module
from .llamalite import LlamaLiteClient


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaLiteNode:
    """
    A ComfyUI custom node that provides an interface to interact with llama.cpp servers.
    
    This node wraps around the LlamaLiteClient to enable seamless integration of
    local language models into ComfyUI workflows. It supports both simple prompts
    and conversation continuations through chat history management.
    
    Features:
    - Connect to any llama.cpp server via URL
    - Send text prompts with optional system prompts
    - Maintain conversation history across multiple calls
    - Return both the response message and full chat history
    - Professional error handling and logging
    - Forced execution as output node
    
    Inputs:
    - server_url (required): URL of the llama.cpp server (e.g., "http://localhost:8080/v1")
    - prompt (required): The user's text prompt to send to the model
    - system_prompt (optional): System-level instruction for the model behavior
    - chat_history (optional): JSON string of previous conversation messages
    - image1-5 (optional): Up to 5 ComfyUI image inputs for multimodal processing
    
    Outputs:
    - response_message: The model's response as a plain string
    - chat_history: Complete conversation history as a JSON string
    """
    
    # Node metadata for ComfyUI
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response_message", "chat_history")
    FUNCTION = "execute_llama_chat"
    CATEGORY = "LlamaLite"
    OUTPUT_NODE = True  # Force execution even if this is the only node
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define the input types and configuration for the ComfyUI interface.
        
        This method specifies what inputs the node accepts, their types,
        default values, and validation rules. ComfyUI uses this information
        to generate the appropriate UI elements.
        
        Returns:
            Dict[str, Dict[str, Any]]: Configuration dictionary defining:
                - required: Inputs that must be provided
                - optional: Inputs that have default values
        """
        return {
            "required": {
                "server_url": (
                    "STRING", 
                    {
                        "default": "http://localhost:8080/v1",
                        "multiline": False,
                        "tooltip": "URL of the llama.cpp server endpoint"
                    }
                ),
                "prompt": (
                    "STRING", 
                    {
                        "default": "Hello! How are you today?",
                        "multiline": True,
                        "tooltip": "The text prompt to send to the language model"
                    }
                ),
            },
            "optional": {
                "system_prompt": (
                    "STRING", 
                    {
                        "default": "You are a helpful AI assistant.",
                        "multiline": True,
                        "tooltip": "System message that defines the model's behavior and role"
                    }
                ),
                "chat_history": (
                    "STRING", 
                    {
                        "default": "[]",
                        "multiline": True,
                        "tooltip": "JSON string containing previous conversation messages"
                    }
                ),
                "image1": (
                    "IMAGE",
                    {
                        "tooltip": "Optional image input 1"
                    }
                ),
                "image2": (
                    "IMAGE",
                    {
                        "tooltip": "Optional image input 2"
                    }
                ),
                "image3": (
                    "IMAGE",
                    {
                        "tooltip": "Optional image input 3"
                    }
                ),
                "image4": (
                    "IMAGE",
                    {
                        "tooltip": "Optional image input 4"
                    }
                ),
                "image5": (
                    "IMAGE",
                    {
                        "tooltip": "Optional image input 5"
                    }
                ),
            }
        }
    
    def __init__(self):
        """
        Initialize the LlamaLiteNode.
        
        Sets up logging and initializes any necessary instance variables.
        The actual LlamaLiteClient is created per execution to allow for
        different server URLs in the same workflow.
        """
        logger.info("LlamaLiteNode initialized")
        self._client_cache = {}  # Cache clients by server URL for efficiency
    
    def open_comfy_image(self, tensor: torch.Tensor) -> Image.Image:
        """
        Convert a ComfyUI image tensor to a PIL Image.
        """
        try:
            image = tensor[0]
            image = image * 255
            image = image.clamp(0, 255).to(torch.uint8)
            image_np = image.cpu().numpy()
            pil_image = Image.fromarray(image_np, 'RGB')
            return pil_image
        except Exception as e:
            logger.error(f"Error opening tensor image: {e}")
            raise
    
    def _get_client(self, server_url: str) -> LlamaLiteClient:
        """
        Get or create a LlamaLiteClient for the specified server URL.
        
        This method implements client caching to avoid recreating clients
        for the same server URL, improving performance in workflows with
        multiple calls to the same server.
        
        Args:
            server_url (str): The base URL of the llama.cpp server
            
        Returns:
            LlamaLiteClient: Configured client instance
        """
        if server_url not in self._client_cache:
            logger.info(f"Creating new LlamaLiteClient for server: {server_url}")
            self._client_cache[server_url] = LlamaLiteClient(base_url=server_url)
        return self._client_cache[server_url]
    
    def _parse_chat_history(self, chat_history_str: str) -> List[Dict[str, Any]]:
        """
        Parse and validate the chat history JSON string.
        
        Safely converts the input chat history string into a list of message
        dictionaries, with comprehensive error handling and validation.
        
        Args:
            chat_history_str (str): JSON string representation of chat history
            
        Returns:
            List[Dict[str, Any]]: Parsed and validated chat history
            
        Raises:
            ValueError: If the chat history format is invalid
        """
        if not chat_history_str or chat_history_str.strip() == "":
            return []
        
        try:
            chat_history = json.loads(chat_history_str)
            
            # Validate that it's a list
            if not isinstance(chat_history, list):
                raise ValueError("Chat history must be a JSON array")
            
            # Validate each message structure
            for i, message in enumerate(chat_history):
                if not isinstance(message, dict):
                    raise ValueError(f"Message {i} must be a dictionary")
                
                if "role" not in message or "content" not in message:
                    raise ValueError(f"Message {i} must have 'role' and 'content' fields")
                
                valid_roles = {"system", "user", "assistant"}
                if message["role"] not in valid_roles:
                    raise ValueError(f"Message {i} has invalid role: {message['role']}. Must be one of {valid_roles}")
            
            logger.info(f"Successfully parsed chat history with {len(chat_history)} messages")
            return chat_history
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in chat_history: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error parsing chat_history: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _format_chat_history_output(self, response_data: Dict[str, Any], 
                                  input_chat_history: List[Dict[str, Any]]) -> str:
        """
        Format the complete chat history for output.
        
        Combines the input chat history with the new response to create
        a complete conversation record that can be used in subsequent calls.
        
        Args:
            response_data (Dict[str, Any]): Response from the llama.cpp server
            input_chat_history (List[Dict[str, Any]]): Original chat history
            
        Returns:
            str: JSON string of the complete chat history
        """
        try:
            # Start with the input chat history
            complete_history = input_chat_history.copy()
            
            # Extract the new messages from the response
            # The response contains the complete messages array including the new assistant response
            if hasattr(response_data, 'choices') and len(response_data.choices) > 0:
                choice = response_data.choices[0]
                if hasattr(choice, 'message'):
                    assistant_message = {
                        "role": "assistant",
                        "content": choice.message.content
                    }
                    complete_history.append(assistant_message)
            
            return json.dumps(complete_history, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error formatting chat history output: {str(e)}")
            # Return the input history as fallback
            return json.dumps(input_chat_history, indent=2, ensure_ascii=False)
    
    def execute_llama_chat(self, server_url: str, prompt: str, 
                          system_prompt: Optional[str] = None, 
                          chat_history: Optional[str] = None,
                          image1: Optional[torch.Tensor] = None,
                          image2: Optional[torch.Tensor] = None,
                          image3: Optional[torch.Tensor] = None,
                          image4: Optional[torch.Tensor] = None,
                          image5: Optional[torch.Tensor] = None) -> Tuple[str, str]:
        """
        Execute the main chat functionality.
        
        This is the primary method called by ComfyUI when the node is executed.
        It coordinates all the components: client creation, input validation,
        API call, and output formatting.
        
        Args:
            server_url (str): URL of the llama.cpp server
            prompt (str): User's text prompt
            system_prompt (Optional[str]): Optional system instruction
            chat_history (Optional[str]): Optional JSON string of chat history
            image1 (Optional[torch.Tensor]): Optional image input 1
            image2 (Optional[torch.Tensor]): Optional image input 2
            image3 (Optional[torch.Tensor]): Optional image input 3
            image4 (Optional[torch.Tensor]): Optional image input 4
            image5 (Optional[torch.Tensor]): Optional image input 5
            
        Returns:
            Tuple[str, str]: (response_message, formatted_chat_history)
            
        Raises:
            Exception: For any errors during execution (logged and re-raised)
        """
        try:
            logger.info(f"Executing LlamaLite chat with server: {server_url}")
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            # Process images if provided
            processed_images = []
            for i, image_tensor in enumerate([image1, image2, image3, image4, image5], 1):
                if image_tensor is not None:
                    logger.info(f"Processing image {i}")
                    pil_image = self.open_comfy_image(image_tensor)
                    processed_images.append(pil_image)
            
            if processed_images:
                logger.info(f"Total images provided: {len(processed_images)}")
            
            # Input validation
            if not server_url or not server_url.strip():
                raise ValueError("server_url cannot be empty")
            
            if not prompt or not prompt.strip():
                raise ValueError("prompt cannot be empty")
            
            # Get or create client for this server
            client = self._get_client(server_url.strip())
            
            # Parse chat history
            parsed_chat_history = []
            if chat_history and chat_history.strip():
                parsed_chat_history = self._parse_chat_history(chat_history.strip())
            
            # Prepare parameters for the chat call
            chat_params = {
                "prompt": prompt.strip(),
                "chat_history": parsed_chat_history,
            }
            
            # Add system prompt if provided
            if system_prompt and system_prompt.strip():
                chat_params["system_prompt"] = system_prompt.strip()
            
            # Add images if provided
            if processed_images:
                chat_params["images"] = processed_images
            
            logger.info("Sending request to llama.cpp server...")
            
            # Make the API call
            response = client.chat(**chat_params)
            
            # Extract the response message
            if not hasattr(response, 'choices') or len(response.choices) == 0:
                raise ValueError("Invalid response from server: no choices found")
            
            choice = response.choices[0]
            if not hasattr(choice, 'message') or not hasattr(choice.message, 'content'):
                raise ValueError("Invalid response from server: no message content found")
            
            response_message = choice.message.content
            logger.info(f"Received response with {len(response_message)} characters")
            
            # Format the complete chat history for output
            formatted_chat_history = self._format_chat_history_output(response, parsed_chat_history)
            
            logger.info("LlamaLite chat execution completed successfully")
            
            return (response_message, formatted_chat_history)
            
        except Exception as e:
            error_msg = f"Error in LlamaLite chat execution: {str(e)}"
            logger.error(error_msg)
            
            # Return error information in a user-friendly format
            error_response = f"Error: {str(e)}"
            error_history = json.dumps([
                {
                    "role": "system", 
                    "content": f"Error occurred: {str(e)}"
                }
            ], indent=2)
            
            return (error_response, error_history)


# Node mapping for ComfyUI registration
# This dictionary tells ComfyUI how to register and display the node
NODE_CLASS_MAPPINGS = {
    "LlamaLiteNode": LlamaLiteNode
}

# Display names for better user experience in ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS = {
    "LlamaLiteNode": "LlamaLite Chat"
}

# Additional metadata for package management
__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "ComfyUI custom node for llama.cpp server integration"

# Export the main class for direct imports
__all__ = ["LlamaLiteNode", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
