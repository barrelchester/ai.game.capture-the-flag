# Capture the Flag Video Game Project Structure

Development code (Jupyter notebooks) and other dev artifacts reside in the 'dev' folder.
The 'app' folder holds the finished python files and other artifacts (in the 'resources' folder) 
necessary for running the game.


Coding Recommendations from my many years of experience in Python:

Please use snake_case for methods and variables, and UpperCamelCase for class names.

When naming variables please don't abbreviate so much that it's impossible to guess what
it stands for (e.g. "Training Function" as 'train_func' vs 'trnfn'). 
Also, when appropriate/necessary, try to name them in a hierarchical manner, like 'player_location' 
rather than 'location' when it's not clear what type of location we're talking about.

Try to comment only where needed to explain a decision or a complex expression. Over-commenting is
tedious (e.g. #this is the constructor for Agent).

Try to write self documenting code that is clear for the reader, not compact complex
indecipherable expressions. 
(e.g. don't do something like this please
x = [l[:next(random.choice(list(range(len(v)))))] for l in iter(open(y).readlines())][:z])
Bias yourself toward writing things in multiple lines to show the steps. Not necessary for
obvious/common things.

It's better to put methods & variables in a class than have them free floating in some module file.
I prefer the only floating method to be the one that starts everything. There's really never a need
for floating variables.

Please name/alias imports (e.g. import my_functions as my_funcs) so that references to members of these
modules can be identified clearly in the code (e.g. my_funcs.awesome_func(x)) rather than
importing everything with no qualifier (from my_functions import *) like in the nightmarish
probabilistic wumpus code.

