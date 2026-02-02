import sys
print(f"Python executable: {sys.executable}")
try:
    import langfuse
    print(f"Langfuse version: {langfuse.version.__version__}")
    print(f"Langfuse file: {langfuse.__file__}")
except ImportError as e:
    print(f"Error importing langfuse: {e}")

try:
    from langfuse.llama_index import LlamaIndexInstrumentor
    print("Successfully imported LlamaIndexInstrumentor")
except ImportError as e:
    print(f"Error importing LlamaIndexInstrumentor: {e}")
