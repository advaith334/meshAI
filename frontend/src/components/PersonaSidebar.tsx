import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { X, Plus, User, Instagram } from "lucide-react";

interface Persona {
  id: string;
  name: string;
  description: string;
  avatar: string;
}

interface PersonaSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  personas: Persona[];
  onAddPersona: (persona: Omit<Persona, 'id'>) => void;
  onDeletePersona: (id: string) => void;
  onScrapePersona: (username: string) => Promise<boolean>;
}

export const PersonaSidebar = ({ 
  isOpen, 
  onClose, 
  personas, 
  onAddPersona,
  onDeletePersona,
  onScrapePersona,
}: PersonaSidebarProps) => {
  const [newPersona, setNewPersona] = useState({
    name: '',
    description: '',
    avatar: '👤'
  });
  const [instagramUsername, setInstagramUsername] = useState("");
  const [isScraping, setIsScraping] = useState(false);

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPersona.name.trim() && newPersona.description.trim()) {
      onAddPersona(newPersona);
      setNewPersona({ name: '', description: '', avatar: '👤' });
    }
  };

  const handleScrapeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instagramUsername.trim()) return;
    
    setIsScraping(true);
    const success = await onScrapePersona(instagramUsername);
    setIsScraping(false);

    if (success) {
      setInstagramUsername("");
      onClose(); // Close sidebar on success to see the new persona
    } else {
      // Optionally: show an error message to the user
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      
      {/* Sidebar */}
      <div className="relative w-96 bg-white shadow-xl h-full overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Manage Personas</h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Add from Instagram */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Instagram className="h-5 w-5 mr-2" /> Add from Instagram
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleScrapeSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="instagram-username">Instagram Username</Label>
                  <Input
                    id="instagram-username"
                    value={instagramUsername}
                    onChange={(e) => setInstagramUsername(e.target.value)}
                    placeholder="e.g., natgeo"
                    disabled={isScraping}
                  />
                </div>
                <Button type="submit" className="w-full" disabled={isScraping}>
                  {isScraping ? "Scraping..." : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Persona
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Add New Persona Form */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Add Manually</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleManualSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="avatar">Avatar (Emoji)</Label>
                  <Input
                    id="avatar"
                    value={newPersona.avatar}
                    onChange={(e) => setNewPersona({ ...newPersona, avatar: e.target.value })}
                    placeholder="👤"
                    maxLength={2}
                    className="text-center text-2xl h-12"
                  />
                </div>
                
                <div>
                  <Label htmlFor="name">Persona Name</Label>
                  <Input
                    id="name"
                    value={newPersona.name}
                    onChange={(e) => setNewPersona({ ...newPersona, name: e.target.value })}
                    placeholder="e.g., Budget-Conscious Buyer"
                  />
                </div>
                
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newPersona.description}
                    onChange={(e) => setNewPersona({ ...newPersona, description: e.target.value })}
                    placeholder="Describe this persona's characteristics and behavior..."
                    rows={3}
                  />
                </div>
                
                <Button type="submit" className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Persona
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Existing Personas */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Your Custom Personas</h3>
            <div className="space-y-3">
              {personas.map((persona) => (
                <Card key={persona.id} className="relative group">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {persona.avatar.startsWith("http") ? (
                        <img src={persona.avatar} alt={persona.name} className="h-10 w-10 rounded-full" />
                      ) : (
                        <span className="text-2xl h-10 w-10 flex items-center justify-center bg-gray-100 rounded-full">{persona.avatar}</span>
                      )}
                      <div className="flex-1">
                        <h4 className="font-medium">{persona.name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{persona.description}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onDeletePersona(persona.id)}
                        className="absolute top-2 right-2 h-7 w-7 text-gray-400 hover:text-red-500 hover:bg-red-100 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {personas.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <User className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No custom personas yet.</p>
                  <p className="text-sm">Add your first persona above!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
