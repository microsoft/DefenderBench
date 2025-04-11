#!/usr/bin/env python
import re
from .base_agent import BaseAgent
from src.utils.llm_api import LLM

class TreeOfThoughtsAgent(BaseAgent):
    """
    A Tree‐of‐Thoughts agent that uses beam search to generate multiple reasoning paths
    (branches) and then uses a critic prompt to select the best final action.
    """
    def __init__(self, model: LLM, max_depth: int = 2, beam_width: int = 2):
        super().__init__()
        self.model = model
        self.max_depth = max_depth # maximum number of expansion iterations
        self.beam_width = beam_width # number of candidate expansions per branch

        # When generating reasoning, this system prompt instructs the LLM to use a chain‐of‐thought process.  
        self.system_prompt = (  
            "You are a cybersecurity assistant using a Tree‐of‐Thoughts strategy. At each step, generate thoughtful reasoning "  
            "to explore multiple potential actions. When you decide, your response must include a line starting with 'Action:' "  
            "followed by your final decision."  
        )  

        # This prompt describes the critic’s role.  
        self.critic_system_prompt = (  
            "You are a critical cybersecurity expert evaluating chain‐of‐thought reasoning. "  
            "Your job is to provide a numerical score (from -10 to 10, where 10 is best) on one new line, "  
            "and then on a subsequent line output the final decision in the format 'Action: <final decision>'."  
        )

        # Template to evaluate a branch. The placeholder {chain} will be replaced by the branch’s full reasoning.  
        self.critic_prompt_template = (  
            "Evaluate the following chain‐of‐thought reasoning in the context of cybersecurity. "  
            "First, provide a numerical score between -10 and 10 on a new line. Then, on another new line, "  
            "provide the final decision in the format 'Action: <final action>'.\n\n"  
            "Chain‐of‐thought:\n{chain}"  
        )

    def beam_search(self, base_context: str) -> list:  
        """  
        Given the base context (environment details and instructions), run a beam search  
        to generate candidate reasoning branches. If any branch contains a final decision,  
        it is treated as terminal and returned.  
        """  
        branches = []  
        # Initial expansion: generate beam_width candidate branches from base_context.  
        initial_prompt = base_context + "\n\nPlease begin your chain‐of‐thought reasoning."  
        for _ in range(self.beam_width):  
            messages = [  
                {"role": "system", "content": self.system_prompt},  
                {"role": "user", "content": initial_prompt}  
            ]  
            candidate = self.model(messages)  
            branch = base_context + "\n" + candidate  
            branches.append(branch)  
        
        # Iteratively expand each branch up to max_depth.  
        for depth in range(1, self.max_depth):  
            new_branches = []  
            terminal_branches = []  
            for branch in branches:  
                for _ in range(self.beam_width):  
                    expansion_prompt = branch + "\n\nContinue your reasoning. Provide the next thought, and if you are ready, "  
                    expansion_prompt += "include a final decision on a new line starting with 'Action:'."  
                    messages = [  
                        {"role": "system", "content": self.system_prompt},  
                        {"role": "user", "content": expansion_prompt}  
                    ]  
                    expansion = self.model(messages)  
                    new_branch = branch + "\n" + expansion  
                    if "Action:" in expansion:  
                        terminal_branches.append(new_branch)  
                    else:  
                        new_branches.append(new_branch)  
            # If any branch has reached a terminal state, return these candidates.  
            if terminal_branches:  
                return terminal_branches  
            # Otherwise, if there are too many branches, prune to the top beam_width using evaluation.  
            if new_branches:  
                if len(new_branches) > self.beam_width:  
                    scored_branches = []  
                    for branch in new_branches:  
                        score, _ = self.evaluate_branch(branch)  
                        scored_branches.append((score, branch))  
                    scored_branches.sort(key=lambda x: x[0], reverse=True)  
                    branches = [branch for score, branch in scored_branches[:self.beam_width]]  
                else:  
                    branches = new_branches  
            else:  
                break  
        return branches  

    def evaluate_branch(self, branch: str) -> (float, str):  
        """  
        Uses the critic prompt to evaluate a candidate branch. Returns a tuple (score, final_action)  
        where score is the numerical rating and final_action is the action extracted from the branch.  
        """  
        prompt = self.critic_prompt_template.format(chain=branch)  
        messages = [  
            {"role": "system", "content": self.critic_system_prompt},  
            {"role": "user", "content": prompt}  
        ]
        try:
            response = self.model(messages)  

            # Look for a numerical score.  
            score_match = re.search(r"([-+]?\d+\.?\d*)", response)  
            # Look for a final action (a line that starts with "Action:"), case-insensitive.  
            action_match = re.search(r"Action:\s*(.*)", response, re.IGNORECASE)  
            
            score = float(score_match.group(1)) if score_match else -100.0  
            action = action_match.group(1).strip() if action_match else ""  
            return score, action
        except Exception as e:
            print(f"Error in evaluate_branch: {e}")
            return float("-inf"), ""

    def act(self, obs, info):  
        """  
        Combines the environment context to initiate tree search and then evaluates all candidate branches  
        to return the final, best action.  
        """  
        base_context = (  
            f"Instructions: {info.get('instructions', '')}\n"  
            f"History: {info.get('history', '')}\n"  
            f"Last Action: {info.get('last_action', '')}\n"  
            f"Observation: {obs}"  
        )  
        candidate_branches = self.beam_search(base_context)  
        best_score = float("-inf")  
        best_action = None  
        
        # Evaluate all candidate branches and select the one with the highest rating.  
        for branch in candidate_branches:  
            score, action_candidate = self.evaluate_branch(branch)  
            if score > best_score:  
                best_score = score
                best_action = action_candidate  
        if best_action is None or best_action == "":  
            best_action = "No valid action found."
        return best_action
