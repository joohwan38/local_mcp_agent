# tools/excel_tool.py
from qwen_agent.tools.base import BaseTool, register_tool
import pandas as pd
import openpyxl
from openpyxl.chart.reference import Reference
from openpyxl.chart.series import Series
from typing import List, Dict

@register_tool('excel_chart_inspector')
class ExcelChartInspector(BaseTool):
    """
    이 도구는 Excel 파일에서 차트 정보를 읽고, 해당 차트가 사용하는 데이터 범위를 추출합니다.
    """
    name = 'excel_chart_inspector'
    description = (
        '지정된 Excel 파일 경로와 시트 이름을 입력받아, 해당 시트의 모든 차트와 그 차트가 참조하는 데이터 범위를 텍스트로 반환합니다.'
    )
    parameters = [{
        'name': 'file_path',
        'type': 'string',
        'description': '분석할 Excel 파일의 경로',
        'required': True
    }, {
        'name': 'sheet_name',
        'type': 'string',
        'description': '차트가 있는 시트의 이름. 지정하지 않으면 첫 번째 시트를 사용합니다.',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            # 파라미터 파싱
            p = self._parse_params(params)
            file_path = p['file_path']
            sheet_name = p.get('sheet_name')

            # 워크북 로드
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            
            # 시트 선택
            if sheet_name:
                sheet = workbook[sheet_name]
            else:
                sheet = workbook.active
                sheet_name = sheet.title

            if not sheet._charts:
                return f"'{sheet_name}' 시트에서 차트를 찾을 수 없습니다."

            chart_infos = []
            for i, chart in enumerate(sheet._charts):
                chart_title = chart.title or f"차트 {i+1}"
                data_references = []
                
                # 차트 시리즈에서 데이터 범위 추출
                if hasattr(chart, 'series'):
                    for s in chart.series:
                        if s.val and s.val.numRef:
                            data_references.append(f"값(values): {s.val.numRef.f}")
                        if s.cat and s.cat.numRef:
                            data_references.append(f"카테고리(categories): {s.cat.numRef.f}")
                        elif s.cat and s.cat.strRef:
                             data_references.append(f"카테고리(categories): {s.cat.strRef.f}")

                info = f"차트 제목: '{chart_title}', 데이터 범위: [{', '.join(data_references)}]"
                chart_infos.append(info)

            if not chart_infos:
                return f"'{sheet_name}' 시트에서 차트는 발견되었지만, 데이터 범위를 추출할 수 없었습니다."

            return "\n".join(chart_infos)
        except Exception as e:
            return f"오류 발생: {str(e)}"