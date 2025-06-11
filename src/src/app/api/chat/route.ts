import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { message, conversationId }: { message: string; conversationId: string } = await req.json();
    
    if (!conversationId) {
      return NextResponse.json(
        { reply: "Conversation ID is required" },
        { status: 400 }
      );
    }

    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000/chat/";
    
    // Forward to Django backend with conversation ID
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId  
      }),
    });

    // Handle Django response
    const responseText = await response.text();
    
    if (!response.ok) {
      console.error("Django API error:", responseText);
      return NextResponse.json(
        { reply: "Backend error: " + responseText },
        { status: 500 }
      );
    }

    const data = JSON.parse(responseText);
    return NextResponse.json({ 
      reply: data.reply,
      conversationId: data.conversation_id || conversationId
    });

  } catch (error) {
    console.error("API route error:", error);
    return NextResponse.json(
      { reply: "Internal server error. Check logs." },
      { status: 500 }
    );
  }
}
