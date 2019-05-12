from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import http.client
import logging
import os
import typing
import json
import socket
import sys
from typing import Any, Dict, List, Optional, Text, Tuple

from rasa_nlu.config import InvalidConfigError, RasaNLUModelConfig
from rasa_nlu.extractors import EntityExtractor
from rasa_nlu.model import Metadata
from rasa_nlu.training_data import Message, TrainingData
from rasa_nlu.components import Component

def lemmatize(text: Text):

        data = ""
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', 9876)
        sock.connect(server_address)
        try:
            # Send data
            sock.sendall(bytes(text + '\n', "utf-8"))
            data = str(sock.recv(16384), "utf-8").strip()
        finally:
            sock.close()
        return data

class FarasaLemmatizer(Component):
    name = "lemma_farasa"

    requires = ["spacy_nlp", "spacy_doc"]
    provides = ["spacy_doc"]

    def doc_for_text(self, text, spacy_nlp):
        if self.component_config.get("case_sensitive"):
            return spacy_nlp(text)
        else:
            return spacy_nlp(text.lower())

    def train(self,
              training_data: TrainingData,
              config: RasaNLUModelConfig,
              **kwargs: Any) -> None:

        spacy_nlp = kwargs.get("spacy_nlp", None)

        for example in training_data.training_examples:
            example.text = example.text.replace('{', '(').replace('}', ')')
            entities = sorted(example.get("entities", []), key=lambda k: k['start'])
            new_msg = ""
            idx = 0
            for i in range(len(example.text)):
                if idx < len(entities) and i == entities[idx]['start']:
                    new_msg += '{'
                    new_msg += example.text[i]
                elif idx < len(entities) and i == entities[idx]['end'] - 1:
                    new_msg += example.text[i]
                    new_msg += '}'
                    idx += 1
                else:
                    new_msg += example.text[i]

            new_msg = lemmatize(lemmatize(new_msg)).replace('{ ', '{').replace(' }', '}')
            tmp_msg = ""
            idx = 0
            for i in range(len(new_msg)):
                if new_msg[i] == '{':
                    entities[idx]['start'] = len(tmp_msg)
                elif new_msg[i] == '}':
                    entities[idx]['end'] = len(tmp_msg)
                    entities[idx]['value'] = tmp_msg[entities[idx]['start']:entities[idx]['end']]
                    idx += 1
                else:
                    tmp_msg += new_msg[i]

            example.text = tmp_msg
            example.set("entities", entities)
            example.set("spacy_doc", self.doc_for_text(example.text, spacy_nlp))

    def process(self, message: Message, **kwargs: Any) -> None:
        spacy_nlp = kwargs.get("spacy_nlp", None)
        message.text = lemmatize(lemmatize(message.text))
        message.set("spacy_doc", self.doc_for_text(message.text, spacy_nlp))
