from abc import abstractmethod


class PromptGenerator:
    basic_prompt: str

    def get_basic_prompt(self):
        return self.basic_prompt

    @abstractmethod
    def get_criteria_prompt(self, crit1, crit2):
        pass

    @abstractmethod
    def get_alternative_prompt(self, alt1, alt2, crit):
        pass
