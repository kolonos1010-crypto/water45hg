"""LangGraph agent graph for the infinity-loop dev+ops cycle.

This graph orchestrates Claude through the NEXT_TASK -> PLAN -> IMPLEMENT ->
TEST & SELF_EVAL cycle, using tools to read/write files and run shell commands.

Requirements:
    pip install langgraph langchain-anthropic langchain-core

Usage:
    python graph.py
"""

import os
import subprocess
from typing import TypedDict, Annotated, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: list
    files_changed: list[str]
    last_task: str
    logs: list[str]
    done: bool
    iteration: int


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def read_file(path: str) -> str:
    """Read file contents from the given path."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: File not found: {path}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating directories as needed."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"OK: Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def list_files(directory: str = ".") -> str:
    """List files in the given directory recursively."""
    result = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden dirs and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in files:
            result.append(os.path.join(root, f))
    return "\n".join(sorted(result))


@tool
def run_shell(command: str) -> str:
    """Run a shell command and return stdout + stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        return output[:5000] if len(output) > 5000 else output
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 120 seconds"
    except Exception as e:
        return f"ERROR: {e}"


TOOLS = [read_file, write_file, list_files, run_shell]

# ---------------------------------------------------------------------------
# Controller prompt
# ---------------------------------------------------------------------------

CONTROLLER_PROMPT = """\
You are an autonomous dev+ops agent. You work in an infinite improvement loop.

Current project: Console Monitoring Automation Engine
- Monitors console for "Loaded [X] | Removed [Y] duplicates" patterns
- Extracts bot counts and inputs them automatically
- Handles API key rotation and error triggers
- Produces batch validation reports

Your cycle:
1. NEXT_TASK - Scan repo files/logs, choose the single most valuable next task
2. PLAN - Output a short plan (3-5 steps)
3. IMPLEMENT - Edit or create files (full file contents, never partial diffs)
4. TEST & SELF_EVAL - Run tests, evaluate, suggest next task

Rules:
- Prefer small, safe changes over giant rewrites
- Do not change the goal or log formats
- Always run tests after implementing
- Set done=True only when all features are implemented and tests pass
"""


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def _get_model():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
    ).bind_tools(TOOLS)


def planner_node(state: AgentState) -> dict:
    """Ask Claude to identify the next task."""
    model = _get_model()
    iteration = state.get("iteration", 0) + 1

    context = (
        f"Iteration: {iteration}\n"
        f"Last task: {state.get('last_task', 'None')}\n"
        f"Files changed so far: {state.get('files_changed', [])}\n"
        f"Recent logs: {state.get('logs', [])[-5:]}\n\n"
        "Scan the repository and output NEXT_TASK with Goal, Files, Risks. "
        "Then output PLAN with steps. Then IMPLEMENT the changes using the tools."
    )

    messages = [
        SystemMessage(content=CONTROLLER_PROMPT),
        HumanMessage(content=context),
    ]

    response = model.invoke(messages)
    return {
        "messages": [response],
        "iteration": iteration,
    }


def executor_node(state: AgentState) -> dict:
    """Execute tool calls from the planner."""
    tool_node = ToolNode(TOOLS)
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        result = tool_node.invoke({"messages": state["messages"]})
        new_messages = result.get("messages", [])

        files_changed = list(state.get("files_changed", []))
        logs = list(state.get("logs", []))

        for msg in new_messages:
            content = msg.content if hasattr(msg, "content") else str(msg)
            if "Written" in content:
                logs.append(content)
            logs.append(str(content)[:200])

        return {
            "messages": new_messages,
            "files_changed": files_changed,
            "logs": logs,
        }

    return {"messages": [], "logs": state.get("logs", [])}


def evaluator_node(state: AgentState) -> dict:
    """Claude evaluates progress and decides whether to continue."""
    model = _get_model()

    context = (
        f"Iteration: {state.get('iteration', 0)}\n"
        f"Files changed: {state.get('files_changed', [])}\n"
        f"Recent logs:\n" + "\n".join(state.get("logs", [])[-10:]) + "\n\n"
        "Output SELF_EVAL with Improvements, Remaining risks, Suggested next task.\n"
        "If all features are implemented and tests pass, set done to True.\n"
        "Respond with JSON: {\"done\": true/false, \"eval\": \"...\"}"
    )

    messages = [
        SystemMessage(content=CONTROLLER_PROMPT),
        HumanMessage(content=context),
    ]

    response = model.invoke(messages)
    content = response.content if hasattr(response, "content") else str(response)

    done = '"done": true' in content.lower() or '"done":true' in content.lower()

    logs = list(state.get("logs", []))
    logs.append(f"SELF_EVAL (iteration {state.get('iteration', 0)}): done={done}")

    return {
        "messages": [response],
        "done": done,
        "logs": logs,
    }


def should_continue(state: AgentState) -> Literal["planner", "__end__"]:
    """Route: loop back to planner or end."""
    if state.get("done", False):
        return "__end__"
    if state.get("iteration", 0) >= 50:
        return "__end__"  # Safety limit
    return "planner"


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("evaluator", evaluator_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "evaluator")
    graph.add_conditional_edges("evaluator", should_continue)

    return graph.compile()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Console Monitoring Engine - LangGraph Agent")
    print("=" * 60)

    app = build_graph()

    initial_state: AgentState = {
        "messages": [],
        "files_changed": [],
        "last_task": "None",
        "logs": [],
        "done": False,
        "iteration": 0,
    }

    for step in app.stream(initial_state):
        node_name = list(step.keys())[0]
        node_state = step[node_name]
        iteration = node_state.get("iteration", "?")
        done = node_state.get("done", False)
        print(f"[{node_name}] iteration={iteration} done={done}")
        if node_state.get("logs"):
            for log in node_state["logs"][-3:]:
                print(f"  LOG: {log[:120]}")
        if done:
            print("\nAgent completed all tasks.")
            break

    print("=" * 60)
    print("Agent loop finished.")
