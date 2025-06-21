import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { X, User } from "lucide-react";

interface Persona {
  name: string;
  description: string;
  avatar: string;
  role: string;
}

interface PersonaSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  personas: Persona[];
}

export const PersonaSidebar = ({
  isOpen,
  onClose,
  personas,
}: PersonaSidebarProps) => {

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

          {/* Existing Personas */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Your Custom Personas</h3>
            <div className="space-y-3">
              {personas.map((persona, index) => (
                <Card key={index} className="relative group">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {persona.avatar.startsWith("http") ? (
                        <img
                          src={persona.avatar}
                          alt={persona.name}
                          className="h-10 w-10 rounded-full"
                        />
                      ) : (
                        <span className="text-2xl h-10 w-10 flex items-center justify-center bg-gray-100 rounded-full">
                          {persona.avatar}
                        </span>
                      )}
                      <div className="flex-1">
                        <h4 className="font-medium">{persona.name}</h4>
                        <p className="text-sm text-gray-500">{persona.role}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          {persona.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {personas.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <User className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No custom personas yet.</p>
                  <p className="text-sm">Create a persona to get started!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
