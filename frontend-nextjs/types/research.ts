export interface ResearchConfig {
  depth?: "quick" | "standard" | "comprehensive";
  max_iterations?: number;
  max_web_results?: number;
}

export interface ResearchRequest {
  query: string;
  config?: ResearchConfig;
}

export interface ResearchResponse {
  session_id: string;
  query: string;
  response: string; // Single AI-generated answer with citations
  sources: Source[];
  timestamp?: string;
}

export interface Source {
  title: string;
  url: string;
  type?: "web";
}

export interface ProgressUpdate {
  status: "started" | "in_progress" | "complete" | "error";
  stage?: string;
  message?: string;
  session_id?: string;
  query?: string;
  data?: {
    web_results?: number;
    reddit_posts?: number;
    scraped_content?: number;
  };
  result?: ResearchResponse;
}
