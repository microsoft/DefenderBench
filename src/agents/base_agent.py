#!/usr/bin/env python
import gymnasium as gym
from tqdm import tqdm
import wandb

class BaseAgent:
    """
    BaseAgent implements the common run loop for an environment.
    Derived classes must override the act(obs, info) method.

    The run() method takes in the environment name and command‐line arguments
    (which may include wandb settings, debug flags, etc.) and proceeds to interact
    with the environment.
    """

    def act(self, obs, info):
        raise NotImplementedError("Subclasses must implement act() method.")

    def run(self, env_name, args):
        # Create the environment.
        env = gym.make("defenderbench/{}-v0".format(env_name), disable_env_checker=True)
        nb_steps = env.unwrapped.nb_steps
        nb_trials = env.unwrapped.nb_trials

        # Initialize wandb logging if requested.  
        if args.use_wandb:  
            wandb.init(project="DefenderBench", name=f"{env_name}/{args.llm_name}",  
                        config={"LLM": args.llm_name, "env": env_name})  
            wandb_table = wandb.Table(columns=["Step", "Instructions", "History", "Obs", "Action", "Feedback", "Reward", "Score"])  
        else:  
            wandb_table = None  

        # Reset environment to get the initial observation and info.  
        _, info = env.reset()  
        step_id = 0  
        pbar = tqdm(total=nb_steps, desc=f"{env_name}", leave=True)  

        done = False  
        while not done:  
            # Display current score.  
            cur_score = info.get('score', 0)  
            max_score = info.get('max_score', 1)  
            pbar.set_postfix_str(f"Score: {cur_score}/{max_score} ({(cur_score/max_score):.1%})")  

            # Obtain action from the agent.  
            action = self.act(info.get('obs', ''), info)  

            if args.debug:  
                from ipdb import set_trace; set_trace()  

            # Step the environment with the chosen action.  
            try:
                _, reward, done, info = env.step(action)
            except Exception as e:
                print(f"Error stepping the environment: {e}")
                reward = 0
                done = True,
                info = {"step_done": True, "score": 0, "max_score": 1}
            
            # Log information if wandb is enabled.  
            if wandb_table is not None:  
                row = [step_id+1,  
                        info.get('instructions', ''),  
                        info.get('history', ''),  
                        info.get('obs', ''),  
                        action,    # We log the action both as "Action" and "Feedback" for simplicity.  
                        action,  
                        reward,  
                        info.get('score', 0)]
                wandb_table.add_data(*row)  
                wandb.log({  
                    "episode/score": info.get('score', 0),  
                    "episode/normalized_score": info.get('score', 0)/max_score  
                }, step=step_id+1)  
            
            # Update progress based on whether the environment reported a completed step.  
            if info.get("step_done", False):  
                pbar.update(1)  
                step_id += 1  

        # Log final metrics if using wandb.  
        if wandb_table is not None:  
            wandb.log({  
                "episode/rollout": wandb_table,  
                "final/normalized_score": info.get('score', 0)/max_score,  
            })  
            wandb.finish()  

        return info.get('score', 0) / max_score