import base64
import os
import subprocess
import sys
import tempfile
from pydantic import BaseModel

def open_file(path: str) -> None:
  if sys.platform.startswith("darwin"):
    subprocess.run(["open", path], check=False)  # macOS
  elif os.name == "nt":  # Windows
    os.startfile(path)  # type: ignore
  elif os.name == "posix":
    subprocess.run(["xdg-open", path], check=False)  # Linux/Unix
  else:
    print(f"Don't know how to open files on this platform: {sys.platform}")

def retrieve_image_from_resources(path: str):
  # If path is absolute, use as is. If not, prepend resources/
  if not os.path.isabs(path):
    path = os.path.join("resources", path)
  with open(path, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode("utf-8")
  return base64_image