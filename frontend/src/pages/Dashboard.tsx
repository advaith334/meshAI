import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Bell,
  HelpCircle,
  User,
  Search,
  Filter,
  Edit,
  Users,
  Settings,
  Waypoints,
} from "lucide-react";
import { PersonaSidebar } from "@/components/PersonaSidebar";
import { CustomizePersona } from "@/components/CustomizePersona";
import { apiClient, DashboardSession } from "@/lib/api";

interface Persona {
  name: string;
  avatar: string;
  role: string;
  description: string;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isCustomizePersonaOpen, setIsCustomizePersonaOpen] = useState(false);
  const [customPersonas, setCustomPersonas] = useState<Persona[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [sessions, setSessions] = useState<DashboardSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);

  // Load sessions from backend
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await apiClient.getDashboardSessions();
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
        setIsLoadingSessions(false);
      }
    };

    loadSessions();
  }, []);

  const activeSessionsData = [
    { name: "Concept Validation", trend: "↗️" },
    { name: "User Feedback", trend: "↗️" },
    { name: "Prototype Testing", trend: "↗️" },
    { name: "Usability Assessment", trend: "↗️" },
  ];

  const handlePersonaAdd = (newPersona: Persona) => {
    setCustomPersonas((prev) => [...prev, newPersona]);
  };

  const filteredSessions = sessions.filter((session) => {
    const matchesSearch = session.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "All" || session.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return "Unknown";
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSessionTypeLabel = (sessionType: string) => {
    switch (sessionType) {
      case "interview":
        return "Interview";
      case "focus-group":
        return "Focus Group";
      default:
        return "Unknown";
    }
  };

  const getSessionTypeColor = (sessionType: string) => {
    switch (sessionType) {
      case "interview":
        return "bg-blue-100 text-blue-800 hover:bg-blue-200";
      case "focus-group":
        return "bg-green-100 text-green-800 hover:bg-green-200";
      default:
        return "bg-gray-100 text-gray-800 hover:bg-gray-200";
    }
  };

  return (
    <>
      <div className="min-h-screen bg-background text-foreground">
        {/* Header */}
        <header className="bg-card text-card-foreground px-6 py-4 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Waypoints className="h-8 w-8 text-primary" />
              <h1 className="text-xl font-semibold">MeshAI</h1>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(true)}
                className="text-foreground hover:bg-muted"
              >
                <Settings className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-foreground hover:bg-muted">
                <Bell className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-foreground hover:bg-muted">
                <HelpCircle className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" className="text-foreground hover:bg-muted">
                <User className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </header>

        <div className="p-6 max-w-7xl mx-auto">
          {/* Top Action Bar */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <Button
              onClick={() => navigate("/session-selection")}
              className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-3 text-lg"
            >
              + New Session
            </Button>
            <Button 
              onClick={() => setIsCustomizePersonaOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 text-lg"
            >
              Create Personas
            </Button>
            <Button 
              onClick={() => navigate("/session-history")}
              variant="outline"
              className="px-6 py-3 text-lg"
            >
              Detailed Session History
            </Button>
            <Select>
              <SelectContent>
                <SelectItem value="csv">Import CSV</SelectItem>
                <SelectItem value="excel">Import Excel</SelectItem>
                <SelectItem value="json">Import JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Session Overview */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <CardTitle className="text-2xl">Session Overview</CardTitle>
                <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 w-full sm:w-64"
                    />
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-full sm:w-32">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="All">Status</SelectItem>
                      <SelectItem value="Completed">Completed</SelectItem>
                      <SelectItem value="In Progress">In Progress</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingSessions ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading sessions...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Session Name</th>
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Type</th>
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Personas</th>
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Duration</th>
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Start Date</th>
                        <th className="text-left py-3 px-2 font-medium text-gray-600">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSessions.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="text-center py-8 text-gray-500">
                            {sessions.length === 0 
                              ? "No sessions found. Start your first interview or focus group!"
                              : "No sessions match your current filters."
                            }
                          </td>
                        </tr>
                      ) : (
                        filteredSessions.map((session) => (
                          <tr key={session.id} className="border-b hover:bg-gray-50">
                            <td className="py-4 px-2 font-medium">{session.name}</td>
                            <td className="py-4 px-2">
                              <Badge className={getSessionTypeColor(session.session_type)}>
                                {getSessionTypeLabel(session.session_type)}
                              </Badge>
                            </td>
                            <td className="py-4 px-2">
                              <div className="flex -space-x-1">
                                {session.persona_avatars.map((avatar, index) => (
                                  <div
                                    key={index}
                                    className="w-8 h-8 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-sm"
                                  >
                                    {avatar}
                                  </div>
                                ))}
                                {session.persona_avatars.length === 0 && (
                                  <div className="w-8 h-8 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center text-xs text-gray-600">
                                    <Users className="h-3 w-3" />
                                  </div>
                                )}
                              </div>
                            </td>
                            <td className="py-4 px-2 text-gray-600">{formatDuration(session.duration)}</td>
                            <td className="py-4 px-2 text-gray-600">{formatDate(session.start_date)}</td>
                            <td className="py-4 px-2">
                              <Badge
                                variant="default"
                                className="bg-teal-100 text-teal-800 hover:bg-teal-200"
                              >
                                {session.status}
                              </Badge>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Persona Sidebar */}
      <PersonaSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        personas={customPersonas}
      />

      {/* Customize Persona Modal */}
      <CustomizePersona
        isOpen={isCustomizePersonaOpen}
        onClose={() => setIsCustomizePersonaOpen(false)}
        onSave={handlePersonaAdd}
      />
    </>
  );
};

export default Dashboard; 