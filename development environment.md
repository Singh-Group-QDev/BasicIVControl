# How to set up a pymeasure development environment

### Who needs this tutorial?

If you just want to write data acquisition code using our fork of pymeasure you don't need this tutorial. Please see: [TODO: Insert link to other tutorial]

Let's say you are trying to set up some data acquisition code using pymeasure and VSCode but pymeasure doesn't have the instruments you need, so you are going to add some instruments to our fork of pymeasure. You would like to have one workspace with two folders: one that is your acquisiton code repository and another that is the pymeasure folder of your local clone of our pymeasure fork. How do you set this up so that you can:

1. Have ```import pymeasure``` reference your local pymeasure repo
2. Modify the local pymeasure repo in the same workspace as the acquisition code and
3. Seamlessly use git/GitHub to track your changes and push them to our pymeasure fork when you are ready to commit

Essentially, how do you set up a python project in VSCode that references another python project while both projects are individual git repos in different places? Like a project reference in VisualStudio.

## 1. Set up a workspace
Make a new workspace in VSCode. Right click in the workspace and use "Add Folder to Workspace" to add the folder that contains your data acquistion code and the folder that contains the pymeasure library code (C:\Users\QET\Documents\GitHub\pymeasure\pymeasure on the QET computer).

## 2. Set up a python virtual environment (venv)
Set up a python virtual environment in your data acquisition folder. Press F1 and find "Python: Create Environment". Use it to create the virtual environment. 

Press F1 and find "Python: Create New Terminal". Select the data aquisiton folder when prompted. This will launch a powershell terminal for your virtual environment. In this environment you can use commands like "pip" and not worry about which version of python's pip it is. It is the pip for, and only for, your virtual environment. Use pip in this terminal to install pymeasure's dependancies. pymeasure should not be installed here. If you do install it as a way to get the dependancies, make sure your uninstall it.

## 3. Set up the reference to pymeasure
Now we would like to tell our workspace where our pymeasure repo is so we can use ```import pymeasure``` as normal. Go to "File > Preferences > Settings". Search for "terminal.integrated.env.windows". There will be two results, one under "User" and the one under "Workspace" click "Workspace" and then click "edit in settings.json".

In the JSON file add the line "PYTHONPATH":"C:\\Users\\QET\\Documents\\GitHub\\pymeasure" in the "terminal.integrated.env.windows" section.

Now when you run your data acquisition code in the terminal using the Python extension the interpreter will find and use the local pymeasure repo. You will notice in the editor ```import pymeasure``` lines will be underlined with a warning that the package could not be found. If this bothers you, you can make a .env file with a PYTHONPATH set to the location of the pymeasure repo.