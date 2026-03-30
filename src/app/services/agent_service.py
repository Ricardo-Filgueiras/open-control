from core.controller.agent_controller import AgentController

class AgentService:
    """Wrapper para desacoplar o Streamlit do Core."""
    
    def __init__(self):
        self.controller = AgentController()

    def process_message(self, message: str) -> str:
        return self.controller.handle_message(message)
