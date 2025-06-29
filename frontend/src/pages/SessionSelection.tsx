import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Users, User, MessageSquare, Clock, Target } from "lucide-react";

const SessionSelection = () => {
  const navigate = useNavigate();

  const sessionTypes = [
    {
      id: "interview",
      title: "One-on-One Interview",
      description: "Conduct a focused interview with a single persona to get detailed insights and feedback.",
      icon: User,
      features: [
        "Deep dive into specific topics",
        "Detailed qualitative feedback",
        "Focused conversation flow",
        "In-depth persona analysis"
      ],
      color: "bg-blue-500",
      hoverColor: "hover:bg-blue-600"
    },
    {
      id: "focus-group",
      title: "Focus Group Discussion",
      description: "Facilitate a group discussion with multiple personas to explore diverse perspectives and group dynamics.",
      icon: Users,
      features: [
        "Multiple persona interactions",
        "Group dynamics and consensus",
        "Diverse perspectives",
        "Comparative insights"
      ],
      color: "bg-green-500",
      hoverColor: "hover:bg-green-600"
    }
  ];

  const handleSessionTypeSelect = (sessionType: string) => {
    if (sessionType === "interview") {
      navigate("/interview");
    } else if (sessionType === "focus-group") {
      navigate("/focus-group");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate("/dashboard")} 
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Choose Session Type</h1>
          <p className="text-gray-600">Select the type of session you'd like to conduct</p>
        </div>

        {/* Session Type Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {sessionTypes.map((sessionType) => {
            const IconComponent = sessionType.icon;
            return (
              <Card 
                key={sessionType.id}
                className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 border-2 hover:border-gray-300"
                onClick={() => handleSessionTypeSelect(sessionType.id)}
              >
                <CardHeader className="text-center pb-4">
                  <div className={`w-16 h-16 ${sessionType.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <IconComponent className="h-8 w-8 text-white" />
                  </div>
                  <CardTitle className="text-xl font-semibold text-gray-900">
                    {sessionType.title}
                  </CardTitle>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {sessionType.description}
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900 mb-3">Key Features:</h4>
                    <ul className="space-y-2">
                      {sessionType.features.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600">
                          <Target className="h-4 w-4 mr-2 text-green-500 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <Button 
                    className={`w-full mt-6 ${sessionType.color} ${sessionType.hoverColor} text-white`}
                    onClick={() => handleSessionTypeSelect(sessionType.id)}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Start {sessionType.title}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Additional Info */}
        <div className="mt-8 p-6 bg-white rounded-lg border">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Session Guidelines</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">One-on-One Interview</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Best for detailed, focused feedback</li>
                <li>• Ideal for exploring specific use cases</li>
                <li>• Perfect for validating assumptions</li>
                <li>• Recommended duration: 15-30 minutes</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Focus Group</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Best for exploring diverse perspectives</li>
                <li>• Ideal for understanding group dynamics</li>
                <li>• Perfect for brainstorming sessions</li>
                <li>• Recommended duration: 30-45 minutes</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionSelection; 