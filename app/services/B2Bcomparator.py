from typing import List, Dict, Optional
from app.models.schemas import ClickUpTask, ZongCallRecord, MatchedResult

class DataComparator:
    @staticmethod
    def normalize_phone_number(phone: Optional[str]) -> Optional[str]:
        if not phone:
            return None
        digits = ''.join(filter(str.isdigit, phone))
        if digits.startswith("92"):
            digits = digits[2:]
        if digits.startswith("0"):
            digits = digits[1:]
        return digits

    @staticmethod
    def extract_primary_phone(zong_record: ZongCallRecord) -> Optional[str]:
        return (
            zong_record.customer_number
            or zong_record.master_number
            or zong_record.callerId
            or zong_record.caller_id
            or zong_record.callerID
            or zong_record.sourceNumber
            or zong_record.source
        )

    @staticmethod
    def extract_phone_from_task(task: ClickUpTask) -> Optional[str]:
        if not task.custom_fields:
            return None
        for field in task.custom_fields:
            name = field.get("name", "").lower()
            if name in ["phone", "primary phone", "mobile", "contact number", "phone number"]:
                return str(field.get("value"))
        return None

    def compare_data(self, zong_data: List[ZongCallRecord], clickup_tasks: List[ClickUpTask]) -> List[MatchedResult]:
        phone_to_task = {}
        for task in clickup_tasks:
            phone = self.extract_phone_from_task(task)
            normalized = self.normalize_phone_number(phone)
            if normalized:
                phone_to_task[normalized] = task

        results = []
        matched_phones = set()

        for record in zong_data:
            phone = self.extract_primary_phone(record)
            normalized = self.normalize_phone_number(phone)
            if normalized and normalized in phone_to_task and normalized not in matched_phones:
                task = phone_to_task[normalized]
                results.append(MatchedResult(
                    task_id=task.id,
                    task_name=task.name,
                    task_url=task.url,
                    phone=phone,
                    zong_call=record
                ))
                matched_phones.add(normalized)
        return results