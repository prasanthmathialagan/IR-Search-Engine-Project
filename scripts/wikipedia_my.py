# Sample script for getting summary of a topic from wikipedia
# For more details https://github.com/goldsmith/Wikipedia
# This script requires wikipedia module. This can be installed by the command "pip install wikipedia"
import wikipedia

wikipedia.set_lang("en")
data = wikipedia.summary("machine learning")
print(data)

ny = wikipedia.page("New York");