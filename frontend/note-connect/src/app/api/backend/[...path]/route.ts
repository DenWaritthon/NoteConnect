import { NextRequest, NextResponse } from "next/server";
import { config } from "@/lib/config";

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

const SUPPORTED_METHODS = ["GET", "POST", "PATCH", "PUT", "DELETE"] as const;

function buildBackendUrl(path: string[], search: string) {
  const backendPath = `/${path.map(encodeURIComponent).join("/")}`;
  const url = new URL(backendPath, config.apiBaseUrl);
  url.search = search;

  return url;
}

async function proxyRequest(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const backendUrl = buildBackendUrl(path, request.nextUrl.search);
  const headers = new Headers();
  const contentType = request.headers.get("content-type");

  headers.set("Accept", "application/json");

  if (contentType) {
    headers.set("Content-Type", contentType);
  }

  const response = await fetch(backendUrl, {
    method: request.method,
    headers,
    body:
      request.method === "GET" || request.method === "HEAD"
        ? undefined
        : await request.text(),
    cache: "no-store",
  });
  const responseBody = await response.text();

  return new NextResponse(responseBody, {
    status: response.status,
    headers: {
      "Content-Type":
        response.headers.get("content-type") ?? "application/json",
    },
  });
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function PUT(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return proxyRequest(request, context);
}

export function OPTIONS() {
  return NextResponse.json({
    methods: SUPPORTED_METHODS,
  });
}
