import json
from typing import Dict, List, Any
from core.base_tool import BaseTool


class SlideFormatterTool(BaseTool):
    """
    슬라이드 포맷팅 도구
    MCP Tool Protocol을 통해 JSON 또는 마크다운 슬라이드 포맷 생성
    """

    def __init__(self):
        self.slide_templates = {
            "basic": {"title": "", "bullets": [], "notes": ""},
            "detailed": {
                "title": "",
                "subtitle": "",
                "bullets": [],
                "sub_bullets": {},
                "conclusion": "",
                "notes": "",
            },
            "comparison": {
                "title": "",
                "left_column": {"title": "", "items": []},
                "right_column": {"title": "", "items": []},
                "notes": "",
            },
        }

    def _extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """텍스트에서 핵심 포인트 추출"""
        # 간단한 문장 분할 및 핵심 내용 추출
        sentences = content.split(".")
        key_points = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # 적절한 길이의 문장
                # 핵심 키워드가 포함된 문장 우선
                keywords = [
                    "정책",
                    "컴플라이언스",
                    "모니터링",
                    "보안",
                    "관리",
                    "거버넌스",
                    "클라우드",
                ]
                if any(keyword in sentence for keyword in keywords):
                    key_points.append(sentence)
                elif len(key_points) < max_points:
                    key_points.append(sentence)

        return key_points[:max_points]

    def _create_basic_slide(self, inputs: Dict) -> Dict:
        """기본 슬라이드 형식 생성"""
        content = inputs.get("content", "")
        title = inputs.get("title", "클라우드 거버넌스")

        bullets = self._extract_key_points(content)

        return {
            "title": title,
            "bullets": bullets,
            "notes": f"총 {len(bullets)}개의 핵심 포인트",
        }

    def _create_detailed_slide(self, inputs: Dict) -> Dict:
        """상세 슬라이드 형식 생성"""
        content = inputs.get("content", "")
        title = inputs.get("title", "클라우드 거버넌스 상세")
        subtitle = inputs.get("subtitle", "핵심 요소 및 구현 방안")

        bullets = self._extract_key_points(content, max_points=3)

        # 각 bullet에 대한 세부 사항 생성
        sub_bullets = {}
        for i, bullet in enumerate(bullets):
            sub_bullets[f"point_{i+1}"] = [
                f"{bullet}의 구현 방법",
                f"{bullet}의 모니터링",
                f"{bullet}의 최적화",
            ]

        return {
            "title": title,
            "subtitle": subtitle,
            "bullets": bullets,
            "sub_bullets": sub_bullets,
            "conclusion": "체계적인 클라우드 거버넌스 구현이 필요합니다.",
            "notes": "상세 내용은 각 포인트별로 구분하여 설명",
        }

    def _create_comparison_slide(self, inputs: Dict) -> Dict:
        """비교 슬라이드 형식 생성"""
        content = inputs.get("content", "")
        title = inputs.get("title", "클라우드 거버넌스 비교")

        # 간단한 before/after 또는 pros/cons 구조
        points = self._extract_key_points(content, max_points=6)
        mid_point = len(points) // 2

        return {
            "title": title,
            "left_column": {"title": "현재 상황", "items": points[:mid_point]},
            "right_column": {"title": "개선 방안", "items": points[mid_point:]},
            "notes": "현재 상황과 개선 방안의 비교",
        }

    def run(self, inputs: Dict) -> Dict:
        """
        MCP Tool Protocol을 통한 슬라이드 포맷팅 실행

        Args:
            inputs (Dict): {
                "content": str,
                "slide_type": str,  # "basic", "detailed", "comparison"
                "title": str,
                "format": str  # "json", "markdown"
            }

        Returns:
            Dict: {"slide": Dict, "markdown": str, "mcp_context": Dict}
        """
        slide_type = inputs.get("slide_type", "basic")
        format_type = inputs.get("format", "json")

        try:
            # 슬라이드 타입에 따른 생성
            if slide_type == "detailed":
                slide_data = self._create_detailed_slide(inputs)
            elif slide_type == "comparison":
                slide_data = self._create_comparison_slide(inputs)
            else:
                slide_data = self._create_basic_slide(inputs)

            # 마크다운 형식 생성
            markdown = self._convert_to_markdown(slide_data, slide_type)

            return {
                "slide": slide_data,
                "markdown": markdown,
                "mcp_context": {
                    "role": "formatter",
                    "status": "success",
                    "slide_type": slide_type,
                    "format": format_type,
                    "total_bullets": len(slide_data.get("bullets", [])),
                },
            }

        except Exception as e:
            return {
                "slide": {},
                "markdown": "",
                "mcp_context": {
                    "role": "formatter",
                    "status": "error",
                    "message": f"슬라이드 생성 중 오류: {str(e)}",
                },
            }

    def _convert_to_markdown(self, slide_data: Dict, slide_type: str) -> str:
        """슬라이드 데이터를 마크다운으로 변환"""
        markdown = f"# {slide_data.get('title', '제목 없음')}\n\n"

        if slide_type == "detailed" and slide_data.get("subtitle"):
            markdown += f"## {slide_data['subtitle']}\n\n"

        if slide_type == "comparison":
            markdown += f"## {slide_data['left_column']['title']}\n"
            for item in slide_data["left_column"]["items"]:
                markdown += f"- {item}\n"
            markdown += f"\n## {slide_data['right_column']['title']}\n"
            for item in slide_data["right_column"]["items"]:
                markdown += f"- {item}\n"
        else:
            markdown += "## 핵심 포인트\n"
            for bullet in slide_data.get("bullets", []):
                markdown += f"- {bullet}\n"

            if slide_type == "detailed" and slide_data.get("sub_bullets"):
                markdown += "\n## 세부 사항\n"
                for key, sub_items in slide_data["sub_bullets"].items():
                    for sub_item in sub_items:
                        markdown += f"  - {sub_item}\n"

            if slide_data.get("conclusion"):
                markdown += f"\n## 결론\n{slide_data['conclusion']}\n"

        if slide_data.get("notes"):
            markdown += f"\n---\n*{slide_data['notes']}*\n"

        return markdown
