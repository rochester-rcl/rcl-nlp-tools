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
                        The number of topics to model. Default is 20.
  -nw NUM_WORDS, --num_words NUM_WORDS
                        The number of words to export per topic.
                        Default is 3.
```

For example, to retrieve all sentences in a PDF that do not contain words in a stop list of words, starting at page 5, run this command:

`python3 sentence_processor.py --input my_pdf.pdf --output my_output.csv --text stop_words.txt --mode stop --offset 5`

To find all sentences in a PDF that contain words in a list of words starting at page 5, you would just switch the mode to 'find':

`python3 sentence_processor.py --input my_pdf.pdf --output my_output.csv --text stop_words.txt --mode find --offset 5`

The script outputs 2 files, one appended *sentence.csv* and the other appended *topic_model.csv*.

The first file contains the results produced by the SentenceProcessor instance and contains the page number, the matched sentence, and the count for how many times a stop word or key word occurred on the given page.

The second file contains the results of the TopicModeler instance and contains the topic number (set by the -nt or --num_topics flag), the most probabilistic word(s) (set by -nw or --num_words) occurring in that topic, and their probability rating.
