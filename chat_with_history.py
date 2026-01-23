import os
import sqlite3
import uuid
from agno.agent import Agent
from agno.models.openai import OpenAILike

DB = "conversations.db"
SESSION_ID = str(uuid.uuid4())  # one conversation

# ---------- DB HELPERS ----------
def save(role, message):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (session_id, role, message) VALUES (?, ?, ?)",
        (SESSION_ID, role, message)
    )
    conn.commit()
    conn.close()

def load_history(limit=10):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message
        FROM chats
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
    """, (SESSION_ID, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- AGENT ----------
agent = Agent(
    name="History Agent",
    model=OpenAILike(
        # Example for the latest Qwen3 32B model
        id="Qwen/Qwen3-32B", 
        base_url="https://llm.chutes.ai/v1",
        api_key=os.getenv("CHUTES_API_TOKEN")
    ),
)
print("\n🟢 Chat started (history enabled)")
print("Type 'exit' to stop\n")

# ---------- CHAT LOOP ----------
while True:
    user = input("You: ")
    if user.lower() == "exit":
        print("🔴 Conversation ended.")
        break

    save("user", user)

    # build context like ChatGPT
    history = load_history()
    context = ""
    for role, msg in history:
        context += f"{role.upper()}: {msg}\n"

    prompt = f"""
Use the following conversation history to answer.

{context}

Now answer this:
{user}
"""

    response = agent.run(prompt)
    assistant_text = response.content

    print("\nAgent:", assistant_text, "\n")

    save("assistant", assistant_text)
