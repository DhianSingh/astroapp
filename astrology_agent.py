from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.files import FileTools
from agno.models.groq import GroqModel

class AstrologyRAGAgent:
    def __init__(self, groq_api_key, knowledge_text=""):
        self.model = Groq(
            id="llama-3.3-70b-versatile",  # Or your preferred model
            api_key=groq_api_key
        )
        self.knowledge_text = knowledge_text
        self.agent = Agent(
            model=self.model,
            tools=[ReasoningTools(), DuckDuckGoTools()],
            description=(
                "You are an expert astrology assistant. "
                "if user wants query  for any other person you will ask for their date of birth,proffesion and relationship status"
                "Use the uploaded knowledge base and web search if needed. "
                "ask automatic questions to user to gather missing information"
                "Do NOT use function calls or tool calls in your answer. "
                "Just answer in plain text, markdown, or bullet points. "
                "Structure your answers in 3-6 clear, concise points or steps. "
                "If you don't have enough info, clearly state what is missing."
                "ask automatic questions to user to gather missing information"
            ),
            markdown=True,
            show_tool_calls=False  # Hide tool calls in output
        )

    def ask(self, prompt):
        context = f"Knowledge Base:\n{self.knowledge_text[:3000]}\n\n" if self.knowledge_text else ""
        full_prompt = f"""
        {context}
        {prompt}
        """
        return self.agent.run(full_prompt).content
