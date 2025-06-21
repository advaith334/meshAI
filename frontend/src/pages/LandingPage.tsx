import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Gauge, MessagesSquare, Users, Waypoints } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-8">
      <div className="text-center">
        <Waypoints className="h-24 w-24 mx-auto mb-6 text-primary" />
        <h1 className="text-5xl font-bold mb-4">Welcome to MeshAI</h1>
        <p className="text-xl mb-8 text-muted-foreground">
          Your intelligent platform for deep user understanding
        </p>
        <Button
          onClick={() => navigate("/dashboard")}
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-4 text-xl rounded-lg"
        >
          Go to Dashboard
        </Button>
      </div>

      <div className="mt-16 grid gap-8 md:grid-cols-3 max-w-6xl text-center">
        <Card className="bg-card border-primary/20 text-card-foreground flex flex-col">
          <CardHeader className="items-center">
            <Users className="h-12 w-12 mb-4 text-primary" />
            <CardTitle className="text-primary">Multiple Personas</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>
              Choose from diverse AI personas representing different customer
              types and perspectives
            </p>
          </CardContent>
        </Card>
        <Card className="bg-card border-primary/20 text-card-foreground flex flex-col">
          <CardHeader className="items-center">
            <MessagesSquare className="h-12 w-12 mb-4 text-primary" />
            <CardTitle className="text-primary">
              Interactive Discussions
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>
              Watch personas interact with each other and see how their
              opinions evolve
            </p>
          </CardContent>
        </Card>
        <Card className="bg-card border-primary/20 text-card-foreground flex flex-col">
          <CardHeader className="items-center">
            <Gauge className="h-12 w-12 mb-4 text-primary" />
            <CardTitle className="text-primary">Sentiment Analysis</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>
              Track how sentiments change through interactions and get valuable
              insights
            </p>
          </CardContent>
        </Card>
      </div>
      <footer className="absolute bottom-8 text-muted-foreground">
        <p>&copy; {new Date().getFullYear()} MeshAI. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage; 