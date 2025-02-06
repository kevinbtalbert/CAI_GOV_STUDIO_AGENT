import { NextRequest, NextResponse } from 'next/server';
import { Metadata } from '@grpc/grpc-js';
import { AgentStudioClient } from '@/studio/proto/agent_studio';
import { credentials } from '@grpc/grpc-js';

function queryToJson(query: URLSearchParams): Record<string, string> {
  const json: Record<string, string> = {};
  query.forEach((value, key) => {
    json[key] = value;
  });
  return json;
}

export async function GET(request: NextRequest) {
  return handleRequest(request, 'GET');
}

export async function POST(request: NextRequest) {
  return handleRequest(request, 'POST');
}

async function handleRequest(request: NextRequest, method: string) {
  const addr = `${process.env.AGENT_STUDIO_SERVICE_IP}:${process.env.AGENT_STUDIO_SERVICE_PORT}`;
  const client = new AgentStudioClient(addr, credentials.createInsecure());

  const slug = request.nextUrl.pathname.split('/api/grpc/')[1];

  if (!slug || !(slug in client)) {
    return NextResponse.json({ error: `Unknown gRPC method: ${slug}` }, { status: 404 });
  }

  try {
    let body =
      method === 'POST'
        ? await request.json() // For POST, parse JSON body
        : queryToJson(request.nextUrl.searchParams); // For GET, parse query params

    /*
      -- Special handling for file upload requests --
      I know this is super fishy, but I've not been able to find any other workaround for now.
      Since the rpc message body expects bytes for file content,
      but whatever we send from the react client(I've tried list of integers, base64 encoded strings, etc)
      gets lost in translation.
      TODO: Find a better solution for this.
    */
    if (slug === 'nonStreamingTemporaryFileUpload') {
      // Convert base64 to Uint8Array
      const binaryString = atob(body.full_content);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      body = {
        full_content: bytes,
        file_name: body.file_name,
      };
    }

    const grpcMethod = (client as any)[slug].bind(client);

    const grpcResponse = await new Promise((resolve, reject) => {
      grpcMethod(body, (err: Error | null, response: any) => {
        if (err) {
          return reject(err);
        }
        resolve(response);
      });
    });

    return NextResponse.json(grpcResponse);
  } catch (error: any) {
    console.error('Error:', error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
