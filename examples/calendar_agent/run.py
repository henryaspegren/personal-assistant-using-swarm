from swarm.repl import run_demo_loop
from agents import calendar_agent

if __name__ == "__main__":
    run_demo_loop(calendar_agent, stream=True)
