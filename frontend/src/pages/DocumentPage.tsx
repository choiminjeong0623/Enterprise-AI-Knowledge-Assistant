import {
  useEffect,
  useRef,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import {
  deleteDocument,
  getDocumentChunks,
  getDocuments,
  uploadDocument,
} from "../api/document";
import type {
  Document as DocumentItem,
} from "../types/document";
import { removeAccessToken } from "../utils/authStorage";

import "./DocumentPage.css";


interface DocumentChunkCountMap {
  [documentId: number]: number;
}


function DocumentPage() {
  const navigate = useNavigate();

  const fileInputRef = useRef<HTMLInputElement | null>(
    null
  );

  const [documents, setDocuments] = useState<DocumentItem[]>(
    []
  );

  const [chunkCounts, setChunkCounts] =
    useState<DocumentChunkCountMap>({});

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [deletingDocumentId, setDeletingDocumentId] =
    useState<number | null>(null);

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");


  useEffect(() => {
    loadDocuments();
  }, []);


  const clearMessages = () => {
    setErrorMessage("");
    setSuccessMessage("");
  };


  const loadChunkCounts = async (
    documentList: DocumentItem[]
  ) => {
    const nextChunkCounts: DocumentChunkCountMap = {};

    await Promise.all(
      documentList.map(async (document) => {
        try {
          const chunks = await getDocumentChunks(
            document.id
          );

          nextChunkCounts[document.id] =
            chunks.length;
        } catch {
          nextChunkCounts[document.id] = 0;
        }
      })
    );

    setChunkCounts(nextChunkCounts);
  };

  // 문서 목록 조회
  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setErrorMessage("");

      const data = await getDocuments();

      setDocuments(data);

      await loadChunkCounts(data);
    } catch {
      setErrorMessage(
        "문서 목록을 불러오지 못했습니다."
      );
    } finally {
      setIsLoading(false);
    }
  };


  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    clearMessages();

    const file = event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const filename = file.name.toLowerCase();

    const isSupportedFile =
      filename.endsWith(".pdf") ||
      filename.endsWith(".txt");

    if (!isSupportedFile) {
      setSelectedFile(null);

      setErrorMessage(
        "PDF 또는 TXT 파일만 업로드할 수 있습니다."
      );

      event.target.value = "";

      return;
    }

    setSelectedFile(file);
  };

  // 문서 Upload
  const handleUploadDocument = async () => {
    if (!selectedFile || isUploading) {
      return;
    }

    try {
      setIsUploading(true);
      clearMessages();

      const response = await uploadDocument(
        selectedFile
      );

      setDocuments((previousDocuments) => [
        response.document,
        ...previousDocuments,
      ]);

      setChunkCounts((previousChunkCounts) => ({
        ...previousChunkCounts,
        [response.document.id]:
          response.chunk_count,
      }));

      setSuccessMessage(
        `${response.document.original_filename} 업로드가 완료되었습니다.`
      );

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch {
      setErrorMessage(
        "문서 업로드에 실패했습니다."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // 문서 삭제
  const handleDeleteDocument = async (
    documentId: number
  ) => {
    if (deletingDocumentId !== null) {
      return;
    }

    const targetDocument = documents.find(
      (document) => document.id === documentId
    );

    if (!targetDocument) {
      return;
    }

    const confirmed = window.confirm(
      `${targetDocument.original_filename} 문서를 삭제할까요?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingDocumentId(documentId);
      clearMessages();

      await deleteDocument(documentId);

      setDocuments((previousDocuments) =>
        previousDocuments.filter(
          (document) =>
            document.id !== documentId
        )
      );

      setChunkCounts((previousChunkCounts) => {
        const nextChunkCounts = {
          ...previousChunkCounts,
        };

        delete nextChunkCounts[documentId];

        return nextChunkCounts;
      });

      setSuccessMessage(
        `${targetDocument.original_filename} 문서가 삭제되었습니다.`
      );
    } catch {
      setErrorMessage(
        "문서를 삭제하지 못했습니다."
      );
    } finally {
      setDeletingDocumentId(null);
    }
  };


  const handleMoveToChat = () => {
    navigate("/chat");
  };


  const handleLogout = () => {
    removeAccessToken();
    navigate("/login");
  };


  const formatCreatedAt = (
    createdAt: string
  ) => {
    const date = new Date(createdAt);

    if (Number.isNaN(date.getTime())) {
      return createdAt;
    }

    return date.toLocaleString("ko-KR");
  };


  const formatFileSize = (
    size: number
  ) => {
    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${(
      size /
      (1024 * 1024)
    ).toFixed(1)} MB`;
  };


  return (
    <div className="document-page">
      <header className="document-page__header">
        <div>
          <h1 className="document-page__title">
            Document Management
          </h1>

          <p className="document-page__subtitle">
            AI 답변에 사용할 PDF 또는 TXT 문서를
            관리합니다.
          </p>
        </div>

        <div className="document-page__header-actions">
          <button
            type="button"
            className="document-page__chat-button"
            onClick={handleMoveToChat}
          >
            Chat
          </button>

          <button
            type="button"
            className="document-page__logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="document-page__main">
        {errorMessage && (
          <div className="document-page__message document-page__message--error">
            <span>{errorMessage}</span>

            <button
              type="button"
              className="document-page__message-close"
              onClick={() => setErrorMessage("")}
            >
              ×
            </button>
          </div>
        )}

        {successMessage && (
          <div className="document-page__message document-page__message--success">
            <span>{successMessage}</span>

            <button
              type="button"
              className="document-page__message-close"
              onClick={() => setSuccessMessage("")}
            >
              ×
            </button>
          </div>
        )}

        <section className="document-page__upload-card">
          <div className="document-page__section-header">
            <div>
              <h2>Upload document</h2>

              <p>
                업로드된 문서는 텍스트 추출,
                Chunking, Embedding 과정을 거칩니다.
              </p>
            </div>
          </div>

          <div className="document-page__upload-area">
            <input
              ref={fileInputRef}
              type="file"
              className="document-page__file-input"
              accept=".pdf,.txt,application/pdf,text/plain"
              disabled={isUploading}
              onChange={handleFileChange}
            />

            <div className="document-page__selected-file">
              {selectedFile ? (
                <>
                  <div className="document-page__file-icon">
                    {selectedFile.name
                      .toLowerCase()
                      .endsWith(".pdf")
                      ? "PDF"
                      : "TXT"}
                  </div>

                  <div className="document-page__file-info">
                    <strong>
                      {selectedFile.name}
                    </strong>

                    <span>
                      {formatFileSize(
                        selectedFile.size
                      )}
                    </span>
                  </div>
                </>
              ) : (
                <div className="document-page__file-placeholder">
                  업로드할 PDF 또는 TXT 파일을
                  선택하세요.
                </div>
              )}
            </div>

            <button
              type="button"
              className="document-page__upload-button"
              disabled={
                !selectedFile ||
                isUploading
              }
              onClick={handleUploadDocument}
            >
              {isUploading
                ? "Processing..."
                : "Upload"}
            </button>
          </div>

          {isUploading && (
            <div className="document-page__processing">
              <div className="document-page__spinner" />

              <div>
                <strong>
                  문서를 처리하고 있습니다.
                </strong>

                <p>
                  텍스트 추출과 Embedding 생성으로
                  시간이 걸릴 수 있습니다.
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="document-page__list-card">
          <div className="document-page__section-header">
            <div>
              <h2>Uploaded documents</h2>

              <p>
                현재 계정에 등록된 문서입니다.
              </p>
            </div>

            <button
              type="button"
              className="document-page__refresh-button"
              disabled={isLoading}
              onClick={loadDocuments}
            >
              {isLoading
                ? "Loading..."
                : "Refresh"}
            </button>
          </div>

          {isLoading ? (
            <div className="document-page__empty">
              <div className="document-page__spinner" />

              <h3>
                문서 목록을 불러오는 중입니다.
              </h3>
            </div>
          ) : documents.length === 0 ? (
            <div className="document-page__empty">
              <h3>
                업로드된 문서가 없습니다.
              </h3>

              <p>
                위의 파일 선택 영역에서 첫 문서를
                업로드하세요.
              </p>
            </div>
          ) : (
            <div className="document-page__document-list">
              {documents.map((document) => (
                <article
                  className="document-page__document-item"
                  key={document.id}
                >
                  <div className="document-page__document-icon">
                    {document.original_filename
                      .toLowerCase()
                      .endsWith(".pdf")
                      ? "PDF"
                      : "TXT"}
                  </div>

                  <div className="document-page__document-content">
                    <h3>
                      {document.original_filename}
                    </h3>

                    <div className="document-page__document-meta">
                      <span>
                        Document ID: {document.id}
                      </span>

                      <span>
                        Chunks:{" "}
                        {chunkCounts[document.id] ??
                          0}
                      </span>

                      <span>
                        {formatCreatedAt(
                          document.created_at
                        )}
                      </span>
                    </div>

                    <div className="document-page__content-type">
                      {document.content_type ??
                        "Unknown content type"}
                    </div>
                  </div>

                  <button
                    type="button"
                    className="document-page__delete-button"
                    disabled={
                      deletingDocumentId !== null
                    }
                    onClick={() =>
                      handleDeleteDocument(
                        document.id
                      )
                    }
                  >
                    {deletingDocumentId ===
                    document.id
                      ? "Deleting..."
                      : "Delete"}
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}


export default DocumentPage;