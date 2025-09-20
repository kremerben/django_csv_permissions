# AI Prompt used with Junie / Pycharm AI Assistant

Lets create a plugin for Django that will let us easily handle admin permissions based on a csv file.

First, we need to rough in the typical file structure for a django plugin.

Make a commit of the work here.

Second, we need a management command to download a csv file where the rows are the classes, and the columns are all the User groups' permissions. For each User group there would be 3 columns,  ["add", "change", "view"].

Make another commit of the work here.

Third, a management command to upload the same csv file, verify the data, and update the django admin permissions based on values added to the cells. Any truthy value should count as "has that permission" and any Falsy or empty value would be "no permission".

Make another commit of the work here.

Fourth, Add unit tests to the code. Update the tests until they are passing.  

Make another commit of the work here.

Finally, assess the work and fill in the README.md file with relevant information.

Make another commit of the work here.
