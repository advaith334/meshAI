import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  ArrowRight,
  Users,
  MessageSquare,
  TrendingUp,
  Settings,
} from "lucide-react";
import { PersonaSidebar } from "@/components/PersonaSidebar";
import { apiClient, PersonaReaction as ApiPersonaReaction } from "@/lib/api";

interface Persona {
  id: string;
  name: string;
  description: string;
  avatar: string;
}

const defaultPersonas: Persona[] = [
  {
    id: "tech-enthusiast",
    name: "Tech Enthusiast",
    description: "Always excited about the latest innovations and gadgets",
    avatar: "🤖"
  },
  {
    id: "price-sensitive",
    name: "Price-Sensitive Shopper",
    description: "Focused on value and getting the best deals",
    avatar: "💰"
  },
  {
    id: "eco-conscious",
    name: "Eco-Conscious Consumer",
    description: "Prioritizes sustainability and environmental impact",
    avatar: "🌱"
  },
  {
    id: "early-adopter",
    name: "Early Adopter",
    description: "First to try new products and trends",
    avatar: "🚀"
  },
  {
    id: "skeptical-buyer",
    name: "Skeptical Buyer",
    description: "Cautious and requires convincing before making decisions",
    avatar: "🤔"
  }
];

interface PersonaReaction {
  name: string;
  sentiment: string;
  reaction: string;
  avatar: string;
}

const Index = () => {
  const [currentView, setCurrentView] = useState<'landing' | 'main' | 'results'>('landing');
  const [question, setQuestion] = useState('');
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([]);
  const [initialReactions, setInitialReactions] = useState<PersonaReaction[]>([]);
  const [updatedReactions, setUpdatedReactions] = useState<PersonaReaction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [customPersonas, setCustomPersonas] = useState<Persona[]>([]);

  // Combine default and custom personas
  const allPersonas = [...defaultPersonas, ...customPersonas];

  const handlePersonaSelection = (personaId: string) => {
    setSelectedPersonas(prev => 
      prev.includes(personaId)
        ? prev.filter(id => id !== personaId)
        : [...prev, personaId]
    );
  };

  const handlePersonaAdd = (newPersona: Omit<Persona, 'id'>) => {
    const persona: Persona = {
      ...newPersona,
      id: `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
    setCustomPersonas(prev => [...prev, persona]);
  };

  const handlePersonaDelete = (id: string) => {
    setCustomPersonas(prev => prev.filter(p => p.id !== id));
    setSelectedPersonas(prev => prev.filter(pid => pid !== id));
  };

  const generateMockReactions = (selectedIds: string[]): PersonaReaction[] => {
    const reactions = {
      "tech-enthusiast": {
        sentiment: "positive",
        reaction: "This is fascinating! I love exploring new technological possibilities."
      },
      "price-sensitive": {
        sentiment: "neutral", 
        reaction: "Interesting, but I'd need to see the cost-benefit analysis first."
      },
      "eco-conscious": {
        sentiment: "positive",
        reaction: "I appreciate the focus on sustainable solutions."
      },
      "early-adopter": {
        sentiment: "positive",
        reaction: "Count me in! I'm always ready to try something new."
      },
      "skeptical-buyer": {
        sentiment: "negative",
        reaction: "I have some concerns about this approach. Need more proof."
      }
    };

    return selectedIds.map(id => {
      const persona = allPersonas.find(p => p.id === id)!;
      const defaultReaction = reactions[id as keyof typeof reactions];
      
      return {
        name: persona.name,
        sentiment: defaultReaction?.sentiment || "neutral",
        reaction: defaultReaction?.reaction || "This is an interesting perspective to consider.",
        avatar: persona.avatar
      };
    });
  };

  const generateUpdatedReactions = (initial: PersonaReaction[]): PersonaReaction[] => {
    return initial.map(reaction => ({
      ...reaction,
      sentiment: reaction.sentiment === "negative" ? "neutral" : "positive",
      reaction: reaction.sentiment === "negative" 
        ? "After hearing other perspectives, I'm more open to this idea."
        : reaction.sentiment === "neutral"
        ? "The discussion has convinced me - this could really work!"
        : reaction.reaction + " The group discussion reinforced my enthusiasm!"
    }));
  };

  const handleAskQuestion = async () => {
    if (!question.trim() || selectedPersonas.length === 0) return;
    
    setIsLoading(true);
    
    try {
      const response = await apiClient.simpleInteraction(question, selectedPersonas);
      
      if (response.error) {
        console.error('API Error:', response.error);
        // Fallback to mock data if API fails
        const reactions = generateMockReactions(selectedPersonas);
        setInitialReactions(reactions);
      } else if (response.data) {
        // Convert API response to frontend format
        const reactions: PersonaReaction[] = response.data.reactions.map((apiReaction: ApiPersonaReaction) => ({
          name: apiReaction.name,
          sentiment: apiReaction.sentiment,
          reaction: apiReaction.reaction,
          avatar: apiReaction.avatar
        }));
        setInitialReactions(reactions);
      }
      
      setCurrentView('main');
    } catch (error) {
      console.error('Network error:', error);
      // Fallback to mock data on network error
      const reactions = generateMockReactions(selectedPersonas);
      setInitialReactions(reactions);
      setCurrentView('main');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunInteraction = async () => {
    setIsLoading(true);
    
    try {
      // Convert frontend reactions to API format
      const apiReactions: ApiPersonaReaction[] = selectedPersonas.map((personaId, index) => {
        const reaction = initialReactions[index];
        return {
          persona_id: personaId,
          name: reaction.name,
          avatar: reaction.avatar,
          reaction: reaction.reaction,
          sentiment: reaction.sentiment,
          sentiment_score: reaction.sentiment === 'positive' ? 2 : reaction.sentiment === 'negative' ? -2 : 0
        };
      });
      
      const response = await apiClient.groupDiscussion(question, selectedPersonas, apiReactions);
      
      if (response.error) {
        console.error('Group discussion API Error:', response.error);
        // Fallback to mock data if API fails
        const updated = generateUpdatedReactions(initialReactions);
        setUpdatedReactions(updated);
      } else if (response.data) {
        // Process group discussion results to show updated reactions
        const lastMessages = response.data.discussion_messages.slice(-selectedPersonas.length);
        const updated: PersonaReaction[] = lastMessages.map(msg => ({
          name: msg.persona_name,
          sentiment: msg.sentiment,
          reaction: msg.content,
          avatar: msg.avatar
        }));
        setUpdatedReactions(updated);
      }
      
      setCurrentView('results');
    } catch (error) {
      console.error('Group discussion network error:', error);
      // Fallback to mock data on network error
      const updated = generateUpdatedReactions(initialReactions);
      setUpdatedReactions(updated);
      setCurrentView('results');
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'bg-green-100 text-green-800';
      case 'negative': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (currentView === 'landing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        {/* Hero Section */}
        <div className="container mx-auto px-4 py-16">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 animate-fade-in">
              MeshAI
            </h1>
            <p className="text-2xl text-gray-600 mb-8 animate-fade-in">
              Explore how different personas react to your questions
            </p>
            <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto animate-fade-in">
              MeshAI allows you to interact with a community of AI personas and see how they react to your questions. 
              Get insights, compare sentiments, and simulate interactions!
            </p>
            
            <Button 
              onClick={() => setCurrentView('main')} 
              size="lg" 
              className="text-lg px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 animate-fade-in"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Features Section */}
          <div className="grid md:grid-cols-3 gap-8 mt-20 max-w-5xl mx-auto">
            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 animate-fade-in">
              <CardHeader>
                <Users className="h-12 w-12 mx-auto text-blue-600 mb-4" />
                <CardTitle>Multiple Personas</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Choose from diverse AI personas representing different customer types and perspectives
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 animate-fade-in">
              <CardHeader>
                <MessageSquare className="h-12 w-12 mx-auto text-purple-600 mb-4" />
                <CardTitle>Interactive Discussions</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Watch personas interact with each other and see how their opinions evolve
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 animate-fade-in">
              <CardHeader>
                <TrendingUp className="h-12 w-12 mx-auto text-green-600 mb-4" />
                <CardTitle>Sentiment Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Track how sentiments change through interactions and get valuable insights
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (currentView === 'main') {
    return (
      <>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
          <div className="container mx-auto max-w-4xl">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-4 mb-4">
                <h1 className="text-4xl font-bold text-gray-800">Ask Your Question</h1>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setIsSidebarOpen(true)}
                  className="hover:bg-blue-50"
                >
                  <Settings className="h-5 w-5" />
                </Button>
              </div>
              <p className="text-gray-600">Select personas and see how they react</p>
            </div>

            <Card className="mb-8 shadow-lg">
              <CardHeader>
                <CardTitle>Your Question</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="What would you like to ask? (e.g., 'What are the latest tech trends?')"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="text-lg p-4"
                />
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Select Personas</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    {allPersonas.map((persona) => (
                      <div key={persona.id} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                        <Checkbox
                          checked={selectedPersonas.includes(persona.id)}
                          onCheckedChange={() => handlePersonaSelection(persona.id)}
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{persona.avatar}</span>
                            <span className="font-medium">{persona.name}</span>
                            {persona.id.startsWith('custom-') && (
                              <Badge variant="secondary" className="text-xs">Custom</Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-500">{persona.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <Button 
                  onClick={handleAskQuestion}
                  disabled={!question.trim() || selectedPersonas.length === 0 || isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  size="lg"
                >
                  {isLoading ? "Processing..." : "Ask Question"}
                </Button>
              </CardContent>
            </Card>

            {initialReactions.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-center">Initial Reactions</h2>
                <div className="grid gap-4 mb-8">
                  {initialReactions.map((reaction, index) => (
                    <Card key={index} className="shadow-lg hover:shadow-xl transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start gap-4">
                          <span className="text-3xl">{reaction.avatar}</span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="font-semibold text-lg">{reaction.name}</h3>
                              <Badge className={getSentimentColor(reaction.sentiment)}>
                                {reaction.sentiment}
                              </Badge>
                            </div>
                            <p className="text-gray-600">{reaction.reaction}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <div className="text-center">
                  <Button 
                    onClick={handleRunInteraction}
                    disabled={isLoading}
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                    size="lg"
                  >
                    {isLoading ? "Running Interaction..." : "Run Interaction"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        <PersonaSidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          personas={customPersonas}
          onAddPersona={handlePersonaAdd}
          onDeletePersona={handlePersonaDelete}
        />
      </>
    );
  }

  if (currentView === 'results') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Updated Reactions</h1>
            <p className="text-gray-600">See how sentiments changed after persona interaction</p>
          </div>

          <div className="grid gap-4 mb-8">
            {updatedReactions.map((reaction, index) => (
              <Card
                key={index}
                className={getSentimentColor(reaction.sentiment)}
              >
                <CardHeader className="flex flex-row items-center gap-4">
                  {reaction.avatar.startsWith("http") ? (
                    <img
                      src={reaction.avatar}
                      alt={reaction.name}
                      className="h-10 w-10 rounded-full"
                    />
                  ) : (
                    <div className="h-10 w-10 rounded-full bg-white flex items-center justify-center text-xl">
                      {reaction.avatar}
                    </div>
                  )}
                  <p className="font-bold">{reaction.name}</p>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={getSentimentColor(reaction.sentiment)}>
                      {reaction.sentiment}
                    </Badge>
                    {initialReactions[index]?.sentiment !== reaction.sentiment && (
                      <Badge variant="outline" className="text-blue-600">
                        Changed from {initialReactions[index]?.sentiment}
                      </Badge>
                    )}
                  </div>
                  <p className="text-gray-600">{reaction.reaction}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="shadow-lg bg-gradient-to-r from-blue-100 to-purple-100">
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-3">Summary</h3>
              <p className="text-gray-700">
                After the interaction, {updatedReactions.filter(r => r.sentiment === 'positive').length} out of {updatedReactions.length} personas 
                have a positive sentiment. The discussion helped personas understand different perspectives and generally improved overall sentiment.
              </p>
            </CardContent>
          </Card>

          <div className="text-center mt-8">
            <Button 
              onClick={() => {
                setCurrentView('main');
                setQuestion('');
                setSelectedPersonas([]);
                setInitialReactions([]);
                setUpdatedReactions([]);
              }}
              variant="outline"
              size="lg"
              className="mr-4"
            >
              Ask Another Question
            </Button>
            <Button 
              onClick={() => setCurrentView('landing')}
              variant="outline"
              size="lg"
            >
              Back to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default Index;
