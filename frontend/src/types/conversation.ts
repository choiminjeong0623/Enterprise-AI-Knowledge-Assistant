export type MessageRole = "user" | "assistant" | "system";

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
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  assistant_message: Message;
}