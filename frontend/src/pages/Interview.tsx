import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
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
  User,
  Clock,
  MessageSquare,
  Send,
  Mic,
  MicOff,
  Settings,
  Download,
  BarChart3,
  Activity,
  Star,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface Persona {
  id: string;
  name: string;
  avatar: string;
  description: string;
  role?: string;
  traits?: string[];
}

interface Message {
  id: string;
  sender: "user" | "persona";
  content: string;
  timestamp: Date;
  sentiment?: "positive" | "neutral" | "negative";
}

interface InterviewData {
  name: string;
  purpose: string;
  selectedPersona: Persona | null;
  startTime?: Date;
  endTime?: Date;
  messages: Message[];
  duration: number;
  insights: string[];
  keyTakeaways: string[];
}

const Interview = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<'config' | 'chat' | 'analytics'>('config');
  const [interviewData, setInterviewData] = useState<InterviewData>({
    name: 'One-on-One Interview',
    purpose: '',
    selectedPersona: null,
    messages: [],
    duration: 0,
    insights: [],
    keyTakeaways: [],
  });
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [availablePersonas, setAvailablePersonas] = useState<Persona[]>([]);
  const [isLoadingPersonas, setIsLoadingPersonas] = useState(true);
  const [isLoadingResponse, setIsLoadingResponse] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isInterviewActive && currentStep === 'chat') {
      interval = setInterval(() => {
        setInterviewData(prev => ({
          ...prev,
          duration: prev.duration + 1
        }));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isInterviewActive, currentStep]);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [interviewData.messages]);

  // Load personas from API
  useEffect(() => {
    const loadPersonas = async () => {
      try {
        const response = await apiClient.getDisplayPersonas();
        if (response.error) {
          console.error('Failed to load personas:', response.error);
          setAvailablePersonas([]);
        } else if (response.data) {
          setAvailablePersonas(response.data);
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

  const startInterview = async () => {
    if (interviewData.name && interviewData.purpose && interviewData.selectedPersona) {
      setInterviewData(prev => ({
        ...prev,
        startTime: new Date()
      }));
      setCurrentStep('chat');
      setIsInterviewActive(true);
      
      // Add initial greeting
      const initialMessage: Message = {
        id: Date.now().toString(),
        sender: 'persona',
        content: `Hello! I'm ${interviewData.selectedPersona?.name}. I'm here to help you with ${interviewData.purpose.toLowerCase()}. What would you like to know?`,
        timestamp: new Date(),
        sentiment: 'positive'
      };
      
      setInterviewData(prev => ({
        ...prev,
        messages: [initialMessage]
      }));
    }
  };

  const sendMessage = async () => {
    if (!newQuestion.trim() || !interviewData.selectedPersona) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: newQuestion,
      timestamp: new Date()
    };

    setInterviewData(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }));

    setNewQuestion('');
    setIsLoadingResponse(true);

    try {
      // Call the API to get persona response
      const response = await apiClient.simpleInteraction(
        newQuestion,
        [interviewData.selectedPersona.id]
      );

      if (response.error) {
        console.error('Failed to get response:', response.error);
        // Fallback response
        const fallbackMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'persona',
          content: `I understand you're asking about "${newQuestion}". Based on my perspective as ${interviewData.selectedPersona.name}, I'd like to share my thoughts on this.`,
          timestamp: new Date(),
          sentiment: 'neutral'
        };
        setInterviewData(prev => ({
          ...prev,
          messages: [...prev.messages, fallbackMessage]
        }));
      } else if (response.data?.reactions && response.data.reactions.length > 0) {
        const personaResponse = response.data.reactions[0];
        const personaMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'persona',
          content: personaResponse.reaction,
          timestamp: new Date(),
          sentiment: personaResponse.sentiment as "positive" | "neutral" | "negative"
        };
        setInterviewData(prev => ({
          ...prev,
          messages: [...prev.messages, personaMessage]
        }));
      }
    } catch (error) {
      console.error('Network error:', error);
      // Fallback response
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'persona',
        content: `Thank you for that question. As ${interviewData.selectedPersona.name}, I find this topic quite interesting and would be happy to discuss it further.`,
        timestamp: new Date(),
        sentiment: 'neutral'
      };
      setInterviewData(prev => ({
        ...prev,
        messages: [...prev.messages, fallbackMessage]
      }));
    } finally {
      setIsLoadingResponse(false);
    }
  };

  const endInterview = () => {
    setIsInterviewActive(false);
    setInterviewData(prev => ({
      ...prev,
      endTime: new Date()
    }));
    setCurrentStep('analytics');
    
    // Generate insights from the conversation
    const insights = [
      "Key insights from the conversation",
      "Main concerns and pain points identified",
      "Positive feedback and suggestions",
      "Areas for improvement discussed"
    ];
    
    const keyTakeaways = [
      "Primary takeaway from the interview",
      "Most important feedback received",
      "Action items for follow-up",
      "Recommendations based on responses"
    ];
    
    setInterviewData(prev => ({
      ...prev,
      insights,
      keyTakeaways
    }));
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getSentimentEmoji = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  if (currentStep === 'config') {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Button variant="ghost" onClick={() => navigate('/session-selection')} className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Session Selection
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Configure One-on-One Interview</h1>
            
            {/* Progress Steps */}
            <div className="flex items-center mt-6 space-x-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </div>
                <span className="ml-2 text-blue-600 font-medium">Setup</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                  2
                </div>
                <span className="ml-2 text-gray-600">Interview</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-300"></div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">
                  3
                </div>
                <span className="ml-2 text-gray-600">Analytics</span>
              </div>
            </div>
          </div>

          {/* Configuration Form */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Interview Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="name">Interview Name</Label>
                <Input
                  id="name"
                  value={interviewData.name}
                  onChange={(e) => setInterviewData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter interview name"
                />
              </div>
              
              <div>
                <Label htmlFor="purpose">Interview Purpose</Label>
                <Textarea
                  id="purpose"
                  value={interviewData.purpose}
                  onChange={(e) => setInterviewData(prev => ({ ...prev, purpose: e.target.value }))}
                  placeholder="Describe the purpose of this interview..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Persona Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Select Persona</CardTitle>
              <p className="text-sm text-gray-600">Choose one persona to interview</p>
            </CardHeader>
            <CardContent>
              {isLoadingPersonas ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Loading personas...</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {availablePersonas.map((persona) => (
                    <Card
                      key={persona.id}
                      className={`cursor-pointer transition-all duration-200 ${
                        interviewData.selectedPersona?.id === persona.id
                          ? 'ring-2 ring-blue-500 bg-blue-50'
                          : 'hover:shadow-md'
                      }`}
                      onClick={() => setInterviewData(prev => ({ ...prev, selectedPersona: persona }))}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">{persona.avatar}</div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{persona.name}</h3>
                            <p className="text-sm text-gray-600">{persona.role}</p>
                            <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                              {persona.description}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Start Button */}
          <div className="mt-8 flex justify-center">
            <Button
              onClick={startInterview}
              disabled={!interviewData.name || !interviewData.purpose || !interviewData.selectedPersona}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg"
            >
              <Play className="h-5 w-5 mr-2" />
              Start Interview
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'chat') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={() => window.history.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{interviewData.name}</h1>
                <p className="text-sm text-gray-600">Interview with {interviewData.selectedPersona?.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                <span>{formatDuration(interviewData.duration)}</span>
              </div>
              <Button
                variant="outline"
                onClick={endInterview}
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                <Square className="h-4 w-4 mr-2" />
                End Interview
              </Button>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {interviewData.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-lg p-4 ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border'
                    }`}
                  >
                    {message.sender === 'persona' && (
                      <div className="flex items-center mb-2">
                        <span className="text-lg mr-2">{interviewData.selectedPersona?.avatar}</span>
                        <span className="font-medium text-gray-900">{interviewData.selectedPersona?.name}</span>
                        {message.sentiment && (
                          <Badge className={`ml-2 ${getSentimentColor(message.sentiment)}`}>
                            {getSentimentEmoji(message.sentiment)}
                          </Badge>
                        )}
                      </div>
                    )}
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {isLoadingResponse && (
                <div className="flex justify-start">
                  <div className="bg-white border rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      <span className="text-sm text-gray-600">Persona is typing...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t bg-white p-4">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Input
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your question..."
                    disabled={isLoadingResponse}
                  />
                </div>
                <Button
                  onClick={sendMessage}
                  disabled={!newQuestion.trim() || isLoadingResponse}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsRecording(!isRecording)}
                  className={isRecording ? 'bg-red-100 text-red-600' : ''}
                >
                  {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'analytics') {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Interview Analytics</h1>
            <p className="text-gray-600">Analysis of your interview with {interviewData.selectedPersona?.name}</p>
          </div>

          {/* Summary Cards */}
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600">Duration</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {formatDuration(interviewData.duration)}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-600">Messages</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {interviewData.messages.length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-purple-600" />
                  <span className="text-sm font-medium text-gray-600">Persona</span>
                </div>
                <p className="text-lg font-semibold text-gray-900 mt-2">
                  {interviewData.selectedPersona?.name}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Activity className="h-5 w-5 text-orange-600" />
                  <span className="text-sm font-medium text-gray-600">Status</span>
                </div>
                <Badge className="mt-2 bg-green-100 text-green-800">Completed</Badge>
              </CardContent>
            </Card>
          </div>

          {/* Insights and Takeaways */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Key Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {interviewData.insights.map((insight, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Star className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{insight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ThumbsUp className="h-5 w-5 mr-2" />
                  Key Takeaways
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {interviewData.keyTakeaways.map((takeaway, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <ThumbsUp className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{takeaway}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex justify-center space-x-4">
            <Button variant="outline" className="flex items-center">
              <Download className="h-4 w-4 mr-2" />
              Export Transcript
            </Button>
            <Button onClick={() => navigate('/dashboard')} className="bg-blue-600 hover:bg-blue-700">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default Interview; 