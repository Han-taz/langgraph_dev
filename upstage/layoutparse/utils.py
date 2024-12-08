from .state import ParseState
from .base import BaseNode
import pymupdf
import os


class SplitPDFFilesNode(BaseNode):

    def __init__(self, batch_size=10, test_page=None, **kwargs):
        super().__init__(**kwargs)
        self.name = "SplitPDFNode"
        self.batch_size = batch_size
        self.test_page = test_page

    def execute(self, state: ParseState) -> ParseState:
        """
        입력 PDF를 여러 개의 작은 PDF 파일로 분할합니다.

        :param state: GraphState 객체, PDF 파일 경로와 배치 크기 정보를 포함
        :return: 분할된 PDF 파일 경로 목록을 포함한 GraphState 객체
        """
        # PDF 파일 경로와 배치 크기 추출
        filepath = state["filepath"]

        # PDF 파일 열기
        input_pdf = pymupdf.open(filepath)
        num_pages = len(input_pdf)
        self.log(f"파일의 전체 페이지 수: {num_pages} Pages.")

        if self.test_page is not None:
            if self.test_page < num_pages:
                num_pages = self.test_page

        ret = []
        # PDF 분할 작업 시작
        for start_page in range(0, num_pages, self.batch_size):
            # 배치의 마지막 페이지 계산 (전체 페이지 수를 초과하지 않도록)
            end_page = min(start_page + self.batch_size, num_pages) - 1

            # 분할된 PDF 파일명 생성
            input_file_basename = os.path.splitext(filepath)[0]
            output_file = f"{input_file_basename}_{start_page:04d}_{end_page:04d}.pdf"
            self.log(f"분할 PDF 생성: {output_file}")

            # 새로운 PDF 파일 생성 및 페이지 삽입
            with pymupdf.open() as output_pdf:
                output_pdf.insert_pdf(input_pdf, from_page=start_page, to_page=end_page)
                output_pdf.save(output_file)
                ret.append(output_file)

        # 원본 PDF 파일 닫기
        input_pdf.close()

        # 분할된 PDF 파일 경로 목록을 포함한 GraphState 객체 반환
        return ParseState(split_filepaths=ret)