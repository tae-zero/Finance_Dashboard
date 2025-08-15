import pandas as pd
import json
from typing import List, Dict, Any

class DataProcessor:
    @staticmethod
    def normalize_mongodb_data(cursor_data: List[Dict], field_mapping: Dict[str, str] = None):
        """MongoDB 데이터를 pandas DataFrame으로 정규화"""
        if not cursor_data:
            return pd.DataFrame()
        
        # 데이터 정규화
        df = pd.json_normalize(cursor_data)
        
        # 필드명 매핑이 있으면 적용
        if field_mapping:
            df = df.rename(columns=field_mapping)
        
        return df
    
    @staticmethod
    def convert_to_json_friendly(data: Any):
        """데이터를 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        elif isinstance(data, pd.Series):
            return data.to_dict()
        elif isinstance(data, (int, float)):
            return float(data) if pd.isna(data) else data
        elif isinstance(data, str):
            return data.strip() if data else ""
        else:
            return data
    
    @staticmethod
    def safe_numeric_conversion(value, default=0):
        """안전한 숫자 변환"""
        try:
            if pd.isna(value) or value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def format_currency(value, currency="KRW"):
        """통화 형식으로 포맷팅"""
        try:
            if pd.isna(value):
                return "0"
            
            num = float(value)
            if num >= 1e12:  # 1조 이상
                return f"{num/1e12:.1f}조"
            elif num >= 1e8:  # 1억 이상
                return f"{num/1e8:.1f}억"
            elif num >= 1e4:  # 1만 이상
                return f"{num/1e4:.1f}만"
            else:
                return f"{num:,.0f}"
        except:
            return str(value)
    
    @staticmethod
    def extract_top_rankings(df: pd.DataFrame, columns: List[str], top_n: int = 5):
        """상위 순위 데이터 추출"""
        result = {}
        
        for col in columns:
            if col in df.columns:
                # 숫자 변환
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
                # 상위 N개 추출
                top_data = df.nlargest(top_n, col)[["기업명", col]]
                result[f"{col}_TOP{top_n}"] = top_data.to_dict(orient="records")
        
        return result
