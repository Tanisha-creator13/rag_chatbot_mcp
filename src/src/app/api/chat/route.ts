import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  // Replace with your Django backend endpoint
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000/chat/";

  // Forward the message to Django backend
  const response = await fetch(backendUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();

  return NextResponse.json({ reply: data.reply });
}
