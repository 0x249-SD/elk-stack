import random
import string
import datetime
from typing import Any, Dict

class DataGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def generate_string(self, length: int = 10) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_integer(self, min_value: int = 0, max_value: int = 100) -> int:
        return random.randint(min_value, max_value)
    
    def generate_float(self, min_value: float = 0.0, max_value: float = 100.0) -> float:
        return round(random.uniform(min_value, max_value), 2)
    
    def generate_boolean(self) -> bool:
        return random.choice([True, False])
    
    def generate_date(self, start_year: int = 2000, end_year: int = 2030) -> str:
        start_date = datetime.date(start_year, 1, 1)
        end_date = datetime.date(end_year, 12, 31)
        random_days = random.randint(0, (end_date - start_date).days)
        return (start_date + datetime.timedelta(days=random_days)).isoformat()

    def generate_email(self):
        return f"{self.generate_string(8)}@{self.generate_string(6)}.com"
    
    def generate_list(self, item_type: str = "string", length: int = 5) -> list:
        generators = {
            "string": self.generate_string,
            "int": self.generate_integer,
            "float": self.generate_float,
            "bool": self.generate_boolean,
            "date": self.generate_date
        }
        return [generators[item_type]() for _ in range(length)]
    
    def generate_nested_object(self, depth: int = 1) -> Dict[str, Any]:
        if depth <= 0:
            return {"value": self.generate_string()}
        return {
            "name": self.generate_string(),
            "attributes": self.generate_nested_object(depth - 1)
        }
    
    def generate_random_data(self) -> Dict[str, Any]:
        return {
            "id": self.generate_string(8),
            "name": self.generate_string(12),
            "age": self.generate_integer(18, 65),
            "email": self.generate_email(),
            "score": self.generate_float(0.0, 100.0),
            "active": self.generate_boolean(),
            "created_at": self.generate_date(2010, 2025),
            "metadata": self.generate_nested_object(2)
        }

