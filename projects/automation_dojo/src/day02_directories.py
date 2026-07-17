from pathlib import Path #python's understanding of the file system
from datetime import datetime #python's understanding of dates

#save your working directory into a variable
current_location = Path.cwd()

output_folder = current_location / "output"
output_folder.mkdir(exist_ok=True)

#create timestamps for automation
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

output_file = output_folder / f"run_{timestamp}.txt"

content = (
    "Automation Practice - Day 2 \n"
    f"Run: {timestamp}.txt\n"
    f"Working Directory: {current_location}\n"
)

output_file.write_text(content)
