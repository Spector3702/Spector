from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings


def create_vectorstore():
    loader = PyPDFLoader("spector/愛你、愛我，該怎麼說？怎麼做.pdf")

    splitter = RecursiveCharacterTextSplitter(chunk_size = 512, chunk_overlap = 128)
    doc_split = loader.load_and_split(splitter)

    embeddings = OpenAIEmbeddings()

    vectorstore = Chroma.from_documents(
        documents=doc_split,
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever()

    return retriever