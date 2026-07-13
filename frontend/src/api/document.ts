import client from "./client";

import type {
  Document,
  DocumentChunk,
  DocumentDeleteResponse,
  DocumentSearchResult,
  DocumentUploadResponse,
  DocumentRetryResponse,
} from "../types/document";

// 현재 로그인한 사용자의 문서 목록을 가져온다.
export const getDocuments = async (): Promise<Document[]> => {
  const response = await client.get<Document[]>("/documents");

  return response.data;
};

// 브라우저에서 선택한 파일을 Backend로 업로드한다.
export const uploadDocument = async (
  file: File
): Promise<DocumentUploadResponse> => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await client.post<DocumentUploadResponse>(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

// 특정 문서의 Chunk 목록 조회
export const getDocumentChunks = async (
  documentId: number
): Promise<DocumentChunk[]> => {
  const response = await client.get<DocumentChunk[]>(
    `/documents/${documentId}/chunks`
  );

  return response.data;
};

// 문서 Vector Search API를 호출한다.
export const searchDocumentChunks = async (
  query: string,
  limit: number = 5
): Promise<DocumentSearchResult[]> => {
  const response = await client.get<DocumentSearchResult[]>(
    "/documents/search",
    {
      params: {
        query,
        limit,
      },
    }
  );

  return response.data;
};

// 특정 문서의 목록을 삭제한다.
export const deleteDocument = async (
  documentId: number
): Promise<DocumentDeleteResponse> => {
  const response = await client.delete<DocumentDeleteResponse>(
    `/documents/${documentId}`
  );

  return response.data;
};

export const retryDocument = async (
  documentId: number
): Promise<DocumentRetryResponse> => {
  const response =
    await client.post<DocumentRetryResponse>(
      `/documents/${documentId}/retry`
    );

  return response.data;
};