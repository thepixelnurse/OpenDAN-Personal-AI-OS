import os

from .object import ObjectStore, ObjectRelationStore
from .data import ChunkStore, ChunkTracker, ChunkListWriter, ChunkReader
from .vector import ChromaVectorStore, VectorBase
import logging
import aios_kernel

# KnowledgeStore class, which aggregates ChunkStore, ChunkTracker, and ObjectStore, and is a global singleton that makes it easy to use these three built-in store examples
class KnowledgeStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            knowledge_dir = aios_kernel.storage.AIStorage().get_myai_dir() / "knowledge"

            if not os.path.exists(knowledge_dir):
                os.makedirs(knowledge_dir)

            cls._instance.__singleton_init__(knowledge_dir)

        return cls._instance

    def __singleton_init__(self, root_dir: str):
        logging.info(f"will init knowledge store, root_dir={root_dir}")

        self.root = root_dir

        relation_store_dir = os.path.join(root_dir, "relation")
        self.relation_store = ObjectRelationStore(relation_store_dir)

        object_store_dir = os.path.join(root_dir, "object")
        self.object_store = ObjectStore(object_store_dir)

        chunk_store_dir = os.path.join(root_dir, "chunk")
        self.chunk_store = ChunkStore(chunk_store_dir)
        self.chunk_tracker = ChunkTracker(chunk_store_dir)
        self.chunk_list_writer = ChunkListWriter(self.chunk_store, self.chunk_tracker)
        self.chunk_reader = ChunkReader(self.chunk_store, self.chunk_tracker)
        self.vector_store = {}
    
    def get_relation_store(self) -> ObjectRelationStore:
        return self.relation_store

    def get_object_store(self) -> ObjectStore:
        return self.object_store

    def get_chunk_store(self) -> ChunkStore:
        return self.chunk_store

    def get_chunk_tracker(self) -> ChunkTracker:
        return self.chunk_tracker
    
    def get_chunk_list_writer(self) -> ChunkListWriter:
        return self.chunk_list_writer
    
    def get_chunk_reader(self) -> ChunkReader:
        return self.chunk_reader
    
    def get_vector_store(self, model_name: str) -> VectorBase:
        if model_name not in self.vector_store:
            self.vector_store[model_name] = ChromaVectorStore(model_name)
        return self.vector_store[model_name]
