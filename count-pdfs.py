from pathlib import Path


parentFolder = Path("NOUs")

print(len(list(parentFolder.glob("**/*.pdf"))))