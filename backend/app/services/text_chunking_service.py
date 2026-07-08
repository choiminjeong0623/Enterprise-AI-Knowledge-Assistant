## 긴 문서를 작은 조각(Chunk)으로 나누는 역할을 한다.
## 전체 문서 텍스트
## → chunk 0
## → chunk 1
## → chunk 2
## → chunk 3
class TextChunkingService:
    ## text를 받아서 list[str], 즉 문자열 리스트로 반환한다.
    def split_text(
        self,
        text: str,              ## 분할할 전체 문서 텍스트
        chunk_size: int = 800,  ## chunk 하나의 최대 길이. 기본값 800자
        overlap: int = 100,     ## 이전 chunk와 다음 chunk가 겹치는 길이. 기본값 100자.
                                ## 다음 chunk가 이전 chunk의 끝부분을 조금 포함하게 한다.
                                ## chunk1 : a는 b이다. b는 c...
                                ## chunk2 : b는 c이다. 따라서, a는 c이다.
    ) -> list[str]:
        cleaned_text = text.strip()     ## 문자열 앞뒤 공백, 줄바꿈을 제거한다.

        if not cleaned_text:
            return []

        chunks = [] ## 나눠진 chunk들을 저장할 리스트
        start = 0   ## 문자열을 어디서부터 자를지 나타내는 시작 위치다.(파이썬 문자열 인덱스는 0부터 시작한다.)
        text_length = len(cleaned_text)

        while start < text_length:  ## start가 전체 텍스트 길이보다 작을 동안 반복
            end = start + chunk_size    ## chunk의 끝 위치를 지정한다.
            
            chunk = cleaned_text[start:end].strip() ## start부터 end전(!)까지 텍스트를 자른다.

            if chunk:
                chunks.append(chunk)

            start = end - overlap   ## 다음 chunk의 시작점을 정한다.

            if start < 0:   ## start가 음수가 되면 0으로 보장한다.
                start = 0

            if start >= text_length:    ## 다음 시작 위치가 이미 텍스트 끝을 넘어가면 종료한다.
                break

        return chunks