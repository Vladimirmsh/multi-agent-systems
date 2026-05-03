import os
import pickle
import time
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from config import settings

def ingest_documents():
    data_dir = "./data"
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"1. Завантаження PDF документів з директорії {data_dir}/...")
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()
    
    if not documents:
        print(f"❌ Немає документів у папці {data_dir}/. Додайте PDF файли та спробуйте знову.")
        return

    print(f"   Знайдено сторінок: {len(documents)}")

    print("2. Розбиття текстів на чанки...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"   Створено чанків: {len(chunks)}")

    print("3. Ініціалізація Google Embeddings (gemini-embedding-001)...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001", 
        google_api_key=settings.GOOGLE_API_KEY
    )

    print("4. Збереження векторів до локальної БД Qdrant (з обходом лімітів API)...")
    qdrant_path = "./qdrant_db"
    batch_size = 80 # Відправляємо по 80 чанків, щоб не перевищити ліміт 100/хв
    qdrant = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"   -> Обробка батчу {i//batch_size + 1} (чанки {i} - {min(i+batch_size, len(chunks))})...")
        
        if qdrant is None:
            # Перший батч створює базу
            qdrant = QdrantVectorStore.from_documents(
                batch,
                embeddings,
                path=qdrant_path,
                collection_name="research_knowledge",
                force_recreate=True
            )
        else:
            # Наступні батчі просто додаються
            qdrant.add_documents(batch)
            
        # Якщо це не останній батч, робимо паузу
        if i + batch_size < len(chunks):
            print("   ⏳ Очікування 60 секунд (ліміт безкоштовного API Google: 100 запитів/хв)...")
            time.sleep(60)

    print("5. Збереження документів для BM25 (Lexical Search)...")
    os.makedirs("./local_indexes", exist_ok=True)
    with open("./local_indexes/bm25_docs.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Ingestion успішно завершено! Дані готові до пошуку.")

if __name__ == "__main__":
    ingest_documents()