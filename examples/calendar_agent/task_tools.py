# import subprocess

# def get_reminders():
#     script = '''
#     tell application "Reminders"
#         set remindersList to name of every reminder of list "Agent Test" whose completed is false
#     end tell
#     return remindersList
#     '''
#     result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
#     return result.stdout.strip().split(", ")

def get_tasks():
    tasks = [
        {'name': 'Groceries', 'description': 'Get groceries for the week', 'duration (hours)': 1},
        {'name': 'Blog post', 'description': 'write a blog post about agents', 'duration (hours)': 3},
    ]
    print(tasks)
    return str(tasks)