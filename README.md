# LoLStats
---
## Prerequisites
- 🐍 Python 3.12^

## How to install and run
1. Start by cloning the repository to the desired path on your system
### Create a virtual environment
To avoid any conflicts with installed Python libraries on your system, we'll need to create a virtual environment to avoid these conflicts.

**Steps:**
1. Create a folder called "venv". This is where all of your virtual environment files will go. You can run the command below to get started.
>mkdir venv
2. After you've made the new folder, navigate into it the folder
>cd  ./venv
3. Run the command to create the virtual environemtn
>python -m venv ./
4. Once properly setup, you can activate your virtual environment via the scripts generated.

To activate (Windows Powershell):
> ./PATH_TO_YOUR_VENV_FOLDER/Scripts/Activate.ps1

To activate (MacOS zsh):
> source ./PATH_TO_YOUR_VENV_FOLDER/Scripts/activate

### Installing the libraries
Once you have your virtual environment set up, you can begin installing the required libraries.
Navigate to the root of the project where the `requirements.txt` is located. In that directory run the following command.
> pip install -r requirements.txt

This command will automatically install all the necessary libraries to run the application

### Launching the application
After you've installing all of the neccessary libraries, you are ready to run the app. In the root of the project, try running `main.py` with the following command.
>python main.py



