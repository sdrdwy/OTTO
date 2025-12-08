import json
import os
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class KnowledgeBase:
    def __init__(self, knowledge_file: str = "knowledge.jsonl"):
        self.knowledge_file = knowledge_file
        self.knowledge = []
        self.load_knowledge()
        
        # Initialize LangChain components
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize vector store for semantic search
        self.vector_store = None
        self.update_vector_store()
    
    def load_knowledge(self):
        """Load knowledge from the JSONL file"""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.knowledge.append(json.loads(line.strip()))
    
    def update_vector_store(self):
        """Update the vector store with all knowledge"""
        documents = []
        for item in self.knowledge:
            content = item.get("content", "")
            if content:
                doc = Document(
                    page_content=content,
                    metadata={
                        "topic": item.get("topic"),
                        "subtopic": item.get("subtopic"),
                        "difficulty": item.get("difficulty"),
                        "source": item.get("source")
                    }
                )
                documents.append(doc)
        
        if documents:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
    
    def get_topics(self) -> List[str]:
        """Get all available topics in the knowledge base"""
        topics = set()
        for item in self.knowledge:
            if "topic" in item:
                topics.add(item["topic"])
        return list(topics)
    
    def get_knowledge_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get knowledge items by topic"""
        return [item for item in self.knowledge if item.get("topic") == topic]
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge based on query using semantic search"""
        if self.vector_store is None:
            # Fallback to simple search if vector store is not available
            results = []
            query_lower = query.lower()
            
            for item in self.knowledge:
                if query_lower in item.get("content", "").lower() or query_lower in item.get("topic", "").lower():
                    results.append(item)
            
            return results
        
        # Use semantic search
        docs = self.vector_store.similarity_search(query, k=10)  # Get top 10 results
        
        results = []
        for doc in docs:
            item = {
                "content": doc.page_content,
                "topic": doc.metadata.get("topic"),
                "subtopic": doc.metadata.get("subtopic"),
                "difficulty": doc.metadata.get("difficulty"),
                "source": doc.metadata.get("source")
            }
            
            # Add to results if not already present
            if item not in results:
                results.append(item)
        
        return results