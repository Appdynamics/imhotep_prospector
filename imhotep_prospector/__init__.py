import os
import sys
import logging

# because the logger of imhotep doesn't allow configuration,
# we allow this environment variable to be set so that we can
# direct logging to standard out if necessary. Helps in debugging
# Jenkins jobs.
if os.environ.get('IMHOTEP_PROSPECTOR_STDOUT_LOG'):
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ch)
