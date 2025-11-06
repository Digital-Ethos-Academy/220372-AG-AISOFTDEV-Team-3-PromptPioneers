# RAG System for AI-Powered Requirement Analyzer
# This module provides PRD generation functionality for the React frontend

import sys
import os
from typing import List, TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

# Import your utils
from utils import setup_llm_client

# Initialize the LLM client
client, model_name, api_provider = setup_llm_client(model_name="gpt-4.1")

# Create knowledge base
def create_knowledge_base():
    """Creates the knowledge base for PRD generation."""
    artifact_paths = ["artifacts/prd_gen.md", "artifacts/schema.sql", "artifacts/adr.md"]
    all_docs = []
    
    for path in artifact_paths:
        if os.path.exists(path):
            loader = TextLoader(path)
            docs = loader.load()
            for doc in docs:
                doc.metadata = {"source": path}
            all_docs.extend(docs)
    
    if not all_docs:
        # Create a minimal knowledge base with PRD examples
        example_doc = Document(
            page_content="""
            Product Requirements Document Template:
            1. Executive Summary: Brief overview of the product
            2. Objectives: Clear business goals and success metrics
            3. Features: Key functionalities and capabilities
            4. User Stories: As a [user], I want [feature], so that [benefit]
            5. Technical Requirements: Technology stack and infrastructure needs
            
            Example Features:
            - User authentication and profile management
            - Data visualization and analytics
            - Mobile-responsive interface
            - Real-time notifications
            - Integration with third-party services
            
            Example User Stories:
            - As a user, I want to create an account, so that I can save my preferences
            - As a user, I want to view analytics, so that I can track my progress
            - As a user, I want mobile access, so that I can use the app anywhere
            """,
            metadata={"source": "template"}
        )
        all_docs = [example_doc]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    
    vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    return vectorstore.as_retriever()

# Initialize retriever
retriever = create_knowledge_base()

# PRD Agent State
class PRDAgentState(TypedDict):
    user_input: str
    conversation_history: List[Dict[str, str]]
    retrieved_context: List[Document]
    analysis_result: Dict[str, Any]
    prd_content: Dict[str, Any]
    clarifying_questions: List[str]
    processing_stage: str
    error_message: str

# Agent functions
def input_analyzer_agent(state: PRDAgentState) -> PRDAgentState:
    """Analyzes user input for PRD generation."""
    user_input = state["user_input"]
    
    # Retrieve relevant context
    context_query = f"product requirements examples features user stories {user_input}"
    retrieved_docs = retriever.invoke(context_query)
    state["retrieved_context"] = retrieved_docs
    
    # Analyze input
    analysis_prompt = f"""
    Analyze this product idea: "{user_input}"
    
    Extract:
    1. Product type/category
    2. Main purpose/goal  
    3. Target users
    4. Key features mentioned
    5. Technical requirements
    6. Business objectives
    
    Respond in JSON: {{"product_type": "", "purpose": "", "target_users": [], "features": [], "technical_requirements": [], "business_objectives": []}}
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Extract structured information from product ideas. Respond only with valid JSON."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.1
        )
        
        analysis_result = json.loads(response.choices[0].message.content)
        state["analysis_result"] = analysis_result
        state["processing_stage"] = "analyzed"
    except Exception as e:
        state["error_message"] = f"Analysis failed: {str(e)}"
        state["processing_stage"] = "error"
    
    return state

def prd_generator_agent(state: PRDAgentState) -> PRDAgentState:
    """Generates PRD content matching your App.js structure."""
    analysis = state["analysis_result"]
    context_docs = state["retrieved_context"]
    
    # Create context from retrieved documents
    context_text = "\n\n".join([doc.page_content[:500] for doc in context_docs[:3]])
    
    # Create PRD content that matches your React component structure exactly
    prd_prompt = f"""
    Based on this analysis: {json.dumps(analysis, indent=2)}
    
    And these examples: {context_text}
    
    Generate a PRD with these EXACT fields to match the React app structure:
    
    {{
        "title": "A clear, compelling product title",
        "overview": "2-3 sentences describing the product and its value proposition",
        "objectives": ["Business objective 1", "Business objective 2", "Business objective 3"],
        "features": ["Feature 1: Description", "Feature 2: Description", "Feature 3: Description", "Feature 4: Description"],
        "requirements": ["Technical requirement 1", "Technical requirement 2", "Technical requirement 3"],
        "userStories": ["As a user, I want X, so that Y", "As a user, I want A, so that B", "As a user, I want C, so that D"]
    }}
    
    Make it specific to the analyzed product idea. Ensure all arrays have at least 3 items. Respond with valid JSON only.
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Generate PRD content as valid JSON matching the exact field structure provided. Be specific and detailed."},
                {"role": "user", "content": prd_prompt}
            ],
            temperature=0.2
        )
        
        prd_content = json.loads(response.choices[0].message.content)
        
        # Ensure all fields exist and are correct types
        prd_content.setdefault("title", "Product Requirements Document")
        prd_content.setdefault("overview", "Product overview will be generated from your input.")
        prd_content.setdefault("objectives", [])
        prd_content.setdefault("features", [])
        prd_content.setdefault("requirements", [])
        prd_content.setdefault("userStories", [])
        
        # Ensure arrays are actually arrays
        for field in ["objectives", "features", "requirements", "userStories"]:
            if not isinstance(prd_content[field], list):
                prd_content[field] = [str(prd_content[field])] if prd_content[field] else []
            
            # Ensure minimum number of items
            if len(prd_content[field]) == 0:
                if field == "objectives":
                    prd_content[field] = ["Define clear business goals", "Identify target market", "Establish success metrics"]
                elif field == "features":
                    prd_content[field] = ["Core functionality", "User interface", "Data management", "User authentication"]
                elif field == "requirements":
                    prd_content[field] = ["Web-based application", "Mobile responsive design", "Secure data storage"]
                elif field == "userStories":
                    prd_content[field] = ["As a user, I want to access the application, so that I can use its features", "As a user, I want to save my data, so that I can access it later"]
        
        state["prd_content"] = prd_content
        state["processing_stage"] = "generated"
    except Exception as e:
        state["error_message"] = f"PRD generation failed: {str(e)}"
        state["processing_stage"] = "error"
    
    return state

def clarification_agent(state: PRDAgentState) -> PRDAgentState:
    """Generates clarifying questions."""
    user_input = state["user_input"]
    analysis = state.get("analysis_result", {})
    
    questions_prompt = f"""
    For this product idea: "{user_input}"
    
    Based on analysis: {json.dumps(analysis, indent=2)}
    
    Generate 2-3 specific clarifying questions to improve the PRD.
    Focus on missing details about users, features, or requirements.
    
    Respond as JSON array: ["Question 1?", "Question 2?", "Question 3?"]
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Generate clarifying questions as a JSON array."},
                {"role": "user", "content": questions_prompt}
            ],
            temperature=0.1
        )
        
        questions = json.loads(response.choices[0].message.content)
        state["clarifying_questions"] = questions
    except:
        state["clarifying_questions"] = ["Could you provide more details about your target users?", "What are the most important features for your users?"]
    
    return state

# Routing logic
def determine_next_step(state: PRDAgentState) -> str:
    stage = state.get("processing_stage", "")
    if stage == "analyzed":
        return "generate_prd"
    elif stage == "generated":
        return "generate_questions"
    else:
        return "end"

# Create the graph
def create_prd_rag_graph():
    workflow = StateGraph(PRDAgentState)
    
    workflow.add_node("analyze_input", input_analyzer_agent)
    workflow.add_node("generate_prd", prd_generator_agent)
    workflow.add_node("generate_questions", clarification_agent)
    
    workflow.set_entry_point("analyze_input")
    
    workflow.add_conditional_edges(
        "analyze_input",
        determine_next_step,
        {"generate_prd": "generate_prd", "end": END}
    )
    
    workflow.add_conditional_edges(
        "generate_prd", 
        determine_next_step,
        {"generate_questions": "generate_questions", "end": END}
    )
    
    workflow.add_edge("generate_questions", END)
    
    return workflow.compile()

# Initialize the graph
prd_rag_graph = create_prd_rag_graph()

# Main function for API integration
def process_user_input_for_prd(user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Main function to process user input and generate PRD content.
    Returns data structure that matches your React app exactly.
    """
    if conversation_history is None:
        conversation_history = []
    
    initial_state = {
        "user_input": user_input,
        "conversation_history": conversation_history,
        "retrieved_context": [],
        "analysis_result": {},
        "prd_content": {},
        "clarifying_questions": [],
        "processing_stage": "starting",
        "error_message": ""
    }
    
    result = prd_rag_graph.invoke(initial_state)
    
    return {
        "success": result["processing_stage"] not in ["error", "starting"],
        "prd_content": result.get("prd_content", {}),
        "clarifying_questions": result.get("clarifying_questions", []),
        "analysis": result.get("analysis_result", {}),
        "error_message": result.get("error_message", ""),
        "processing_stage": result.get("processing_stage", "unknown")
    }