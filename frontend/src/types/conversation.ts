export type MessageRole = "user" | "assistant" | "system";

export interface Source {
  document_id: number;
  document_filename: string;
  chunk_index: number;
  content: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  created_at: string;
  sources?: Source[];
}

export interface ChatRequest {
  message: string;
  conversation_id: number | null;
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  assistant_message: Message;
  sources?: Source[];
}