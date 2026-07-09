import type { Message } from "./conversation";

export interface Source {
  document_id: number;
  document_filename: string;
  chunk_index: number;
  content: string;
}

export interface SendChatRequest {
  message: string;
  conversation_id: number | null;
}

export interface SendChatResponse {
  conversation_id: number;
  user_message: Message;
  assistant_message: Message;
  sources: Source[];
}