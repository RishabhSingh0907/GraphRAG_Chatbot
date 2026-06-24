# GraphRAG Movie Recommendation Chatbot

A Streamlit chatbot that answers movie questions and recommends films by combining a Neo4j movie knowledge graph with retrieval-augmented generation (RAG). The app uses graph relationships for structured questions such as cast, directors, and actor connections, and a Neo4j vector index for semantic movie-plot search.

## What the app does

- **Movie-focused chat:** Provides conversational answers about movies, actors, and directors while refusing unrelated topics.
- **Graph RAG over Neo4j:** Uses the Neo4j graph schema and generated Cypher queries to answer relationship-heavy questions.
- **Plot-based recommendations:** Retrieves movies from a Neo4j vector index named `moviePlots` using plot embeddings and returns relevant metadata such as title, directors, actors, and TMDB links.
- **Persistent chat history:** Stores each Streamlit session's conversation history in Neo4j so follow-up questions can use prior context.
- **Streamlit UI:** Runs as a lightweight web chat interface on port `8501`.

## Architecture

```text
Streamlit UI (bot.py)
        |
        v
Agent executor (agent.py)
        |
        +-- General Chat tool -> LLM response for movie-only conversation
        +-- Movie Plot Search tool -> Neo4j vector search over Movie.plot
        +-- Movie information tool -> GraphCypherQAChain over Neo4j schema
        |
        v
Neo4j graph database + chat memory
```

### Key files

| File | Purpose |
| --- | --- |
| `bot.py` | Streamlit chat UI and message submission flow. |
| `agent.py` | LangChain ReAct agent, tool registration, and Neo4j-backed chat history. |
| `graph.py` | Neo4j connection created from Streamlit secrets. |
| `llm.py` | Chat model and embedding model configuration. |
| `tools/cypher.py` | Cypher generation prompt and graph question-answering chain. |
| `tools/vector.py` | Lazy Neo4j vector retriever for semantic movie-plot search. |
| `utils.py` | Streamlit message rendering and session ID helper. |
| `requirements.txt` | Python package dependencies. |

## Requirements

- Python 3.12 or a compatible Python 3 version.
- A Neo4j database containing a movie graph with `Movie` and `Person` nodes and relationships such as `ACTED_IN` and `DIRECTED`.
- A Neo4j vector index named `moviePlots` on `Movie.plotEmbedding` for plot retrieval.
- An OpenAI-compatible chat API key. The current code is configured for Groq's OpenAI-compatible endpoint and model `openai/gpt-oss-120b`.
- Ollama with the `mxbai-embed-large` embedding model available locally, because plot retrieval uses `OllamaEmbeddings`.

## Configuration

Create `.streamlit/secrets.toml` in the project root:

```toml
NEO4J_URI = "neo4j+s://<your-instance>.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "<your-password>"
NEO4J_DATABASE = "neo4j"

GROQ_API_KEY = "<your-groq-api-key>"
```

If you use a local Neo4j instance, `NEO4J_URI` may look like `bolt://localhost:7687`.

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit app:

```bash
streamlit run bot.py
```

Open the app at [http://localhost:8501](http://localhost:8501).

## Example questions

- `Recommend a movie about hackers and artificial intelligence.`
- `Who directed The Matrix?`
- `Which actors appeared in Apollo 13?`
- `How is Tom Hanks connected to Kevin Bacon?`
- `Find movies with a plot involving space travel and survival.`

## Data and index expectations

The graph question-answering tool expects the Neo4j schema to include movie and person data with properties such as movie `title`, `plot`, `tmdbId`, and person `name`. The vector search tool expects:

- Node label: `Movie`
- Text property: `plot`
- Embedding property: `plotEmbedding`
- Vector index name: `moviePlots`

If the `moviePlots` index is missing, plot-based questions will fail with an error explaining that the vector index must be created and populated.

## Development notes

- The devcontainer installs dependencies from `requirements.txt` automatically and forwards port `8501`.
- Chat history is keyed by the active Streamlit session ID and stored in Neo4j through `Neo4jChatMessageHistory`.
- The agent prompt instructs the assistant to use tools and avoid answering movie questions from pre-trained knowledge alone.
