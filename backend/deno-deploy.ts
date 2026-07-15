// Quick Deno Deploy wrapper for AudienceOS API
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const BACKEND_URL = "http://localhost:8000"; // Will be replaced with actual backend

serve(async (req: Request) => {
  const url = new URL(req.url);
  
  // CORS headers
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  };

  // Handle OPTIONS
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers });
  }

  // Simple health check
  if (url.pathname === "/") {
    return new Response(JSON.stringify({
      message: "AudienceOS API",
      status: "ready",
      version: "1.0.0",
      endpoints: {
        health: "/health",
        audiences: "/api/v1/audiences",
        research: "/api/v1/research",
        content: "/api/v1/content",
        docs: "/docs"
      }
    }), {
      headers: { ...headers, "Content-Type": "application/json" },
    });
  }

  if (url.pathname === "/health") {
    return new Response(JSON.stringify({
      status: "healthy",
      timestamp: new Date().toISOString()
    }), {
      headers: { ...headers, "Content-Type": "application/json" },
    });
  }

  // Mock audience endpoint
  if (url.pathname === "/api/v1/audiences") {
    return new Response(JSON.stringify({
      audiences: [
        {
          id: "demo-1",
          name: "Startup Founders",
          description: "Early-stage startup founders looking for growth tools",
          size_estimate: 50000,
          platforms: ["reddit", "twitter"],
          created_at: new Date().toISOString()
        }
      ]
    }), {
      headers: { ...headers, "Content-Type": "application/json" },
    });
  }

  return new Response("Not Found", { status: 404, headers });
});