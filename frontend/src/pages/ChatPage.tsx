import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import ConversationSidebar from "../components/conversation/ConversationSidebar";
import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  getConversations,
  updateConversationTitle,
} from "../api/conversation";
import { sendChatMessage } from "../api/chat";
import type { Conversation, Message } from "../types/conversation";
import { removeAccessToken } from "../utils/authStorage";
import "./ChatPage.css";

function ChatPage() {
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<
    number | null
  >(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const skipNextMessageLoadRef = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  const handleAuthError = (error: any) => {
    const status = error.response?.status;

    if (status === 401 || status === 403) {
      removeAccessToken();
      navigate("/login", { replace: true });
      return true;
    }

    return false;
  };

  const loadConversations = async () => {
    setIsLoadingConversations(true);

    try {
      const data = await getConversations();
      setConversations(data);

      if (selectedConversationId === null && data.length > 0) {
        setSelectedConversationId(data[0].id);
      }
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage("대화 목록을 불러오지 못했습니다.");
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadMessages = async (conversationId: number) => {
    setIsLoadingMessages(true);
    setErrorMessage(null);

    try {
      const data = await getConversationMessages(conversationId);
      setMessages(data);
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage("메시지를 불러오지 못했습니다.");
    } finally {
      setIsLoadingMessages(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (selectedConversationId === null) {
      setMessages([]);
      return;
    }

    if (skipNextMessageLoadRef.current) {
      skipNextMessageLoadRef.current = false;
      return;
    }

    loadMessages(selectedConversationId);
  }, [selectedConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleCreateConversation = async () => {
    setErrorMessage(null);

    try {
      const conversation = await createConversation("New Conversation");

      skipNextMessageLoadRef.current = true;
      setConversations((prev) => [conversation, ...prev]);
      setSelectedConversationId(conversation.id);
      setMessages([]);
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage("새 대화를 생성하지 못했습니다.");
    }
  };

  const handleSelectConversation = (conversationId: number) => {
    if (isSending) {
      return;
    }

    setSelectedConversationId(conversationId);
  };

  const handleDeleteConversation = async (conversationId: number) => {
    const confirmed = window.confirm("이 대화를 삭제할까요?");

    if (!confirmed) {
      return;
    }

    setErrorMessage(null);

    try {
      await deleteConversation(conversationId);

      const nextConversations = conversations.filter(
        (conversation) => conversation.id !== conversationId
      );

      setConversations(nextConversations);

      if (selectedConversationId === conversationId) {
        const nextSelectedConversation = nextConversations[0];

        if (nextSelectedConversation) {
          setSelectedConversationId(nextSelectedConversation.id);
        } else {
          setSelectedConversationId(null);
          setMessages([]);
        }
      }
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage("대화를 삭제하지 못했습니다.");
    }
  };

  const handleUpdateConversationTitle = async (
    conversationId: number,
    title: string
  ) => {
    setErrorMessage(null);

    try {
      const updatedConversation = await updateConversationTitle(
        conversationId,
        title
      );

      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId ? updatedConversation : conversation
        )
      );
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage("대화 제목을 수정하지 못했습니다.");
    }
  };

  const getDefaultConversationTitle = (message: string) => {
    const trimmedMessage = message.trim();

    if (trimmedMessage.length <= 30) {
      return trimmedMessage;
    }

    return `${trimmedMessage.slice(0, 30)}...`;
  };

  const ensureConversation = async (message: string) => {
    if (selectedConversationId !== null) {
      return selectedConversationId;
    }

    const title = getDefaultConversationTitle(message);
    const conversation = await createConversation(title || "New Conversation");

    skipNextMessageLoadRef.current = true;
    setConversations((prev) => [conversation, ...prev]);
    setSelectedConversationId(conversation.id);

    return conversation.id;
  };

  const updateConversationTitleIfNeeded = async (
    conversationId: number,
    message: string
  ) => {
    const currentConversation = conversations.find(
      (conversation) => conversation.id === conversationId
    );

    if (!currentConversation) {
      return;
    }

    const shouldUpdateTitle =
      currentConversation.title === "New Conversation" ||
      currentConversation.title.trim() === "";

    if (!shouldUpdateTitle) {
      return;
    }

    const nextTitle = getDefaultConversationTitle(message);

    try {
      const updatedConversation = await updateConversationTitle(
        conversationId,
        nextTitle
      );

      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId ? updatedConversation : conversation
        )
      );
    } catch {
      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                title: nextTitle,
              }
            : conversation
        )
      );
    }
  };

  const createOptimisticUserMessage = (
    conversationId: number,
    content: string
  ): Message => {
    return {
      id: -Date.now(),
      conversation_id: conversationId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
  };

  const handleSendMessage = async () => {
    const trimmedMessage = inputMessage.trim();

    if (!trimmedMessage || isSending) {
      return;
    }

    setIsSending(true);
    setErrorMessage(null);
    setInputMessage("");

    let optimisticMessageId: number | null = null;

    try {
      const conversationId = await ensureConversation(trimmedMessage);

      const optimisticUserMessage = createOptimisticUserMessage(
        conversationId,
        trimmedMessage
      );

      optimisticMessageId = optimisticUserMessage.id;

      setMessages((prev) => [...prev, optimisticUserMessage]);

      await updateConversationTitleIfNeeded(conversationId, trimmedMessage);

      const response = await sendChatMessage({
        conversation_id: conversationId,
        message: trimmedMessage,
      });

      setMessages((prev) => {
        const nextMessages = prev.filter(
          (message) => message.id !== optimisticMessageId
        );

        if (response.user_message) {
          nextMessages.push(response.user_message);
        }

        if (response.assistant_message) {
          nextMessages.push(response.assistant_message);
        }

        return nextMessages;
      });

      await loadConversations();
    } catch (error: any) {
      if (handleAuthError(error)) {
        return;
      }

      setMessages((prev) =>
        optimisticMessageId === null
          ? prev
          : prev.filter((message) => message.id !== optimisticMessageId)
      );

      setErrorMessage("메시지 전송에 실패했습니다.");
      setInputMessage(trimmedMessage);
    } finally {
      setIsSending(false);
    }
  };

  const handleLogout = () => {
    removeAccessToken();
    navigate("/login", { replace: true });
  };

  const hasMessages = messages.length > 0;
  const shouldShowWelcome =
    !isLoadingMessages && !isSending && !hasMessages && !errorMessage;

  return (
    <div className="chat-page">
      <ConversationSidebar
        conversations={conversations}
        selectedConversationId={selectedConversationId}
        isLoading={isLoadingConversations}
        onSelectConversation={handleSelectConversation}
        onCreateConversation={handleCreateConversation}
        onDeleteConversation={handleDeleteConversation}
        onUpdateConversationTitle={handleUpdateConversationTitle}
        onLogout={handleLogout}
      />

      <main className="chat-page__main">
        <div className="chat-page__messages">
          {errorMessage && (
            <div className="chat-page__error">
              <span>{errorMessage}</span>

              <button
                type="button"
                className="chat-page__error-close"
                onClick={() => setErrorMessage(null)}
              >
                ×
              </button>
            </div>
          )}

          {isLoadingMessages && (
            <div className="chat-page__loading">Loading messages...</div>
          )}

          {shouldShowWelcome && (
            <div className="chat-page__empty">
              <h1>Enterprise AI Knowledge Assistant</h1>
              <p>
                Ask a question to start a new conversation or select a previous
                conversation from the sidebar.
              </p>
            </div>
          )}

          {!isLoadingMessages &&
            messages
              .filter((message) => message !== undefined && message !== null)
              .map((message) => {
                const isUser = message.role === "user";

                return (
                  <div
                    key={message.id}
                    className={
                      isUser
                        ? "chat-page__message-row chat-page__message-row--user"
                        : "chat-page__message-row chat-page__message-row--assistant"
                    }
                  >
                    <div
                      className={
                        isUser
                          ? "chat-page__message chat-page__message--user"
                          : "chat-page__message chat-page__message--assistant"
                      }
                    >
                      <div className="chat-page__message-role">
                        {isUser ? "You" : "Assistant"}
                      </div>

                      <div className="chat-page__message-content">
                        {message.content}
                      </div>
                    </div>
                  </div>
                );
              })}

          {isSending && (
            <div className="chat-page__message-row chat-page__message-row--assistant">
              <div className="chat-page__message chat-page__message--assistant chat-page__message--loading">
                <div className="chat-page__message-role">Assistant</div>
                <div className="chat-page__typing">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-page__input-area">
          <textarea
            className="chat-page__textarea"
            placeholder="Ask anything..."
            value={inputMessage}
            disabled={isSending}
            onChange={(event) => setInputMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSendMessage();
              }
            }}
          />

          <button
            type="button"
            className="chat-page__send-button"
            onClick={handleSendMessage}
            disabled={isSending || !inputMessage.trim()}
          >
            {isSending ? "Sending..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default ChatPage;