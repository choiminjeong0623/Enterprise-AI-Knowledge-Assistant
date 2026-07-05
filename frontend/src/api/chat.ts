import client from "./client";

export interface ChatRequest {
    message: string;
}

export interface ChatResponse {
    success: boolean;
    message: string;
    data: {
        answer: string;
    }
}

export async function chat(request: ChatRequest) {

    const response = await client.post<ChatResponse>(
        "/chat",
        request
    );

    return response.data;
}