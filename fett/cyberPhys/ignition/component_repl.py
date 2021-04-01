from prompt_toolkit import PromptSession

from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import NestedCompleter
import pygments
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

from component_tester import *


class ServiceParser:
    def __init__(self, srv_grp):
        self._srv_grp = srv_grp

    def parse_and_run(self, tokens):
        toknames, values = list(zip(*tokens))
        if any([Error == i for i in toknames]):
            print("Syntax Error")
            return

        if len(tokens) > 0:
            if len(tokens) == 3 and values[0] == 'START ':
                self._srv_grp.start_component(values[1])
            elif len(tokens) == 3 and values[0] == 'STOP ':
                self._srv_grp.stop_component(values[1])
            else:
                return


service_names = set(ComponentHandler.keywords.keys())
service_completer = NestedCompleter.from_nested_dict({'START': service_names,
                                                      'STOP': service_names,
                                                      'SEND': service_names})

class ServiceLexer(RegexLexer):
    name = 'Service'
    aliases = ['service']
    filenames = ['*.service']

    tokens = {
        'root': [
            (fr'(STOP |START )(\w+)', bygroups(Keyword, Name)),
            ('(SEND )(\w+ )(\w+)', bygroups(Keyword, Text, Text))
        ]
    }


def main():
    active_lexer = ServiceLexer()
    session = PromptSession()
    service_group = ComponentHandler()
    active_parser = ServiceParser(service_group)

    while True:
        try:
            text = session.prompt('> ', lexer=PygmentsLexer(ServiceLexer), completer=service_completer )
        except KeyboardInterrupt:
            continue
        except EOFError:
            service_group.exit()
            break
        else:
            tokens = list(pygments.lex(text, active_lexer))
            active_parser.parse_and_run(tokens)
            #print('You entered:', tokens)
    print('GoodBye!')

if __name__ == '__main__':
    main()
