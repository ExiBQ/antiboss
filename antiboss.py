import requests
import six
import abc
import os
import time
from html.parser import HTMLParser


class DownLoadWebPage(object):
    """docstring for DownLoadWebPage"""

    def __init__(self, url):
        self.url = url
        self.text = None

    def _do_download(self):
        r = requests.get(self.url)
        if r.status_code != 200:
            raise Warning
        self.text = r.text

    def get_web_page(self):
        self._do_download()
        return self.text


@six.add_metaclass(abc.ABCMeta)
class Parser(HTMLParser):
    """docstring for Parser"""

    def __init__(self, web_page, base_url, tag_class_identifier_name):
        super(Parser, self).__init__()
        self.web_page = web_page
        self.base_url = base_url
        self.tag_class_identifier_name = tag_class_identifier_name
        self.identifier_tag = None
        self.subject_dict = {}
        self.flag = False

    def set_base_url(self, url):
        self.base_url = url

    def handle_starttag(self, tag, attrs):
        if self.flag == True:
            for attr in attrs:
                if attr[0] == 'href':
                    self.subject_dict[None] = self.base_url + attr[1]
        else:
            for attr in attrs:
                if attr[1] == self.tag_class_identifier_name and attr[0] == 'class':
                    self.flag = True
                    self.identifier_tag = tag

    def handle_data(self, data):
        if self.flag is True:
            url = self.subject_dict[None]
            del self.subject_dict[None]
            self.subject_dict[data] = url

    def handle_endtag(self, tag):
        if self.flag == True and tag == self.identifier_tag:
            self.flag = False

    def get_subject_dict(self):
        return self.subject_dict

    def parse(self):
        self.feed(self.web_page)
        return bool(self.subject_dict)


class V2EXParser(Parser):
    """ """

    def __init__(self, web_page, base_url):
        super(V2EXParser, self).__init__(web_page, base_url, 'item_title')


class V2EXReviewParser(Parser):
    """docstring for V2EXReviewParser"""

    def __init__(self, web_page, base_url):
        super(V2EXReviewParser, self).__init__(web_page, base_url, 'reply_content')

    def handle_starttag(self, tag, attrs):
        if self.flag == True:
            pass
        else:
            for attr in attrs:
                if attr[1] == self.tag_class_identifier_name and attr[0] == 'class':
                    self.flag = True
                    self.identifier_tag = tag

    def handle_data(self, data):
        if self.flag is True:
            self.subject_dict[data] = self.base_url


@six.add_metaclass(abc.ABCMeta)
class AntiBossBrowser(object):
    """docstring for AntiBossBrowser"""

    def __init__(self, parser_list, ):
        if not isinstance(parser_list, list):
            raise TypeError
        for parser in parser_list:
            if not issubclass(parser, Parser):
                raise TypeError
        self.parser_list = parser_list
        self.this_url = None
        self.this_page = None
        """this page is a list of human readable items"""
        self.previous_pages = []
        self.previous_page_urls = []
        self.clear = lambda: os.system('cls') if os.name == 'nt' else lambda: os.system('clear')

    def clear_console(self):
        self.clear()

    def show_this_page(self):
        self.clear_console()
        for item in self.this_page.keys():
            print(item + '\n')

    def _get_page(self, web_page, base_url):
        for parser in self.parser_list:
            instance = parser(web_page, base_url)
            if instance.parse():
                return instance.get_subject_dict()
        return None

    def jump_to(self, url):

        if url == self.this_url:
            return
        """alreadly at url"""
        web_page = DownLoadWebPage(url).get_web_page()
        anti_boss_page = self._get_page(web_page, url)

        if anti_boss_page is not None:
            if self.this_page is not None:
                self.previous_pages.append(self.this_page)  # TODO   limit of previous pages
                self.previous_page_urls.append(self.this_url)
            self.this_page = anti_boss_page
            self.this_url = url
            self.show_this_page()

        else:
            self.clear_console()
            print('cant jump to %s' % url)

            time.sleep(2)
            if self.this_page:
                self.show_this_page()

    def jump_to_select(self, num):
        if not 0 <= num < len(self.this_page.values()):
            raise IndexError
        else:

            self.jump_to(list(self.this_page.values())[num])

    def jump_back(self):
        if not self.previous_page_urls:
            return
        self.this_page = self.previous_pages.pop()
        self.this_url = self.previous_page_urls.pop()
        self.show_this_page()


class Loop(object):
    """ """

    def __init__(self, ins):
        self.ins = ins

    def run(self):
        url = input('input url to start anti your boss\n')
        self.ins.jump_to(url if url.startswith('http') else 'https://' + url)
        while True:
            select = input('[num] to go forward, b to go back\n')
            if select == 'b':
                self.ins.jump_back()
            elif select.isdigit():
                try:
                    self.ins.jump_to_select(int(select))
                except IndexError as e:
                    print(e)
            else:
                print('wrong input!')


def main():
    j = AntiBossBrowser(parser_list=[V2EXParser, V2EXReviewParser])
    l = Loop(j)
    l.run()


if __name__ == '__main__':
    main()