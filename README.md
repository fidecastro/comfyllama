# ComfyLlama - ComfyUI Node for LlamaLite Integration

A professional-grade ComfyUI custom node that provides seamless integration with llama.cpp servers, enabling you to use local language models directly in your ComfyUI workflows.

## 🚀 Features

- **Easy Integration**: Connect to any llama.cpp server with a simple URL
- **Conversation History**: Maintain context across multiple interactions
- **System Prompts**: Configure model behavior with system-level instructions
- **Professional Error Handling**: Comprehensive logging and graceful error recovery
- **Output Node**: Automatically executes even as a standalone node
- **Caching**: Efficient client caching for improved performance
- **Well-Documented**: Extensive documentation and tooltips for all parameters

## 📋 Requirements

- ComfyUI installed and running
- Python 3.8+
- A running llama.cpp server (local or remote)

### Dependencies

- `openai` - For API communication
- `httpx` - HTTP client with better connection management
- `pillow` - Image processing (if using vision models)

## 🛠️ Installation

### Method 1: Direct Installation

1. **Clone or download** this repository to your ComfyUI custom nodes directory:
   ```bash
   cd /path/to/ComfyUI/custom_nodes/
   git clone https://github.com/your-repo/comfyllama.git
   # OR download and extract the ZIP file
   ```

2. **Install dependencies**:
   ```bash
   cd comfyllama
   pip install -r requirements.txt
   ```

3. **Restart ComfyUI** to load the new nodes.

### Method 2: Manual Installation

1. **Copy the package** to your ComfyUI custom_nodes directory:
   ```
   ComfyUI/
   └── custom_nodes/
       └── comfyllama/
           ├── __init__.py
           ├── comfy_llama_node.py
           ├── llamalite.py
           ├── requirements.txt
           └── README.md
   ```

2. **Install dependencies** using pip:
   ```bash
   pip install openai httpx pillow
   ```

3. **Restart ComfyUI**.

## 🎯 Usage

### Setting up a llama.cpp Server

Before using the ComfyLlama node, you need a running llama.cpp server:

```bash
# Example: Running llama.cpp server
./server -m your-model.gguf -c 4096 --host 0.0.0.0 --port 8080
```

The server will be available at `http://localhost:8080/v1` by default.

### Using the LlamaLite Chat Node

1. **Add the Node**: In ComfyUI, look for "LlamaLite Chat" in the "LlamaLite" category.

2. **Configure Inputs**:
   - **server_url** (required): URL of your llama.cpp server (e.g., `http://localhost:8080/v1`)
   - **prompt** (required): Your text prompt for the model
   - **system_prompt** (optional): System instruction to define model behavior
   - **chat_history** (optional): JSON string of previous conversation messages

3. **Connect Outputs**:
   - **response_message**: The model's response as plain text
   - **chat_history**: Complete conversation history as JSON string

### Example Workflows

#### Simple Text Generation

```
[Text Input] → [LlamaLite Chat] → [Text Output]
```

#### Conversation with History

```
[Text Input] → [LlamaLite Chat] → [Text Output]
              ↗               ↘
[History Input]               [History Output] → [Next LlamaLite Chat]
```

#### System-Prompted Assistant

```
[System Prompt: "You are a helpful coding assistant"]
[User Prompt: "Explain Python decorators"]
                     ↓
              [LlamaLite Chat] → [Response Text]
```

## 🔧 Configuration

### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | STRING | Yes | `http://localhost:8080/v1` | URL of the llama.cpp server endpoint |
| `prompt` | STRING | Yes | `Hello! How are you today?` | The text prompt to send to the model |
| `system_prompt` | STRING | No | `You are a helpful AI assistant.` | System message defining model behavior |
| `chat_history` | STRING | No | `[]` | JSON array of previous conversation messages |

### Chat History Format

The chat history should be a JSON array of message objects:

```json
[
  {
    "role": "system",
    "content": "You are a helpful assistant."
  },
  {
    "role": "user", 
    "content": "What is the capital of France?"
  },
  {
    "role": "assistant",
    "content": "The capital of France is Paris."
  }
]
```

Valid roles: `system`, `user`, `assistant`

## 🐛 Troubleshooting

### Common Issues

1. **"Error: Connection refused"**
   - Ensure your llama.cpp server is running
   - Check the server URL is correct
   - Verify the server is accessible from ComfyUI

2. **"Invalid JSON in chat_history"**
   - Ensure chat history is valid JSON
   - Check that all messages have "role" and "content" fields
   - Verify roles are one of: system, user, assistant

3. **"No response from server"**
   - Check server logs for errors
   - Ensure the model is loaded properly
   - Verify server has sufficient resources

### Debug Information

The node provides detailed logging. Check the ComfyUI console for:
- Connection status messages
- Request/response information
- Error details and stack traces

## 🔍 Advanced Usage

### Custom Server Configurations

For non-standard server configurations, modify the server URL:

```python
# Different port
server_url = "http://localhost:8081/v1"

# Remote server
server_url = "http://192.168.1.100:8080/v1"

# HTTPS server
server_url = "https://your-domain.com/v1"
```

### Error Handling in Workflows

The node handles errors gracefully:
- Connection errors return error messages in the response
- Invalid inputs are validated with clear error messages
- Chat history issues are logged and handled safely

### Performance Optimization

- **Client Caching**: Clients are cached per server URL for efficiency
- **Connection Pooling**: Uses httpx for optimized HTTP connections
- **Memory Management**: Proper cleanup of resources

## 🛡️ Security Considerations

- **Local Servers**: Use `localhost` URLs for local servers
- **Remote Servers**: Ensure secure connections (HTTPS) for remote servers
- **API Keys**: No API keys are required for standard llama.cpp servers
- **Input Validation**: All inputs are validated before processing

## 📚 API Reference

### LlamaLiteNode Class

The main ComfyUI node class that provides the interface.

#### Methods

- `INPUT_TYPES()`: Defines the ComfyUI input configuration
- `execute_llama_chat()`: Main execution method
- `_get_client()`: Client factory with caching
- `_parse_chat_history()`: Chat history validation and parsing
- `_format_chat_history_output()`: Output formatting

### LlamaLiteClient Class

The underlying client for llama.cpp communication.

#### Methods

- `chat()`: Send a chat completion request
- `_pil_image_to_base64()`: Convert images for vision models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **llama.cpp**: For providing the server implementation
- **ComfyUI**: For the excellent workflow framework
- **OpenAI**: For the API standard and Python client

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review ComfyUI console logs
3. Open an issue on GitHub with:
   - ComfyUI version
   - llama.cpp server version
   - Error messages and logs
   - Steps to reproduce

---

**Happy prompting with ComfyLlama! 🦙✨**
