# -*- coding: utf-8 -*-

import os
import requests
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Optional, Literal

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AnyMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


# =========================================================
# ENV
# =========================================================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY missing")

llm = ChatOpenAI(model="gpt-4o")


# =========================================================
# Structured output
# =========================================================
class SocialPost(BaseModel):
    title: str = Field(description="A catchy title for the post")
    summary: str = Field(description="Summary of the selected news")
    image_url: Optional[str] = Field(
        description="Representative image URL if found, else null"
    )


structured_llm = llm.with_structured_output(SocialPost)


# =========================================================
# Utils
# =========================================================
def fetch_web(url: str) -> str:
    r = requests.get(f"https://r.jina.ai/{url}", timeout=30)
    r.raise_for_status()
    return r.text


def classify_intent(message: str) -> Literal["CHAT", "NEW_POST", "POST_FEEDBACK"]:
    prompt = f"""
    Classify the user's intent.

    CHAT = normal conversation or questions
    NEW_POST = generate a post from news/articles
    POST_FEEDBACK = modify an existing post

    Respond ONLY with:
    CHAT
    NEW_POST
    POST_FEEDBACK

    Message:
    {message}
    """
    return llm.invoke(prompt).content.strip()


def extract_url(message: str) -> Optional[str]:
    prompt = f"""
    Extract the URL from the message.
    If none, respond ONLY with: NONE

    Message:
    {message}
    """
    url = llm.invoke(prompt).content.strip()
    return None if url == "NONE" else url


def classify_feedback(feedback: str) -> Literal["EDIT", "RESELECT", "RESCRAPE"]:
    prompt = f"""
    Classify the user's feedback.

    EDIT = modify wording/style/length
    RESELECT = select different news from same content
    RESCRAPE = fetch news from a new URL

    Respond ONLY with:
    EDIT
    RESELECT
    RESCRAPE

    Feedback:
    {feedback}
    """
    return llm.invoke(prompt).content.strip()


# =========================================================
# State
# =========================================================
class PostState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    web_content: Optional[str]
    last_post: Optional[dict]


# =========================================================
# Agent
# =========================================================
class PostAgent:
    def __init__(self):
        self.decision = None

        graph = StateGraph(PostState)
        graph.add_node("generate", self.generate)
        graph.add_node("feedback", self.feedback)
        graph.add_node("publish", self.publish)

        graph.set_entry_point("generate")

        graph.add_conditional_edges(
            "generate",
            self.route,
            {"publish": "publish", "feedback": "feedback"},
        )

        graph.add_edge("feedback", "generate")
        graph.add_edge("publish", END)

        self.graph = graph.compile()

    # -----------------------------------------------------
    def generate(self, state: PostState):
        self.decision = None

        user_msg = state["messages"][-1].content
        web_content = state.get("web_content")
        last_post = state.get("last_post")

        # ============== FEEDBACK MODE =================
        if last_post:
            intent = classify_feedback(user_msg)

            if intent == "EDIT":
                prompt = f"""
                Edit the following social media post according to the feedback.

                POST:
                {last_post}

                FEEDBACK:
                {user_msg}
                """
                result = structured_llm.invoke(prompt)

            elif intent == "RESELECT":
                prompt = f"""
                From the content below, select different news
                and generate a NEW structured social media post.

                CONTENT:
                {web_content[:40000]}

                USER REQUEST:
                {user_msg}
                """
                result = structured_llm.invoke(prompt)

            else:  # RESCRAPE
                url = extract_url(user_msg)
                if not url:
                    print("\n🤖 Necesito una URL para cambiar la fuente.\n")
                    return {"__end__": True}

                web_content = fetch_web(url)

                prompt = f"""
                USER REQUEST:
                {user_msg}

                From the content below, generate a structured social media post 
                with title, summary and image_url. The summary of 3 news items if not specified.

                CONTENT:
                {web_content[:40000]}
                """
                result = structured_llm.invoke(prompt)

            self.preview(result)

            return {
                "messages": [HumanMessage(content=user_msg)],
                "web_content": web_content,
                "last_post": result,
            }

        # ============== INITIAL POST =================
        url = extract_url(user_msg)
        if not url:
            print("\n🤖 Para generar un post necesito que incluyas una URL.\n")
            return {"__end__": True}

        web_content = fetch_web(url)

        prompt = f"""
        USER REQUEST:
        {user_msg}

        From the content below, generate a structured social media post
        with title, summary and image_url. The summary of 3 news items if not specified.

        CONTENT:
        {web_content[:40000]}
        """
        result = structured_llm.invoke(prompt)

        self.preview(result)

        return {
            "messages": [HumanMessage(content=user_msg)],
            "web_content": web_content,
            "last_post": result,
        }

    # -----------------------------------------------------
    def preview(self, result: SocialPost):
        print("\n📰 VISTA PREVIA (JSON):\n")
        print(result.model_dump_json(indent=2))
        print()

        self.decision = input("¿Publicar el post? (yes/no): ").strip().lower()

    # -----------------------------------------------------
    def route(self, state: PostState):
        if state.get("__end__"):
            return END
        return "publish" if self.decision == "yes" else "feedback"

    # -----------------------------------------------------
    def feedback(self, _: PostState):
        fb = input("¿Qué quieres cambiar?: ")
        return {"messages": [HumanMessage(content=fb)]}

    # -----------------------------------------------------
    def publish(self, state: PostState):
        post: SocialPost = state["last_post"]

        payload = post.model_dump()  # dict limpio, Pydantic v2 OK
        if not payload["title"] or not payload["summary"]:
            raise ValueError("Post incompleto, no se envía a la API")

        print("\n🚀 Enviando post a API local...\n")
        print(payload)

        r = requests.post(
            "http://localhost:5000/api/posts",  # ✅ ENDPOINT CORRECTO
            json=payload,
            timeout=10
        )

        r.raise_for_status()

        print("\n✅ POST ENVIADO CORRECTAMENTE")
        print("Respuesta API:", r.json())

        

# =========================================================
# REPL
# =========================================================
if __name__ == "__main__":
    agent = PostAgent()

    print("🧠 News Agent interactivo. Escribe 'quit' para salir.\n")

    post_state = {
        "messages": [],
        "web_content": None,
        "last_post": None,
    }

    while True:
        user_input = input("🧑 Tú: ").strip()

        if user_input.lower() == "quit":
            print("👋 Hasta luego")
            break

        intent = classify_intent(user_input)

        if intent == "CHAT":
            reply = llm.invoke(user_input)
            print(f"\n🤖 {reply.content}\n")
            continue

        post_state = agent.graph.invoke(
            {
                "messages": [HumanMessage(content=user_input)],
                "web_content": post_state["web_content"],
                "last_post": post_state["last_post"],
            }
        )
