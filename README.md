# Multi-Agent RAG System

## 1. Visão Geral da Arquitetura

Este projeto implementa um sistema multi-agentes orquestrado para responder a consultas de usuários de forma inteligente e segura. A arquitetura é projetada para decidir dinamicamente a melhor estratégia de resposta (Direta ou RAG - Retrieval-Augmented Generation) após passar por uma camada de verificação de conformidade.

### Componentes Principais

* **Orchestrator**: O núcleo do sistema. Gerencia o ciclo de vida da requisição, instanciando agentes e controlando o fluxo de dados entre eles.
* **Compliance Agent**: A primeira linha de defesa. Analisa a consulta do usuário em busca de injeção de prompt, conteúdo malicioso ou violações de políticas. Tópicos bloqueados incluem: Violência, Atos Ilegais, Conteúdo Sexual, Política, Religião, Integridade Corporativa (Demissões), Drogas e PII. Se a consulta for rejeitada, o fluxo é interrompido imediatamente.
* **Decision Agent**: O "cérebro" estratégico. Avalia consultas seguras para determinar se o sistema deve responder diretamente (para perguntas gerais/conversa) ou usar RAG (para perguntas que exigem contexto específico do conhecimento ingerido).
* **Direct Answer Agent**: Especializado em respostas diretas e conversacionais que não requerem busca em banco de dados vetorial.
* **RAG Retrieval**: Módulo responsável por buscar documentos relevantes no banco vetorial **Qdrant** utilizando embeddings **HuggingFace** (`all-MiniLM-L6-v2`).
* **RAG Answer Agent**: Sintetiza uma resposta final utilizando o contexto recuperado pelo módulo de Retrieval, garantindo que a resposta seja fundamentada nos dados.
* **API Layer**: Interface RESTful construída com **FastAPI** para integração externa.

---

## 2. Diagrama de Fluxo (Mermaid)

```mermaid
graph TD
    User([Usuário]) -->|Envia Consulta| Orchestrator[Orchestrator]
    
    subgraph "Camada de Segurança"
        Orchestrator --> Compliance{Compliance Agent}
        Compliance -->|Bloqueado| BlockedEnd([Fim: Resposta de Bloqueio])
    end
    
    subgraph "Camada de Decisão"
        Compliance -->|Aprovado| Decision{Decision Agent}
        Decision -->|Estratégia: Direct| DirectAgent[Direct Answer Agent]
        Decision -->|Estratégia: RAG| RAGRetrieval[RAG Retrieval<br/>(Qdrant + HF Embeddings)]
    end
    
    subgraph "Camada de Execução"
        DirectAgent --> Result([Resposta Final])
        RAGRetrieval -->|Contexto| RAGAgent[RAG Answer Agent]
        RAGAgent --> Result
    end

    style Compliance fill:#f96,stroke:#333,stroke-width:2px
    style Decision fill:#69f,stroke:#333,stroke-width:2px
    style RAGRetrieval fill:#6f9,stroke:#333,stroke-width:2px
```

---

## 3. Explicação do Fluxo

1. **Entrada**: O usuário envia uma consulta (query) e opcionalmente um papel (role).
2. **Verificação de Compliance**:
    * O `ComplianceAgent` analisa a entrada.
    * **Se inseguro**: Retorna um status de bloqueio com a razão (ex: *Prompt Injection*). O Orchestrator retorna imediatamente.
    * **Se seguro**: O fluxo continua, possivelmente com uma versão "sanitizada" da query.
3. **Decisão de Estratégia**:
    * O `DecisionAgent` analisa a complexidade e a necessidade de conhecimento externo.
    * **Direct**: Para saudações, perguntas de conhecimento geral ou lógica simples.
    * **RAG**: Para perguntas sobre processos específicos, documentação interna ou dados que requerem fact-checking.
4. **Execução**:
    * **Via Direct**: O `DirectAnswerAgent` gera a resposta usando apenas o conhecimento do LLM.
    * **Via RAG**: O sistema busca os top-chkunks relevantes no Qdrant, concatena o contexto e o envia junto com a pergunta para o `RAGAnswerAgent` gerar a resposta fundamentada.
5. **Saída**: Um objeto JSON padronizado contendo o status, a resposta, a estratégia utilizada e metadados (como tempo ou razões de decisão).

---

## 4. Instruções de Execução

### Pré-requisitos

* Python 3.10+
* Chave de API da OpenAI definida no ambiente (`OPENAI_API_KEY`).
* NLTK Data (baixado automaticamente na primeira execução: `punkt_tab`, `averaged_perceptron_tagger`).

### Instalação

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

## 5. Trade-offs e Decisões Técnicas

* **Arquitetura Baseada em Agentes vs. Chain Simples**:
  * *Decisão*: Optou-se por agentes especializados (Classes separadas) em vez de uma única "chain" longa.
  * *Trade-off*: Aumenta ligeiramente a complexidade do código e a latência (múltiplas chamadas de LLM), mas ganha-se imensamente em **modularidade**, **testabilidade** e **capacidade de depuração**. Cada agente pode ser otimizado ou substituído independentemente.

* **Embeddings HuggingFace (all-MiniLM-L6-v2)**:
  * *Decisão*: Modelo open-source leve e eficiente.
  * *Trade-off*: Menor custo (zero API cost para embeddings) e rapidez. Pode ter menor precisão semântica que modelos maiores (ex: OpenAI text-embedding-3-large) em domínios muito complexos, mas é excelente para propósitos gerais.

* **Camada de Compliance Explícita**:
  * *Decisão*: Separar a segurança da lógica de negócio.
  * *Trade-off*: Adiciona um "hop" extra em todas as requisições. Porém, garante que nenhuma lógica de negócio (ou recuperação de banco de dados) ocorra com inputs maliciosos, protegendo a infraestrutura.

* **Logging Centralizado vs Print**:
  * *Decisão*: Uso de um logger configurado globalmente em vez de `print`.
  * *Trade-off*: Permite melhor rastreabilidade, controle de níveis de log (INFO, ERROR) e formatação consistente, essencial para monitoramento em produção.

---

## 6. Exemplos de Perguntas e Respostas

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
