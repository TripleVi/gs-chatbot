import os
from operator import itemgetter

from dotenv import load_dotenv
from flask import Flask, request
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

import database as db

load_dotenv()

app = Flask(__name__)

model = ChatVertexAI(model_name=os.environ["GOOGLE_MODEL"])
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

index = pc.Index("graduation-showcase")
embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 20, "score_threshold": 0.7},
)

def add_project_documents(project):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(project["description"])
    docs = [
        Document(
            page_content=f"Title: {project['title']}\nContent: {split}",
            metadata={"project_id": project["id"]}
        )
        for split in splits
    ]
    vector_store.add_documents(documents=docs)

def delete_project_documents(id: int):
    vector_store.delete(filter={"project_id": {"$eq": id}})

def generate_chat_title(user_input: str):
    return "chat title"

    prompt_template = ChatPromptTemplate([
        ("system", "You are a friendly assistant. Provide a concise Vietnamese title to the conversation based on the following question. Please respond only with the title in affirmative form, without any special characters (e.g., '.', '?', '\n') at the end."),
        ("human", "{text}")
    ])
    chain = prompt_template | model | StrOutputParser()
    response = chain.invoke({"text": user_input})
    return response.strip()

def get_chat_history(id: int):
    raw_messages = db.get_messages(id)
    return [
        HumanMessage(m["content"]) if i % 2 == 0 else AIMessage(m["content"])
        for i, m in enumerate(raw_messages)
    ]

@tool(parse_docstring=True)
def count_projects(topic: str) -> int:
    """Count how many projects there are by topic.

    Args:
        topic: The topic to which the project belongs.
    """
    return db.count_projects(topic)

def get_tools():
    retrieve_projects = create_retriever_tool(
        retriever,
        "retrieve_graduation_projects",
        "Searches and returns excerpts from Vietnamese articles about University of Greenwich students' graduation projects.",
    )
    available_tools = {
        "retrieve_graduation_projects": retrieve_projects,
        "count_projects": count_projects
    }
    tools = [retrieve_projects, count_projects]
    return (available_tools, tools)

fixed_response = "Dự án tốt nghiệp của sinh viên Đại học Greenwich về Blockchain bao gồm:\n\n* Ví tiền điện tử đa năng dựa trên blockchain\n* Ứng dụng blockchain trong quản lý chuỗi cung ứng\n* Hệ thống quản lý hợp đồng thông minh dựa trên blockchain\n* Hệ thống bỏ phiếu điện tử bảo mật bằng blockchain"

def chatbot(*, chat_id: int, user_input: str):
    return fixed_response

    prompt_template = ChatPromptTemplate([
        ("system", "The system is designed to store and manage Greenwich University students' graduation projects. You are a friendly assistant tasked with answering questions about these projects in Vietnamese. Use only the provided context to answer, keeping responses concise and, if possible, in bullet points. If the information isn't available in the context, just say that you don't know. Avoid generating answers without relevant context."),
        MessagesPlaceholder("chat_history")
    ])
    available_tools, tools = get_tools()
    model_with_tools = model.bind_tools(tools)
    chain = prompt_template | model_with_tools

    chat_history = get_chat_history(chat_id)
    chat_history.append(HumanMessage(user_input))
    global ai_msg
    ai_msg = chain.invoke({"chat_history": chat_history})
    while ai_msg.tool_calls:
        chat_history.append(ai_msg)
        for tool_call in ai_msg.tool_calls:
            selected_tool = available_tools[tool_call["name"].lower()]
            tool_msg = selected_tool.invoke(tool_call)
            chat_history.append(tool_msg)
        ai_msg = chain.invoke({"chat_history": chat_history})
    
    return ai_msg.content.strip()

@app.route("/chats", methods=["POST"])
def handle_new_chat():
    try:
        content, user_id = (
            itemgetter("content", "userId")(request.get_json())
        )
        title = generate_chat_title(content)
        chat_id = db.add_chat(user_id=user_id, title=title)
        response = chatbot(chat_id=chat_id, user_input=content)
        db.add_message(content=content, sender="user", chat_id=chat_id)
        message_id = db.add_message(content=response, sender="assistant", chat_id=chat_id)
        return {
            "chat_id": chat_id,
            "message_id": message_id
        }, 201
    except Exception as err:
        print(err)
        return 'Internal Server', 500

@app.route("/chats/<chat_id>/messages", methods=["POST"])
def handle_chat(chat_id):
    try:
        content = itemgetter("content")(request.get_json())
        chat = db.get_chat(chat_id)
        if not chat:
            return "Not Found", 404
        response = chatbot(chat_id=chat_id, user_input=content)
        db.add_message(content=content, sender="user", chat_id=chat_id)
        message_id = db.add_message(content=response, sender="assistant", chat_id=chat_id)
        return {"message_id": message_id}, 201
    except Exception as err:
        print(err)
        return 'Internal Server', 500
    
@app.route("/projects/<id>", methods=["POST"])
def on_project_added(id):
    status = itemgetter("status")(request.get_json())
    project = db.get_project(id)
    if not project:
        return "Not Found", 404
    
    match status:
        case "created":
            add_project_documents(project)
        # case "updated":
        # case "deleted":
        # case _:
    return "No Content", 204

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(port=port)