from langchain_text_splitters import CharacterTextSplitter


def character_text_splitter(docs):
    """
    문서 분할 메서드

    Args:
        docs: 분할할 문서

    Returns:
        CharacterTextSplitter 객체
    """
    print("Splitting documents")
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    print("Split documents Ended")

    return text_splitter.split_documents(docs)
