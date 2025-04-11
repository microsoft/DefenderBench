#!/usr/bin/env python
import re
from .base_agent import BaseAgent
from src.utils.llm_api import LLM

class ReActAgent(BaseAgent):
    """
    A ReAct agent using chain-of-thought reasoning.


    The agent composes a prompt that includes the current environment context (instructions,  
    history, last action, and observation). It uses a system prompt to instruct the model to output  
    its reasoning step by step (with each thought prefixed by "Thought:") and expects a final decision  
    indicated by a line starting with "Action:".  

    If no "Action:" is found, the agent will prompt further clarification for a few iterations.  
    """  
    def __init__(self, model: LLM, max_iter: int = 3):  
        super().__init__()
        self.model = model  
        self.max_iter = max_iter  
        self.system_prompt = (  
            "You are a cybersecurity assistant that uses the ReAct framework to decide on actions. "  
            "First, reason step by step by writing your thinking process (each step should begin with 'Thought:'). "  
            "Once you are confident, output your final decision on a new line starting with 'Action:' "  
            "followed by only that final actionable decision."
        )

    def act(self, obs, info):
        # Save the base context from the environment.
        base_context = (
        f"Instructions: {info.get('instructions', '')}\n"
        f"History: {info.get('history', '')}\n"
        f"Last Action: {info.get('last_action', '')}\n"
        f"Observation: {obs}"
        )
        # Initialize an empty string to accumulate the chain-of-thought.
        chain_of_thought = ""


        # Iterate up to max_iter times.  
        for i in range(self.max_iter):  
            # Build the full prompt for this iteration that includes both the base context and any previous reasoning.  
            prompt = base_context  
            if chain_of_thought:  
                prompt += "\n\n" + chain_of_thought  
            
            # Prepare the conversation messages: always start with the full context.  
            messages = [  
                {"role": "system", "content": self.system_prompt},  
                {"role": "user", "content": prompt}  
            ]  
            
            # Call the model.  
            try:  
                response = self.model(messages)  
            except Exception as e:  
                continue  
            
            # Append the new response to our chain-of-thought.  
            chain_of_thought += f"\nAssistant: {response}"  
            
            # Check if we have a final action.  
            match = re.search(r"Action:\s*(.*)", response, re.IGNORECASE)  
            if match:  
                action = match.group(1).strip()  
                return action  
            else:  
                # Optionally, if no action is found, you might add an extra prompt to steer towards a final answer.  
                chain_of_thought += "\nUser: Please continue your reasoning until you provide a final action on a new line beginning with 'Action:'."  
        
        # Fallback if no action is identified.  
        return response
