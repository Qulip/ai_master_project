from parsing.load_pdf import load_pdf
from chunking.character_text_splitter import character_text_splitter
from indexing.faiss_imbedding import (
    create_faiss_vector_store,
    save_faiss_vector_store,
    load_faiss_vector_store,
    search_faiss_vector_store,
)
import os
from graph.graph import create_graph
from core.state import State


def pdf_text_splitter_faiss_indexing(query):
    """
    PDF 파일 로드 후 문자 단위로 분할하여 FAISS 벡터 스토어에 저장 및 질의 결과 노출 메서드

    Args:
        query: 검색할 질의
    """

    if os.path.exists("faiss/pdf_faiss_index"):
        vectorstore = load_faiss_vector_store("faiss/pdf_faiss_index")
    else:
        docs = load_pdf()
        chunks = character_text_splitter(docs)
        vectorstore = create_faiss_vector_store(chunks)
        save_faiss_vector_store(vectorstore, "faiss/pdf_faiss_index")

    rst = search_faiss_vector_store(vectorstore, query)

    graph = create_graph()

    state = State(query=query, context=rst, messages=[], response="")

    llm_state = graph.invoke(state)

    print(llm_state["response"])


def __main__():
    pdf_text_splitter_faiss_indexing("2025 고용 전망은 어떠한가?")

    # graph = create_graph()

    # graph_image = graph.get_graph().draw_mermaid_png()

    # output_path = "debate_graph.png"
    # with open(output_path, "wb") as f:
    #     f.write(graph_image)


if __name__ == "__main__":
    __main__()
