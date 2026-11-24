# ChatbotFVG — Assistente di viaggio per il Friuli Venezia Giulia

Prototipo di assistente agentico (Traccia B) che aiuta il turista a organizzare una visita in regione:
luoghi da visitare, come arrivare, dove mangiare, tenendo conto del meteo e delle distanze tra le località.

- **LLM locale** servito da LM Studio (API compatibile OpenAI)
- **Agente** LangGraph con numero massimo di iterazioni esplicito
- **Strumenti MCP**: `cerca_luoghi`, `meteo`, `distanza`
- **RAG** su pagine Wikivoyage in italiano (CC BY-SA), indicizzate in Qdrant
- **Interfaccia web** React con conversazioni persistite su PostgreSQL

## Architettura

```
frontend (React + nginx)  ──/api──▶  backend (FastAPI + agente LangGraph)  ──▶  LM Studio (host)
                                         │            │
                                         │            └──MCP──▶ mcp_server ──▶ Qdrant
                                         ▼                         └──▶ Open-Meteo
                                     PostgreSQL
ingestion (una tantum) ──▶ Wikivoyage API ──▶ chunk + embedding ──▶ Qdrant
```

| Cartella      | Contenuto                                                          | Responsabile |
|---------------|--------------------------------------------------------------------|--------------|
| `backend/`    | API conversazioni, database, agente LangGraph, client MCP          | Applicazione / Agente |
| `mcp_server/` | Server MCP con gli strumenti `cerca_luoghi`, `meteo`, `distanza`   | Agente / Retrieval |
| `ingestion/`  | Download, pulizia, chunking, embedding e indicizzazione Wikivoyage | Documenti e retrieval |
| `frontend/`   | Interfaccia web                                                    | Applicazione |
| `docs/`       | Rapporto di valutazione e casi di prova                            | Tutti |

## Prerequisiti

- Docker Desktop (con Docker Compose v2)
- [LM Studio](https://lmstudio.ai/) con server locale attivo sulla porta `1234` e caricati:
  - un modello chat con supporto tool calling (es. `qwen2.5-7b-instruct`)
  - un modello di embedding (es. `text-embedding-nomic-embed-text-v1.5`)

## Configurazione

```bash
cp .env.example .env
```

Adattare in `.env` almeno `LLM_MODEL` ed `EMBEDDING_MODEL` ai nomi dei modelli caricati in LM Studio.

## Ingestion dei documenti

Con Qdrant avviato, eseguire una volta:

```bash
docker compose up -d qdrant
docker compose --profile ingestion run --rm ingestion
```

### Località del corpus

Trieste, Udine, Pordenone, Gorizia, Cividale del Friuli, Aquileia, Grado, Lignano Sabbiadoro, Palmanova,
San Daniele del Friuli, Venzone, Gemona del Friuli, Tarvisio, Sauris, Spilimbergo, Sacile, Duino-Aurisina,
Muggia, Tolmezzo, Valvasone Arzene.

(Elenco definito in `ingestion/ingestion/localita.py`.)

## Avvio

```bash
docker compose up --build
```

- Interfaccia: http://localhost:5173
- API backend: http://localhost:8000/api/health

## Formati concordati tra i componenti

> Bozza da confermare all'avvio del lavoro.

### Risultato di `cerca_luoghi`

```json
{
  "risultati": [
    {
      "testo": "…",
      "localita": "Cividale del Friuli",
      "sezione": "Da vedere",
      "url": "https://it.wikivoyage.org/wiki/Cividale_del_Friuli",
      "punteggio": 0.83
    }
  ],
  "errore": null
}
```

Errori: `nessun_risultato`, `localita_non_coperta`.

### Messaggi interfaccia ↔ backend

`POST /api/conversations/{id}/messages` — richiesta:

```json
{ "content": "Sabato vorrei visitare Cividale…" }
```

Risposta:

```json
{
  "id": "…",
  "role": "assistant",
  "content": "markdown…",
  "sources": [{ "documento": "Cividale del Friuli", "sezione": "Da vedere", "url": "…" }],
  "tool_calls": [{ "nome": "meteo", "argomenti": {}, "esito": "ok", "durata_ms": 412 }],
  "error": null,
  "created_at": "2026-11-24T12:00:00Z"
}
```

Altri endpoint: `GET /api/conversations`, `POST /api/conversations`, `GET /api/conversations/{id}`.

## Licenze e fonti

I contenuti testuali provengono da [Wikivoyage in italiano](https://it.wikivoyage.org/) (licenza CC BY-SA);
ogni risposta cita la pagina e la sezione di origine. Dati meteo da [Open-Meteo](https://open-meteo.com/).
