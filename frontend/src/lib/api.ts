const API_BASE_URL = 'http://localhost:5000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface Persona {
  id: string;
  name: string;
  avatar: string;
  description: string;
  traits: string[];
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
}

export const apiClient = new ApiClient(API_BASE_URL); 