``` mermaid
flowchart TD
    A[Campaign Brief] --> B[Input Validation]
    B --> C[LLM-Based Extraction]
    B --> D[Rule-Based Extraction]
    C --> E[Merge Candidate Requirements]
    D --> E
    E --> F[Evidence and Schema Validation]
    F --> G{Conflicts or Ambiguity?}
    G -->|Yes| H[Flag for Clarification]
    G -->|No| I[Structured Requirements]
    H --> I
```