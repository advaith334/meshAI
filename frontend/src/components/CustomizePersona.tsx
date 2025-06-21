import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  X,
  ArrowLeft,
  HelpCircle,
  Edit,
  Trash2,
  Plus,
  Copy,
} from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface CustomPersona {
  id: string;
  name: string;
  avatar: string;
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

interface CustomizePersonaProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (persona: CustomPersona) => void;
  onDelete: (personaId: string) => void;
  existingPersonas: CustomPersona[];
  editingPersona?: CustomPersona | null;
}

const defaultAvatars = [
  "👩", "👨", "🧑", "👩‍💼", "👨‍💼", "👩‍🔬", "👨‍🔬", "👩‍🎓", "👨‍🎓",
  "👩‍💻", "👨‍💻", "👩‍🏫", "👨‍🏫", "👩‍⚕️", "👨‍⚕️"
];

const industries = [
  "Technology", "Healthcare", "Finance", "Education", "Retail", "Manufacturing",
  "Media", "Government", "Non-profit", "Consulting", "Real Estate", "Transportation"
];

const motivationOptions = [
  "Innovation", "Growth", "Efficiency", "Recognition", "Collaboration",
  "Remote Work", "Stability", "Learning", "Leadership", "Work-Life Balance"
];

const behavioralTraitOptions = [
  "Optimistic", "Skeptical", "Analytical", "Creative", "Detail-oriented",
  "Big-picture", "Risk-averse", "Adventurous", "Collaborative", "Independent",
  "Empathetic", "Logical", "Intuitive", "Methodical", "Flexible", "Structured"
];

export const CustomizePersona = ({
  isOpen,
  onClose,
  onSave,
  onDelete,
  existingPersonas,
  editingPersona
}: CustomizePersonaProps) => {
  const [currentView, setCurrentView] = useState<'list' | 'create' | 'edit'>('list');
  const [selectedPersona, setSelectedPersona] = useState<CustomPersona | null>(null);
  const [customAttributes, setCustomAttributes] = useState<{ [key: string]: string }>({});
  const [newAttributeKey, setNewAttributeKey] = useState("");
  const [newAttributeValue, setNewAttributeValue] = useState("");

  const [formData, setFormData] = useState<CustomPersona>({
    id: '',
    name: '',
    avatar: '👤',
    industry: '',
    role: '',
    ageGroup: '',
    gender: '',
    ethnicity: '',
    religion: '',
    education: '',
    income: '',
    location: '',
    riskTolerance: 50,
    techAdoption: 50,
    emotionalSensitivity: 50,
    opennessToIdeas: 50,
    motivations: [],
    customAttributes: {},
    behavioralTraits: [],
    engagementScore: 75,
    description: ''
  });

  useEffect(() => {
    if (editingPersona) {
      setFormData(editingPersona);
      setCustomAttributes(editingPersona.customAttributes);
      setCurrentView('edit');
    } else if (isOpen) {
      setCurrentView('list');
      resetForm();
    }
  }, [editingPersona, isOpen]);

  const resetForm = () => {
    setFormData({
      id: '',
      name: '',
      avatar: '👤',
      industry: '',
      role: '',
      ageGroup: '',
      gender: '',
      ethnicity: '',
      religion: '',
      education: '',
      income: '',
      location: '',
      riskTolerance: 50,
      techAdoption: 50,
      emotionalSensitivity: 50,
      opennessToIdeas: 50,
      motivations: [],
      customAttributes: {},
      behavioralTraits: [],
      engagementScore: 75,
      description: ''
    });
    setCustomAttributes({});
  };

  const handleSave = () => {
    const personaToSave = {
      ...formData,
      id: formData.id || `persona-${Date.now()}`,
      customAttributes,
      engagementScore: Math.round((formData.riskTolerance + formData.techAdoption + formData.opennessToIdeas) / 3)
    };
    onSave(personaToSave);
    resetForm();
    setCurrentView('list');
  };

  const handleMotivationToggle = (motivation: string) => {
    setFormData(prev => ({
      ...prev,
      motivations: prev.motivations.includes(motivation)
        ? prev.motivations.filter(m => m !== motivation)
        : [...prev.motivations, motivation]
    }));
  };

  const handleTraitToggle = (trait: string) => {
    setFormData(prev => ({
      ...prev,
      behavioralTraits: prev.behavioralTraits.includes(trait)
        ? prev.behavioralTraits.filter(t => t !== trait)
        : [...prev.behavioralTraits, trait]
    }));
  };

  const addCustomAttribute = () => {
    if (newAttributeKey && newAttributeValue) {
      setCustomAttributes(prev => ({
        ...prev,
        [newAttributeKey]: newAttributeValue
      }));
      setNewAttributeKey("");
      setNewAttributeValue("");
    }
  };

  const removeCustomAttribute = (key: string) => {
    setCustomAttributes(prev => {
      const updated = { ...prev };
      delete updated[key];
      return updated;
    });
  };

  const duplicatePersona = (persona: CustomPersona) => {
    const duplicated = {
      ...persona,
      id: `persona-${Date.now()}`,
      name: `${persona.name} (Copy)`
    };
    setFormData(duplicated);
    setCustomAttributes(duplicated.customAttributes);
    setCurrentView('create');
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] flex flex-col p-0">
        {/* Header */}
        <DialogHeader className="p-6 flex-shrink-0 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {currentView !== 'list' && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setCurrentView('list')}
                >
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              )}
              <DialogTitle className="text-xl">Customize Personas</DialogTitle>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon">
                <HelpCircle className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>
          
          {/* Breadcrumb */}
          <div className="text-sm text-muted-foreground mt-2">
            Dashboard / Personas / {currentView === 'list' ? 'Manage' : currentView === 'create' ? 'Create' : 'Edit'}
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto min-h-0">
          {currentView === 'list' ? (
            // Persona List View
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Manage Personas</h2>
                <Button onClick={() => setCurrentView('create')} className="bg-blue-600 text-white hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Persona
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {existingPersonas.map((persona) => (
                  <Card 
                    key={persona.id} 
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => {
                      setFormData(persona);
                      setCustomAttributes(persona.customAttributes);
                      setCurrentView('edit');
                    }}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">{persona.avatar}</span>
                          <div>
                            <h3 className="font-semibold">{persona.name}</h3>
                            <p className="text-sm text-gray-600">{persona.role}</p>
                          </div>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(persona.id);
                            }}
                            className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Industry:</span>
                          <span>{persona.industry}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Role:</span>
                          <span>{persona.role}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Engagement:</span>
                          <Badge variant="secondary">{persona.engagementScore}%</Badge>
                        </div>
                        <div className="mt-3">
                          <div className="flex flex-wrap gap-1">
                            {persona.behavioralTraits.slice(0, 3).map((trait) => (
                              <Badge key={trait} variant="outline" className="text-xs">
                                {trait}
                              </Badge>
                            ))}
                            {persona.behavioralTraits.length > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{persona.behavioralTraits.length - 3}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            // Create/Edit View
            <div className="flex h-full">
              {/* Avatar Selection */}
              <div className="w-80 bg-slate-50 p-6 border-r flex-shrink-0">
                <h3 className="font-semibold mb-4">Select Avatar</h3>
                <div className="grid grid-cols-3 gap-3">
                  {defaultAvatars.map((avatar, index) => (
                    <button
                      key={index}
                      onClick={() => setFormData(prev => ({ ...prev, avatar }))}
                      className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl border-2 transition-colors ${
                        formData.avatar === avatar 
                          ? 'border-blue-500 bg-blue-100' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {avatar}
                    </button>
                  ))}
                </div>
              </div>

              {/* Form */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <Accordion type="multiple" defaultValue={['item-1', 'item-2']} className="w-full space-y-4">
                  {/* Basic Info */}
                  <AccordionItem value="item-1" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Basic Information
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="grid grid-cols-2 gap-4 pt-4">
                        <div>
                          <Label htmlFor="name">Persona Name</Label>
                          <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                            placeholder="e.g., Sarah the Marketing Analyst"
                          />
                        </div>
                        <div>
                          <Label htmlFor="industry">Industry</Label>
                          <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({ ...prev, industry: value }))}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select industry" />
                            </SelectTrigger>
                            <SelectContent>
                              {industries.map((industry) => (
                                <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="role">Role</Label>
                          <Input
                            id="role"
                            value={formData.role}
                            onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                            placeholder="e.g., Data Analyst"
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                  
                  {/* Demographics */}
                  <AccordionItem value="item-2" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Demographics
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="grid grid-cols-2 gap-4 pt-4">
                        <div>
                          <Label htmlFor="ageGroup">Age Group</Label>
                          <Select value={formData.ageGroup} onValueChange={(value) => setFormData(prev => ({ ...prev, ageGroup: value }))}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select age group" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="18-24">18-24</SelectItem>
                              <SelectItem value="25-34">25-34</SelectItem>
                              <SelectItem value="35-44">35-44</SelectItem>
                              <SelectItem value="45-54">45-54</SelectItem>
                              <SelectItem value="55-64">55-64</SelectItem>
                              <SelectItem value="65+">65+</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="gender">Gender</Label>
                          <Select value={formData.gender} onValueChange={(value) => setFormData(prev => ({ ...prev, gender: value }))}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select gender" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Female">Female</SelectItem>
                              <SelectItem value="Male">Male</SelectItem>
                              <SelectItem value="Non-binary">Non-binary</SelectItem>
                              <SelectItem value="Prefer not to say">Prefer not to say</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="ethnicity">Ethnicity</Label>
                          <Input
                            id="ethnicity"
                            value={formData.ethnicity}
                            onChange={(e) => setFormData(prev => ({ ...prev, ethnicity: e.target.value }))}
                            placeholder="e.g., Hispanic, Asian, etc."
                          />
                        </div>
                        <div>
                          <Label htmlFor="religion">Religion</Label>
                          <Input
                            id="religion"
                            value={formData.religion}
                            onChange={(e) => setFormData(prev => ({ ...prev, religion: e.target.value }))}
                            placeholder="e.g., Christian, Muslim, etc."
                          />
                        </div>
                        <div>
                          <Label htmlFor="education">Education Level</Label>
                          <Select value={formData.education} onValueChange={(value) => setFormData(prev => ({ ...prev, education: value }))}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select education level" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="High School">High School</SelectItem>
                              <SelectItem value="Associate Degree">Associate Degree</SelectItem>
                              <SelectItem value="Bachelor's Degree">Bachelor's Degree</SelectItem>
                              <SelectItem value="Master's Degree">Master's Degree</SelectItem>
                              <SelectItem value="Doctorate">Doctorate</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="income">Income Level</Label>
                          <Select value={formData.income} onValueChange={(value) => setFormData(prev => ({ ...prev, income: value }))}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select income level" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Under $30k">Under $30k</SelectItem>
                              <SelectItem value="$30k-$50k">$30k-$50k</SelectItem>
                              <SelectItem value="$50k-$75k">$50k-$75k</SelectItem>
                              <SelectItem value="$75k-$100k">$75k-$100k</SelectItem>
                              <SelectItem value="$100k-$150k">$100k-$150k</SelectItem>
                              <SelectItem value="Over $150k">Over $150k</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Behavioral Data */}
                  <AccordionItem value="item-3" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Behavioral Data
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="space-y-6 pt-4">
                        <div className="space-y-4">
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <Label>Risk Tolerance</Label>
                              <span className="text-sm text-gray-600">
                                {formData.riskTolerance < 30 ? 'Low' : formData.riskTolerance < 70 ? 'Medium' : 'High'}
                              </span>
                            </div>
                            <Slider
                              value={[formData.riskTolerance]}
                              onValueChange={(value) => setFormData(prev => ({ ...prev, riskTolerance: value[0] }))}
                              max={100}
                              step={1}
                              className="w-full"
                            />
                          </div>
                          
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <Label>Tech Adoption</Label>
                              <span className="text-sm text-gray-600">
                                {formData.techAdoption < 30 ? 'Low' : formData.techAdoption < 70 ? 'Medium' : 'High'}
                              </span>
                            </div>
                            <Slider
                              value={[formData.techAdoption]}
                              onValueChange={(value) => setFormData(prev => ({ ...prev, techAdoption: value[0] }))}
                              max={100}
                              step={1}
                              className="w-full"
                            />
                          </div>
                          
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <Label>Emotional Sensitivity</Label>
                              <span className="text-sm text-gray-600">
                                {formData.emotionalSensitivity < 30 ? 'Low' : formData.emotionalSensitivity < 70 ? 'Medium' : 'High'}
                              </span>
                            </div>
                            <Slider
                              value={[formData.emotionalSensitivity]}
                              onValueChange={(value) => setFormData(prev => ({ ...prev, emotionalSensitivity: value[0] }))}
                              max={100}
                              step={1}
                              className="w-full"
                            />
                          </div>
                          
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <Label>Openness to Ideas</Label>
                              <span className="text-sm text-gray-600">
                                {formData.opennessToIdeas < 30 ? 'Low' : formData.opennessToIdeas < 70 ? 'Medium' : 'High'}
                              </span>
                            </div>
                            <Slider
                              value={[formData.opennessToIdeas]}
                              onValueChange={(value) => setFormData(prev => ({ ...prev, opennessToIdeas: value[0] }))}
                              max={100}
                              step={1}
                              className="w-full"
                            />
                          </div>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Motivations and Preferences */}
                  <AccordionItem value="item-4" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Motivations and Preferences
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="flex flex-wrap gap-2 pt-4">
                        {motivationOptions.map((motivation) => (
                          <Badge
                            key={motivation}
                            variant={formData.motivations.includes(motivation) ? "default" : "outline"}
                            className={`cursor-pointer ${formData.motivations.includes(motivation) ? 'bg-blue-600 text-white' : ''}`}
                            onClick={() => handleMotivationToggle(motivation)}
                          >
                            {motivation}
                          </Badge>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Behavioral Traits */}
                  <AccordionItem value="item-5" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Behavioral Traits
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="flex flex-wrap gap-2 pt-4">
                        {behavioralTraitOptions.map((trait) => (
                          <Badge
                            key={trait}
                            variant={formData.behavioralTraits.includes(trait) ? "default" : "outline"}
                            className={`cursor-pointer ${formData.behavioralTraits.includes(trait) ? 'bg-blue-600 text-white' : ''}`}
                            onClick={() => handleTraitToggle(trait)}
                          >
                            {trait}
                          </Badge>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Custom Attributes */}
                  <AccordionItem value="item-6" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Custom Attributes
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <div className="space-y-4 pt-4">
                        <div className="flex gap-2">
                          <Input
                            placeholder="Attribute name"
                            value={newAttributeKey}
                            onChange={(e) => setNewAttributeKey(e.target.value)}
                          />
                          <Input
                            placeholder="Attribute value"
                            value={newAttributeValue}
                            onChange={(e) => setNewAttributeValue(e.target.value)}
                          />
                          <Button onClick={addCustomAttribute} size="sm">
                            <Plus className="h-4 w-4" />
                          </Button>
                        </div>
                        
                        <div className="space-y-2">
                          {Object.entries(customAttributes).map(([key, value]) => (
                            <div key={key} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                              <span className="text-sm">
                                <strong>{key}:</strong> {value}
                              </span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeCustomAttribute(key)}
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Description */}
                  <AccordionItem value="item-7" className="border rounded-lg bg-white">
                    <AccordionTrigger className="px-4 py-3 font-semibold hover:no-underline">
                      Description
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pt-0 pb-4">
                      <Textarea
                        placeholder="Describe this persona's background, goals, and any additional context..."
                        value={formData.description}
                        onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                        rows={4}
                        className="mt-4"
                      />
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>

                {/* Save Button */}
                <div className="flex justify-end pt-6">
                  <Button onClick={handleSave} className="bg-blue-600 text-white hover:bg-blue-700 px-8">
                    {currentView === 'edit' ? 'Save Changes' : 'Create Persona'}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}; 