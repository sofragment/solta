# solta: where building ai agents is a breeze (and fun) :>

solta is a python framework for crafting ai agents that interact with the ollama api. inspired by discord.py’s cog system (because why reinvent good ideas?), solta makes creating, managing, and deploying ai agents modular and structured without sucking the fun out of it.

# features

•🛠️ **agent-based architecture**: build modular ai systems like a pro.
•🌐 **ollama api integration**: plug and play with your favorite model.
•📋 **standardized structure**: because chaos is for your personal life, not your code.
•🧩 **tool system**: extend your agent’s powers with custom tools.
•🎯 **decorator-based commands**: easy-to-use, clean syntax for handling logic.

---
**installation** 🚀

installing solta is easier than opening a jar of pickles (unless you’re a pickle-opener pro, in which case… it’s still easy):

```bash
pip install solta
```

---
**basic usage** 🐍

here’s a quick peek at how to get your first agent up and running:

```python
from solta import Agent, setup_agent

class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        
    @setup_agent
    async def on_ready(self):
        print("agent is ready!")
        
    @setup_agent
    async def on_message(self, message):
        # handle incoming messages
        pass
```

---
**create and run your agent**
```python
agent = MyAgent()
agent.run()
```
yes, it’s really that simple.

---
**project structure** 🗂️

solta keeps things organized so you don’t lose your mind halfway through development. here’s the standard structure for your agent project:
```
your_agent/
├── agent.py      # main agent logic
├── tools.py      # custom tools for the agent
└── setup.py      # agent configuration and setup
```
think of it as the ikea of project layouts—except with actual instructions.

---
**documentation** 📚

need more details? check out our [docs link] for the full breakdown of solta’s features, usage, and tips for making your ai agents smarter, faster, and cooler.

---
**license** ⚖️

solta is licensed under the mit license because we believe in open-source goodness. check out the license file for the fine print.

---

did you know octopuses have three hearts, and two of them stop beating when they swim? also, solta has zero hearts, but if it did, it would beat for you. probably. :>