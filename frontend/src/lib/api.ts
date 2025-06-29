const API_BASE_URL = 'http://127.0.0.1:5000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface Persona {
  id: string;
  name: string;
  avatar: string;
  description: string;
  role?: string;
  traits?: string[];
}

export interface CustomPersonaData {
  name: string;
  avatar: string;
  description: string;
  traits: string[];
}

export interface PersonaReaction {
  persona_id: string;
  name: string;
  avatar: string;
  reaction: string;
  sentiment: string;
  sentiment_score: number;
}

export interface GroupDiscussionMessage {
  id: string;
  persona_id: string;
  persona_name: string;
  avatar: string;
  content: string;
  sentiment: string;
  sentiment_score: number;
  timestamp: string;
  round: number;
}

export interface FocusGroupResult {
  session_id: string;
  campaign_description: string;
  initial_reactions: PersonaReaction[];
  discussion_messages: GroupDiscussionMessage[];
  sentiment_intervals: Array<{
    round: number;
    timestamp: string;
    overall_sentiment: number;
    persona_sentiments: Record<string, number>;
  }>;
  final_summary: {
    overall_sentiment: number;
    sentiment_shift: number;
    key_insights: string[];
    recommendations: string[];
  };
}

export interface SessionData {
  session_type: "interview" | "focus-group";
  session_name: string;
  purpose: string;
  goals?: string[];
  selected_personas: string[];
  messages: any[];
  duration: number;
  insights?: string[];
  key_takeaways?: string[];
  start_time?: string;
  end_time?: string;
  enhanced_personas?: Array<{
    id: string;
    name: string;
    role: string;
    avatar: string;
    description: string;
  }>;
}

export interface SavedSession {
  filename: string;
  metadata: {
    session_type: string;
    session_name: string;
    timestamp: number;
    created_at: string;
    duration_seconds: number;
  };
  session_data: SessionData;
}

export interface DashboardSession {
  id: string;
  name: string;
  session_type: "interview" | "focus-group" | "unknown";
  persona_avatars: string[];
  start_date: string;
  duration: number;
  status: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        return { error: errorData.error || `HTTP ${response.status}` };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return { error: error instanceof Error ? error.message : 'Network error' };
    }
  }

  async getPersonas(): Promise<ApiResponse<Persona[]>> {
    return this.request('/api/personas');
  }

  async getDisplayPersonas(): Promise<ApiResponse<Persona[]>> {
    return this.request('/display-personas');
  }

  async savePersona(personaData: Omit<Persona, 'id'>): Promise<ApiResponse<{ message: string; filename: string; filepath: string }>> {
    return this.request('/save-persona', {
      method: 'POST',
      body: JSON.stringify(personaData),
    });
  }

  async getSavedPersonas(): Promise<ApiResponse<Persona[]>> {
    return this.request('/api/saved-personas');
  }

  async deletePersona(filename: string): Promise<ApiResponse<{ message: string }>> {
    return this.request(`/api/delete-persona/${filename}`, {
      method: 'DELETE',
    });
  }

  async simpleInteraction(question: string, personas: string[]): Promise<ApiResponse<{
    question: string;
    reactions: PersonaReaction[];
    timestamp: string;
  }>> {
    return this.request('/api/simple-interaction', {
      method: 'POST',
      body: JSON.stringify({
        question,
        personas
      }),
    });
  }

  async groupDiscussion(question: string, personas: string[], initialReactions: PersonaReaction[]): Promise<ApiResponse<{
    question: string;
    discussion_messages: GroupDiscussionMessage[];
    timestamp: string;
  }>> {
    return this.request('/api/group-discussion', {
      method: 'POST',
      body: JSON.stringify({
        question,
        personas,
        initial_reactions: initialReactions
      }),
    });
  }

  async focusGroupSimulation(campaignDescription: string, personas: string[], goals: string[]): Promise<ApiResponse<FocusGroupResult>> {
    return this.request('/api/focus-group', {
      method: 'POST',
      body: JSON.stringify({
        campaign_description: campaignDescription,
        personas,
        goals
      }),
    });
  }

  async focusGroupStart(campaignDescription: string, personas: string[], goals: string[]): Promise<ApiResponse<{
    phase: string;
    messages: GroupDiscussionMessage[];
    timestamp: string;
  }>> {
    return this.request('/api/focus-group-start', {
      method: 'POST',
      body: JSON.stringify({
        campaign_description: campaignDescription,
        personas,
        goals
      }),
    });
  }

  async focusGroupRound(campaignDescription: string, personas: string[], roundNumber: number, previousMessages: any[]): Promise<ApiResponse<{
    phase: string;
    round_number: number;
    messages: GroupDiscussionMessage[];
    timestamp: string;
  }>> {
    return this.request('/api/focus-group-round', {
      method: 'POST',
      body: JSON.stringify({
        campaign_description: campaignDescription,
        personas,
        round_number: roundNumber,
        previous_messages: previousMessages
      }),
    });
  }

  async createCustomPersona(personaData: CustomPersonaData): Promise<ApiResponse<{ success: boolean; persona: Persona; message: string }>> {
    return this.request('/api/custom-persona', {
      method: 'POST',
      body: JSON.stringify(personaData),
    });
  }

  async healthCheck(): Promise<ApiResponse<{
    status: string;
    timestamp: string;
    gemini_configured: boolean;
    agents_loaded: number;
    tasks_loaded: number;
  }>> {
    return this.request('/api/health');
  }

  async saveSession(sessionData: SessionData): Promise<ApiResponse<{ message: string; filename: string; filepath: string }>> {
    return this.request('/api/save-session', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async getSessions(): Promise<ApiResponse<SavedSession[]>> {
    return this.request('/api/get-sessions');
  }

  async getDashboardSessions(): Promise<ApiResponse<DashboardSession[]>> {
    return this.request('/api/dashboard-sessions');
  }

  async generateInsights(sessionData: SessionData): Promise<ApiResponse<{ insights: string[]; generated_at: string }>> {
    return this.request('/api/generate-insights', {
      method: 'POST',
      body: JSON.stringify({ session_data: sessionData }),
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL); 