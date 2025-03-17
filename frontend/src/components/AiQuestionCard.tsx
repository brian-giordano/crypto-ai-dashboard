import React, { useState } from "react";
import { Sparkles } from "lucide-react";
import { Button } from "./ui/button";
import { useQuery } from "@tanstack/react-query";
import AnimatedResponse from "./AnimatedResponse";

interface AIResponse {
  text: string;
  sentiment?: string;
  confidence?: number;
  metrics?: {
    price: string;
    marketCap: string;
    volume24h: string;
    change24h: string;
  };
}

const AiQuestionCard: React.FC = () => {
  const [question, setQuestion] = useState<string>("");
  const [currentQuestion, setCurrentQuestion] = useState<string>("");

  // Use React Query for data fetching with proper caching
  const {
    data: response,
    isLoading,
    error,
    // refetch,
    isError,
  } = useQuery<AIResponse, Error>({
    queryKey: ["aiResponse", currentQuestion],
    queryFn: async () => {
      if (!currentQuestion) return null;

      const res = await fetch("/api/ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: currentQuestion }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Failed to get AI response");
      }

      return res.json();
    },
    enabled: !!currentQuestion, // Only run the query if we have a question
    staleTime: 1000 * 60 * 5, // Cache responses for 5 minutes
  });

  const suggestedQuestions = [
    "What is the trend for Bitcoin?",
    "Show me the top 5 cryptocurrencies",
    "What is the market sentiment today?",
    "Predict Ethereum price for next week",
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setCurrentQuestion(question);
  };

  const selectSuggestedQuestion = (q: string) => {
    setQuestion(q);
    setCurrentQuestion(q); // Immediately trigger the query
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div>
        <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-white flex items-center">
          <Sparkles className="h-6 w-6 mr-2 text-pink-500" />
          Ask Vision
        </h2>

        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex items-stretch">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask about crypto trends, predictions, or insights..."
              className="flex-grow px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white h-10"
            />
            <Button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="rounded-l-none h-10 bg-pink-500"
              variant="default"
            >
              {isLoading ? (
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </Button>
          </div>
        </form>

        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
            Suggested Questions:
          </h3>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, index) => (
              <button
                key={index}
                onClick={() => selectSuggestedQuestion(q)}
                className="text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-2 py-1 rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {isLoading && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-2 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
              <div className="h-2 w-28 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
              <div className="h-2 w-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        )}

        {isError && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 rounded-lg p-4 mb-4">
            <p>
              {error?.message ||
                "An error occurred while processing your question."}
            </p>
          </div>
        )}

        {response && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="mb-4 text-gray-800 dark:text-gray-200">
              <AnimatedResponse text={response.text} />
            </p>

            {response.sentiment && (
              <div className="mb-4 text-sm">
                <span className="text-gray-500 dark:text-gray-400">
                  Sentiment:{" "}
                </span>
                <span
                  className={`font-medium ${
                    response.sentiment.toUpperCase() === "POSITIVE"
                      ? "text-green-500"
                      : response.sentiment.toUpperCase() === "NEGATIVE"
                      ? "text-red-500"
                      : "text-gray-500"
                  }`}
                >
                  {response.sentiment}
                </span>
                {response.confidence && (
                  <span className="text-gray-500 dark:text-gray-400 ml-2">
                    (Confidence:{" "}
                    {Math.min(Math.round(response.confidence * 100), 99.9)}%)
                  </span>
                )}
              </div>
            )}

            {response.metrics && (
              <div className="grid grid-cols-2 gap-2 mt-4">
                <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Price
                  </p>
                  <p className="font-medium">{response.metrics.price}</p>
                </div>
                <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Market Cap
                  </p>
                  <p className="font-medium">{response.metrics.marketCap}</p>
                </div>
                <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    24h Volume
                  </p>
                  <p className="font-medium">{response.metrics.volume24h}</p>
                </div>
                <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    24h Change
                  </p>
                  <p
                    className={`font-medium ${
                      response.metrics &&
                      response.metrics.change24h &&
                      parseFloat(response.metrics.change24h) > 0
                        ? "text-green-500"
                        : "text-red-500"
                    }`}
                  >
                    {response.metrics && response.metrics.change24h
                      ? `${parseFloat(response.metrics.change24h).toFixed(2)}%`
                      : "N/A"}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AiQuestionCard;
