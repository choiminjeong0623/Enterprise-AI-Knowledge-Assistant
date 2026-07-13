import {
  useEffect,
  useRef,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import {
  deleteDocument,
  getDocuments,
  uploadDocument,
} from "../api/document";
import type {
  Document as DocumentItem,
  DocumentStatus,
} from "../types/document";
import { removeAccessToken } from "../utils/authStorage";

import "./DocumentPage.css";


const DOCUMENT_POLLING_INTERVAL_MS = 2000;


function DocumentPage() {
  const navigate = useNavigate();

  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [isUploading, setIsUploading] =
    useState(false);

  const [
    deletingDocumentId,
    setDeletingDocumentId,
  ] = useState<number | null>(null);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  // 문서 목록 중 하나라도 처리 중인지 확인
  const hasProcessingDocument =
    documents.some(
      (document) =>
        document.status === "UPLOADED" ||
        document.status === "PROCESSING"
    );


  useEffect(() => {
    loadDocuments();
  }, []);

  // Polling UseEffect
  useEffect(() => {
    if (!hasProcessingDocument) {
      return;
    }

    // 문서 처리 중에 2초마다 목록 API를 호출
    const pollingTimer = window.setInterval(
      async () => {
        await refreshDocumentsForPolling();
      },
      DOCUMENT_POLLING_INTERVAL_MS
    );

    return () => {
      window.clearInterval(pollingTimer);
    };
  }, [hasProcessingDocument]);


  const clearMessages = () => {
    setErrorMessage("");
    setSuccessMessage("");
  };


  const handleAuthError = (
    error: unknown
  ) => {
    const status =
      (
        error as {
          response?: {
            status?: number;
          };
        }
      )?.response?.status;

    if (
      status === 401 ||
      status === 403
    ) {
      removeAccessToken();
      navigate("/login");

      return true;
    }

    return false;
  };

  /**
   * 기존에 업로드한 Documents 목록을 조회한다.
   * @returns 
   */
  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setErrorMessage("");

      const data = await getDocuments();

      setDocuments(data);
    } catch (error) {
      if (handleAuthError(error)) {
        return;
      }

      setErrorMessage(
        "문서 목록을 불러오지 못했습니다."
      );
    } finally {
      setIsLoading(false);
    }
  };


  const refreshDocumentsForPolling =
    async () => {
      try {
        const data = await getDocuments();

        setDocuments(data);
      } catch (error) {
        if (handleAuthError(error)) {
          return;
        }

        console.error(
          "Failed to poll document status.",
          error
        );
      }
    };


  const handleFileChange = (
    event:
      React.ChangeEvent<HTMLInputElement>
  ) => {
    clearMessages();

    const file =
      event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const filename =
      file.name.toLowerCase();

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


  const handleUploadDocument =
    async () => {
      if (
        !selectedFile ||
        isUploading
      ) {
        return;
      }

      try {
        setIsUploading(true);
        clearMessages();
       
        // 수정 전 : response.document
        // 수정 후 : Document 객체
        const uploadedDocument =
          await uploadDocument(
            selectedFile
          );

        setDocuments(
          (previousDocuments) => [
            uploadedDocument,
            ...previousDocuments.filter(
              (document) =>
                document.id !==
                uploadedDocument.id
            ),
          ]
        );

        setSuccessMessage(
          `${uploadedDocument.original_filename} 업로드가 접수되었습니다.`
        );

        setSelectedFile(null);

        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } catch (error) {
        if (handleAuthError(error)) {
          return;
        }

        setErrorMessage(
          "문서 업로드에 실패했습니다."
        );
      } finally {
        setIsUploading(false);
      }
    };


  const handleDeleteDocument =
    async (
      documentId: number
    ) => {
      if (
        deletingDocumentId !== null
      ) {
        return;
      }

      const targetDocument =
        documents.find(
          (document) =>
            document.id === documentId
        );

      if (!targetDocument) {
        return;
      }

      const confirmed =
        window.confirm(
          `${targetDocument.original_filename} 문서를 삭제할까요?`
        );

      if (!confirmed) {
        return;
      }

      try {
        setDeletingDocumentId(
          documentId
        );

        clearMessages();

        await deleteDocument(
          documentId
        );

        setDocuments(
          (previousDocuments) =>
            previousDocuments.filter(
              (document) =>
                document.id !==
                documentId
            )
        );

        setSuccessMessage(
          `${targetDocument.original_filename} 문서가 삭제되었습니다.`
        );
      } catch (error) {
        if (handleAuthError(error)) {
          return;
        }

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


  const formatDateTime = (
    value: string | null
  ) => {
    if (!value) {
      return "-";
    }

    const date = new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return value;
    }

    return date.toLocaleString(
      "ko-KR"
    );
  };


  const formatFileSize = (
    size: number
  ) => {
    if (size < 1024) {
      return `${size} B`;
    }

    if (
      size < 1024 * 1024
    ) {
      return `${(
        size / 1024
      ).toFixed(1)} KB`;
    }

    return `${(
      size /
      (1024 * 1024)
    ).toFixed(1)} MB`;
  };


  const getStatusLabel = (
    status: DocumentStatus
  ) => {
    switch (status) {
      case "UPLOADED":
        return "업로드 완료";

      case "PROCESSING":
        return "처리 중";

      case "COMPLETED":
        return "처리 완료";

      case "FAILED":
        return "처리 실패";

      default:
        return status;
    }
  };


  const getStatusClassName = (
    status: DocumentStatus
  ) => {
    return (
      "document-page__status " +
      `document-page__status--${status.toLowerCase()}`
    );
  };


  const isDocumentProcessing = (
    status: DocumentStatus
  ) => {
    return (
      status === "UPLOADED" ||
      status === "PROCESSING"
    );
  };


  return (
    <div className="document-page">
      <header className="document-page__header">
        <div>
          <h1 className="document-page__title">
            Document Management
          </h1>

          <p className="document-page__subtitle">
            AI 답변에 사용할 PDF 또는 TXT
            문서를 관리합니다.
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
            <span>
              {errorMessage}
            </span>

            <button
              type="button"
              className="document-page__message-close"
              onClick={() =>
                setErrorMessage("")
              }
            >
              ×
            </button>
          </div>
        )}

        {successMessage && (
          <div className="document-page__message document-page__message--success">
            <span>
              {successMessage}
            </span>

            <button
              type="button"
              className="document-page__message-close"
              onClick={() =>
                setSuccessMessage("")
              }
            >
              ×
            </button>
          </div>
        )}

        <section className="document-page__upload-card">
          <div className="document-page__section-header">
            <div>
              <h2>
                Upload document
              </h2>

              <p>
                업로드 후 텍스트 추출,
                Chunking 및 Embedding 처리가
                백그라운드에서 실행됩니다.
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
              onChange={
                handleFileChange
              }
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
                      {
                        selectedFile.name
                      }
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
                  업로드할 PDF 또는 TXT
                  파일을 선택하세요.
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
              onClick={
                handleUploadDocument
              }
            >
              {isUploading
                ? "Uploading..."
                : "Upload"}
            </button>
          </div>

          {hasProcessingDocument && (
            <div className="document-page__processing">
              <div className="document-page__spinner" />

              <div>
                <strong>
                  문서를 처리하고 있습니다.
                </strong>

                <p>
                  처리 상태는 자동으로
                  갱신됩니다.
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="document-page__list-card">
          <div className="document-page__section-header">
            <div>
              <h2>
                Uploaded documents
              </h2>

              <p>
                현재 계정에 등록된
                문서입니다.
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
                문서 목록을 불러오는
                중입니다.
              </h3>
            </div>
          ) : documents.length === 0 ? (
            <div className="document-page__empty">
              <h3>
                업로드된 문서가 없습니다.
              </h3>

              <p>
                위의 파일 선택 영역에서 첫
                문서를 업로드하세요.
              </p>
            </div>
          ) : (
            <div className="document-page__document-list">
              {documents.map(
                (document) => (
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
                      <div className="document-page__document-title-row">
                        <h3>
                          {
                            document.original_filename
                          }
                        </h3>

                        <span
                          className={
                            getStatusClassName(
                              document.status
                            )
                          }
                        >
                          {isDocumentProcessing(
                            document.status
                          ) && (
                            <span className="document-page__status-dot" />
                          )}

                          {getStatusLabel(
                            document.status
                          )}
                        </span>
                      </div>

                      <div className="document-page__document-meta">
                        <span>
                          Document ID:{" "}
                          {document.id}
                        </span>

                        <span>
                          Chunks:{" "}
                          {
                            document.chunk_count
                          }
                        </span>

                        <span>
                          업로드:{" "}
                          {formatDateTime(
                            document.created_at
                          )}
                        </span>

                        {document.processed_at && (
                          <span>
                            처리 완료:{" "}
                            {formatDateTime(
                              document.processed_at
                            )}
                          </span>
                        )}
                      </div>

                      <div className="document-page__content-type">
                        {document.content_type ??
                          "Unknown content type"}
                      </div>

                      {document.status ===
                        "FAILED" &&
                        document.error_message && (
                          <div className="document-page__document-error">
                            {
                              document.error_message
                            }
                          </div>
                        )}
                    </div>

                    <button
                      type="button"
                      className="document-page__delete-button"
                      disabled={
                        deletingDocumentId !==
                        null
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
                )
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}


export default DocumentPage;