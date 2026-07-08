import { useState } from "react";
import type { Conversation } from "../../types/conversation";
import "./ConversationSidebar.css";

interface ConversationSidebarProps {
  conversations: Conversation[];
  selectedConversationId: number | null;
  isLoading: boolean;
  onSelectConversation: (conversationId: number) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (conversationId: number) => void;
  onUpdateConversationTitle: (
    conversationId: number,
    title: string
  ) => void;
  onLogout: () => void;
}

function ConversationSidebar({
  conversations,
  selectedConversationId,
  isLoading,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onUpdateConversationTitle,
  onLogout,
}: ConversationSidebarProps) {
  const [editingConversationId, setEditingConversationId] = useState<
    number | null
  >(null);
  const [editingTitle, setEditingTitle] = useState("");

  const startEdit = (conversation: Conversation) => {
    setEditingConversationId(conversation.id);
    setEditingTitle(conversation.title);
  };

  const cancelEdit = () => {
    setEditingConversationId(null);
    setEditingTitle("");
  };

  const submitEdit = (conversationId: number) => {
    const trimmedTitle = editingTitle.trim();

    if (!trimmedTitle) {
      cancelEdit();
      return;
    }

    onUpdateConversationTitle(conversationId, trimmedTitle);
    cancelEdit();
  };

  const handleDelete = (
    event: React.MouseEvent<HTMLButtonElement>,
    conversationId: number
  ) => {
    event.stopPropagation();
    onDeleteConversation(conversationId);
  };

  return (
    <aside className="conversation-sidebar">
      <div className="conversation-sidebar__header">
        <h2 className="conversation-sidebar__title">Conversations</h2>

        <button
          type="button"
          className="conversation-sidebar__new-button"
          onClick={onCreateConversation}
        >
          + New
        </button>
      </div>

      <div className="conversation-sidebar__list">
        {isLoading && (
          <p className="conversation-sidebar__status">Loading...</p>
        )}

        {!isLoading && conversations.length === 0 && (
          <p className="conversation-sidebar__empty">No conversations yet.</p>
        )}

        {!isLoading &&
          conversations.map((conversation) => {
            const isSelected = selectedConversationId === conversation.id;
            const isEditing = editingConversationId === conversation.id;

            return (
              <div
                key={conversation.id}
                className={
                  isSelected
                    ? "conversation-sidebar__item conversation-sidebar__item--selected"
                    : "conversation-sidebar__item"
                }
                onClick={() => onSelectConversation(conversation.id)}
              >
                {isEditing ? (
                  <input
                    className="conversation-sidebar__edit-input"
                    value={editingTitle}
                    autoFocus
                    onChange={(event) => setEditingTitle(event.target.value)}
                    onBlur={() => submitEdit(conversation.id)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        submitEdit(conversation.id);
                      }

                      if (event.key === "Escape") {
                        cancelEdit();
                      }
                    }}
                    onClick={(event) => event.stopPropagation()}
                  />
                ) : (
                  <button
                    type="button"
                    className="conversation-sidebar__name-button"
                    onDoubleClick={(event) => {
                      event.stopPropagation();
                      startEdit(conversation);
                    }}
                    title={conversation.title}
                  >
                    {conversation.title}
                  </button>
                )}

                <button
                  type="button"
                  className="conversation-sidebar__delete-button"
                  onClick={(event) => handleDelete(event, conversation.id)}
                >
                  ×
                </button>
              </div>
            );
          })}
      </div>

      <div className="conversation-sidebar__footer">
        <button
          type="button"
          className="conversation-sidebar__logout-button"
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </aside>
  );
}

export default ConversationSidebar;