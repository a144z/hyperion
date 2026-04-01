# main.py

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from .lean_interface import LeanInterface
from .search import HyperionProver
from .config import config
from .training import nightly_training
from .selfplay import SelfPlayGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global instances
lean_interface = LeanInterface(num_workers=config.lean_worker_count)

class ProveRequest(BaseModel):
    theorem: str

class ProveResponse(BaseModel):
    proof: str
    success: bool

@app.post("/prove", response_model=ProveResponse)
async def prove_theorem(req: ProveRequest):
    try:
        prover = HyperionProver(lean_interface)
        proof_tactics = await prover.prove(req.theorem)
        if proof_tactics is None:
            return ProveResponse(proof="", success=False)
        proof_str = prover.extract_proof(proof_tactics)
        return ProveResponse(proof=proof_str, success=True)
    except Exception as e:
        logger.exception("Error during proving")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/selfplay")
async def start_selfplay():
    generator = SelfPlayGenerator(lean_interface)
    await generator.generate_curriculum(num_problems=10)
    return {"status": "self‑play completed"}

@app.post("/train")
async def trigger_training():
    # In production, you'd run this as a background task
    asyncio.create_task(nightly_training())
    return {"status": "training started"}

@app.on_event("shutdown")
async def shutdown():
    await lean_interface.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)