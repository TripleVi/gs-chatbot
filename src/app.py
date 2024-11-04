from datetime import datetime, timezone
import os
from operator import itemgetter

from flask import Flask, request
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import mysql.connector
from pinecone import Pinecone

app = Flask(__name__)

# model = ChatVertexAI(model_name=os.environ["GOOGLE_MODEL"])
# pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# index = pc.Index("graduation-showcase")
# embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
# vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# retriever = vector_store.as_retriever(
#     search_type="similarity_score_threshold",
#     search_kwargs={"k": 20, "score_threshold": 0.8},
# )

# def generate_chat_title(model, question):
#     prompt_template = ChatPromptTemplate([
#         ("system", "You are a friendly assistant. Provide a concise Vietnamese title to the conversation based on the following question. Please respond only with the title in affirmative form, without any special characters (e.g., '.', '?') at the end."),
#         ("user", "{text}")
#     ])
#     chain = prompt_template | model | StrOutputParser()
#     response = chain.invoke({"text": question})
#     return response.strip()

# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)

# def chatbot(user_input):
#     system_template = """
#     The system is designed to store and manage Greenwich University students' graduation projects. You are a friendly assistant tasked with answering questions about these projects in Vietnamese. Use only the provided context below to answer, keeping responses concise and, if possible, in bullet points. If the information isn't available in the context, respond with "I don't know". Avoid generating answers without relevant context.
#     Context: {context}
#     """
#     prompt_template = ChatPromptTemplate([
#         ("system", system_template),
#         ("user", "{text}")
#     ])
#     chain = (
#         {"context": retriever | format_docs, "text": RunnablePassthrough()}
#         | prompt_template
#         | model
#         | StrOutputParser()
#     )
#     response = chain.invoke(user_input)
#     return response.strip()

# def get_db_connection():
#     return mysql.connector.connect(
#         host=os.environ["DB_HOST"],
#         port=os.environ["DB_PORT"],
#         user=os.environ["DB_USERNAME"],
#         password=os.environ["DB_PASSWORD"],
#         database=os.environ["DB_DATABASE"]
#     )

# sample_response = "Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi. Ứng dụng cung cấp các tính năng ghi lại các chỉ số như nhịp tim, huyết áp, và mức độ hoạt động thể chất, giúp người dùng có thể theo dõi sự biến đổi của các chỉ số này theo thời gian. Ngoài ra, ứng dụng còn cung cấp các lời khuyên sức khỏe cá nhân hoá dựa trên các chỉ số đã thu thập, giúp người dùng có những hướng dẫn kịp thời và phù hợp để duy trì sức khỏe tim mạch. Mục tiêu của dự án là tạo ra một công cụ hữu ích, dễ sử dụng để người dùng có thể nâng cao nhận thức và cải thiện sức khỏe tim mạch của mình.\n\n- Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi.\n- Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi.\n- Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi.\n- Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi.\n- Ứng dụng di động theo dõi sức khỏe tim mạch là một giải pháp công nghệ hỗ trợ người dùng kiểm tra và giám sát tình trạng tim mạch của mình một cách hiệu quả và tiện lợi."

# @app.route("/chats", methods=["POST"])
# def handle_new_chat():
#     try:
#         content, user_id = (
#             itemgetter("content", "userId")(request.get_json())
#         )
#         # title = generate_chat_title(model, content)
#         title = "chat title"
#         cnx = get_db_connection()
#         cur = cnx.cursor(dictionary=True)
#         add_chat = """
#             INSERT INTO chat (user_id, title, created_at)
#             VALUES (%s, %s, %s)
#         """
#         now = datetime.now(timezone.utc)
#         data_chat = (user_id, title, now)
#         cur.execute(add_chat, data_chat)
#         chat_id = cur.lastrowid
#         add_message = """
#             INSERT INTO message (content, sender, chat_id, created_at)
#             VALUES (%s, %s, %s, %s)
#         """
#         data_message = (content, "user", chat_id, now)
#         cur.execute(add_message, data_message)
        
#         # response = chatbot(content)
#         response = sample_response
#         now = datetime.now(timezone.utc)
#         data_message = (response, "assistant", chat_id, now)
#         cur.execute(add_message, data_message)
#         message_id = cur.lastrowid
#         cnx.commit()
#         return {
#             "chat_id": chat_id,
#             "message_id": message_id,
#         }, 201
#     except mysql.connector.Error as err:
#         return {'error': str(err)}, 500
#     finally:
#         cur.close()
#         cnx.close()

# @app.route("/chats/<chat_id>/messages", methods=["POST"])
# def handle_chat(chat_id):
#     try:
#         content = itemgetter("content")(request.get_json())
#         cnx = get_db_connection()
#         cur = cnx.cursor(dictionary=True)
#         get_chat = "SELECT * FROM chat WHERE id = %s"
#         cur.execute(get_chat, (chat_id,))
#         chat = cur.fetchone()
#         if not chat:
#             return "Not Found", 404
#         add_message = """
#             INSERT INTO message (content, sender, chat_id, created_at)
#             VALUES (%s, %s, %s, %s)
#         """
#         now = datetime.now(timezone.utc)
#         data_message = (content, "user", chat_id, now)
#         cur.execute(add_message, data_message)

#         response = sample_response
#         now = datetime.now(timezone.utc)
#         data_message = (response, "assistant", chat_id, now)
#         cur.execute(add_message, data_message)
#         message_id = cur.lastrowid

#         cnx.commit()
#         return {"message_id": message_id}, 201
#     except mysql.connector.Error as err:
#         return {'error': str(err)}, 500
#     finally:
#         cur.close()
#         cnx.close()

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(port=port)