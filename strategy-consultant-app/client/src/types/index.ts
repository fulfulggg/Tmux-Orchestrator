export interface Project {
  id: number;
  name: string;
  client_name: string;
  industry: string;
  theme: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Argument {
  id: number;
  project_id: number;
  major_point: string;
  medium_point: string;
  minor_point: string;
  hypothesis: string;
  verification_approach: string;
  required_data: string;
  assignee: string;
  priority: 'high' | 'medium' | 'low';
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold';
  deadline: string;
  ai_consensus: number;
  ai_feedback: string;
  created_at: string;
  updated_at: string;
}

export interface PastCase {
  id: number;
  industry: string;
  theme: string;
  tags: string;
  project_scale: string;
  region: string;
  urgency: string;
  outcome: string;
  arguments_json: string;
  lessons_learned: string;
  created_at: string;
}

export interface ClientInfo {
  id: number;
  project_id: number;
  company_name: string;
  industry: string;
  business_scale: string;
  revenue: string;
  employees: string;
  regions: string;
  business_model: string;
  key_challenges: string;
  stakeholders: string;
  decision_process: string;
  kpis: string;
  financial_info: string;
  competitive_landscape: string;
  past_initiatives: string;
}

export interface AIFeedback {
  claude_feedback: string;
  openai_feedback: string;
  gemini_feedback: string;
  consensus: number;
  overall_feedback: string;
}