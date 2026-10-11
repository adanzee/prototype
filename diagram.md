``` mermaid 
graph TD
    %% System Flow Definition
    Brief[Campaign Brief] --> Req[Requirement Understanding]
    
    Req --> Market[Market / Audience Research]
    Req --> Brand[Brand Campaign Context]
    
    Market --> Retrieval[Knowledge Retrieval]
    Brand --> Retrieval
    
    Retrieval --> Guidance[Market Aware Guidance]
    Guidance --> Design[Campaign Design]
    Design --> Analysis[Design Analysis<br/><i>VLLM Reasoning</i>]
    Analysis --> Recs[Explainable Recommendations]

    %% Styling classes
    classDef process fill:#f9f,stroke:#333,stroke-width:2px;
    classDef input fill:#bbf,stroke:#333,stroke-width:1px;
    class Brief,Req,Market,Brand,Retrieval,Guidance,Design,Analysis,Recs process;
    ```