interface SentimentResponse {
  sentiment: string;
  score: number;
}

interface AIResponse {
  text: string;
  sentiment: string | null;
  confidence: number | null;
  metrics: {
    price: string;
    marketCap: string;
    volume24h: string;
    change24h: string;
  } | null;
}

const backendUrl = process.env.API_URL; // FastAPI backend URL

export const analyzeSentiment = async (
  text: string
): Promise<SentimentResponse> => {
  console.log("backendUrl: ", backendUrl);
  const response = await fetch(`${backendUrl}/analyze-sentiment/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze sentiment");
  }

  return response.json();
};

export const askAI = async (question: string): Promise<AIResponse> => {
  const response = await fetch(`${backendUrl}/ask/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Failed to get AI response");
  }

  return response.json();
};
