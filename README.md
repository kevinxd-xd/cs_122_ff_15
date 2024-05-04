# LoLStats
---
## Prerequisites
- 🐍 Python 3.12^

## How to install and run
1. Start by cloning the repository to the desired path on your system
### Create a virtual environment
To avoid any conflicts with installed Python libraries on your system, we'll need to create a virtual environment to
avoid these conflicts.

**Tip**: To ensure installation process goes as smoothly as possible, please start in the root of the project directory.

**Steps:**
1. Create a folder called "venv". This is where all of your virtual environment files will go. You can run the command
2. below to get started.
>mkdir venv
2. After you've made the new folder, navigate into it the folder
>cd  ./venv
3. Run the command to create the virtual environment
>python -m venv ./
4. Once properly setup, you can activate your virtual environment via the scripts generated.

To activate (Windows Powershell):
> /PATH_TO_YOUR_VENV_FOLDER/Scripts/Activate.ps1

**WARNING**: You may have execution issues on Windows powershell due to the default execution-policy set. You will need
to change it to run the virtual environment.

To activate (MacOS zsh):
> source /PATH_TO_YOUR_VENV_FOLDER/Scripts/activate

If you are unable to execute it due to permissions, add the **sudo** command in front of the command.

### Installing the libraries
Once you have your virtual environment set up, you can begin installing the required libraries.
Navigate to the root of the project where the `requirements.txt` is located. In that directory run the following command.
> pip install -r requirements.txt

This command will automatically install all the necessary libraries to run the application

### Launching the application
After you've installing all the necessary libraries, you are ready to run the app. In the root of the project, try 
running the flask with the following command.
>flask --app app run

If you are having issues with the command above, try adding `python -m flask` in front.
>python -m flask --app app run

**Tip**: Some systems may have two versions of Python installed. Running the command with `python` may refer to an
outdated version of Python. In most systems, the most recent Python binary can be called with `python3`.
The resulting new command would be `python3 -m flask --app app run`.

### Visiting the site
Once the flask server is up and running, you can visit it to verify everything is working. By default, the server should
be listening on port 5000 on localhost.
> http://127.0.0.1:5000

**OR**

> http://localhost:5000

Either of the links should bring you to the homepage.

# Running the testcases
In the zipped file, there should be a folder named testcases. In this folder, there should be 5 testcases that you can
upload to the web app to create the data analytics. Not all of the five files will work since we added a few to test the
error handling capabilities of our applicaiton. Here is a table of the expected results for each uploaded file.

| Testcase File                           | Expected Results                                                                               |
|-----------------------------------------|------------------------------------------------------------------------------------------------|
| testcase_1.json                         | SUCCESS: Displays Body#NA1’s player information and graphs                                     |
| testcase_2.json                         | SUCCESS: Displays Her Challenger#Luna’s player information and graphs                          |
| testcase_3.json                         | SUCCESS: SUCCESS: Displays Fish Kid#NA1’s player information and graphs                        |
| testcase_4.json                         | FAILURE: User sees a 400 page due to a non-JSON file submission                                |
| testcase_5.json                         | FAILURE: User sees a 400 page due to incorrect JSON data information that could not be parsed. |
| Search function with no/invalid API Key | FAILURE: User sees a 403 page stating “Invalid API Key”                                        |

The last testcase does not have a file associated with it. To test this feature, please fill out the
"Search via the Riot API" form and attempt to submit. You should see an error be thrown about there being no valid API
key. This happens because you need a valid API key to access the game server's data. Without the key, you will be unable
to complete the search, throwing an error.