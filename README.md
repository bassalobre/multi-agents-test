# Multi-Agent RAG System

## 1. Architecture Overview

This project implements an orchestrated multi-agent system to answer user queries intelligently and securely. The architecture is designed to dynamically decide the best response strategy (Direct or RAG - Retrieval-Augmented Generation) after passing through a compliance verification layer.

### Key Components

* **Orchestrator**: The core of the system. Manages the request lifecycle, instantiating agents and controlling the data flow between them.
* **Compliance Agent**: The first line of defense. Analyzes the user query for prompt injection, malicious content, or policy violations. Blocked topics include: Violence, Illegal Acts, Sexual Content, Politics, Religion, Corporate Integrity (Layoffs), Drugs, and PII. If the query is rejected, the flow is stopped immediately.
* **Decision Agent**: The strategic "brain". Evaluates safe queries to determine if the system should answer directly (for general questions/conversation) or use RAG (for questions requiring specific context from ingested knowledge).
* **Direct Answer Agent**: Specialized in direct and conversational responses that do not require searching a vector database.
* **RAG Retrieval**: Module responsible for fetching relevant documents from the **Qdrant** vector database using **HuggingFace** embeddings (`all-MiniLM-L6-v2`).
* **RAG Answer Agent**: Synthesizes a final answer using the context retrieved by the Retrieval module, ensuring the response is grounded in the data.
* **API Layer**: RESTful interface built with **FastAPI** for external integration.

---

## 2. Flow Diagram (Mermaid)

```mermaid
graph TD
    User([User]) -->|Sends Query| Orchestrator[Orchestrator]
    
    subgraph "Security Layer"
        Orchestrator --> Compliance{Compliance Agent}
        Compliance -->|Blocked| BlockedEnd([End: Block Response])
    end
    
    subgraph "Decision Layer"
        Compliance -->|Approved| Decision{Decision Agent}
        Decision -->|Strategy: Direct| DirectAgent[Direct Answer Agent]
        Decision -->|Strategy: RAG| RAGRetrieval[RAG Retrieval<br/>(Qdrant + HF Embeddings)]
    end
    
    subgraph "Execution Layer"
        DirectAgent --> Result([Final Response])
        RAGRetrieval -->|Context| RAGAgent[RAG Answer Agent]
        RAGAgent --> Result
    end

    style Compliance fill:#f96,stroke:#333,stroke-width:2px
    style Decision fill:#69f,stroke:#333,stroke-width:2px
    style RAGRetrieval fill:#6f9,stroke:#333,stroke-width:2px
```

---

## 3. Flow Explanation

1. **Input**: The user sends a query and optionally a role.
2. **Compliance Verification**:
    * The `ComplianceAgent` analyzes the input.
    * **If unsafe**: Returns a block status with the reason (e.g., *Prompt Injection*). The Orchestrator returns immediately.
    * **If safe**: The flow continues, possibly with a "sanitized" version of the query.
3. **Strategy Decision**:
    * The `DecisionAgent` analyzes the complexity and need for external knowledge.
    * **Direct**: For greetings, general knowledge questions, or simple logic.
    * **RAG**: For questions about specific processes, internal documentation, or data requiring fact-checking.
4. **Execution**:
    * **Via Direct**: The `DirectAnswerAgent` generates the response using only the LLM's knowledge.
    * **Via RAG**: The system fetches the top relevant chunks in Qdrant, concatenates the context, and sends it along with the question to the `RAGAnswerAgent` to generate the grounded response.
5. **Output**: A standardized JSON object containing the status, response, strategy used, and metadata (such as time or decision reasons).

---

## 4. Execution Instructions

### Prerequisites

* Python 3.10+
* **Environment Configuration**: Create a `.env` file in the root directory (copy from `.env.example`) and add your OpenAI API Key:

  ```env
  OPENAI_API_KEY=your_api_key_here
  ```

* NLTK Data (downloaded automatically on first run: `punkt_tab`, `averaged_perceptron_tagger`).

### Installation

```bash
pip install -r requirements.txt
```

### Executing via API (FastAPI)

To start the API server:

```bash
uvicorn src.server:app --reload
```

Interactive documentation is available at `http://localhost:8000/docs`.

**Example Request:**

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "Hello", "role": "standard"}'
```

**Ingestion Request:**

You can trigger the ingestion process via the API. This will process documents in the specified directory (default: "docs").

```bash
curl -X POST "http://localhost:8000/ingest" \
     -H "Content-Type: application/json" \
     -d '{"directory_path": "docs"}'
```

The system supports ingestion of `.txt`, `.md`, and `.pdf` files. It automatically handles text extraction, chunking, and vectorization.

### Running via Docker

To run the full containerized application:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

---

## 5. Trade-offs and Technical Decisions

* **Agent-Based Architecture vs. Simple Chain**:
  * *Decision*: Opted for specialized agents (Separate Classes) instead of a single long "chain".
  * *Trade-off*: Slightly increases code complexity and latency (multiple LLM calls), but gains immensely in **modularity**, **testability**, and **debuggability**. Each agent can be optimized or replaced independently.

* **HuggingFace Embeddings (all-MiniLM-L6-v2)**:
  * *Decision*: Lightweight and efficient open-source model.
  * *Trade-off*: Lower cost (zero API cost for embeddings) and speed. May have lower semantic precision than larger models (e.g., OpenAI text-embedding-3-large) in very complex domains, but is excellent for general purposes.

* **Explicit Compliance Layer**:
  * *Decision*: Separate security from business logic.
  * *Trade-off*: Adds an extra "hop" in all requests. However, ensures that no business logic (or database retrieval) occurs with malicious inputs, protecting the infrastructure.

* **Centralized Logging vs Print**:
  * *Decision*: Use of a globally configured logger instead of `print`.
  * *Trade-off*: Allows better traceability, log level control (INFO, ERROR), and consistent formatting, essential for production monitoring.

---

## 6. Example Questions and Answers

1. **What is William Bassalobre’s professional background?**

    **Expected Answer:**
    William Bassalobre is a Software Engineer and Full Stack Developer with over 8 years of experience building scalable web applications. He specializes in Node.js, React, AWS, cloud-native architectures, and AI-powered systems, including RAG solutions.

2. **What are William’s main technical skills?**

    **Expected Answer:**
    His main technical skills include Retrieval-Augmented Generation (RAG), FastAPI, LlamaIndex, Node.js, TypeScript, Python, React, AWS, Docker, Terraform, and CI/CD pipelines.

3. **Where is William currently located?**

    **Expected Answer:**
    William is based in Maringá, Paraná, Brazil.

4. **What AI-related technologies and architectures does William work with?**

    **Expected Answer:**
    William works with AI-powered applications, including RAG systems using LlamaIndex and Agno, MCP (Model Context Protocol) servers, event-driven microservices, and robust cloud infrastructure.

5. **What programming languages does William have professional experience with?**

    **Expected Answer:**
    William has professional experience with JavaScript, TypeScript, Python, PHP, and has also worked with Elixir and Java in specific projects.

6. **What type of projects has William worked on throughout his career?**

    **Expected Answer:**
    William has worked on projects for startups and enterprise companies, including payment processing systems, educational platforms, internal management systems, open banking solutions, AI-powered applications, and cloud-based microservices.

7. **What is William’s educational background?**

    **Expected Answer:**
    William holds a Bachelor’s degree in Computer Software Engineering from Unicesumar and a Mechatronics Technician degree from Senai Maringá.
