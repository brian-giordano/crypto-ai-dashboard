// api/ai: Receives the question from the frontend, validates that a questions was provided,
// forwards request to FastAPI, Returns the reponse from backend to the frontend

import { NextRequest, NextResponse } from "next/server";
import { mockAIResponse } from "@/lib/mock-data";

const IS_DEMO = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export async function POST(request: NextRequest) {
  // 🚀 DEMO MODE - Instant mock AI responses (perfect for portfolio demo)
  if (IS_DEMO) {
    const body = await request.json();
    const question = body.question || "";

    await new Promise((resolve) => setTimeout(resolve, 920)); // simulates AI thinking time

    return NextResponse.json(mockAIResponse(question));
  }

  // === REAL IMPLEMENTATION (FastAPI proxy) - used when demo mode is disabled ===
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;

  try {
    const body = await request.json();

    // Call FastAPI backend
    const response = await fetch(`${backendUrl}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("FastAPI error:", errorText);
      return NextResponse.json(
        { error: "Failed to get response from AI service" },
        { status: response.status },
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in AI API route: ", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
