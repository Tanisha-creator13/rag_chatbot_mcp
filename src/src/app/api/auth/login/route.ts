import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { username, password } = await req.json();
  try {
    // Forward to Django login endpoint
    const res = await fetch("http://localhost:8000/api/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    console.log("Backend response:", data, typeof data);
    
    if (!res.ok) {
      return NextResponse.json({ error: data.detail || "Login failed" }, { status: 401 });
    }

    // Set HTTP-only cookie (secure, same-site, etc.)
    const response = NextResponse.json({ success: true });
    response.cookies.set("access_token", data.access, { 
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
    });
    return response;
  } catch (error) {
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}
