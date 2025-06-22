import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { X } from "lucide-react";

interface Persona {
  name: string;
  role: string;
  description: string;
  avatar: string;
  traits?: string[];
}

interface CustomizePersonaProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (persona: Persona) => void;
}

const defaultAvatars = [
  "👩", "👨", "🧑", "👩‍💼", "👨‍💼", "👩‍🔬", "👨‍🔬", "👩‍🎓", "👨‍🎓",
  "👩‍💻", "👨‍💻", "👩‍🏫", "👨‍🏫", "👩‍⚕️", "👨‍⚕️"
];

export const CustomizePersona = ({
  isOpen,
  onClose,
  onSave,
}: CustomizePersonaProps) => {
  const [persona, setPersona] = useState<Persona>({
    name: "",
    role: "",
    description: "",
    avatar: "👤",
    traits: [],
  });

  const handleSave = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/save-persona", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(persona),
      });
      if (response.ok) {
        const result = await response.json();
        console.log(result.message);
        onSave(persona); // To update UI locally if needed
        onClose();
      } else {
        console.error("Failed to save persona");
      }
    } catch (error) {
      console.error("Error saving persona:", error);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Persona</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Avatar
            </Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="col-span-3 justify-start">
                  <span className="text-2xl">{persona.avatar}</span>
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <div className="grid grid-cols-5 gap-2 p-4">
                  {defaultAvatars.map((avatar) => (
                    <Button
                      key={avatar}
                      variant={persona.avatar === avatar ? "default" : "outline"}
                      size="icon"
                      onClick={() => setPersona((p) => ({ ...p, avatar }))}
                      className="text-2xl"
                    >
                      {avatar}
                    </Button>
                  ))}
                </div>
              </PopoverContent>
            </Popover>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input
              id="name"
              value={persona.name}
              onChange={(e) => setPersona({ ...persona, name: e.target.value })}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="role" className="text-right">
              Role
            </Label>
            <Input
              id="role"
              value={persona.role}
              onChange={(e) => setPersona({ ...persona, role: e.target.value })}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="description" className="text-right">
              Description
            </Label>
            <Textarea
              id="description"
              value={persona.description}
              onChange={(e) => setPersona({ ...persona, description: e.target.value })}
              className="col-span-3"
              placeholder="Describe the persona's background, goals, and motivations."
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" onClick={handleSave}>Save Persona</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}; 
