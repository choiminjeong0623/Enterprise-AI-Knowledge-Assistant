export type DocumentStatus =
  | "UPLOADED"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED";


export interface Document {
  id: number;
  user_id: number;
  original_filename: string;
  stored_filename: string;
  content_type: string | null;

  chunk_count: number | null;

  status: DocumentStatus;
  error_message: string | null;
  processed_at: string | null;
  created_at: string;
}

// 새 업로드 API 응답은 문서(Document) 자체이다.
export type DocumentUploadResponse = Document;


export interface DocumentChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  created_at: string;
}


export interface DocumentDeleteResponse {
  message: string;
  document_id: number;
}


export interface DocumentSearchResult {
  id: number;
  document_id: number;
  document_filename: string;
  chunk_index: number;
  content: string;
  similarity: number;
  created_at: string;
}

export interface DocumentRetryResponse {
  message: string;
  document_id: number;
  status: DocumentStatus;
}