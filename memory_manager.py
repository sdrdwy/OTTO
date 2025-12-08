import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


class MemoryManager:
    def __init__(self, memory_file: str = "memory.jsonl"):
        self.memory_file = memory_file
        self.memories = []
        self.load_memories()
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize vector store for semantic search
        self.vector_store = None
        self.update_vector_store()
    
    def load_memories(self):
        """Load memories from the JSONL file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.memories.append(json.loads(line.strip()))
    
    def save_memories(self):
        """Save memories to the JSONL file"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            for memory in self.memories:
                f.write(json.dumps(memory) + '\n')
    
    def add_memory(self, memory: Dict[str, Any]):
        """Add a new memory with access count and timestamp"""
        memory["timestamp"] = datetime.now().isoformat()
        memory["access_count"] = memory.get("access_count", 0) + 1
        self.memories.append(memory)
        self.save_memories()
        
        # Update vector store with the new memory
        self.update_vector_store()
    
    def update_vector_store(self):
        """Update the vector store with all memories"""
        documents = []
        for memory in self.memories:
            content = memory.get("content", "")
            if content:
                doc = Document(
                    page_content=content,
                    metadata={
                        "agent_id": memory.get("agent_id"),
                        "day": memory.get("day"),
                        "time_period": memory.get("time_period"),
                        "type": memory.get("type"),
                        "timestamp": memory.get("timestamp"),
                        "access_count": memory.get("access_count", 0)
                    }
                )
                documents.append(doc)
        
        if documents:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
    
    def search_memories(self, query: str, agent_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories based on query, agent, and limit using semantic search"""
        if self.vector_store is None:
            # Fallback to simple search if vector store is not available
            results = []
            for memory in self.memories:
                if agent_id and memory.get("agent_id") != agent_id:
                    continue
                if query.lower() in memory.get("content", "").lower():
                    results.append(memory)
            # Sort by access count (descending)
            results.sort(key=lambda x: x.get("access_count", 0), reverse=True)
            return results[:limit]
        
        # Use semantic search
        docs = self.vector_store.similarity_search(query, k=limit*2)  # Get more results to filter
        
        results = []
        for doc in docs:
            memory = {
                "content": doc.page_content,
                "agent_id": doc.metadata.get("agent_id"),
                "day": doc.metadata.get("day"),
                "time_period": doc.metadata.get("time_period"),
                "type": doc.metadata.get("type"),
                "timestamp": doc.metadata.get("timestamp"),
                "access_count": doc.metadata.get("access_count", 0)
            }
            
            # Apply agent filter if specified
            if agent_id and memory["agent_id"] != agent_id:
                continue
                
            # Add to results if not already present
            if memory not in results:
                results.append(memory)
        
        # Sort by access count (descending) to prioritize frequently accessed memories
        results.sort(key=lambda x: x["access_count"], reverse=True)
        
        return results[:limit]
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]):
        """Update an existing memory"""
        for i, memory in enumerate(self.memories):
            if memory.get("id") == memory_id:
                self.memories[i].update(updates)
                self.memories[i]["access_count"] = self.memories[i].get("access_count", 0) + 1
                self.save_memories()
                
                # Update vector store
                self.update_vector_store()
                return True
        return False