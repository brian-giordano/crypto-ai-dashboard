// api/ai: Receives the question from the frontend, validates that a questions was provided,
// forwards request to FastAPI, Returns the reponse from backend to the frontend

import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { question } = body;

    if (!question) {
      return NextResponse.json(
        { error: "Question is required" },
        { status: 400 }
      );
    }

    // Call FastAPI backend
    const response = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || "Failed to get response from AI service" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in AI API route: ", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
