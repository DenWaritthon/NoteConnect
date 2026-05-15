const API_BASE_URL = process.env.NOTE_CONNECT_API_BASE_URL ?? "http://127.0.0.1:6550";
const API_KEY = process.env.API_SECRET_KEY ?? process.env.NOTE_CONNECT_API_KEY;
const API_KEY_HEADER_NAME = process.env.API_KEY_HEADER_NAME ?? "X-API-Key";

type RouteParams = {
  params: Promise<{
    path: string[];
  }>;
};

async function proxy(request: Request, { params }: RouteParams) {
  const { path } = await params;
  const incomingUrl = new URL(request.url);
  const upstreamUrl = new URL(path.join("/"), `${API_BASE_URL.replace(/\/$/, "")}/`);
  upstreamUrl.search = incomingUrl.search;

  const headers = new Headers();
  if (!API_KEY) {
    return Response.json(
      { error: "Missing API key. Set API_SECRET_KEY in frontend/.env.local." },
      { status: 500 },
    );
  }

  headers.set(API_KEY_HEADER_NAME, API_KEY);

  // Forward only the headers the backend needs so browser cookies stay client-side.
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }

  const response = await fetch(upstreamUrl, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
    cache: "no-store",
  });

  const responseHeaders = new Headers();
  const responseType = response.headers.get("content-type");
  if (responseType) {
    responseHeaders.set("content-type", responseType);
  }

  return new Response(await response.text(), {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
