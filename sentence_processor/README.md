# Sentence Processor

## Usage Options



```
required arguments:
  -i INPUT, --input INPUT
                        input pdf
  -o OUTPUT, --output OUTPUT
                        output file in csv format
                        
optional arguments:
  -h, --help            show this help message and exit
  -txt TEXT, --text TEXT
                        Optional text file for storing key words to look for
                        or to exclude
  -m MODE, --mode MODE  Set to 'stop' to use the words in the txt file as stop
                        words. Set to 'find' to search for those words.
  -off OFFSET, --offset OFFSET
                        Enter the page number to start reading the PDF from.
                        If not set, the PDF will start at page 1.
  -nt NUM_TOPICS, --num_topics NUM_TOPICS
                        The number of topics to model. Default is 20
  -nw NUM_WORDS, --num_words NUM_WORDS
                        The number of words to export per topic
```
