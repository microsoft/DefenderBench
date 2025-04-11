#!/usr/bin/env python
from src.utils.llm_api import LLM
from src.agents.base_agent import BaseAgent

class ActorCriticAgent(BaseAgent):
    """
    A simple actor–critic agent that uses two LLM calls:
    • actor() produces a candidate action based on the current context.
    • critic() refines that candidate action into a final decision.


    The act() method uses actor() plus critic() in sequence.  
    """  
    def __init__(self, model: LLM):  
        super().__init__()
        self.model = model  

    def actor(self, info: dict) -> str:  
        prompt = (  
            "You are a cybersecurity analyst tasked with deciding the best next action. "  
            "Consider the following details:\n"  
            f"  • Instructions: {info.get('instructions', '')}\n"  
            f"  • History: {info.get('history', '')}\n"  
            f"  • Last Action: {info.get('last_action', '')}\n"  
            f"  • Current Observation: {info.get('obs', '')}\n\n"  
            "Provide a candidate action (along with a brief rationale) for the situation."  
        )  
        messages = [{"role": "user", "content": prompt}]  
        candidate = self.model(messages)  
        return candidate  

    def critic(self, info: dict, candidate: str) -> str:  
        prompt = (  
            "You are now a critical cybersecurity expert. Your job is to evaluate and refine the candidate action. "  
            "Consider the following context:\n"  
            f"  • Instructions: {info.get('instructions', '')}\n"  
            f"  • History: {info.get('history', '')}\n"  
            f"  • Last Action: {info.get('last_action', '')}\n"  
            f"  • Current Observation: {info.get('obs', '')}\n\n"  
            f"Candidate Action: {candidate}\n\n"  
            "Now provide the final, refined action (make sure it is concise and actionable)."  
        )  
        messages = [{"role": "user", "content": prompt}]  
        final_action = self.model(messages)  
        return final_action  

    def act(self, obs, info):  
        # Run the two-stage process.  
        candidate = self.actor(info)  
        final_action = self.critic(info, candidate)  
        return final_action
