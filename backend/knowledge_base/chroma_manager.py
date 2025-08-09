import chromadb
from chromadb.config import Settings
import json
import uuid
from typing import Dict, Any, List, Optional
import os

class ChromaManager:
    """Manage ChromaDB operations for knowledge base storage and retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"description": "File-based knowledge base for dashboard generation"}
        )
    
    def store_file_context(self, context_data: Dict[str, Any]) -> str:
        """
        Store file context in ChromaDB
        
        Args:
            context_data: Generated context from ContextExtractor
            
        Returns:
            str: Document ID for the stored context
        """
        doc_id = str(uuid.uuid4())
        
        # Prepare documents for embedding
        documents = []
        metadatas = []
        ids = []
        
        # Store table description
        documents.append(f"Table: {context_data['file_info']['file_name']}\n{context_data['table_description']}")
        metadatas.append({
            "type": "table_description",
            "file_name": context_data['file_info']['file_name'],
            "file_path": context_data['file_info']['file_path'],
            "doc_id": doc_id
        })
        ids.append(f"{doc_id}_table")
        
        # Store column insights
        for i, col_insight in enumerate(context_data['column_insights']):
            documents.append(f"Column: {col_insight['column_name']}\n{col_insight['insight']}")
            metadatas.append({
                "type": "column_insight",
                "file_name": context_data['file_info']['file_name'],
                "column_name": col_insight['column_name'],
                "data_type": col_insight['data_type'],
                "doc_id": doc_id
            })
            ids.append(f"{doc_id}_col_{i}")
        
        # Store business context
        documents.append(f"Business Context: {context_data['file_info']['file_name']}\n{context_data['business_context']}")
        metadatas.append({
            "type": "business_context",
            "file_name": context_data['file_info']['file_name'],
            "doc_id": doc_id
        })
        ids.append(f"{doc_id}_business")
        
        # Store query suggestions
        query_suggestions_text = "\n".join(context_data['query_suggestions'])
        documents.append(f"Query Suggestions: {context_data['file_info']['file_name']}\n{query_suggestions_text}")
        metadatas.append({
            "type": "query_suggestions",
            "file_name": context_data['file_info']['file_name'],
            "doc_id": doc_id
        })
        ids.append(f"{doc_id}_queries")
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Store complete context as metadata for retrieval
        self._store_complete_context(doc_id, context_data)
        
        return doc_id
    
    def query_relevant_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query ChromaDB for relevant context based on user prompt
        
        Args:
            query: User's natural language query
            n_results: Number of results to return
            
        Returns:
            List of relevant context documents
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        relevant_contexts = []
        for i, doc in enumerate(results['documents'][0]):
            relevant_contexts.append({
                "document": doc,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        
        return relevant_contexts
    
    def get_file_context(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete context for a specific file
        
        Args:
            file_name: Name of the file to get context for
            
        Returns:
            Complete context data or None if not found
        """
        results = self.collection.query(
            query_texts=[f"file:{file_name}"],
            where={"file_name": file_name},
            n_results=1
        )
        
        if results['documents'][0]:
            doc_id = results['metadatas'][0][0]['doc_id']
            return self._get_complete_context(doc_id)
        
        return None
    
    def list_available_files(self) -> List[Dict[str, str]]:
        """
        List all files in the knowledge base
        
        Returns:
            List of file information
        """
        # Get all unique files from metadata
        all_results = self.collection.get()
        
        files = {}
        for metadata in all_results['metadatas']:
            file_name = metadata.get('file_name')
            if file_name and file_name not in files:
                files[file_name] = {
                    'file_name': file_name,
                    'file_path': metadata.get('file_path', ''),
                    'doc_id': metadata.get('doc_id')
                }
        
        return list(files.values())
    
    def delete_file_context(self, file_name: str) -> bool:
        """
        Delete all context for a specific file
        
        Args:
            file_name: Name of the file to delete
            
        Returns:
            bool: Success status
        """
        try:
            # Get all documents for this file
            results = self.collection.get(
                where={"file_name": file_name}
            )
            
            if results['ids']:
                # Delete from ChromaDB
                self.collection.delete(ids=results['ids'])
                
                # Delete complete context file
                doc_id = results['metadatas'][0]['doc_id']
                context_file = os.path.join(self.persist_directory, f"{doc_id}_context.json")
                if os.path.exists(context_file):
                    os.remove(context_file)
                
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting file context: {e}")
            return False
    
    def _store_complete_context(self, doc_id: str, context_data: Dict[str, Any]):
        """Store complete context data as JSON file for full retrieval"""
        context_file = os.path.join(self.persist_directory, f"{doc_id}_context.json")
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2, default=str)
    
    def _get_complete_context(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete context data from JSON file"""
        context_file = os.path.join(self.persist_directory, f"{doc_id}_context.json")
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                return json.load(f)
        return None