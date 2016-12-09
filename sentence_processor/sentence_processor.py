import collections
import argparse
import csv
from PyPDF2 import PdfFileReader as reader
from stop_words import get_stop_words
import re
import nltk
import codecs
from gensim import corpora, models
import gensim
import os

class PDFParse(object):
  def __init__(self, input_pdf, *args, **kwargs):
    self.pdf_reader = PDFParse.open_pdf(input_pdf)
    self.pages = self.pdf_reader.getNumPages()

    if kwargs['offset'] is not None:
      self.offset = kwargs['offset']
      print("Reading PDF from page {}".format(self.offset))

    else:
      self.offset = 0
      print('No offset added, reading PDF from page 1')

  def __iter__(self):
    i = self.offset
    for page in range(self.offset, self.pages):
      pdf_page = self.pdf_reader.getPage(i)
      # reads the text from each page as a string
      yield {'page_number': i, 'text': pdf_page.extractText()}
      i += 1

  @staticmethod
  def open_pdf(input_pdf):
    with open(input_pdf, 'rb'):
      return reader(input_pdf)


class SentenceProcessor(object):

  def __init__(self, txt, mode, *args, **kwargs):
    if txt is not None:
      self.term_list = SentenceProcessor.read_txt_file(txt)

    else:
      self.term_list = []

    self.term_list_mode = mode
    self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

  def tokenize_and_filter(self, input_text):
    sentences = self.sentence_tokenizer.tokenize(input_text)
    filtered_sentences = []

    if self.term_list_mode == 'stop':
      for sentence in sentences:
        if all(term not in sentence for term in self.term_list):
          filtered_sentences.append(sentence)

    elif self.term_list_mode == 'find':
      for sentence in sentences:
        if any(term in sentence for term in self.term_list):
          filtered_sentences.append(sentence)

    else:
      filtered_sentences = sentences

    return filtered_sentences

  @staticmethod
  def read_txt_file(txt_file):
    with codecs.open(txt_file, 'r', encoding='utf-8', errors='ignore') as txt:
      return txt.read().splitlines()


class TopicModeler(object):
  def __init__(self, num_topics):
    self.composite_text = []
    self.num_topics = num_topics
    self.stemmer = nltk.stem.porter.PorterStemmer()
    self.stop_words = get_stop_words('en')
    self.word_tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    self.processed_text = []

  def push_text(self, document):
    self.composite_text.append(document)

  def pre_process_composite_text(self):
    for document in self.composite_text:
      to_lower = document.lower()
      tokenized = self.word_tokenizer.tokenize(to_lower)
      # Remove any words with single or double characters + stop words, not interested in words like 'to'
      filtered_tokens = [word for word in tokenized if word not in self.stop_words and len(word) > 2]
      self.processed_text.append(filtered_tokens)

  def run_topic_model(self):
    tm_dict = corpora.Dictionary(self.processed_text)
    corpus = [tm_dict.doc2bow(document) for document in self.processed_text]
    print(len(corpus))
    return gensim.models.ldamodel.LdaModel(corpus, num_topics=self.num_topics, id2word=tm_dict, passes=20)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Count sentences in a pdf file")  # Setting up our Argument Parser
  named_arguments = parser.add_argument_group('required arguments')
  named_arguments.add_argument('-i', '--input', help="input pdf", required=True, type=str)  # Adding an input argument
  named_arguments.add_argument('-o', '--output', help="output file in csv format", required=True, type=str)  # adding an output argument
  parser.add_argument('-txt', '--text', help="Optional text file for storing key words to look for or to exclude",
                      type=str)
  parser.add_argument('-m', '--mode',
                      help="Set to 'stop' to use the words in the txt file as stop words. Set to 'find' to search for those words.",
                      type=str)
  parser.add_argument('-off', '--offset',
                      help="Enter the page number to start reading the PDF from. If not set, the PDF will start at page 1.",
                      type=int)
  parser.add_argument('-nt', '--num_topics', help="The number of topics to model. Default is 20", default=20, type=int)
  parser.add_argument('-nw', '--num_words', help="The number of words to export per topic", default=3, type=int)

  args = vars(parser.parse_args())  # Get some variables from parse_args dictionary (directory, output)
  required_args = vars(named_arguments.parse_args())

  input_file = required_args['input']
  output_file = required_args['output']
  text = args['text']  # the text file with our control words
  mode = args['mode']
  offset = args['offset']
  num_topics = args['num_topics']
  num_words = args['num_words']


  print("Initializing PDF parser")
  pdf_parser = PDFParse(input_file, offset=offset)

  print("Loading text file {} in {} mode".format(text, mode))
  processor = SentenceProcessor(text, mode)

  topic_modeler = TopicModeler(num_topics)
  print("Processing {}".format(input_file))

  basename, extension = os.path.splitext(output_file)
  sentence_output = "{}_sentence{}".format(basename, extension)
  topic_model_output = "{}_topic_model{}".format(basename, extension)

  with open(sentence_output, 'w') as sentence_csv:
    writer = csv.writer(sentence_csv)
    header = 'page_number', 'sentence', 'term_occurrence_count_on_page'
    # write header row to csv first
    writer.writerow(header)

    for page in pdf_parser:
      text = page['text']
      results = processor.tokenize_and_filter(text)

      if len(results) > 0:
        for index, result in enumerate(results):
          if len(result) > 1:
            formatted = page['page_number'], result, index + 1
            writer.writerow(formatted)

      topic_modeler.push_text(" ".join(results))

    print("Saved sentence count output to {}".format(sentence_output))

  print("Running LDA topic modeling on results")
  topic_modeler.pre_process_composite_text()
  model = topic_modeler.run_topic_model()
  topics = model.show_topics(num_topics=-1, formatted=True, num_words=num_words)

  print("Writing LDA topic model to {}".format(topic_model_output))
  with open(topic_model_output, 'w') as topic_model_csv:
    writer = csv.writer(topic_model_csv)
    header = 'topic_number', 'word', 'probability'
    writer.writerow(header)
    for topic in topics:
      for word in topic[1].split('+'):
        topic_number = topic[0] + 1
        result_split = word.split('*')
        formatted = topic_number, result_split[1].replace('"', ''), result_split[0]
        writer.writerow(formatted)





