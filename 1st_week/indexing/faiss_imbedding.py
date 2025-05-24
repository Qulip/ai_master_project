from langchain_community.vectorstores import FAISS
import os
from conf.settings import get_embeddings


def create_faiss_vector_store(documents):
    """
    벡터스토어 생성 메서드

    Args:
        documents: 저장할 문서
        embeddings: 사용할 임베딩 객체

    Returns:
        FAISS 벡터스토어 객체
    """
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(documents, embedding=get_embeddings())
    print("FAISS vector store created successfully")
    return vectorstore


def save_faiss_vector_store(vectorstore, folder_path):
    """
    벡터스토어 로컬 폴더 저장 메서드

    Args:
        vectorstore: 저장할 FAISS 벡터스토어
        folder_path: 저장할 폴더 경로
    """
    print(f"Saving FAISS vector store to {folder_path}...")
    os.makedirs(folder_path, exist_ok=True)
    vectorstore.save_local(folder_path)
    print(f"FAISS vector store saved successfully to {folder_path}")


def load_faiss_vector_store(folder_path):
    """
    로컬 폴더의 벡터스토어 로드 메서드

    Args:
        folder_path: 로드할 폴더 경로

    Returns:
        FAISS 벡터스토어 객체
    """
    embeddings = get_embeddings()
    print(f"Loading FAISS vector store from {folder_path}...")
    vectorstore = FAISS.load_local(
        folder_path, embeddings, allow_dangerous_deserialization=True
    )
    print(f"FAISS vector store loaded successfully from {folder_path}")
    return vectorstore


def search_faiss_vector_store(vectorstore, query, k=5):
    """
    벡터스토어 검색 메서드

    Args:
        vectorstore: 검색할 FAISS 벡터스토어
        query: 검색할 질의

    Returns:
        similarity_search_results: 유사도 검색 결과
        similarity_search_with_score_results: 유사도 검색 결과 (점수 포함)
    """

    print(f"Searching FAISS vector store for query: {query}")
    print("Similarity Search Started")
    similarity_search_results = vectorstore.similarity_search(query, k=k)
    print(f"Found {len(similarity_search_results)} results")

    for rst in similarity_search_results:
        print(f"* {rst.page_content[:100]} | {rst.metadata}")

    print("Similarity Search With Scroe Started")
    similarity_search_with_score_results = vectorstore.similarity_search_with_score(
        query, k=k
    )
    print(f"Found {len(similarity_search_with_score_results)} results")

    for rst, score in similarity_search_with_score_results:
        print(f"* {rst.page_content[:100]} | {rst.metadata} | {score}")

    dict = {
        "similarity_search_results": similarity_search_results,
        "similarity_search_with_score_results": similarity_search_with_score_results,
    }

    return dict
