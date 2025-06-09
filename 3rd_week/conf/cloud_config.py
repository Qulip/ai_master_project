import os
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from pydantic_settings import BaseSettings


class GoogleCloudConfig(BaseSettings):
    """Google Cloud 설정"""

    project_id: str = "your-project-id"
    topic_prefix: str = "agent-communication"
    region: str = "asia-northeast3"  # 서울 리전

    class Config:
        env_prefix = "GCP_"
        env_file = ".env"


def get_credentials():
    """Google Cloud 인증 정보 가져오기"""
    try:
        credentials, project = default()
        return credentials, project
    except DefaultCredentialsError:
        print("Google Cloud 인증 정보를 찾을 수 없습니다.")
        print("다음 방법 중 하나를 사용하여 인증하세요:")
        print("1. gcloud auth application-default login")
        print("2. GOOGLE_APPLICATION_CREDENTIALS 환경변수 설정")
        print("3. 서비스 계정 키 파일 경로 설정")
        raise


def validate_cloud_setup():
    """Cloud 설정 검증"""
    try:
        credentials, project = get_credentials()
        print(f"Google Cloud 프로젝트: {project}")
        return True
    except Exception as e:
        print(f"Google Cloud 설정 오류: {e}")
        return False


# 전역 설정 인스턴스
cloud_config = GoogleCloudConfig()
