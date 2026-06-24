# Setup Guide

This guide explains how to configure and run the GraphRAG Movie Recommendation Chatbot locally or in the included devcontainer.

## 1. Prepare Python

Use Python 3.12 if you are using the provided devcontainer, or another compatible Python 3 version in a local environment.

Optional local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

> Note: `llm.py` imports `OllamaEmbeddings` from `langchain_ollama`. If your environment does not already include that package, install the matching `langchain-ollama` package before using plot search.

## 2. Prepare Neo4j

Create or choose a Neo4j database that contains a movie recommendation graph. The application expects movie and person data similar to this structure:

- `(:Movie)` nodes with properties such as `title`, `plot`, `tmdbId`, and `plotEmbedding`.
- `(:Person)` nodes with properties such as `name`, `born`, and `tmdbId`.
- Relationships such as `(:Person)-[:ACTED_IN]->(:Movie)` and `(:Person)-[:DIRECTED]->(:Movie)`.

The application uses Neo4j for three things:

1. Cypher-based answers about movie facts and relationships.
2. Vector retrieval over movie plots.
3. Session-based chat history.

## 3. Create the movie plot vector index

Plot-based recommendations require a Neo4j vector index named `moviePlots` over `Movie.plotEmbedding`.

The index should match these application settings:

- Index name: `moviePlots`
- Node label: `Movie`
- Text property used for retrieved context: `plot`
- Embedding property: `plotEmbedding`

Create the index with dimensions that match the embedding model you use. The configured embedding model is Ollama `mxbai-embed-large`, which commonly uses 1024-dimensional embeddings:

```cypher
CREATE VECTOR INDEX moviePlots IF NOT EXISTS
FOR (m:Movie)
ON (m.plotEmbedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1024,
    `vector.similarity_function`: 'cosine'
  }
};
```

Ensure each indexed `Movie` node has a populated `plotEmbedding` value before using plot search.

## 4. Configure application secrets

Create a `.streamlit` directory and a `secrets.toml` file:

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Add your Neo4j and LLM credentials:

```toml
NEO4J_URI = "neo4j+s://<your-instance>.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "<your-password>"
NEO4J_DATABASE = "neo4j"

GROQ_API_KEY = "<your-groq-api-key>"
```

For a local Neo4j database, use a URI such as:

```toml
NEO4J_URI = "bolt://localhost:7687"
```

## 5. Prepare Ollama embeddings

The vector retriever uses the local Ollama embedding model `mxbai-embed-large`.

Install and start Ollama, then pull the model:

```bash
ollama pull mxbai-embed-large
```

Keep Ollama running while using plot-based recommendations.

## 6. Run the app

Start Streamlit from the repository root:

```bash
streamlit run bot.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

If you are using the devcontainer or GitHub Codespaces, port `8501` is forwarded automatically.

## 7. Verify the chatbot

Try questions that exercise each tool:

- General movie conversation: `What makes a good sci-fi movie?`
- Cypher graph QA: `Who directed The Matrix?`
- Relationship traversal: `How is Tom Hanks connected to Kevin Bacon?`
- Vector plot search: `Recommend movies about space exploration and survival.`

## Troubleshooting

### `moviePlots` vector index not found

Create the `moviePlots` vector index and make sure `Movie` nodes have `plotEmbedding` values.

### Authentication or connection errors

Check the values in `.streamlit/secrets.toml`, especially `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`.

### Plot search cannot load embeddings

Confirm Ollama is installed, running, and has the `mxbai-embed-large` model available. Also confirm `langchain-ollama` is installed in your Python environment if it is not already present.

### The bot answers only movie-related questions

This is expected. The agent prompt intentionally restricts the assistant to movies, actors, and directors.
