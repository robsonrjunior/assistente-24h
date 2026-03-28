import hmac
import os

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query, status
from assistant.assistant import answer_question
import uvicorn

load_dotenv()

app = FastAPI()


def _validate_token(token: str) -> None:
    expected_token = os.getenv("WEBHOOK_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WEBHOOK_TOKEN nao configurado",
        )

    if not hmac.compare_digest(token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )

@app.post("/send_message")
def send_message(
    token: str = Query(..., description="Auth token"),
    message: str = Body(..., embed=True, description="Message for the assistant"),
):
    _validate_token(token)
    answer = answer_question(message)
    return {"answer": answer}

def start():
    """Starts the FastAPI server to receive messages."""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start()
