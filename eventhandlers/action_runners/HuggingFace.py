from .ActionRunner import ActionRunner

class HuggingFaceZeroShotClassificationAction(ActionRunner):
    def execute_pre_conditions(self, session) -> bool:
        print("Executed pre conditions")
        return True

    def execute_action(self, session) -> bool:
        print("Executing action")
        return True