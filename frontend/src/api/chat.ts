import client from "./client";
import type { ChatResponse } from "../types/conversation";

export interface Source {
  document_id: number;
  document_filename: string;
  chunk_index: number;
  content: string;
}

interface SendChatRequest {
  conversation_id: number | null;
  message: string;
}

export const sendChatMessage = async (
  request: SendChatRequest
): Promise<ChatResponse> => {
  const response = await client.post<ChatResponse>("/chat", request);
  return response.data;
};