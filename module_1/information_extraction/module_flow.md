``` mermaid
graph TD
    A[1. Parse brief to clean text + positions<br/>txt / docx / pdf] --> B[2. Section segmentation<br/>heading rules]
    B --> C[3. Rule layer<br/>regex, dictionaries, dateparser, NER]
    C --> D{All fields<br/>filled and valid?}
    D -- yes --> G[6. Verification<br/>grounding, format, logic]
    D -- no --> E[4. Targeted chunk retrieval<br/>per missing field]
    E --> F[5. Small LLM<br/>schema + evidence quote]
    F --> G
    G -- pass --> H[7. Gap and ambiguity detection]
    G -- fail --> R[Retry once with error message<br/>or escalate to stronger model]
    R --> G
    R -- still failing --> N[Mark needs_review]
    N --> H
    H --> I[8. Requirement JSON<br/>+ downstream hand-off keys]

    classDef rule fill:#dff0d8,stroke:#3c763d,stroke-width:1px,color:#000000;
    classDef llm fill:#d9edf7,stroke:#31708f,stroke-width:1px,color:#000000;
    classDef check fill:#fcf8e3,stroke:#8a6d3b,stroke-width:1px,color:#000000;
    classDef out fill:#e8daef,stroke:#6c3483,stroke-width:1px,color:#000000;

    class A,B,C,E rule;
    class F llm;
    class D,G,R,N,H check;
    class I out;
```