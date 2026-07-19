# Self-Correcting Code Assistant

An autonomous AI agent that writes Python code, executes it, reads its own errors, and rewrites the code until it works — powered entirely by a local LLM via Ollama.

Instead of generating code once and hoping for the best, this agent works in a loop:

```
User gives a task
      ↓
AI writes code
      ↓
Code gets executed
      ↓
Errors are captured
      ↓
AI analyzes the error
      ↓
AI rewrites the code
      ↓
Repeat until success (or max retries)
```

This project demonstrates core AI agent concepts: LLM orchestration, feedback loops, autonomous retry logic, and tool use — all with free, open-source tools.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3.9+** | Core language |
| **Ollama** | Runs the LLM locally on your machine |
| **DeepSeek-Coder 6.7B** | The coding model that writes/fixes code |
| **LangChain** | Simple interface to call the local model |
| **subprocess** (stdlib) | Executes generated code and captures errors |

No API keys. No cloud costs. Everything runs on your own machine.

---

## Requirements

- Windows, macOS, or Linux
- Python 3.9 or higher
- ~8 GB RAM recommended (CPU-only works, just slower)
- A GPU is optional but speeds up generation

---

## Project Structure

```
self_correcting_agent/
├── venv/                  # virtual environment (created by you)
├── prompts.py             # system + debug prompt templates
├── executor.py             # runs generated code, captures output/errors
├── agent.py                # main loop — the actual agent
└── generated_code.py       # auto-created/overwritten by the agent each run
```

---

## Setup

### 1. Install Ollama and pull the coding model

Install Ollama from [ollama.com](https://ollama.com), then pull the model:

```bash
ollama pull deepseek-coder:6.7b
```

### 2. Create the project folder and virtual environment

```bash
mkdir self_correcting_agent
cd self_correcting_agent
python -m venv venv
```

Activate it:

```bash
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install langchain langchain-community ollama
```

### 4. Add the project files

Create `prompts.py`, `executor.py`, and `agent.py` in the project folder (see [Files](#files) below).

---

## Usage

Make sure Ollama is running in the background, then simply run:

```bash
python agent.py
```

### Example output

```
Attempt 1 failed...
FileNotFoundError: salaries.csv not found

Attempt 2 failed...
ValueError: invalid column name

FINAL WORKING CODE:
...

OUTPUT:
...
```

To change what the agent builds, edit the `user_task` variable inside `agent.py`.

---

## Files

### `prompts.py`

```python
SYSTEM_PROMPT = """
You are an expert Python engineer.

Your task is to:
1. Write clean Python code
2. Fix bugs when errors appear
3. Return ONLY executable Python code
4. Do not include markdown
5. Ensure the code runs correctly
"""

DEBUG_PROMPT = """
The following Python code failed.

CODE:
{code}

ERROR:
{error}

Fix the issue and return corrected executable Python code only.
"""
```

### `executor.py`

```python
import subprocess

def run_code(file_path):
    try:
        result = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout
            }

        return {
            "success": False,
            "error": result.stderr
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### `agent.py`

```python
from langchain_community.llms import Ollama
from prompts import SYSTEM_PROMPT, DEBUG_PROMPT
from executor import run_code

MAX_RETRIES = 5

llm = Ollama(model="deepseek-coder:6.7b")

user_task = """
Create a Python script that:
1. Reads a CSV file
2. Calculates average salary
3. Displays the result
"""

def generate_code(prompt):
    return llm.invoke(prompt)

code_prompt = f"""
{SYSTEM_PROMPT}

TASK:
{user_task}
"""

generated_code = generate_code(code_prompt)

for attempt in range(MAX_RETRIES):

    with open("generated_code.py", "w") as f:
        f.write(generated_code)

    result = run_code("generated_code.py")

    if result["success"]:
        print("\nFINAL WORKING CODE:\n")
        print(generated_code)

        print("\nOUTPUT:\n")
        print(result["output"])

        break

    print(f"\nAttempt {attempt + 1} failed...")
    print(result["error"])

    debug_prompt = DEBUG_PROMPT.format(
        code=generated_code,
        error=result["error"]
    )

    generated_code = generate_code(debug_prompt)

else:
    print("Agent failed after maximum retries.")
```

---

## How It Works

1. **`prompts.py`** defines how the model should behave — write clean code, no markdown fences, fix bugs when shown an error.
2. **`executor.py`** runs the generated file as a subprocess, captures stdout on success or stderr on failure, and enforces a 10-second timeout.
3. **`agent.py`** ties it together: generate → write to file → execute → check result → if failed, feed the error back into the model → regenerate → repeat, up to `MAX_RETRIES` times.

The key insight: the error message itself becomes the next prompt, which is what makes this "self-correcting" rather than just "code-generating."

---

## ⚠️ Security Note

This project runs AI-generated code directly on your machine using `subprocess`, with **no sandboxing**. This is fine for personal experimentation but is **not safe** for production use or untrusted tasks. In a real-world system, run generated code inside a Docker container (or similar isolated sandbox) rather than directly on your host machine.

---

## Customization Ideas

- Swap `deepseek-coder:6.7b` for any other Ollama-supported coding model
- Increase/decrease `MAX_RETRIES`
- Add logging to a file instead of just printing to console
- Sandbox execution with Docker for safety
- Replace the local Ollama model with an API-based model (OpenAI, Anthropic, etc.) by swapping the LangChain LLM wrapper — the loop logic stays the same

---

## Credit

Based on the tutorial ["Creating a Self-Correcting Code Assistant"](https://amanxai.com/2026/05/20/creating-a-self-correcting-code-assistant/) by Aman Kharwal.
