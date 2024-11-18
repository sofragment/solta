# solta v0.0.4: smarter, faster, and more dynamic >:>

this release brings major upgrades to solta, making it smarter, more flexible, and packed with new features to help you build ai agents like a pro. here’s the rundown:
---

## what’s new?

**router system upgrades** 🔍

•	replaced the “prefix” parameter in `Client` with `router` for better clarity (because words matter).

•	added custom router support—load your own router implementations for full control.

•	introduced the shiny new `DefaultRouter` as the standard routing option (because it's clearly the best router).

•	improved message routing and broadcasting, ensuring agents stay in the loop.

**ai provider integration** 🤖

•	integrated ollama provider with streaming response support—no more waiting for answers.

•	created an extensible ai provider interface for future integrations (openai, anthropic, google, etc.).

•	baked ai capabilities right into the base Agent class for seamless ai interactions.

**framework reorganization** 🛠️

we gave solta’s structure a glow-up for better organization and usability:

```python
solta/
├── core/
│   ├── ai_providers.py    # handles ai integrations
│   ├── default_router.py  # routes messages like a boss
│   ├── client.py          # now supports custom routers
│   └── agent.py           # ai-enabled and ready for action
└── examples/
    └── multi_agent_demo/
        ├── calculator_agent/
        │   ├── agent.py   # math operations and tools
        │   └── tools.py
        └── memory_agent/
            ├── agent.py   # persistent memory and inter-agent comms
            └── tools.py
```

## key features:

•	custom router loading—bring your own router logic for ultimate flexibility.

•	ollama provider integration with streaming responses (it’s fast, it’s smooth, it just works).

•	improved agent discovery and hot reloading—edit your agents and see the updates instantly.

## usage example 🐍

```python
from solta.core import Client

# using default router
client = Client(
    router="default",
    agent_dirs=["my_agents"],
    live_reload=True
)

# using a custom router
client = Client(
    router="path/to/custom_router.py",
    agent_dirs=["my_agents"]
)

client.run()
```

## next steps 🛠️

•	expand ai provider integrations (openai, google, anthropic—looking at you).

•	implement advanced conversation history management (because context is everything).

•	build cli tools to simplify agent creation and management (you’re welcome).

---

solta is evolving, and this release sets the stage for even bigger things. dynamic, smarter, and more modular than ever, v0.0.4 is here to make your agent-building journey smoother and more fun. happy coding! :>