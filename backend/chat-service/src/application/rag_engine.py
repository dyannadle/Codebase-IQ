from src.infrastructure.qdrant import qdrant_db
from src.infrastructure.neo4j import neo4j_db
from src.application.llm_service import generate_embedding, stream_chat_response

SYSTEM_PROMPT_TEMPLATE = """
[SYSTEM]
You are an expert Software Architect analyzing the user's repository.
You MUST base your answer EXCLUSIVELY on the provided <CODE CONTEXT> and <GRAPH CONTEXT>.
If the context does not contain the answer, state clearly: "I cannot determine this from the current context."
Do NOT invent file paths or code that isn't provided. Cite your sources.

[GRAPH CONTEXT]
{graph_context}

[CODE CONTEXT]
{code_context}

[USER QUERY]
{query}
"""

class RAGEngine:
    
    async def process_query(self, query: str, org_id: str, repo_ids: list[str]):
        """Executes the Hybrid RAG Pipeline and returns a streaming generator."""
        
        # 1. Embed the user's query
        query_vector = await generate_embedding(query)
        
        # 2. Semantic Search (Qdrant)
        search_results = await qdrant_db.search(query_vector, org_id, repo_ids, limit=3)
        
        code_context = ""
        graph_context = ""
        
        if search_results:
            for result in search_results:
                payload = result.payload
                file_path = payload.get("filepath", "Unknown")
                content = payload.get("content", "")
                code_context += f"--- {file_path} ---\n{content}\n\n"
                
                # 3. Structural Search (Neo4j) - Find dependencies for the top matched file
                # In a production system, this would be done for all top N files concurrently
                deps = await neo4j_db.get_dependencies(file_path, repo_ids[0])
                if deps["imports"] or deps["imported_by"]:
                    graph_context += f"File: {file_path}\n"
                    if deps["imports"]:
                        graph_context += f"  Imports: {', '.join(deps['imports'])}\n"
                    if deps["imported_by"]:
                        graph_context += f"  Imported By: {', '.join(deps['imported_by'])}\n\n"

        # 4. Assemble Final Prompt
        final_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            graph_context=graph_context if graph_context else "No structural dependencies found.",
            code_context=code_context if code_context else "No relevant code chunks found.",
            query=query
        )
        
        # 5. Stream LLM Response
        return stream_chat_response(final_prompt)

rag_engine = RAGEngine()
