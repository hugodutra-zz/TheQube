# -*- coding: utf-8 -*-

# The Qube Messages Translator
# A part of The Qube accessible social networking client
# Copyright © Andre Polykanine A.K.A. Menelion Elensúlë, 2014
# Based on Goslate, a Google translate binding by Zhuo Qiang

from __future__ import unicode_literals

import sys
import os
import json
import itertools
import functools
import time
import socket
import random
import requests
import re
import htmlentitydefs

from urllib import urlencode, unquote_plus, quote_plus
from urlparse import urljoin
from itertools import izip

try:
    import concurrent.futures
    _g_executor = concurrent.futures.ThreadPoolExecutor(max_workers=120)
except ImportError:
    _g_executor = None

from logger import logger
logging = logger.getChild('core.translator')

def _is_sequence(arg):
    return (not isinstance(arg, unicode)) and (
        not isinstance(arg, bytes)) and (
        hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))
    
def _is_bytes(arg):
    return isinstance(arg, bytes)


def _unwrapper_single_element(elements):
    if len(elements) == 1:
        return elements[0]
    return elements

def html_unescape(text):
 def fixup(m):
  text = m.group(0)
  if text[:2] == "&#":
   # character reference
   try:
    if text[:3] == "&#x":
     return unichr(int(text[3:-1], 16))
    else:
     return unichr(int(text[2:-1]))
   except ValueError:
    pass
  else:
   # named entity
   try:
    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
   except KeyError:
    pass
  return text # leave as is
 return re.sub("&#?\w+;", fixup, text)


class TranslatorError(Exception): pass

WRITING_NATIVE = ('trans',)
'''native target language writing system'''

WRITING_ROMAN = ('translit',)
'''romanlized writing system. only valid for some langauges, otherwise it outputs empty string'''

WRITING_NATIVE_AND_ROMAN = WRITING_NATIVE + WRITING_ROMAN
'''both native and roman writing. The output will be a tuple'''

class Translator(object):

    _MAX_LENGTH_PER_QUERY = 1800

    def __init__(self, writing=WRITING_NATIVE, retry_times=4, timeout=4, service_urls=('http://translate.google.com',)):
        self._MIN_TASKS_FOR_CONCURRENT = 2
        self._languages = None
        self._TIMEOUT = timeout
        self._RETRY_TIMES = retry_times
        self._writing = writing
        if _is_sequence(service_urls):
            self._service_urls = service_urls
        else:
            self._service_urls = (service_urls,)

    def _open_url(self, url):
        if len(url) > self._MAX_LENGTH_PER_QUERY+100:
            raise TranslatorError('input too large')

        # Google forbits urllib2 User-Agent: Python-urllib/2.7
        r = requests.get(url, headers={'User-Agent':'Mozilla/4.0'})

        exception = None
        # retry when get (<class 'socket.error'>, error(54, 'Connection reset by peer')
        for i in xrange(self._RETRY_TIMES):
            try:
                response = r.text
                return response
            except Exception as e:
                logging.exception("Translator error. Unable to get response: {0}".format(e))

    def _execute(self, tasks):
        first_tasks = [next(tasks, None) for i in range(self._MIN_TASKS_FOR_CONCURRENT)]
        tasks = (task for task in itertools.chain(first_tasks, tasks) if task)

        if not first_tasks[-1] or not self._executor:
            for each in tasks:
                yield each()
        else:
            exception = None
            for each in [self._executor.submit(t) for t in tasks]:
                if exception:
                    each.cancel()
                else:
                    exception = each.exception()
                    if not exception:
                        yield each.result()

            if exception:
                raise exception


    def _basic_translate(self, text, target_language, source_language, host_language='en'):
        # assert _is_bytes(text)
        
        if not target_language:
            raise TranslatorError('invalid target language')

        if not text.strip():
            return tuple(u'' for i in xrange(len(self._writing))) , unicode(target_language)

        # Browser request for 'hello world' is:
        # http://translate.google.com/translate_a/t?client=t&hl=en&sl=en&tl=zh-CN&ie=UTF-8&oe=UTF-8&multires=1&prev=conf&psl=en&ptl=en&otf=1&it=sel.2016&ssel=0&tsel=0&prev=enter&oc=3&ssel=0&tsel=0&sc=1&text=hello%20world

        # TODO: we could randomly choose one of the google domain URLs for concurrent support
        GOOGLE_TRANSLATE_URL = urljoin(random.choice(self._service_urls), '/translate_a/t')
        GOOGLE_TRANSLATE_PARAMETERS = {
            # 't' client will receiver non-standard json format
            # change client to something other than 't' to get standard json response
            'client': 'z',
            'sl': source_language,
            'tl': target_language,
            'hl': host_language,
            'ie': 'UTF-8',
            'oe': 'UTF-8',
            'text': text
            }

        url = '?'.join((GOOGLE_TRANSLATE_URL, urlencode(GOOGLE_TRANSLATE_PARAMETERS)))
        response_content = self._open_url(url)
        data = json.loads(response_content)
        
        # google may change space to no-break space, we may need to change it back
        translation = tuple(u''.join(i[part] for i in data['sentences']).replace(u'\xA0', u' ') for part in self._writing)
        
        detected_source_language = data['src']
        return translation, detected_source_language


    def get_languages(self, host_language='en'):
        if self._languages:
            return self._languages
        GOOGLE_TRANSLATOR_URL = 'http://translate.google.com/translate_a/l'
        GOOGLE_TRANSLATOR_PARAMETERS = {
            'client': 'z',
            'hl': host_language
            }

        url = '?'.join((GOOGLE_TRANSLATOR_URL, urlencode(GOOGLE_TRANSLATOR_PARAMETERS)))
        response_content = self._open_url(url)
        data = json.loads(response_content)
        languages = data['sl']
        languages.update(data['tl'])
        if 'auto' in languages:
            del languages['auto']
        # Replacing dashes with underscores to fit the getText requirements and turning HTML entities into plain chars
        self._languages = {k.replace('-', '_'): html_unescape(v) for k, v in languages.items()}
        return self._languages


    _SEPARATORS = [quote_plus(i.encode('utf-8')) for i in
                   u'.!?,;。，？！:："“”’‘#$%&()（）*×+/<=>@＃￥[\]…［］^`{|}｛｝～~\n\r\t ']

    def _translate_single_text(self, text, target_language, source_language):
        assert _is_bytes(text)
        def split_text(text):
            start = 0
            text = quote_plus(text)
            length = len(text)
            while (length - start) > self._MAX_LENGTH_PER_QUERY:
                for separator in self._SEPARATORS:
                    index = text.rfind(separator, start, start+self._MAX_LENGTH_PER_QUERY)
                    if index != -1:
                        break
                else:
                    raise Error('input too large')
                end = index + len(separator)
                yield unquote_plus(text[start:end])
                start = end

            yield unquote_plus(text[start:])

        def make_task(text):
            return lambda: self._basic_translate(text, target_language, source_language)[0]

        results = list(self._execute(make_task(i) for i in split_text(text)))
        return tuple(''.join(i[n] for i in results) for n in range(len(self._writing)))


    def translate(self, text, target_language, source_language='', host_language='en'):
        '''Translate text from source language to target language

        .. note::
        
         - Input all source strings at once. Goslate will batch and fetch concurrently for maximize speed.
         - `futures <https://pypi.python.org/pypi/futures>`_ is required for best performance.
         - It returns generator on batch input in order to better fit pipeline architecture

        :param text: The source text(s) to be translated. Batch translation is supported via sequence input
        :type text: UTF-8 str; unicode; string sequence (list, tuple, iterator, generator)

        :param target_language: The language to translate the source text into.
         The value should be one of the language codes listed in :func:`get_languages`
        :type target_language: str; unicode

        :param source_language: The language of the source text.
                                The value should be one of the language codes listed in :func:`get_languages`.
                                If a language is not specified,
                                the system will attempt to identify the source language automatically.
        :type source_language: str; unicode
        
        :returns: the translated text(s)
        
          - unicode: on single string input
          - generator of unicode: on batch input of string sequence
          - tuple: if WRITING_NATIVE_AND_ROMAN is specified, it will return tuple/generator for tuple (u"native", u"roman format")

        :raises:
         - :class:`Error` ('invalid target language') if target language is not set
         - :class:`Error` ('input too large') if input a single large word without any punctuation or space in between


        :Example:
        
         >>> gs = Goslate()
         >>> print(gs.translate('Hello World', 'de'))
         Hallo Welt
         >>> 
         >>> for i in gs.translate(['good', u'morning'], 'de'):
         ...     print(i)
         ...
         gut
         Morgen

        To output romanlized translation

        :Example:
        
         >>> gs_roman = Goslate(WRITING_ROMAN)
         >>> print(gs_roman.translate('Hello', 'zh'))
         Nǐ hǎo
        
        '''


        if not target_language:
            raise Error('invalid target language')

        if target_language.lower() == 'zh':
            target_language = 'zh-CN'
            
        if source_language.lower() == 'zh':
            source_language = 'zh-CN'
            
        if not _is_sequence(text):
            if isinstance(text, unicode):
                text = text.encode('utf-8')
            return _unwrapper_single_element(self._translate_single_text(text, target_language, source_language))

        JOINT = u'\u26ff'
        UTF8_JOINT = (u'\n%s\n' % JOINT).encode('utf-8')

        def join_texts(texts):
            def convert_to_utf8(texts):
                for i in texts:
                    if isinstance(i, unicode):
                        i = i.encode('utf-8')
                    yield i.strip()
                
            texts = convert_to_utf8(texts)
            text = next(texts)
            for i in texts:
                new_text = UTF8_JOINT.join((text, i))
                if len(quote_plus(new_text)) < self._MAX_LENGTH_PER_QUERY:
                    text = new_text
                else:
                    yield text
                    text = i
            yield text


        def make_task(text):
            def task():
                r = self._translate_single_text(text, target_language, source_language)
                r = tuple([i.strip('\n') for i in n.split(JOINT)] for n in r)
                return izip(*r)
                # return r[0]
            return task
                
        return (_unwrapper_single_element(i) for i in
                itertools.chain.from_iterable(self._execute(make_task(i) for i in join_texts(text))))


    def _detect_language(self, text):
        if _is_bytes(text):
            text = text.decode('utf-8')
        return self._basic_translate(text[:50].encode('utf-8'), 'en', '')[1]


    def detect(self, text):
        '''Detect language of the input text

        .. note::
        
         - Input all source strings at once. Goslate will detect concurrently for maximize speed.
         - `futures <https://pypi.python.org/pypi/futures>`_ is required for best performance.
         - It returns generator on batch input in order to better fit pipeline architecture.

        :param text: The source text(s) whose language you want to identify.
                     Batch detection is supported via sequence input
        :type text: UTF-8 str; unicode; sequence of string
        :returns: the language code(s)
        
          - unicode: on single string input
          - generator of unicode: on batch input of string sequence

        :raises: :class:`Error` if parameter type or value is not valid

        Example::
        
         >>> gs = Goslate()
         >>> print(gs.detect('hello world'))
         en
         >>> for i in gs.detect([u'hello', 'Hallo']):
         ...     print(i)
         ...
         en
         de

        '''
        if _is_sequence(text):
            return self._execute(functools.partial(self._detect_language, i) for i in text)
        return self._detect_language(text)


def _main(argv):
    import optparse

    usage = "usage: %prog [options] <file1 file2 ...>\n<stdin> will be used as input source if no file specified."
    
    parser = optparse.OptionParser(usage=usage, version="%%prog %s @ Copyright %s" % (__version__, __copyright__))
    parser.add_option('-t', '--target-language', metavar='zh-CN',
                      help='specify target language to translate the source text into')
    parser.add_option('-s', '--source-language', default='', metavar='en',
                      help='specify source language, if not provide it will identify the source language automatically')
    parser.add_option('-i', '--input-encoding', default=sys.getfilesystemencoding(), metavar='utf-8',
                      help='specify input encoding, default to current console system encoding')
    parser.add_option('-o', '--output-encoding', default=sys.getfilesystemencoding(), metavar='utf-8',
                      help='specify output encoding, default to current console system encoding')
    parser.add_option('-r', '--roman', action="store_true",
                      help='change translation writing to roman (e.g.: output pinyin instead of Chinese charactors for Chinese. It only valid for some of the target languages)')

    
    options, args = parser.parse_args(argv[1:])
    
    if not options.target_language:
        print('Error: missing target language!')
        parser.print_help()
        return
    
    writing = WRITING_NATIVE
    if options.roman:
        writing = WRITING_ROMAN
    
    gs = Goslate(writing=writing)
    import fileinput
    # inputs = fileinput.input(args, mode='rU', openhook=fileinput.hook_encoded(options.input_encoding))
    inputs = fileinput.input(args, mode='rb')
    inputs = (i.decode(options.input_encoding) for i in inputs)
    outputs = gs.translate(inputs, options.target_language, options.source_language)
    for i in outputs:
        sys.stdout.write((i+u'\n').encode(options.output_encoding))
        sys.stdout.flush()
    
    
if __name__ == '__main__':
    try:
        _main(sys.argv)
    except:
        error = sys.exc_info()[1]
        if len(str(error)) > 2:
            print(error)
