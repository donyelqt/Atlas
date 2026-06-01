export interface AnalysisSummary {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  repo_url: string;
  framework?: string | null;
  language?: string | null;
  file_count: number;
  directory_count: number;
  architecture_type?: string | null;
  complexity?: string | null;
  error?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  path: string;
  language?: string | null;
  size: number;
  children?: string[];
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  label?: string | null;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface FileInfo {
  path: string;
  name: string;
  type: string;
  language?: string | null;
  size: number;
  content_preview?: string | null;
  imports?: string[];
  exports?: string[];
  functions?: string[];
  classes?: string[];
}

export interface ModuleInfo {
  name: string;
  path: string;
  files: FileInfo[];
  dependencies: string[];
  description?: string | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface RepoUrlRequest {
  repo_url: string;
}

export interface ChatRequest {
  analysis_id: string;
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources?: string[];
}

export interface ArchitectureSummary {
  architecture_type?: string | null;
  key_modules?: { name: string; description?: string }[];
  complexity?: string | null;
  summary?: string;
}

export interface OnboardingPlan {
  steps?: { title: string; description: string; files: string[]; estimated_minutes: number }[];
  total_estimated_minutes?: number;
  prerequisites?: string[];
}
