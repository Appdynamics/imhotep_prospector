from imhotep.tools import Tool
from collections import defaultdict
import re
import logging

log = logging.getLogger(__name__)


root = logging.getLogger()
root.setLevel(logging.DEBUG)

OUTPUT_STYLE_PYLINT = "pylint"
OUTPUT_STYLE_PROSPECTOR = "prospector"
OUTPUT_STYLE = OUTPUT_STYLE_PROSPECTOR


class Prospector(Tool):
    response_format = re.compile(r'(?P<filename>.*):(?P<line_num>\d+):'
                                 '(?P<message>.*)')
    line_number_format = re.compile(r'  Line: (?P<line_num>\d+)')

    '''
    The following is adapted from the original imhotep_pylint,
    and will work when the prospector is told to output in pylint
    format. You can switch back to this format of output using
    the defined OUTPUT_STYLE options above.
    '''
    def process_line(self, dirname, line):
        match = self.response_format.search(line)
        if match is not None:
            if len(self.filenames) != 0:
                if match.group('filename') not in self.filenames:
                    return
            filename, line, messages = match.groups()
            return filename, line, messages

    def get_command(self, dirname, **kwargs):
        if OUTPUT_STYLE is OUTPUT_STYLE_PYLINT:
            cmd = 'prospector --output-format=pylint'
        else:
            cmd = 'prospector '
        return cmd

    def process_pylint_output(self, result, dirname):
        retval = defaultdict(lambda: defaultdict(list))
        for line in result.split('\n'):
            output = self.process_line(dirname, line)
            if output is not None:
                filename, lineno, messages = output

                if filename.startswith(dirname):
                    filename = filename[len(dirname) + 1:]
                retval[filename][lineno].append(messages)
        return retval

    def process_prospector_output(self, result):
        retval = defaultdict(lambda: defaultdict(list))

        sections = result.split('\n\n')  # split on blank lines
        sections.pop(0)  # First section is just the log header "Messages"
        for section in sections:
            lines = section.split('\n')  # examine each line
            # first line is going to be file name
            filename = lines.pop(0)
            # Only return messages on files that were changed
            if filename in self.filenames:
                current_line = 0
                for line in lines:
                    match = self.line_number_format.search(line)
                    if match is not None:
                        current_line = match.group('line_num')
                    else:
                        # this is a message line
                        retval[filename][current_line].append(line)
        return retval

    def invoke(self, dirname, filenames=set(), linter_configs=set()):
        """
        Main entrypoint for all plugins.

        Returns results in the format of:

        {'filename': {
          'line_number': [
            'error1',
            'error2'
            ]
          }
        }


        """
        retval = defaultdict(lambda: defaultdict(list))

        log.debug("Here's the files passed in: %s", filenames)
        self.filenames = filenames
        # Run the prospector command on the root directory
        # of the project as passed in.
        cmd = '%s %s' % (self.get_command(
            dirname, linter_configs=linter_configs), dirname)
        log.debug("cmd = %s", cmd)
        result = self.executor(cmd)
        if OUTPUT_STYLE is OUTPUT_STYLE_PYLINT:
            retval = self.process_pylint_output(result, dirname)
        else:
            retval = self.process_prospector_output(result)

        return retval
