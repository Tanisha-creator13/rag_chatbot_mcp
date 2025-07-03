// import { NextRequest, NextResponse } from "next/server";

// export async function POST(req: NextRequest) {
//   try {
//     const authHeader = req.headers.get("Authorization");

//     if (!authHeader) {
//       return NextResponse.json(
//         { error: "Authorization header required" },
//         { status: 401 }
//       );
//     }

//     const { message, session_id }: { message?: string; session_id?: string } = await req.json();

//     if (!message || message.trim() === "") {
//       return NextResponse.json(
//         { error: "Message is required" },
//         { status: 400 }
//       );
//     }

//     const backendUrl = process.env.BACKEND_URL || "http://localhost:8000/api/chat/";

//     const response = await fetch(backendUrl, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "Authorization": authHeader,
//       },
//       body: JSON.stringify({ message, session_id }),
//     });

//     const text = await response.text();
//     console.log("Raw response from backend:", text);
//     let data;
//     try {
//       data = JSON.parse(text);
//     } catch (e) {
//       console.error("Failed to parse JSON:", text);
//       return NextResponse.json({ error: "Backend returned invalid JSON." }, { status: 500 });
//     }

//     if (!response.ok) {
//       console.error("Django API error:", data);
//       return NextResponse.json(
//         { error: data.error || "Backend error" },
//         { status: response.status }
//       );
//     }

//     return NextResponse.json({
//       reply: data.reply,
//       session_id: data.session_id || session_id,
//     });
//   } catch (error) {
//     console.error("API route error:", error);
//     return NextResponse.json(
//       { error: "Internal server error. Check logs." },
//       { status: 500 }
//     );
//   }
