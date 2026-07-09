import client from "./client";
import type { Conversation, Message } from "../types/conversation";

export const getConversations = async (): Promise<Conversation[]> => {
  const response = await client.get<Conversation[]>("/conversations");
  return response.data;
};

export const createConversation = async (
  title: string
): Promise<Conversation> => {
  const response = await client.post<Conversation>("/conversations", {
    title,
  });

  return response.data;
};

export const updateConversationTitle = async (
  conversationId: number,
  title: string
): Promise<Conversation> => {
  const response = await client.patch<Conversation>(
    `/conversations/${conversationId}`,
    {
      title,
    }
  );

  return response.data;
};

export const deleteConversation = async (
  conversationId: number
): Promise<void> => {
  await client.delete(`/conversations/${conversationId}`);
};

export const getConversationMessages = async (
  conversationId: number
): Promise<Message[]> => {
  const response = await client.get<Message[]>(
    `/conversations/${conversationId}/messages`
  );

  return response.data;
};
