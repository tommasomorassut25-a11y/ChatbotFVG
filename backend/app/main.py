from fastapi import FastAPI

app = FastAPI(title="ChatbotFVG - backend")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# TODO: router conversazioni (app/api), agente LangGraph (app/agent), modelli DB (app/db)
