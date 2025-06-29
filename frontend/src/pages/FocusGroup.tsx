import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ArrowLeft,
  Play,
  Pause,
  Square,
  Users,
  Clock,
  MessageSquare,
  TrendingUp,
  Download,
  Filter,
  BarChart3,
  PieChart,
  Activity,
  Star,
  ThumbsUp,
  Send,
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface Persona {
  id: string;
  name: string;
  avatar: string;
  description: string;
  role?: string;
  traits?: string[];
  // Display properties for focus group
  sentiment?: "positive" | "neutral" | "negative";
  npsScore?: number;
  csatScore?: number;
  keyPoints?: string[];
  questions?: string[];
}

interface Message {
  id: string;
  personaId: string;
  personaName: string;
  avatar: string;
  content: string;
  timestamp: Date;
  sentiment: "positive" | "neutral" | "negative";
}

interface SessionData {
  name: string;
  purpose: string;
  goals: string[];
  personas: Persona[];
  startTime?: Date;
  endTime?: Date;
  messages: Message[];
  overallNPS: number;
  overallCSAT: number;
  avgSentiment: number;
}

const FocusGroup = () => {
  const [currentStep, setCurrentStep] = useState<'config' | 'chat' | 'analytics'>('config');
  const [sessionData, setSessionData] = useState<SessionData>({
    name: 'Dog Vitals Monitoring Tool Focus Group',
    purpose: 'To gather qualitative insights into consumer perceptions and preferences regarding a vitals monitoring tool for dogs.',
    goals: [
      'To identify key drivers of interest and potential barriers to adoption for the vitals monitoring tool.',
      'To understand consumer reactions to proposed features, branding, and pricing.',
      'To uncover unmet needs or pain points that the new product could address.'
    ],
    personas: [],
    messages: [],
    overallNPS: 0,
    overallCSAT: 0,
    avgSentiment: 0,
  });
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionDuration, setSessionDuration] = useState(0);
  const [newGoal, setNewGoal] = useState('');
  const [availablePersonas, setAvailablePersonas] = useState<Persona[]>([]);
  const [isLoadingPersonas, setIsLoadingPersonas] = useState(true);
  const [streamingStatus, setStreamingStatus] = useState<string>('');
  const [currentRound, setCurrentRound] = useState<number>(0);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSessionActive && currentStep === 'chat') {
      interval = setInterval(() => {
        setSessionDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isSessionActive, currentStep]);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [sessionData.messages]);

  // Load personas from API
  useEffect(() => {
    const loadPersonas = async () => {
      try {
        const response = await apiClient.getDisplayPersonas();
        if (response.error) {
          console.error('Failed to load personas:', response.error);
          // Fallback to empty array if API fails
          setAvailablePersonas([]);
        } else if (response.data) {
          // Transform API personas to include focus group display properties
          const transformedPersonas: Persona[] = response.data.map((persona, index) => ({
            ...persona,
            role: persona.role,
            description: persona.description,
            sentiment: (["positive", "neutral", "negative"][index % 3]) as "positive" | "neutral" | "negative",
            npsScore: Math.floor(Math.random() * 6) + 4, // 4-9
            csatScore: Math.random() * 2 + 3, // 3-5
            keyPoints: ["Key insight 1", "Key insight 2", "Key insight 3"], // Default key points since traits are empty
            questions: [`What are your thoughts on this?`, `How does this align with your goals?`] // Default questions
          }));
          setAvailablePersonas(transformedPersonas);
        }
      } catch (error) {
        console.error('Network error loading personas:', error);
        setAvailablePersonas([]);
      } finally {
        setIsLoadingPersonas(false);
      }
    };

    loadPersonas();
  }, []);

  // Mock conversation generator
  const generateMockConversation = () => {
    const mockMessages: Message[] = [
      {
        id: '1',
        personaId: '1',
        personaName: 'Sarah Marketing',
        avatar: '👩‍💼',
        content: 'I think this product has great potential for our target market. The user experience seems intuitive.',
        timestamp: new Date(Date.now() - 300000),
        sentiment: 'positive'
      },
      {
        id: '2',
        personaId: '4',
        personaName: 'Sales Tom',
        avatar: '👨‍💼',
        content: 'I\'m concerned about the pricing. Our clients might find it too expensive compared to alternatives.',
        timestamp: new Date(Date.now() - 240000),
        sentiment: 'negative'
      },
      {
        id: '3',
        personaId: '2',
        personaName: 'Tech Mike',
        avatar: '👨‍💻',
        content: 'From a technical standpoint, we need to consider the API limitations and scalability issues.',
        timestamp: new Date(Date.now() - 180000),
        sentiment: 'neutral'
      },
      {
        id: '4',
        personaId: '3',
        personaName: 'Customer Lisa',
        avatar: '👩‍🔬',
        content: 'The innovation aspect is exciting! This could really differentiate us in the market.',
        timestamp: new Date(Date.now() - 120000),
        sentiment: 'positive'
      },
      {
        id: '5',
        personaId: '5',
        personaName: 'Data Anna',
        avatar: '👩‍🎓',
        content: 'We should focus on the data accuracy and reporting capabilities. What metrics can we actually track?',
        timestamp: new Date(Date.now() - 60000),
        sentiment: 'neutral'
      }
    ];

    setSessionData(prev => ({
      ...prev,
      messages: mockMessages,
      overallNPS: 6.4,
      overallCSAT: 3.7,
      avgSentiment: 0.6
    }));
  };

  const addGoal = () => {
    if (newGoal.trim()) {
      setSessionData(prev => ({
        ...prev,
        goals: [...prev.goals, newGoal.trim()]
      }));
      setNewGoal('');
    }
  };

  const removeGoal = (index: number) => {
    setSessionData(prev => ({
      ...prev,
      goals: prev.goals.filter((_, i) => i !== index)
    }));
  };

  const togglePersonaSelection = (persona: Persona) => {
    setSessionData(prev => {
      const isSelected = prev.personas.some(p => p.id === persona.id);
      if (isSelected) {
        return {
          ...prev,
          personas: prev.personas.filter(p => p.id !== persona.id)
        };
      } else if (prev.personas.length < 20) {
        return {
          ...prev,
          personas: [...prev.personas, persona]
        };
      }
      return prev;
    });
  };

  const startSession = async () => {
    if (sessionData.name && sessionData.purpose) {
      setSessionData(prev => ({
        ...prev,
        startTime: new Date()
      }));
      setCurrentStep('chat');
      setIsSessionActive(true);
      
      try {
        await runStreamingFocusGroup();
      } catch (error) {
        console.error('Focus group network error:', error);
        // Fallback to mock conversation
        generateMockConversation();
      }
    }
  };

  const runStreamingFocusGroup = async () => {
    const personaIds = sessionData.personas.map(p => p.id);
    let allMessages: Message[] = [];
    
    try {
      // Phase 1: Initial Reactions
      setStreamingStatus('Collecting initial reactions...');
      setCurrentRound(0);
      console.log('🚀 Starting initial reactions...');
      
      const initialResponse = await apiClient.focusGroupStart(
        sessionData.purpose,
        personaIds,
        sessionData.goals
      );
      
      if (initialResponse.error) {
        console.error('Initial reactions error:', initialResponse.error);
        setStreamingStatus('Error collecting initial reactions');
        return;
      }
      
      if (initialResponse.data?.messages) {
        const initialMessages: Message[] = initialResponse.data.messages.map(msg => ({
          id: msg.id,
          personaId: msg.persona_id,
          personaName: msg.persona_name,
          avatar: msg.avatar,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          sentiment: msg.sentiment as "positive" | "neutral" | "negative"
        }));
        
        allMessages = [...allMessages, ...initialMessages];
        
        // Update UI with initial messages
        setSessionData(prev => ({
          ...prev,
          messages: [...allMessages]
        }));
        
        console.log(`✅ Added ${initialMessages.length} initial reactions`);
      }
      
      // Phase 2: Discussion Rounds (3 rounds)
      for (let round = 1; round <= 3; round++) {
        setStreamingStatus(`Running discussion round ${round}...`);
        setCurrentRound(round);
        console.log(`🔄 Starting discussion round ${round}...`);
        
        // Add a small delay between rounds to make it feel more natural
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const roundResponse = await apiClient.focusGroupRound(
          sessionData.purpose,
          personaIds,
          round,
          allMessages.map(msg => ({
            id: msg.id,
            persona_id: msg.personaId,
            persona_name: msg.personaName,
            content: msg.content,
            sentiment: msg.sentiment,
            timestamp: msg.timestamp.toISOString(),
            round: 0 // Will be updated by backend
          }))
        );
        
        if (roundResponse.error) {
          console.error(`Round ${round} error:`, roundResponse.error);
          setStreamingStatus(`Error in round ${round}`);
          continue;
        }
        
        if (roundResponse.data?.messages) {
          const roundMessages: Message[] = roundResponse.data.messages.map(msg => ({
            id: msg.id,
            personaId: msg.persona_id,
            personaName: msg.persona_name,
            avatar: msg.avatar,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            sentiment: msg.sentiment as "positive" | "neutral" | "negative"
          }));
          
          allMessages = [...allMessages, ...roundMessages];
          
          // Update UI with new messages
          setSessionData(prev => ({
            ...prev,
            messages: [...allMessages]
          }));
          
          console.log(`✅ Added ${roundMessages.length} messages from round ${round}`);
        }
      }
      
      // Calculate final metrics
      setStreamingStatus('Calculating final insights...');
      const avgSentiment = allMessages.reduce((sum, msg) => {
        const score = msg.sentiment === 'positive' ? 1 : msg.sentiment === 'negative' ? -1 : 0;
        return sum + score;
      }, 0) / allMessages.length;
      
      setSessionData(prev => ({
        ...prev,
        overallNPS: Math.max(0, Math.min(10, 5 + avgSentiment * 3)),
        overallCSAT: Math.max(1, Math.min(5, 3 + avgSentiment)),
        avgSentiment: avgSentiment
      }));
      
      setStreamingStatus('Focus group completed!');
      setTimeout(() => setStreamingStatus(''), 3000);
      console.log('🎉 Focus group simulation completed!');
      
    } catch (error) {
      console.error('Streaming focus group error:', error);
      setStreamingStatus('Error occurred - using mock data');
      // Fallback to mock conversation
      generateMockConversation();
    }
  };

  const endSession = async () => {
    setIsSessionActive(false);
    setSessionData(prev => ({
      ...prev,
      endTime: new Date()
    }));
    setCurrentStep('analytics');

    // Save session data to backend
    try {
      const sessionDataToSave = {
        session_type: "focus-group" as const,
        session_name: sessionData.name,
        purpose: sessionData.purpose,
        goals: sessionData.goals,
        selected_personas: sessionData.personas.map(p => p.id),
        messages: sessionData.messages.map(msg => ({
          id: msg.id,
          persona_id: msg.personaId,
          persona_name: msg.personaName,
          avatar: msg.avatar,
          content: msg.content,
          timestamp: msg.timestamp.toISOString(),
          sentiment: msg.sentiment
        })),
        duration: sessionDuration,
        insights: [
          "Key insights from the focus group discussion",
          "Main themes and patterns identified",
          "Consensus and disagreements among participants",
          "Actionable recommendations from the group"
        ],
        key_takeaways: [
          "Primary conclusions from the session",
          "Most important feedback points",
          "Areas requiring further investigation",
          "Next steps based on group input"
        ],
        start_time: sessionData.startTime?.toISOString(),
        end_time: new Date().toISOString()
      };

      const response = await apiClient.saveSession(sessionDataToSave);
      if (response.error) {
        console.error('Failed to save session:', response.error);
      } else {
        console.log('Session saved successfully:', response.data);
      }
    } catch (error) {
      console.error('Error saving session:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  if (currentStep === 'config') {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Button variant="ghost" onClick={() => window.history.back()} className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Configure New Focus Group</h1>
            
            {/* Progress Steps */}
            <div className="flex items-center mt-6 space-x-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </div>
                <span className="ml-2 text-blue-600 font-medium">Purpose</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                  2
                </div>
                <span className="ml-2 text-gray-600">Participants</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                  3
                </div>
                <span className="ml-2 text-gray-600">Logistics</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                  4
                </div>
                <span className="ml-2 text-gray-600">Review</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-8">
            {/* Main Configuration */}
            <div className="col-span-2 space-y-6">
              {/* Purpose Section */}
              <Card>
                <CardHeader>
                  <CardTitle>Purpose</CardTitle>
                  <p className="text-gray-600">Describe the primary goal of the focus group.</p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="sessionName">Session Name</Label>
                    <Input
                      id="sessionName"
                      value={sessionData.name}
                      onChange={(e) => setSessionData(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Product Feedback Session"
                    />
                  </div>
                  <div>
                    <Label htmlFor="purpose">Purpose</Label>
                    <Textarea
                      id="purpose"
                      value={sessionData.purpose}
                      onChange={(e) => setSessionData(prev => ({ ...prev, purpose: e.target.value }))}
                      placeholder="Describe what you want to achieve with this focus group..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label>Research Goals</Label>
                    <div className="flex gap-2 mb-2">
                      <Input
                        value={newGoal}
                        onChange={(e) => setNewGoal(e.target.value)}
                        placeholder="Add a research goal..."
                        onKeyPress={(e) => e.key === 'Enter' && addGoal()}
                      />
                      <Button onClick={addGoal}>Add</Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {sessionData.goals.map((goal, index) => (
                        <Badge key={index} variant="secondary" className="cursor-pointer" onClick={() => removeGoal(index)}>
                          {goal} ×
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Persona Selection */}
              <Card>
                <CardHeader>
                  <CardTitle>Select Personas</CardTitle>
                  <p className="text-gray-600">Choose personas for your focus group.</p>
                </CardHeader>
                <CardContent>
                  {isLoadingPersonas ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        <p className="text-sm text-gray-600">Loading personas...</p>
                      </div>
                    </div>
                  ) : availablePersonas.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-600 mb-2">No personas available</p>
                      <p className="text-sm text-gray-500">Add personas to the personas directory</p>
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        {availablePersonas.map((persona) => (
                          <div
                            key={persona.id}
                            onClick={() => togglePersonaSelection(persona)}
                            className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                              sessionData.personas.some(p => p.id === persona.id)
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-2xl">{persona.avatar}</span>
                              <div>
                                <h3 className="font-medium">{persona.name}</h3>
                                <p className="text-sm text-gray-600">{persona.role}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <p className="text-sm text-gray-600 mt-4">
                        Selected: {sessionData.personas.length}
                      </p>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Live Summary */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Live Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Purpose</h4>
                    <p className="text-sm text-gray-600">
                      {sessionData.purpose || 'Not specified'}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Research Goals</h4>
                    <div className="space-y-1">
                      {sessionData.goals.length > 0 ? (
                        sessionData.goals.map((goal, index) => (
                          <p key={index} className="text-sm text-gray-600">• {goal}</p>
                        ))
                      ) : (
                        <p className="text-sm text-gray-400">No goals added</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Personas</h4>
                    <div className="space-y-2">
                      {sessionData.personas.map((persona) => (
                        <div key={persona.id} className="flex items-center gap-2">
                          <span className="text-lg">{persona.avatar}</span>
                          <span className="text-sm">{persona.name}</span>
                        </div>
                      ))}
                      {sessionData.personas.length === 0 && (
                        <p className="text-sm text-gray-400">No personas selected</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Logistics</h4>
                    <p className="text-sm text-gray-600">
                      {sessionData.personas.length >= 2 ? 'Ready to start' : 'Incomplete'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="space-y-3">
                <Button 
                  onClick={startSession}
                  // disabled={!sessionData.name || !sessionData.purpose || sessionData.personas.length < 2}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Generate Focus Group Plan
                </Button>
                <Button variant="outline" className="w-full">
                  Save Draft
                </Button>
                <Button variant="outline" className="w-full">
                  Preview
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'chat') {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">{sessionData.name}</h1>
              <p className="text-gray-600">{sessionData.purpose}</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                {formatDuration(sessionDuration)}
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Users className="h-4 w-4" />
                {sessionData.personas.length} participants
              </div>
              <Button
                onClick={endSession}
                variant="destructive"
                size="sm"
              >
                <Square className="h-4 w-4 mr-2" />
                End Session
              </Button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(100vh-80px)]">
          {/* Participants Sidebar */}
          <div className="w-80 bg-white border-r p-4">
            <h3 className="font-medium mb-4">Participants</h3>
            <div className="space-y-3">
              {sessionData.personas.map((persona) => (
                <div key={persona.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <span className="text-2xl">{persona.avatar}</span>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{persona.name}</h4>
                    <p className="text-xs text-gray-600">{persona.role}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className={`w-2 h-2 rounded-full ${
                      persona.sentiment === 'positive' ? 'bg-green-500' :
                      persona.sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Session Stats */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-3">Live Stats</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Messages:</span>
                  <span>{sessionData.messages.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Sentiment:</span>
                  <span>{getSentimentEmoji('positive')}</span>
                </div>
                <div className="flex justify-between">
                  <span>Engagement:</span>
                  <span>High</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {sessionData.messages.map((message) => (
                <div key={message.id} className="flex gap-3">
                  <span className="text-2xl">{message.avatar}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{message.personaName}</span>
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getSentimentColor(message.sentiment)}`}
                      >
                        {message.sentiment}
                      </Badge>
                    </div>
                    <div className="bg-white p-3 rounded-lg border">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            {/* Status Bar */}
            <div className="border-t bg-white p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {streamingStatus ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-blue-600 font-medium">{streamingStatus}</span>
                      {currentRound > 0 && (
                        <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                          Round {currentRound}/3
                        </span>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-4">
                      <span>Session in progress...</span>
                      <div className="flex items-center gap-1">
                        <Activity className="h-4 w-4" />
                        <span>AI personas are discussing</span>
                      </div>
                    </div>
                  )}
                </div>
                <Button onClick={endSession} variant="destructive">
                  End & Analyze
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Analytics Dashboard
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" onClick={() => setCurrentStep('config')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Configuration
            </Button>
            <Button 
              onClick={() => window.location.href = '/dashboard'}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Back to Dashboard
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Session Analytics</h1>
              <p className="text-gray-600">{sessionData.name}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export PDF
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export Excel
              </Button>
            </div>
          </div>
        </div>

        {/* Session Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Session Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-5 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{sessionData.name}</div>
                <div className="text-sm text-gray-600">Session Name</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {sessionData.startTime?.toLocaleDateString()}
                </div>
                <div className="text-sm text-gray-600">Date</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{sessionData.personas.length}</div>
                <div className="text-sm text-gray-600">Participants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{formatDuration(sessionDuration)}</div>
                <div className="text-sm text-gray-600">Duration</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{sessionData.overallNPS}</div>
                <div className="text-sm text-gray-600">Avg NPS Score</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Insights */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">NPS Score</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{sessionData.overallNPS}</div>
              <p className="text-xs text-muted-foreground">
                +12% from last session
              </p>
              <Progress value={sessionData.overallNPS * 10} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">CSAT Score</CardTitle>
              <ThumbsUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{sessionData.overallCSAT}</div>
              <p className="text-xs text-muted-foreground">
                +0.3 from last session
              </p>
              <Progress value={sessionData.overallCSAT * 20} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sentiment Analysis</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">Positive</div>
              <p className="text-xs text-muted-foreground">
                60% positive, 30% neutral, 10% negative
              </p>
              <div className="flex gap-1 mt-2">
                <div className="h-2 bg-green-500 rounded flex-1"></div>
                <div className="h-2 bg-yellow-500 rounded w-8"></div>
                <div className="h-2 bg-red-500 rounded w-4"></div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feedback Breakdown */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Feedback Breakdown by Participant</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {sessionData.personas.map((persona) => (
                <div key={persona.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{persona.avatar}</span>
                      <div>
                        <h3 className="font-medium">{persona.name}</h3>
                        <p className="text-sm text-gray-600">{persona.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge className={getSentimentColor(persona.sentiment)}>
                        {persona.sentiment} {getSentimentEmoji(persona.sentiment)}
                      </Badge>
                      <div className="text-right">
                        <div className="text-sm font-medium">NPS: {persona.npsScore}</div>
                        <div className="text-sm text-gray-600">CSAT: {persona.csatScore}</div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Key Points</h4>
                      <ul className="space-y-1">
                        {persona.keyPoints.map((point, index) => (
                          <li key={index} className="text-sm text-gray-600">• {point}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Questions Raised</h4>
                      <ul className="space-y-1">
                        {persona.questions.map((question, index) => (
                          <li key={index} className="text-sm text-gray-600">• {question}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actionable Insights */}
        <div className="grid grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Discussion Heatmap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Pricing Discussion</span>
                  <div className="flex items-center gap-2">
                    <Progress value={85} className="w-24" />
                    <span className="text-sm text-gray-600">85%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Feature Requests</span>
                  <div className="flex items-center gap-2">
                    <Progress value={70} className="w-24" />
                    <span className="text-sm text-gray-600">70%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">User Experience</span>
                  <div className="flex items-center gap-2">
                    <Progress value={65} className="w-24" />
                    <span className="text-sm text-gray-600">65%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Technical Concerns</span>
                  <div className="flex items-center gap-2">
                    <Progress value={45} className="w-24" />
                    <span className="text-sm text-gray-600">45%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recommendations for Action</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-1">High Priority</h4>
                  <p className="text-sm text-green-700">Review pricing strategy based on competitive analysis feedback</p>
                </div>
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-medium text-yellow-800 mb-1">Medium Priority</h4>
                  <p className="text-sm text-yellow-700">Improve mobile optimization and user interface design</p>
                </div>
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-1">Low Priority</h4>
                  <p className="text-sm text-blue-700">Enhance reporting capabilities and data accuracy features</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default FocusGroup; 