"""Research mode guard — blocks Edit/Write when .research-mode flag exists."""
import json
import sys
import os

FLAG_FILE = os.path.expanduser("~/.claude/.research-mode")

# If research mode is not active, allow everything
if not os.path.exists(FLAG_FILE):
    sys.exit(0)

input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")

# Block file modification tools
BLOCKED_TOOLS = {"Edit", "Write", "NotebookEdit"}

if tool_name in BLOCKED_TOOLS:
    output = {
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": f"RESEARCH MODE: {tool_name} blocked. Only read/search operations allowed. Disable with /research-off."
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Also block destructive bash commands (but allow reads)
if tool_name == "Bash":
    command = input_data.get("tool_input", {}).get("command", "")
    # Block commands that write files
    write_patterns = [">", ">>", "tee ", "mv ", "cp ", "mkdir ", "touch "]
    for pattern in write_patterns:
        if pattern in command:
            output = {
                "hookSpecificOutput": {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"RESEARCH MODE: File-writing bash command blocked. Only read operations allowed. Disable with /research-off."
                }
            }
            print(json.dumps(output))
            sys.exit(0)

sys.exit(0)
