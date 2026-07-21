import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field

class Cause(BaseModel):
    description: str = Field(description="Description of the likely cause.")
    likelihood: float = Field(description="Likelihood score between 0 and 1.")
    fix_suggestion: str = Field(description="Suggestion on how to fix this cause.")

class AnalysisResult(BaseModel):
    causes: list[Cause] | None = Field(default=None, description="List of likely causes ranked by likelihood (descending).")
    missing_evidence: list[str] | None = Field(default=None, description="List of questions or missing information needed to narrow down the cause.")
    reproduction_code: str | None = Field(default=None, description="Optional Python code snippet that might reproduce the issue.")

class StackTraceAnalyzer:
    def __init__(self):
        # Assumes OPENAI_API_KEY is in environment or loaded via dotenv
        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = "gemini-2.5-flash" # Good for structured output

    def analyze(self, error_input: str, code_context: str = "") -> AnalysisResult:
        prompt = f"""
        You are an expert software debugger.
        Analyze the following error output / stack trace:
        
        <error_input>
        {error_input}
        </error_input>
        
        Code context (if any):
        <code_context>
        {code_context}
        </code_context>
        
        Please provide:
        1. A ranked list of likely causes (with fix suggestions).
        2. If the issue is ambiguous, a list of missing evidence (e.g., "What are the values of variables X and Y?", "Please provide the log prior to this error").
        3. If possible, a standalone Python code snippet that reproduces the issue.
        """
        
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful debugging assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=AnalysisResult,
        )
        
        return response.choices[0].message.parsed
