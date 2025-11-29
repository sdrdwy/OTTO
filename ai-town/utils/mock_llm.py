"""
Mock LLM for testing purposes
"""
import random
from langchain_core.messages import AIMessage


class MockChatOpenAI:
    """Mock ChatOpenAI for testing without API key"""
    
    def __init__(self, *args, **kwargs):
        self.responses = [
            "That's an interesting point. From my perspective, this topic has many facets worth exploring.",
            "I think there are several ways to approach this. First, we should consider the fundamental principles involved.",
            "Based on what we know, the most important aspect is understanding the underlying mechanisms.",
            "In my experience, the key is to balance multiple perspectives when considering this issue.",
            "This reminds me of similar concepts in other fields. The connections are quite fascinating.",
            "A thoughtful analysis reveals that context is crucial when discussing this topic.",
            "From an educational standpoint, it's important to build knowledge progressively.",
            "The interplay between different elements creates a complex but understandable system.",
            "Historical examples provide valuable insights into how we might approach this today.",
            "Looking at this from multiple angles helps form a more complete understanding."
        ]

    def invoke(self, messages):
        # Return a random response from our list
        response_text = random.choice(self.responses)
        return AIMessage(content=response_text)