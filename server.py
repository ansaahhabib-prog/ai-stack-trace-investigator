import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

load_dotenv()

from analyzer import StackTraceAnalyzer
from sandbox import DockerSandbox

app = FastAPI(title="AI Stack Trace Investigator API")

# Allow requests from Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    error_input: str
    code_context: Optional[str] = None

class RunSandboxRequest(BaseModel):
    reproduction_code: str

@app.post("/api/analyze")
async def analyze_stack_trace(request: AnalyzeRequest):
    if not request.error_input or not request.error_input.strip():
        raise HTTPException(status_code=400, detail="Error input is required.")
        
    analyzer = StackTraceAnalyzer()
    try:
        # Assuming result is a Pydantic model or dataclass that can be converted to dict
        result = analyzer.analyze(request.error_input, request.code_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze: {str(e)}")

@app.post("/api/run-sandbox")
async def run_sandbox(request: RunSandboxRequest):
    if not request.reproduction_code or not request.reproduction_code.strip():
        raise HTTPException(status_code=400, detail="Reproduction code is required.")
        
    sandbox = DockerSandbox()
    try:
        res = sandbox.run_reproduction(request.reproduction_code)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
