# main.py (TypeError 해결된 최종 버전)

import os
import json
import inspect
import importlib.util
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.tools.base import BaseTool

def get_tool_names_from_directory(path: str) -> list:
    """지정된 디렉토리에서 @register_tool로 등록된 도구의 'name' 목록을 찾아서 반환합니다."""
    tool_names = []
    if not os.path.exists(path):
        return []

    for filename in os.listdir(path):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            filepath = os.path.join(path, filename)
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BaseTool) and cls is not BaseTool:
                    if hasattr(cls, 'name'):
                        tool_names.append(cls.name)
    return tool_names

def setup_dynamic_agent():
    """동적 툴과 MCP 서버를 사용하는 에이전트 설정"""
    
    # 1. Python으로 만든 커스텀 도구 이름들을 가져옵니다.
    py_tool_names = []
    py_tool_names.extend(get_tool_names_from_directory('tools'))
    py_tool_names.extend(get_tool_names_from_directory('tool_hub'))
    py_tool_names.append('code_interpreter') # 내장 도구 추가
    
    # 2. function_list에 Python 도구 이름들을 먼저 추가합니다.
    #    (list로 변환하여 복사본을 만듭니다)
    final_tool_list = sorted(list(set(py_tool_names)))
    
    # 3. config.json에서 MCP 서버 설정을 로드하고, function_list에 추가합니다.
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            if 'mcpServers' in config_data:
                # MCP 서버 설정 전체(dict)를 리스트의 한 요소로 추가
                final_tool_list.append({'mcpServers': config_data['mcpServers']})
    
    print(f"INFO: 최종적으로 등록된 도구 및 MCP 서버 목록: {final_tool_list}")

    llm_config = {
        'model': 'qwen3:latest',
        'model_server': 'http://localhost:11434/v1',
        'api_key': 'ollama'
    }

    system_instruction = """너는 여러 도구를 사용할 수 있는 만능 어시스턴트야.
    - 너는 'playwright' 도구를 사용해서 웹 브라우저를 제어할 수 있어. 웹사이트에 접속하고, 정보를 읽고, 클릭하는 모든 작업이 가능해.
    - 그 외에도 주식 조회, 날씨 확인, 엑셀 분석 등 다양한 Python 도구를 사용할 수 있어.
    - 사용자의 요청을 해결하기 위해 어떤 도구가 필요한지 먼저 생각하고, 최적의 도구를 선택해서 작업을 수행해.
    - 모든 답변은 한국어로 해줘.
    """

    # mcp_servers 파라미터를 삭제하고, 모든 것을 function_list 하나로 전달합니다.
    bot = Assistant(
        llm=llm_config,
        system_message=system_instruction,
        function_list=final_tool_list
    )
    return bot

def main():
    bot = setup_dynamic_agent()
    WebUI(bot).run()

if __name__ == '__main__':
    main()