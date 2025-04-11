#!/usr/bin/env python
import argparse
import os
import sys
from termcolor import colored

from src.agents.random_agent import RandomAgent
from src.agents.actor_critic import ActorCriticAgent
from src.agents.react_agent import ReActAgent
from src.agents.tree_of_thoughts_agent import TreeOfThoughtsAgent
from src.utils.llm_api import LLM
from src.defenderbench import benchmark_v0

def main(args):  
    # Choose the agent based on an added --agent_type argument.
    if args.agent == "random":
        agent = RandomAgent()
    elif args.agent == "react":
        # Instantiate the LLM and wrap it in our ReActAgent.
        model = LLM(args.model, verbose=args.verbose)
        agent = ReActAgent(model)
    elif args.agent == 'actor_critic': # Fall back to actor-critic.
        model = LLM(args.model, verbose=args.verbose)
        agent = ActorCriticAgent(model)
    else: # Fall back to actor-critic.
        model = LLM(args.model, verbose=args.verbose)
        agent = TreeOfThoughtsAgent(model)

    score_dict = {}
    for env_name in args.env_names:
        print(f"Running environment: {env_name}")
        score = agent.run(env_name, args)
        score_dict[env_name] = score

    print("Normalized scores on each task:", score_dict)
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent', help='Type of Agent: random, human, react, or actor_critic', default="random")
    parser.add_argument('--model', help='Name of the LLM backend or "human"/"random"', default='random')
    parser.add_argument('--env_names', nargs="+", help='List of environments to run. Choices: {}'.format(benchmark_v0))
    parser.add_argument('--verbose', action="store_true", help='Verbose mode')
    parser.add_argument('--debug', action="store_true", help='Debug mode before sending an action to the environment.')
    parser.add_argument('--use-wandb', action="store_true", help='Log experiment using wandb.')

    args = parser.parse_args()
    if args.env_names is None:
        args.env_names = benchmark_v0
    main(args)
