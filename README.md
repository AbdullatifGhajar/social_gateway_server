# Locus server

## How it works

This server is an API for the Locus app. It provides the list of prompts and user authentication. It also stores the responses collected by the Locus App and hosts a website with instructions on how to use Locus and Aware Light. Here is a link to Locus documentation: https://github.com/AbdullatifGhajar/social_gateway/blob/master/README.md. 

### Prompts & Reflection Questions

All prompts are stored in prompts.json. Each prompt has the following attributes:

- english (str): the English translation of the prompt. This means that other languages would get a different attribute.
- answerable (bool): whether the prompt is a question that needs to be answered. The opposite is just a hint for the day.
- prompt_type (str): there are normal prompts that appear when apps are opened and there are reflection questions that appear at the end of the day.
- blacklist (list\[str\]): the list of apps where this prompt should never appear.
- Whitelist (list\[str\]): the list of apps for which this prompt should be answered. This means that you can only receive this prompt if you open one of these apps.

### User authentication

With a Google Sheet, you can store a list of participants with their credentials. This makes it easier to authenticate and maintain this list manually. It is very important to adjust the participants_api.py file when the Google Sheet layout changes.

### Storage

The users' answers are stored in answers.csv.

### Tutorials

Tutorials can be found in the templates. Here is the link to the websites

- Locus: https://hpi.de/baudisch/projects/neo4j/api/locus
- Aware Light: https://hpi.de/baudisch/projects/neo4j/api/aware

## Usage

To start the server type `make start` in the terminal. To stop it type `make stop` and ignore the error.