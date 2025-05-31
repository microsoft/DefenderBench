# DefenderBench: A Toolkit for Evaluating Language Agents in Cybersecurity Environments

<p align="center">
  <a href="mailto:chiyuzh@mail.ubc.ca">Chiyu Zhang</a>,
  <a href="mailto:macote@microsoft.com">Marc-Alexandre Côté</a>,
  <a href="mailto:malbada@microsoft.com">Michael Albada</a>,
  <a href="mailto:asankaran@microsoft.com">Anush Sankaran</a>,
  <a href="mailto:jstokes@microsoft.com">Jack W. Stokes</a>,
</p>
<p align="center">
  <a href="mailto:tong.wang@microsoft.com">Tong Wang</a>,
  <a href="mailto:amirabdi@microsoft.com">Amir Abdi</a>,
  <a href="mailto:william.blum@microsoft.com">William Blum</a>,
  <a href="mailto:muhammad.mageed@ubc.ca">Muhammad Abdul-Mageed</a>
</p>


<p align="center">
  <img src="image/Microsoft.jpg" height="50" />
  <span>&nbsp;&nbsp;&nbsp;&nbsp;</span>
  <img src="image/ubc_logo.png" height="50" />
</p>



<p align="center" width="100%"><a href="https://github.com/microsoft/DefenderBench" target="github">GitHub</a>, <a href="https://arxiv.org/abs/" target="github">Paper</a></p>


We introduce DefenderBench, a practical, open-source toolkit for evaluating language agents across offense, defense, and cybersecurity knowledge-based tasks. DefenderBench includes environments for network intrusion, malicious content detection, code vulnerability analysis, and cybersecurity knowledge assessment. It is intentionally designed to be affordable and easily accessible for researchers while providing fair and rigorous assessment. We benchmark several state-of-the-art (SoTA) and popular LLMs, including both open- and closed-weight models, using a standardized agentic framework. 

<p align="center" width="100%">
    <a><img src="image/overview.png" alt="Title" style="width: 50%; min-width: 300px; display: block; margin: auto;"></a>
</p>

- [Tasks](#Tasks)
- [Modules](#Modules)
- [Installation](#Installation)
- [Usage](#Usage)
- [Contributing](#Contributing)
- [Trademarks](#Trademarks)

## Tasks

Currently, DefenderBench consists of five cybersecurity task types.
* **Computer Network Intrusion Simulation.** We leverage the network intrusion simulation tool CyberBattleSim (CBS) (Team., 2021) to evaluate the ability of LLM agents to identify vulnerabilities in a network. CyberBattleSim is parameterized by a fixed topology and a set of node vulnerabilities that agents can exploit to move laterally within the network.

* **Malicious Content Detection.**  We include two task, MALICIOUS-TEXT and MALICIOUS-WEB, for malicious content detection (Alvarado., 2024) and phishing website detection (Ariyadasa et al., 2021), respectively.

* **Cyber Threat Intelligence (CTI) Multiple Choice Question Answering.** A multiple-choice question answering task that uses the CTI-MCQA dataset introduced by Alam et al. (2024).

* **Code Vulnerability Detection.** We include two two datasets, VULNERABLE-CG (Lu et al., 2021) and VULNERABLE-DV (Zhou et al., 2019), for code vulnerability detection.

* **Code Vulnerability Fixing.** We use the CVEFix dataset (Bhandari et al., 2021) for the vulnerability fixing task.

## Modules
DefenderBench leverages publicly accessible cybersecurity datasets and turns them into interactive environments to evaluate LLM agents. The toolkit comprises three main modules: data preprocessing, task environment, and agent interface. Additionally, we provide instructions to enable users to modify and expand each module.

* **Data Preprocessing.** The DefenderBench toolkit automatically downloads the required datasets from their respective sources, shuffles the samples randomly according to a fixed random seed, and splits them into a test set and a few-shot sample pool for in-context learning. Once preprocessed, the datasets are cached locally. The data preparation of each task can be found in `src/defenderbench/{task_name}/{task_name}_data.py`.

* **Task Environment.** For each task, we set up a task environment that provides task-specific instructions, defines the action space for the agent, loads the relevant datasets and constructs few-shot examples if few-shot in-context learning is being conducted. The task environment definition of each task is in `src/defenderbench/{task_name}/{task_name}_evn.py`.

* **Agent Interface.** Our DefenderBench is equipped with an LLM agent interface that enables users to integrate both open- and closed-weight LLMs. Users can also seamlessly incorporate their own agentic system to perform the tasks. The agent interface can be found in `src/agents/`. 
  
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

### Usage using a custom agent

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
