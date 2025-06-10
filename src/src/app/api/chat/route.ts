import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000/chat/";

    console.log("Forwarding to Django:", { message, backendUrl });
    
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const responseText = await response.text();
    console.log("Django response:", { 
      status: response.status, 
      body: responseText 
    });

    if (!response.ok) {
      return NextResponse.json(
        { reply: "Backend error: " + responseText }, 
        { status: 500 }
      );
    }

    const data = JSON.parse(responseText);
    return NextResponse.json({ reply: data.reply });
  } catch (error) {
    console.error("API route error:", error);
    return NextResponse.json(
      { reply: "Internal server error. Check logs." }, 
      { status: 500 }
    );
  }
}
