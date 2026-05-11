import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { question, history } = await req.json();

  const res = await fetch("http://127.0.0.1:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });

  const data = await res.json();
  return NextResponse.json(data);
}