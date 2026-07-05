# Hidden Trusted Web Evidence Tool

OcuCare now includes a backend-only web evidence layer for text chat answers.
It is not shown as a separate UI tool. When configured, the `/get` text route can quietly search trusted medical websites and add that evidence to the chatbot context.

## Why This Helps The Research

- Gives the chatbot a clear difference from a plain PDF-only Gemini workflow.
- Supports current ophthalmology guidance when the local PDF knowledge base is limited.
- Keeps the feature medically safer by using an allowlist of trusted domains.
- Shows source evidence in the answer footer when web evidence is actually used.

## Supported Providers

Use one of these providers:

```env
TRUSTED_WEB_EVIDENCE_ENABLED=true
TRUSTED_WEB_EVIDENCE_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_key
```

or:

```env
TRUSTED_WEB_EVIDENCE_ENABLED=true
TRUSTED_WEB_EVIDENCE_PROVIDER=brave
BRAVE_SEARCH_API_KEY=your_brave_search_key
```

Optional settings:

```env
TRUSTED_WEB_EVIDENCE_MAX_RESULTS=3
TRUSTED_WEB_EVIDENCE_TIMEOUT_SECONDS=6
TRUSTED_WEB_EVIDENCE_ALLOWED_DOMAINS=nei.nih.gov,medlineplus.gov,aao.org,cdc.gov,who.int,ncbi.nlm.nih.gov,nhs.uk,mayoclinic.org,aoa.org
```

## When It Runs

The tool runs only for eye-health questions that appear to need current or external evidence, such as questions containing:

- latest, recent, current, updated
- guideline, guidelines
- research, study, evidence
- source, website, article, news

Normal symptom questions and image screening flows continue to use the existing RAG, CNN, and multimodal logic.

## Safety Design

- Local Pinecone RAG evidence is still used first.
- Web evidence is injected into the LLM prompt as source snippets, not as instructions.
- Web citations use `[W1]`, `[W2]`, etc. so they do not collide with PDF/RAG citations like `[1]`.
- The query is minimized before external search by stripping obvious emails, phone-like numbers, and age phrases.
- Search failures fail closed and the app continues with the existing chatbot behavior.
