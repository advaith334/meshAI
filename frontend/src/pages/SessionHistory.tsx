import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  ArrowLeft,
  Search,
  Users,
  User,
  Clock,
  MessageSquare,
  Calendar,
  Download,
  Eye,
  Filter,
} from "lucide-react";
import { apiClient, SavedSession } from "@/lib/api";

const SessionHistory = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<SavedSession[]>([]);
  const [filteredSessions, setFilteredSessions] = useState<SavedSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    filterSessions();
  }, [sessions, searchQuery, typeFilter]);

  const loadSessions = async () => {
    try {
      const response = await apiClient.getSessions();
      if (response.error) {
        console.error('Failed to load sessions:', response.error);
        setSessions([]);
      } else if (response.data) {
        setSessions(response.data);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
      setSessions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterSessions = () => {
    let filtered = sessions;

    // Filter by type
    if (typeFilter !== "all") {
      filtered = filtered.filter(session => 
        session.metadata.session_type === typeFilter
      );
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(session =>
        session.metadata.session_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.session_data.purpose.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredSessions(filtered);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSessionIcon = (sessionType: string) => {
    return sessionType === "interview" ? User : Users;
  };

  const getSessionColor = (sessionType: string) => {
    return sessionType === "interview" ? "bg-blue-500" : "bg-green-500";
  };

  const exportSession = (session: SavedSession) => {
    const dataStr = JSON.stringify(session, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${session.metadata.session_type}_${session.metadata.session_name}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading session history...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate("/dashboard")} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Session History</h1>
          <p className="text-gray-600">View and manage your previous interview and focus group sessions</p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search sessions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={typeFilter === "all" ? "default" : "outline"}
              onClick={() => setTypeFilter("all")}
              className="flex items-center"
            >
              <Filter className="h-4 w-4 mr-2" />
              All
            </Button>
            <Button
              variant={typeFilter === "interview" ? "default" : "outline"}
              onClick={() => setTypeFilter("interview")}
              className="flex items-center"
            >
              <User className="h-4 w-4 mr-2" />
              Interviews
            </Button>
            <Button
              variant={typeFilter === "focus-group" ? "default" : "outline"}
              onClick={() => setTypeFilter("focus-group")}
              className="flex items-center"
            >
              <Users className="h-4 w-4 mr-2" />
              Focus Groups
            </Button>
          </div>
        </div>

        {/* Sessions Grid */}
        {filteredSessions.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No sessions found</h3>
              <p className="text-gray-600 mb-4">
                {sessions.length === 0 
                  ? "You haven't conducted any sessions yet. Start your first interview or focus group!"
                  : "No sessions match your current filters."
                }
              </p>
              {sessions.length === 0 && (
                <Button onClick={() => navigate("/session-selection")}>
                  Start New Session
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSessions.map((session) => {
              const IconComponent = getSessionIcon(session.metadata.session_type);
              return (
                <Card key={session.filename} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 ${getSessionColor(session.metadata.session_type)} rounded-full flex items-center justify-center`}>
                          <IconComponent className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{session.metadata.session_name}</CardTitle>
                          <Badge variant="outline" className="mt-1">
                            {session.metadata.session_type === "interview" ? "Interview" : "Focus Group"}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-1">Purpose</h4>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {session.session_data.purpose}
                      </p>
                    </div>
                    
                    {session.session_data.enhanced_personas && session.session_data.enhanced_personas.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Participants</h4>
                        <div className="flex flex-wrap gap-2">
                          {session.session_data.enhanced_personas.map((persona, index) => (
                            <div key={index} className="flex items-center space-x-1 bg-gray-100 rounded-full px-2 py-1">
                              <span className="text-sm">{persona.avatar}</span>
                              <span className="text-xs text-gray-700">{persona.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{formatDuration(session.metadata.duration_seconds)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{session.session_data.messages.length} messages</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="h-4 w-4 mr-1" />
                      {formatDate(session.metadata.timestamp)}
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => exportSession(session)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Export
                      </Button>
                      {/* <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => {
                          // TODO: Implement session detail view
                          console.log('View session details:', session);
                        }}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button> */}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Summary Stats */}
        {sessions.length > 0 && (
          <div className="mt-8 grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600">Total Sessions</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">{sessions.length}</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-blue-600" />
                  <span className="text-sm font-medium text-gray-600">Interviews</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {sessions.filter(s => s.metadata.session_type === "interview").length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-gray-600">Focus Groups</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {sessions.filter(s => s.metadata.session_type === "focus-group").length}
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-purple-600" />
                  <span className="text-sm font-medium text-gray-600">Total Time</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatDuration(sessions.reduce((total, s) => total + s.metadata.duration_seconds, 0))}
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionHistory; 