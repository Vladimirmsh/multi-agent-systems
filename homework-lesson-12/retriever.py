import pickle
import atexit  # <-- Додали імпорт
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder
from config import settings

class CustomHybridRetriever:
    def __init__(self):
        # 1. Semantic Search (Qdrant)
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001", 
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.client = QdrantClient(path="./qdrant_db")
        
        # <-- РЯТІВНИЙ РЯДОК: Коректно закриваємо БД перед самим виходом з програми
        atexit.register(self.client.close)
        
        self.qdrant = QdrantVectorStore(
            client=self.client, 
            collection_name="research_knowledge", 
            embedding=embeddings
        )

        # 2. Lexical Search (BM25)
        try:
            with open("./local_indexes/bm25_docs.pkl", "rb") as f:
                chunks = pickle.load(f)
            self.bm25_retriever = BM25Retriever.from_documents(chunks)
            self.bm25_retriever.k = 5
        except FileNotFoundError:
            print("⚠️ Увага: BM25 індекс не знайдено.")
            self.bm25_retriever = None

        # 3. Reranker (HuggingFace BAAI)
        print("⏳ Ініціалізація RAG: Завантаження моделі Reranker (перший запуск може зайняти хвилину)...")
        self.reranker = CrossEncoder("BAAI/bge-reranker-base")
        print("✅ RAG систему успішно підключено!")

    def invoke(self, query: str):
        # 1. Отримуємо результати з обох баз
        semantic_docs = self.qdrant.similarity_search(query, k=5)
        lexical_docs = self.bm25_retriever.invoke(query) if self.bm25_retriever else []
        
        # 2. Об'єднуємо та видаляємо дублікати за текстом
        unique_docs = {}
        for doc in semantic_docs + lexical_docs:
            unique_docs[doc.page_content] = doc
            
        combined_docs = list(unique_docs.values())
        if not combined_docs:
            return []
            
        # 3. Формуємо пари [запит, текст_документа] для крос-енкодера
        pairs = [[query, doc.page_content] for doc in combined_docs]
        
        # 4. Cross-Encoder оцінює релевантність (від 0 до 1)
        scores = self.reranker.predict(pairs)
        
        # 5. Сортуємо документи за оцінкою від найвищої до найнижчої
        scored_docs = sorted(zip(combined_docs, scores), key=lambda x: x[1], reverse=True)
        
        # 6. Повертаємо Топ-3 найрелевантніших
        return [doc for doc, score in scored_docs[:3]]

# Створюємо глобальний екземпляр retriever при імпорті
try:
    rag_retriever = CustomHybridRetriever()
except Exception as e:
    print(f"⚠️ Помилка ініціалізації RAG retriever: {e}")
    rag_retriever = None