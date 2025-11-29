"""
Qwen LLM Wrapper for using Alibaba Cloud's Qwen model
"""
import os
from typing import List
from langchain_core.messages import BaseMessage, AIMessage
from dashscope import Generation


class QwenChatModel:
    """Wrapper for Qwen model from Alibaba Cloud"""
    
    def __init__(self, model_name: str = "qwen-max", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is required for Qwen model")
    
    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """
        Invoke the Qwen model with the given messages
        """
        # Convert LangChain messages to the format expected by DashScope
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, 'content'):
                role = 'user' if hasattr(msg, '__class__') and 'HumanMessage' in str(msg.__class__) else 'system'
                if 'SystemMessage' in str(msg.__class__):
                    role = 'system'
                elif 'AIMessage' in str(msg.__class__):
                    role = 'assistant'
                else:
                    role = 'user'
                formatted_messages.append({
                    'role': role,
                    'content': msg.content
                })
        
        # Make the API call to Qwen
        try:
            response = Generation.call(
                model=self.model_name,
                messages=formatted_messages,
                api_key=self.api_key,
                temperature=self.temperature,
                result_format='message'  # Enable streaming and get detailed response
            )
            
            if response.status_code == 200:
                # Extract the content from the response
                content = response.output.choices[0].message.content
                return AIMessage(content=content)
            else:
                # Fallback to mock response if API call fails
                return AIMessage(content="I'm having trouble connecting to the Qwen service. Please check your API key and connection.")
                
        except Exception as e:
            # Handle any errors and return a fallback response
            print(f"Error calling Qwen API: {e}")
            return AIMessage(content="I encountered an error while processing your request. Please try again later.")