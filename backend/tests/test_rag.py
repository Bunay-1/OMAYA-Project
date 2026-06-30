import pytest
import os
import shutil
from backend.RAG.rag_logic import RAGManager

@pytest.fixture
def temp_rag_manager():
    storage = "backend/RAG/test_documents"
    index = "backend/RAG/test_faiss_index"
    if os.path.exists(storage): shutil.rmtree(storage)
    if os.path.exists(index): shutil.rmtree(index)
    os.makedirs(storage)

    manager = RAGManager(storage_path=storage, index_path=index)
    yield manager

    if os.path.exists(storage): shutil.rmtree(storage)
    if os.path.exists(index): shutil.rmtree(index)

def test_rag_manager_stats(temp_rag_manager):
    stats = temp_rag_manager.get_stats()
    assert stats["indexed_files"] == 0
    assert "odt" in stats["supported_formats"]

def test_rag_manager_indexing(temp_rag_manager):
    # Add a sample file
    test_file = os.path.join(temp_rag_manager.storage_path, "test.txt")
    with open(test_file, "w") as f:
        f.write("OMAYA is an industrial monitoring platform.")

    new_files, new_chunks = temp_rag_manager.index_files()
    assert new_files == 1
    assert new_chunks > 0

    stats = temp_rag_manager.get_stats()
    assert stats["indexed_files"] == 1
    assert stats["total_chunks"] == new_chunks

def test_rag_manager_query(temp_rag_manager):
    test_file = os.path.join(temp_rag_manager.storage_path, "test.txt")
    with open(test_file, "w") as f:
        f.write("OMAYA uses FAISS for vector storage.")

    temp_rag_manager.index_files()
    results = temp_rag_manager.query("What does OMAYA use for storage?")

    assert len(results) > 0
    assert "FAISS" in results[0]["content"]
