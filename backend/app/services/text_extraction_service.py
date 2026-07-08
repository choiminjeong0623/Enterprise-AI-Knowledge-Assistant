from pathlib import Path    ## 파일 경로나 확장자를 다룰 때 쓰는 파이썬 표준 라이브러이다.

from fastapi import (
    HTTPException,  ## API에서 에러 응답을 보낼 때 사용
    UploadFile  ## FastAPI에서 업로드 파일을 표현하는 타입
)
from pypdf import PdfReader ## PDF 파일을 읽기 위한 라이브러리다.

## 기 서비스는 업로드된 파일에서 텍스트를 추출하는 역할을 한다.
## 지원하는 파일 : .txt, .pdf
class TextExtractionService:
    ## 파일 정보를 보고 PDF인지 TXT인지 판단한 뒤, 알맞은 추출 함수를 호출한다.
    def extract_text(
        self,
        file: UploadFile,   ## FastAPI에서 받은 업로드 파일 객체
        file_path: str, ## 서버에 저장된 파일 경로
    ) -> str:
        ## 파일의 확장자를 구한다.
        suffix = Path(file.filename or "").suffix.lower()

        if suffix == ".txt":
            return self._extract_txt(file_path)

        if suffix == ".pdf":
            return self._extract_pdf(file_path)

        ## PDF나 TXT가 아니면 400에러를 반환한다.
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    ## TXT 파일을 읽어서 문자열로 반환한다.
    def _extract_txt(
        self,
        file_path: str,
    ) -> str:
        try:
            ## UTF-8 인코딩으로 파일을 읽는다.
            ## with open(...) as file: : 파일을 열고, 사용이 끝나면 자동으로 닫아주는 문법이다.
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()  ## 파일 전체 내용을 문자열로 읽는다.
        except UnicodeDecodeError:  ## UTF-8로 읽다가 인코딩 오류가 나면 에러를 발생시킨다.
            ## 한국어 Windows 환경에서 저장한 txt 파일은 cp949 인코딩일수 있어서 예외 처리를 둔다.
            with open(file_path, "r", encoding="cp949") as file:    ## UTF-8 실패 시 CP949로 다시 읽는다.
                return file.read()

    ## PDF 파일에서 텍스트를 추출한다.
    def _extract_pdf(
        self,
        file_path: str,
    ) -> str:
        reader = PdfReader(file_path)   ## PDF 파일을 읽는 객체를 만든다.
        texts = []

        for page in reader.pages:   ## PDF의 각 페이지를 반복한다.(1페이지, 2페이지, 3페이지... 순서대로 돌면서 처리한다.)
            page_text = page.extract_text() ## 현재 페이지에서 텍스트를 추출한다.

            if page_text:
                texts.append(page_text) ## 추출된 텍스트가 있으면 리스트에 추가한다.
                                        ## 스캔 PDF, 이미지 PDF는 extract_text()로 텍스트 추출이 잘 안 될 수 있다.

        return "\n\n".join(texts)   ## 페이지별 텍스트를 \n\n으로 이어붙인다.