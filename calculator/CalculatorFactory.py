from calculator.AHPCalculator import AHPCalculator
from calculator.CrispAHPCalculator import CrispAHPCalculator


class CalculatorFactory:
    @staticmethod
    def create(method_type: str) -> AHPCalculator:
        if method_type == 'crisp':
            return CrispAHPCalculator()
