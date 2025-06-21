import { useState } from "react";
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

interface Persona {
  id: string;
  name: string;
  description: string;
  avatar: string;
}

interface CustomPersona {
  id: string;
  name: string;
  avatar: string;
  persona: string;
  industry: string;
  role: string;
  ageGroup: string;
  gender: string;
  ethnicity: string;
  religion: string;
  education: string;
  income: string;
  location: string;
  riskTolerance: number;
  techAdoption: number;
  emotionalSensitivity: number;
  opennessToIdeas: number;
  motivations: string[];
  customAttributes: { [key: string]: string };
  behavioralTraits: string[];
  engagementScore: number;
  description: string;
}

interface Session {
  id: string;
  name: string;
  client: string;
  avatars: string[];
  startDate: string;
  status: "Completed" | "In Progress" | "In P.";
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isCustomizePersonaOpen, setIsCustomizePersonaOpen] = useState(false);
  const [customPersonas, setCustomPersonas] = useState<Persona[]>([]);
  const [detailedPersonas, setDetailedPersonas] = useState<CustomPersona[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  // Mock data for sessions
  const sessions: Session[] = [
    {
      id: "1",
      name: "Product Feedback",
      client: "Acme Corp",
      avatars: ["👤", "👩", "👨", "🧑"],
      startDate: "4/22/2021",
      status: "Completed",
    },
    {
      id: "2",
      name: "Customer Insights",
      client: "Beta Ltd",
      avatars: ["👩", "👨", "🧑", "👤"],
      startDate: "4/22/2021",
      status: "Completed",
    },
    {
      id: "3",
      name: "Market Research",
      client: "Gamma inc",
      avatars: ["👤", "👩", "👨", "🧑"],
      startDate: "3/26/2021",
      status: "In Progress",
    },
    {
      id: "4",
      name: "Brand Perception",
      client: "Delta Co",
      avatars: ["👩", "👨", "🧑", "👤"],
      startDate: "3/23/2021",
      status: "Completed",
    },
    {
      id: "5",
      name: "Feature Testing",
      client: "Epsilon LLC",
      avatars: ["👤", "👩", "👨", "🧑"],
      startDate: "3/17/2021",
      status: "In Progress",
    },
  ];

  const activeSessionsData = [
    { name: "Concept Validation", trend: "↗️" },
    { name: "User Feedback", trend: "↗️" },
    { name: "Prototype Testing", trend: "↗️" },
    { name: "Usability Assessment", trend: "↗️" },
  ];

  const handlePersonaAdd = (newPersona: Omit<Persona, "id">) => {
    const persona: Persona = {
      ...newPersona,
      id: `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
    setCustomPersonas((prev) => [...prev, persona]);
  };

  const handlePersonaDelete = (id: string) => {
    setCustomPersonas((prev) => prev.filter((p) => p.id !== id));
  };

  const handleDetailedPersonaSave = (persona: CustomPersona) => {
    setDetailedPersonas((prev) => {
      const existingIndex = prev.findIndex(p => p.id === persona.id);
      if (existingIndex >= 0) {
        // Update existing persona
        const updated = [...prev];
        updated[existingIndex] = persona;
        return updated;
      } else {
        // Add new persona
        return [...prev, persona];
      }
    });
  };

  const handleDetailedPersonaDelete = (personaId: string) => {
    setDetailedPersonas((prev) => prev.filter((p) => p.id !== personaId));
  };

  const filteredSessions = sessions.filter((session) => {
    const matchesSearch = session.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         session.client.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "All" || session.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

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
              onClick={() => navigate("/focus-group")}
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
                      <SelectItem value="In P.">In P.</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-2 font-medium text-gray-600">Session Name</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-600">Client</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-600">Avatars</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-600">Start Date</th>
                      <th className="text-left py-3 px-2 font-medium text-gray-600">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSessions.map((session) => (
                      <tr key={session.id} className="border-b hover:bg-gray-50">
                        <td className="py-4 px-2 font-medium">{session.name}</td>
                        <td className="py-4 px-2 text-gray-600">{session.client}</td>
                        <td className="py-4 px-2">
                          <div className="flex -space-x-1">
                            {session.avatars.map((avatar, index) => (
                              <div
                                key={index}
                                className="w-8 h-8 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-sm"
                              >
                                {avatar}
                              </div>
                            ))}
                            <div className="w-8 h-8 rounded-full bg-gray-300 border-2 border-white flex items-center justify-center text-xs text-gray-600">
                              <Users className="h-3 w-3" />
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-2 text-gray-600">{session.startDate}</td>
                        <td className="py-4 px-2">
                          <Badge
                            variant={
                              session.status === "Completed"
                                ? "default"
                                : session.status === "In Progress"
                                ? "secondary"
                                : "outline"
                            }
                            className={
                              session.status === "Completed"
                                ? "bg-teal-100 text-teal-800 hover:bg-teal-200"
                                : session.status === "In Progress"
                                ? "bg-blue-100 text-blue-800 hover:bg-blue-200"
                                : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                            }
                          >
                            {session.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Persona Sidebar */}
      <PersonaSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        personas={customPersonas}
        onAddPersona={handlePersonaAdd}
        onDeletePersona={handlePersonaDelete}
      />

      {/* Customize Persona Modal */}
      <CustomizePersona
        isOpen={isCustomizePersonaOpen}
        onClose={() => setIsCustomizePersonaOpen(false)}
        onSave={handleDetailedPersonaSave}
        onDelete={handleDetailedPersonaDelete}
        existingPersonas={detailedPersonas}
      />
    </>
  );
};

export default Dashboard; 