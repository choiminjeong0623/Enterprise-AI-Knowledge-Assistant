import client from "./client";
import type { ChatResponse } from "../types/conversation";

interface SendChatRequest {
  conversation_id: number;
  message: string;
}

export const sendChatMessage = async (
  request: SendChatRequest
): Promise<ChatResponse> => {
  const response = await client.post<ChatResponse>("/chat", request);
  return response.data;
};