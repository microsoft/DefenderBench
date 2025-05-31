# DefenderBench: A Toolkit for Evaluating Language Agents in Cybersecurity Environments

<p align="center"> Chiyu Zhang, Marc-Alexandre Côté, Michael Albada, Anush Sankaran, Jack W. Stokes, </p>
<p align="center"> Tong Wang, Amir Abdi, William Blum, Muhammad Abdul-Mageed


<p align="center" float="left">
  <img src="image/Microsoft.jpg" height="70" />
  <img src="image/ubc_logo.png" height="70" />
</p>


<p align="center" width="100%"><a href="https://github.com/microsoft/DefenderBench" target="github">GitHub</a>, <a href="https://arxiv.org/abs/" target="github">Paper</a></p>

<p align="center" width="100%">
    <a><img src="image/overview.png" alt="Title" style="width: 90%; min-width: 300px; display: block; margin: auto;"></a>
</p>
We introduce DefenderBench, a practical, open-source toolkit for evaluating language agents across offense, defense, and cybersecurity knowledge-based tasks. DefenderBench includes environments for network intrusion, malicious content detection, code vulnerability analysis, and cybersecurity knowledge assessment. It is intentionally designed to be affordable and easily accessible for researchers while providing fair and rigorous assessment. We benchmark several state-of-the-art (SoTA) and popular LLMs, including both open- and closed-weight models, using a standardized agentic framework. 

## Installation 

First create a virtual environment and activate it:

    conda create -n defenderbench python=3.10
    conda activate defenderbench

Then install the benchmark:

        pip install .


## Usage

To run the benchmark, use the following script:

    python -m src.examples.run_experiment

For instance, to run the random baseline on all the environments/tasks

    python -m src.examples.run_experiment --llm random

To manually run a specific environment/task

    python -m src.examples.run_experiment --llm human --env_name CyberBattleChain10

To list all the available environments/tasks and additional settings use:

    python -m src.examples.run_experiment --help

## Usage using a custom agent

Here's a simple example of an actor-critic multi-agent architecture

    python agents/actor_critic.py

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
