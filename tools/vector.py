import streamlit as st
from llm import llm, embeddings
from graph import graph

from langchain_neo4j import Neo4jVector
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

from langchain_core.prompts import ChatPromptTemplate


# Lazy initialization of Neo4jVector
_neo4jvector = None
_plot_retriever = None

def _initialize_vector_store():
    """Initialize the Neo4j vector store and retriever."""
    global _neo4jvector, _plot_retriever
    
    if _neo4jvector is not None:
        return _neo4jvector, _plot_retriever
    
    try:
        _neo4jvector = Neo4jVector.from_existing_index(
            embeddings,                              # (1)
            graph=graph,                             # (2)
            index_name="moviePlots",                 # (3)
            node_label="Movie",                      # (4)
            text_node_property="plot",               # (5)
            embedding_node_property="plotEmbedding", # (6)
            retrieval_query="""
RETURN
    node.plot AS text,
    score,
    {
        title: node.title,
        directors: [ (person)-[:DIRECTED]->(node) | person.name ],
        actors: [ (person)-[r:ACTED_IN]->(node) | [person.name, r.role] ],
        tmdbId: node.tmdbId,
        source: 'https://www.themoviedb.org/movie/'+ node.tmdbId
    } AS metadata
"""
        )

        retriever = _neo4jvector.as_retriever()

        instructions = (
            "Use the given context to answer the question."
            "If you don't know the answer, say you don't know."
            "Context: {context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        _plot_retriever = create_retrieval_chain(
            retriever, 
            question_answer_chain
        )
        
        return _neo4jvector, _plot_retriever
    
    except ValueError as e:
        if "does not exist" in str(e):
            raise ValueError(
                f"Neo4j vector index 'moviePlots' not found. Please ensure:\n"
                f"1. Neo4j database is running\n"
                f"2. The 'moviePlots' vector index has been created\n"
                f"3. Movies have been indexed with embeddings\n"
                f"Original error: {str(e)}"
            ) from e
        raise

def get_movie_plot(input):
    """Retrieve movie plot information. Initializes vector store on first call."""
    _, plot_retriever = _initialize_vector_store()
    return plot_retriever.invoke({"input": input})