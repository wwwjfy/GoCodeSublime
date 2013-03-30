import sublime
import sublime_plugin

import os
import subprocess


class AutocompleteAll(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(0, 'source.go'):
            return []
        commands = [os.path.join(view.settings().get('GOROOT', ''),
                    'bin', 'gocode')]
        commands.append('-f=csv')
        commands.append('autocomplete')
        commands.append(str(locations[0]))
        p = subprocess.Popen(commands, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = p.communicate(
                            bytes(view.substr(sublime.Region(0, view.size())),
                                  'utf-8'))
        result = []
        for line in output.decode().splitlines():
            parts = line.split(',,')
            type_ = parts[0]
            compl = parts[1]
            desc = parts[2]

            if len(desc) > 0:
                desc = "%s [%s]" % (compl, desc)
            elif len(type_) > 0:
                desc = "%s [%s]" % (compl, type_)
            else:
                desc = compl

            if type_ == 'func':
                flag = False
                if desc:
                    left = desc.find('(')
                    if left > -1:
                        right = desc.find(')')
                        if right > -1:
                            parts = desc[left+1:right].split(', ')
                            count = 0
                            for i in range(len(parts)):
                                parts[count] = (parts[count].
                                                    replace('{', '\\{').
                                                    replace('}', '\\}'))
                                parts[count] = '${{{}:{}}}'.format(
                                                    count + 1, parts[count])
                                count += 1
                            compl += '({})'.format(', '.join(parts))
                            flag = True
                if not flag:
                    compl += '($0)'
            result.append((desc, compl))
        return result