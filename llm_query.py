import os, re, json
import cohere
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain.prompts import PromptTemplate

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

co = cohere.Client(COHERE_API_KEY)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

cypher_template = """
You are an expert Neo4j Cypher query generator.
Return ONLY a valid Cypher query (no commentary, no code fences).

Graph:
Nodes:
  - Artist (name, mbid, country, aliases)
  - Release (title, date, status, label)
  - Recording (title, length_ms)
  - Genre (name)
  - Tag (name)

Relationships:
  (Artist)-[:RELEASED]->(Release)
  (Release)-[:HAS_TRACK]->(Recording)
  (Artist|Release|Recording)-[:HAS_GENRE]->(Genre)
  (Artist|Release|Recording)-[:HAS_TAG]->(Tag)

MATCHING RULES (very important):
- Always match artists case-insensitively and consider aliases:
  WHERE toLower(a.name) CONTAINS toLower('<artist>')
     OR ANY(al IN coalesce(a.aliases, []) WHERE toLower(al) CONTAINS toLower('<artist>'))
- When matching an album by title, use CONTAINS, case-insensitive:
  WHERE toLower(r.title) CONTAINS toLower('<album>')
- For year filters, use:
  WHERE toInteger(left(r.date, 4)) >= 2011   // example
- Always RETURN friendly column names like name, title, date, label, genre, tag.

Question: {question}
Cypher:
""".strip()

cypher_prompt = PromptTemplate(template=cypher_template, input_variables=["question"])

def extract_cypher(txt: str) -> str:
    txt = re.sub(r"^```(?:cypher)?|```$", "", txt.strip(), flags=re.MULTILINE | re.IGNORECASE)
    m = re.search(r"\b(MATCH|WITH|CALL)\b", txt, re.IGNORECASE)
    return txt[m.start():].strip() if m else txt.strip()

def run_cypher(query: str):
    with driver.session() as session:
        return [dict(r) for r in session.run(query)]

def ask_llm(question: str, debug: bool = True):
    # 1) Cypher via Chat API
    raw = co.chat(
        model="command-r-plus-08-2024",
        message=cypher_prompt.format(question=question),
        temperature=0,
    ).text.strip()
    cypher = extract_cypher(raw)

    if debug:
        print("=== Raw LLM output ===\n", raw, "\n")
        print("=== Cypher used ===\n", cypher, "\n")

    # 2) Exec
    try:
        rows = run_cypher(cypher)
    except Exception as e:
        return f"❌ Cypher failed:\n{cypher}\nError: {e}"

    if not rows:
        return "No results found."

    if debug:
        print("=== Neo4j rows ===")
        print(json.dumps(rows[:10], indent=2, ensure_ascii=False))

    # 3) Summarize with Chat
    summary_prompt = f"""
Question: {question}
Rows: {json.dumps(rows[:25], ensure_ascii=False)}
Answer in plain English:
""".strip()

    ans = co.chat(
        model="command-r-plus-08-2024",
        message=summary_prompt,
        temperature=0.3,
    ).text.strip()

    return ans

if __name__ == "__main__":
    print(ask_llm("List all Coldplay albums after 2010", debug=True))
