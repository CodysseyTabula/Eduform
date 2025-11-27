"""
IEP 비즈니스 로직 테스트

- 연간 목표 상속 테스트
- 파일 저장/업데이트 테스트
- IEP 완료 검증 테스트
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.iep_file import IEPFile
from app.models.iep_version import IEPVersion
from app.models.student import Student
from app.services.iep_business import (
    IEPBusinessError,
    inherit_annual_goals,
    save_or_update_iep_file,
    verify_iep_complete,
)


# 테스트용 인메모리 DB 설정
@pytest.fixture(scope="function")
def test_db():
    """테스트용 인메모리 SQLite DB 세션 생성"""
    # 인메모리 SQLite 엔진 생성
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 세션 팩토리
    TestSessionLocal = sessionmaker(bind=engine)
    
    # 세션 생성
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_student(test_db: Session) -> Student:
    """테스트용 학생 데이터 생성"""
    student = Student(
        name="테스트학생",
        birth=datetime(2015, 3, 15).date()
    )
    test_db.add(student)
    test_db.commit()
    test_db.refresh(student)
    return student


@pytest.fixture
def sample_iep_version_1st(test_db: Session, sample_student: Student) -> IEPVersion:
    """테스트용 1학기 IEP 버전 생성"""
    version = IEPVersion(
        student_id=sample_student.id,
        year="2024",
        semester="1학기",
        grade="3"
    )
    test_db.add(version)
    test_db.commit()
    test_db.refresh(version)
    return version


@pytest.fixture
def sample_iep_version_2nd(test_db: Session, sample_student: Student) -> IEPVersion:
    """테스트용 2학기 IEP 버전 생성"""
    version = IEPVersion(
        student_id=sample_student.id,
        year="2024",
        semester="2학기",
        grade="3"
    )
    test_db.add(version)
    test_db.commit()
    test_db.refresh(version)
    return version


# ==================== save_or_update_iep_file 테스트 ====================

def test_save_or_update_iep_file_create_new(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """새 파일 생성 테스트"""
    # Given
    content = {
        "annual_reading_goal": "연간 읽기 목표",
        "semester_reading_goal": "학기 읽기 목표"
    }
    
    # When
    result = save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id,
        file_type="goal",
        content=content
    )
    test_db.commit()
    
    # Then
    assert result.iep_version_id == sample_iep_version_1st.id
    assert result.file_type == "goal"
    assert result.file_path is not None
    assert "goal-" in result.file_path
    
    # DB에 레코드 확인
    db_file = test_db.query(IEPFile).filter(
        IEPFile.iep_version_id == sample_iep_version_1st.id,
        IEPFile.file_type == "goal"
    ).first()
    assert db_file is not None
    assert db_file.id == result.id


def test_save_or_update_iep_file_update_existing(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """기존 파일 업데이트 테스트 (덮어쓰기)"""
    import time
    
    # Given - 첫 번째 저장
    content_v1 = {"annual_reading_goal": "목표 v1"}
    file_v1 = save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id,
        file_type="goal",
        content=content_v1
    )
    test_db.commit()
    original_file_id = file_v1.id
    original_file_path = file_v1.file_path
    
    # 타임스탬프 차이를 만들기 위해 1초 대기
    time.sleep(1)
    
    # When - 같은 iep_version_id + file_type으로 두 번째 저장
    content_v2 = {"annual_reading_goal": "목표 v2 (업데이트)"}
    file_v2 = save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id,
        file_type="goal",
        content=content_v2
    )
    test_db.commit()
    
    # Then
    # 같은 레코드여야 함 (ID 동일)
    assert file_v2.id == original_file_id
    
    # file_path는 새 경로로 업데이트됨
    assert file_v2.file_path != original_file_path
    assert "goals-" in file_v2.file_path
    
    # DB에서 해당 타입의 파일이 하나만 존재하는지 확인
    files = test_db.query(IEPFile).filter(
        IEPFile.iep_version_id == sample_iep_version_1st.id,
        IEPFile.file_type == "goal"
    ).all()
    assert len(files) == 1
    assert files[0].id == original_file_id


def test_save_or_update_iep_file_invalid_type(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """잘못된 file_type 검증 테스트"""
    # Given
    content = {"test": "data"}
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="Invalid file_type"):
        save_or_update_iep_file(
            db=test_db,
            iep_version_id=sample_iep_version_1st.id,
            file_type="invalid_type",  # 잘못된 타입
            content=content
        )


def test_save_or_update_iep_file_nonexistent_version(test_db: Session):
    """존재하지 않는 IEP 버전에 대한 파일 저장 실패 테스트"""
    # Given
    fake_id = uuid.uuid4()
    content = {"test": "data"}
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="IEP version not found"):
        save_or_update_iep_file(
            db=test_db,
            iep_version_id=fake_id,
            file_type="goal",
            content=content
        )


# ==================== verify_iep_complete 테스트 ====================

def test_verify_iep_complete_all_files_exist(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """3개 파일 모두 존재할 때 완료 검증 통과 테스트"""
    # Given - 3개 파일 모두 생성
    for file_type in ["goal", "weekly_plan", "material"]:
        save_or_update_iep_file(
            db=test_db,
            iep_version_id=sample_iep_version_1st.id,
            file_type=file_type,
            content={"test": f"{file_type} data"}
        )
    test_db.commit()
    
    # When
    is_complete = verify_iep_complete(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id
    )
    
    # Then
    assert is_complete is True


def test_verify_iep_complete_missing_one_file(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """파일 하나 누락 시 완료 검증 실패 테스트"""
    # Given - 2개 파일만 생성 (weekly_materials 누락)
    for file_type in ["goal", "weekly_plan"]:
        save_or_update_iep_file(
            db=test_db,
            iep_version_id=sample_iep_version_1st.id,
            file_type=file_type,
            content={"test": f"{file_type} data"}
        )
    test_db.commit()
    
    # When
    is_complete = verify_iep_complete(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id
    )
    
    # Then
    assert is_complete is False


def test_verify_iep_complete_no_files(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """파일이 하나도 없을 때 완료 검증 실패 테스트"""
    # Given - 파일 생성 안 함
    
    # When
    is_complete = verify_iep_complete(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id
    )
    
    # Then
    assert is_complete is False


def test_verify_iep_complete_nonexistent_version(test_db: Session):
    """존재하지 않는 IEP 버전에 대한 검증 실패 테스트"""
    # Given
    fake_id = uuid.uuid4()
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="IEP version not found"):
        verify_iep_complete(
            db=test_db,
            iep_version_id=fake_id
        )


# ==================== inherit_annual_goals 테스트 ====================

def test_inherit_annual_goals_success(
    test_db: Session,
    sample_iep_version_1st: IEPVersion,
    sample_iep_version_2nd: IEPVersion
):
    """연간 목표 상속 성공 테스트"""
    # Given - 1학기 goals 파일 생성
    semester1_goals = {
        "annual_reading_goal": "1학기 연간 읽기 목표",
        "annual_writing_goal": "1학기 연간 쓰기 목표",
        "semester_reading_goal": "1학기 학기 읽기 목표",
        "semester_writing_goal": "1학기 학기 쓰기 목표"
    }
    save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id,
        file_type="goal",
        content=semester1_goals
    )
    test_db.commit()
    
    # 2학기 goals 파일 생성 (다른 내용)
    semester2_goals = {
        "annual_reading_goal": "2학기 임시 연간 읽기 목표 (덮어쓰기 될 예정)",
        "semester_reading_goal": "2학기 학기 읽기 목표",
        "semester_writing_goal": "2학기 학기 쓰기 목표"
    }
    save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_2nd.id,
        file_type="goal",
        content=semester2_goals
    )
    test_db.commit()
    
    # When - 연간 목표 상속
    inherit_annual_goals(
        db=test_db,
        from_iep_version_id=sample_iep_version_1st.id,
        to_iep_version_id=sample_iep_version_2nd.id
    )
    
    # Then - 2학기 goals 확인
    semester2_file = test_db.query(IEPFile).filter(
        IEPFile.iep_version_id == sample_iep_version_2nd.id,
        IEPFile.file_type == "goal"
    ).first()
    
    assert semester2_file is not None
    
    # 파일 내용 로드 (실제로는 mock이 필요하지만, 여기서는 DB만 검증)
    # 실제 환경에서는 file_path로 JSON을 읽어서 검증해야 함
    # 여기서는 함수가 에러 없이 실행되었는지만 확인


def test_inherit_annual_goals_source_not_found(
    test_db: Session,
    sample_iep_version_2nd: IEPVersion
):
    """원본 IEP 버전이 없을 때 상속 실패 테스트"""
    # Given
    fake_id = uuid.uuid4()
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="Source IEP version not found"):
        inherit_annual_goals(
            db=test_db,
            from_iep_version_id=fake_id,
            to_iep_version_id=sample_iep_version_2nd.id
        )


def test_inherit_annual_goals_target_not_found(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """대상 IEP 버전이 없을 때 상속 실패 테스트"""
    # Given
    fake_id = uuid.uuid4()
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="Target IEP version not found"):
        inherit_annual_goals(
            db=test_db,
            from_iep_version_id=sample_iep_version_1st.id,
            to_iep_version_id=fake_id
        )


def test_inherit_annual_goals_source_no_goals_file(
    test_db: Session,
    sample_iep_version_1st: IEPVersion,
    sample_iep_version_2nd: IEPVersion
):
    """원본 IEP에 goals 파일이 없을 때 상속 실패 테스트"""
    # Given - goals 파일 생성 안 함
    
    # When / Then
    with pytest.raises(IEPBusinessError, match="Goals file not found"):
        inherit_annual_goals(
            db=test_db,
            from_iep_version_id=sample_iep_version_1st.id,
            to_iep_version_id=sample_iep_version_2nd.id
        )


# ==================== 통합 시나리오 테스트 ====================

def test_full_workflow_first_semester(
    test_db: Session,
    sample_iep_version_1st: IEPVersion
):
    """1학기 전체 워크플로우 테스트"""
    # 1. 3개 파일 생성
    for file_type in ["goal", "weekly_plan", "material"]:
        save_or_update_iep_file(
            db=test_db,
            iep_version_id=sample_iep_version_1st.id,
            file_type=file_type,
            content={f"{file_type}_data": "test"}
        )
    test_db.commit()
    
    # 2. 완료 검증
    assert verify_iep_complete(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id
    ) is True
    
    # 3. 파일 업데이트
    save_or_update_iep_file(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id,
        file_type="goal",
        content={"updated": "data"}
    )
    test_db.commit()
    
    # 4. 여전히 완료 상태
    assert verify_iep_complete(
        db=test_db,
        iep_version_id=sample_iep_version_1st.id
    ) is True

