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
