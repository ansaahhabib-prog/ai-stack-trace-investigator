export interface Cause {
  description: string;
  likelihood: string;
  fix_suggestion: string;
}

export interface AnalysisResult {
  causes: Cause[];
  missing_evidence: string[];
  reproduction_code: string | null;
}

export interface SandboxResult {
  status: string;
  exit_code?: number;
  logs?: string;
  message?: string;
}
