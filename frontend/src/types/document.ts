export interface Document {
  id: number;
  user_id: number;
  original_filename: string;
  stored_filename: string;
  content_type: string | null;  // MIME Type
  created_at: string;
}

// 특정 문서의 Chunk 목록 응답 타입
export interface DocumentChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  created_at: string;
}

export interface DocumentUploadResponse {
  document: Document;
  chunk_count: number;
}

// 문서 삭제 성공 응답 타입
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