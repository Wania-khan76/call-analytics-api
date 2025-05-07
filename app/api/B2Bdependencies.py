

def get_comparator():
    return DataComparator()# app/dependencies.py
from app.services.B2Bzong import ZongService
from app.services.B2Bclickup import ClickUpService
from app.services.B2Bcomparator import DataComparator

def get_zong_service() -> ZongService:
    return ZongService()

def get_clickup_service() -> ClickUpService:
    return ClickUpService()

def get_comparator() -> DataComparator:
    return DataComparator()