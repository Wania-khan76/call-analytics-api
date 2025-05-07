
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List
import os

class Settings(BaseSettings):
    # Zong API Configuration
    vpbx_id: str
    zong_api_token: str
    zong_api_url: str = "https://cap.zong.com.pk:8444/vpbx-apis/customApi/vpbx-custom-apis"
    
    # ClickUp API Configuration (keeping uppercase to match existing code)
    CLICKUP_API_KEY: str
    CLICKUP_TEAM_ID: str
    SURVEY_DATE_FIELD_ID: str
    # CLICKUP_API_URL: str
    clickup_api_url: str
    
    # Optional fields with defaults
    CLICKUP_TOKEN: str = "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7"
    CLICKUP_SURVEY_FIELD_ID: str = "4f8bf712-7ef4-457a-93f9-ad0598b1fefc"
    CLICKUP_HOURS_FIELD_ID: str = "0336d5ec-41c1-4785-89b8-0b63bfaa9150"
    CLICK_UP_INTALLATION_LIST_ID: int = 901802111908
    CLICK_UP_INTALLED_LIST_ID: int = 901802098213
    CLICK_UP_FOLLOWUP_LIST_ID: int = 901802083406

    CLICK_UP_INSTALLED_LIST_ID: int = 901802098213
    CLICKUP_LIST_ID: str = "901802098213"
    INSTALLED_DATE_FIELD_ID: str
    AMOUNT_PAYABLE_FIELD_ID: str
    AMOUNT_RECEIVED_FIELD_ID: str   
    # Application Settings
    days_to_fetch: int = 30


    #B2B
    zong_base_url: str = Field(default="https://cap.zong.com.pk:8444/vpbx-apis/customApi/vpbx-custom-apis")
    zong_token: str
    zong_vpbx_id: str
    zong_default_days: int = Field(default=30)
    
    clickup_api_key: str
    clickup_list_ids: str = Field(default="901802083255,901802083578")  # Store as string
    
    @property
    def clickup_list_ids_list(self) -> List[str]:
        """Returns the list IDs as a proper Python list"""
        return [x.strip() for x in self.clickup_list_ids.split(',') if x.strip()]
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra variables in .env

settings = Settings()