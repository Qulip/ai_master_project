from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import os


load_dotenv()


class config:
    AOAI_API_KEY: str = os.getenv("AOAI_API_KEY")
    AOAI_ENDPOINT: str = os.getenv("AOAI_ENDPOINT")

    def get_llm(self):
        return AzureChatOpenAI(
            openai_api_key=self.AOAI_API_KEY,
            azure_endpoint=self.AOAI_ENDPOINT,
            azure_deployment="gpt-4o",
            # api_version="2024-05-01-preview",
            # temperature=0.7,
            streaming=True,
        )

    def get_embeddings(self):
        return AzureOpenAIEmbeddings(
            model="text-embedding-3-large",
            # openai_api_version=self.AOAI_API_VERSION,
            api_key=self.AOAI_API_KEY,
            azure_endpoint=self.AOAI_ENDPOINT,
        )


config = config()


def get_llm():
    """
    Azure OpenAI LLM 인스턴스 반환 메서드

    Returns:
        AzureChatOpenAI 객체
    """
    return config.get_llm()


def get_embeddings():
    """
    Azure OpenAI Embeddings 인스턴스 반환 메서드

    Returns:
        AzureOpenAIEmbeddings 객체
    """
    return config.get_embeddings()
