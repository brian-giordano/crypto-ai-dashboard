import { useState } from "react";
import { analyzeSentiment } from "@/app/api/api";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

const SentimentAnalyzer: React.FC = () => {
  const [text, setText] = useState<string>("");
  const [result, setResult] = useState<{
    sentiment: string;
    score: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    try {
      const data = await analyzeSentiment(text);
      setResult(data);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
      setResult(null);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiment Analyzer</CardTitle>
      </CardHeader>
      <CardContent>
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to analyze sentiment"
          className="mb-4"
        />
        <Button onClick={handleAnalyze}>Analyze Sentiment</Button>
        {result && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold">Result:</h3>
            <p>Sentiment: {result.sentiment}</p>
            <p>Score: {result.score}</p>
          </div>
        )}
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </CardContent>
    </Card>
  );
};
