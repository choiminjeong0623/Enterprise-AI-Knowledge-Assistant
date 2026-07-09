import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  createConversation,
  deleteConversation,
  getConversationMessages,
  getConversations,
  updateConversationTitle,
} from "../api/conversation";
import { sendChatMessage } from "../api/chat";
import ConversationSidebar from "../components/conversation/ConversationSidebar";
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
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleAuthError = (error: unknown) => {
    const status = (error as any)?.response?.status;

    if (status === 401 || status === 403) {
      removeAccessToken();
      navigate("/login");
      return true;
    }

    return false;
  };

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      setErrorMessage("");

      const data = await getConversations();
      setConversations(data);

      if (data.length > 0 && selectedConversationId === null) {
        setSelectedConversationId(data[0].id);
        await loadMessages(data[0].id);
      }
    } catch (error) {
      if (handleAuthError(error)) return;

      setErrorMessage("대화 목록을 불러오지 못했습니다.");
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadMessages = async (conversationId: number) => {
    try {
      setIsLoadingMessages(true);
      setErrorMessage("");

      const data = await getConversationMessages(conversationId);

      /**
       * 현재 구조에서는 GET /conversations/{id}/messages 응답에는 sources가 없음.
       * sources는 POST /chat 응답에서만 assistant message에 붙음.
       */
      setMessages(data.filter(Boolean));
    } catch (error) {
      if (handleAuthError(error)) return;

      setErrorMessage("메시지를 불러오지 못했습니다.");
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const handleSelectConversation = async (conversationId: number) => {
    if (conversationId === selectedConversationId) return;

    setSelectedConversationId(conversationId);
    await loadMessages(conversationId);
  };

  const handleCreateConversation = async () => {
    try {
      setErrorMessage("");

      const conversation = await createConversation("New Conversation");

      setConversations((prevConversations) => [
        conversation,
        ...prevConversations,
      ]);

      setSelectedConversationId(conversation.id);
      setMessages([]);
    } catch (error) {
      if (handleAuthError(error)) return;

      setErrorMessage("새 대화를 만들지 못했습니다.");
    }
  };

  const handleUpdateConversationTitle = async (
    conversationId: number,
    title: string
  ) => {
    const trimmedTitle = title.trim();

    if (!trimmedTitle) return;

    try {
      setErrorMessage("");

      const updatedConversation = await updateConversationTitle(conversationId, trimmedTitle);

      setConversations((prevConversations) =>
        prevConversations.map((conversation) =>
          conversation.id === conversationId
            ? updatedConversation
            : conversation
        )
      );
    } catch (error) {
      if (handleAuthError(error)) return;

      setErrorMessage("대화 제목을 수정하지 못했습니다.");
    }
  };

  const handleDeleteConversation = async (conversationId: number) => {
    const confirmed = window.confirm("이 대화를 삭제할까요?");

    if (!confirmed) return;

    try {
      setErrorMessage("");

      await deleteConversation(conversationId);

      const nextConversations = conversations.filter(
        (conversation) => conversation.id !== conversationId
      );

      setConversations(nextConversations);

      if (selectedConversationId === conversationId) {
        if (nextConversations.length > 0) {
          setSelectedConversationId(nextConversations[0].id);
          await loadMessages(nextConversations[0].id);
        } else {
          setSelectedConversationId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      if (handleAuthError(error)) return;

      setErrorMessage("대화를 삭제하지 못했습니다.");
    }
  };

  const handleLogout = () => {
    removeAccessToken();
    navigate("/login");
  };

  const handleSendMessage = async () => {
    const trimmedMessage = inputMessage.trim();

    if (!trimmedMessage || isSending) return;

    setInputMessage("");
    setErrorMessage("");
    setIsSending(true);

    /**
     * Optimistic UI용 임시 메시지.
     * 실제 DB id와 충돌하지 않도록 음수 id 사용.
     */
    const temporaryUserMessage: Message = {
      id: -Date.now(),
      conversation_id: selectedConversationId ?? -1,
      role: "user",
      content: trimmedMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((prevMessages) => [...prevMessages, temporaryUserMessage]);

    try {
      const response = await sendChatMessage({
        message: trimmedMessage,
        conversation_id: selectedConversationId,
      });

      const assistantMessageWithSources: Message = {
        ...response.assistant_message,
        sources: response.sources ?? [],
      };

      setSelectedConversationId(response.conversation_id);

      setMessages((prevMessages) => {
        const nextMessages = [
          ...prevMessages.filter(
            (message) => message.id !== temporaryUserMessage.id
          ),
          response.user_message,
          assistantMessageWithSources,
        ].filter(Boolean);

        /**
         * 같은 메시지가 중복으로 들어가는 것을 방지.
         * React key 중복 경고 방지용.
         */
        const uniqueMessages = nextMessages.filter(
          (message, index, array) =>
            array.findIndex(
              (item) => item.id === message.id && item.role === message.role
            ) === index
        );

        return uniqueMessages;
      });

      /**
       * 첫 메시지로 새 conversation이 생성된 경우,
       * sidebar 목록을 다시 불러와서 새 대화가 표시되게 함.
       */
      await loadConversations();
    } catch (error) {
      if (handleAuthError(error)) return;

      setMessages((prevMessages) =>
        prevMessages.filter(
          (message) => message.id !== temporaryUserMessage.id
        )
      );

      setInputMessage(trimmedMessage);
      setErrorMessage("메시지 전송에 실패했습니다.");
    } finally {
      setIsSending(false);
    }
  };

  const handleInputKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-page">
      <ConversationSidebar
        conversations={conversations}
        selectedConversationId={selectedConversationId}
        isLoading={isLoadingConversations}
        onSelectConversation={handleSelectConversation}
        onCreateConversation={handleCreateConversation}
        onUpdateConversationTitle={handleUpdateConversationTitle}
        onDeleteConversation={handleDeleteConversation}
        onLogout={handleLogout}
      />

      <main className="chat-page__main">
        <header className="chat-page__header">
          <div>
            <h1 className="chat-page__title">AI Knowledge Assistant</h1>
            <p className="chat-page__subtitle">
              Ask questions based on your uploaded documents.
            </p>
          </div>
        </header>

        {errorMessage && (
          <div className="chat-page__error">
            <span>{errorMessage}</span>
            <button
              type="button"
              className="chat-page__error-close"
              onClick={() => setErrorMessage("")}
            >
              ×
            </button>
          </div>
        )}

        <section className="chat-page__messages">
          {isLoadingMessages ? (
            <div className="chat-page__empty">
              <h2>메시지를 불러오는 중입니다.</h2>
              <p>잠시만 기다려주세요.</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="chat-page__empty">
              <h2>새 질문을 입력하세요.</h2>
              <p>
                업로드된 문서가 있다면 관련 chunk를 검색해 답변에 반영합니다.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                className={`chat-page__message-row chat-page__message-row--${message.role}`}
                key={`${message.role}-${message.id}-${index}`}
              >
                <div
                  className={`chat-page__message chat-page__message--${message.role}`}
                >
                  <div className="chat-page__message-role">
                    {message.role === "user" ? "You" : "Assistant"}
                  </div>

                  <div className="chat-page__message-content">
                    {message.content}
                  </div>

                  {message.role === "assistant" &&
                    message.sources &&
                    message.sources.length > 0 && (
                      <div className="chat-page__sources">
                        <div className="chat-page__sources-title">
                          Sources
                        </div>

                        {message.sources.map((source, sourceIndex) => (
                          <div
                            className="chat-page__source-item"
                            key={`${source.document_id}-${source.chunk_index}-${sourceIndex}`}
                          >
                            <div className="chat-page__source-filename">
                              {source.document_filename}
                            </div>

                            <div className="chat-page__source-meta">
                              Document ID: {source.document_id} · Chunk{" "}
                              {source.chunk_index}
                            </div>

                            <details className="chat-page__source-details">
                              <summary>View chunk</summary>
                              <p>{source.content}</p>
                            </details>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))
          )}

          {isSending && (
            <div className="chat-page__message-row chat-page__message-row--assistant">
              <div className="chat-page__message chat-page__message--assistant">
                <div className="chat-page__message-role">Assistant</div>

                <div className="chat-page__loading">
                  <span className="chat-page__loading-dot"></span>
                  <span className="chat-page__loading-dot"></span>
                  <span className="chat-page__loading-dot"></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </section>

        <footer className="chat-page__input-area">
          <textarea
            className="chat-page__input"
            value={inputMessage}
            placeholder="메시지를 입력하세요."
            rows={1}
            disabled={isSending}
            onChange={(event) => setInputMessage(event.target.value)}
            onKeyDown={handleInputKeyDown}
          />

          <button
            type="button"
            className="chat-page__send-button"
            disabled={!inputMessage.trim() || isSending}
            onClick={handleSendMessage}
          >
            {isSending ? "Sending..." : "Send"}
          </button>
        </footer>
      </main>
    </div>
  );
}

export default ChatPage;