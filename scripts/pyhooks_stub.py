# Copyright 2024 MosaicML LLM Foundry authors
# SPDX-License-Identifier: Apache-2.0

# git clone git@github.com:databricks-mosaic/mcloud.git to /tmp/mcloud
# git checkout pyhookbuffered
import os
import subprocess
import sys
import time

# execute some shell commands

rank = os.environ.get('RANK')
if rank is None:
    raise ValueError('RANK not set')

try:
    subprocess.run([
        'git',
        'clone',
        'git@github.com:databricks-mosaic/mcloud.git',
        f'/tmp/mcloud-{rank}',
    ],
                   check=True)
    subprocess.run(['git', 'checkout', 'pyhookbuffered'],
                   cwd=f'/tmp/mcloud-{rank}',
                   check=True)
except:
    print('repo already exists, nbd')

# add the following to the PYTHONPATH:
# /tmp/mcloud/finetuning/pyhook
sys.path.append(f'/tmp/mcloud-{rank}/finetuning/')

# run `pip install fickling`
try:
    subprocess.run(['pip', 'install', 'fickling'], check=True)
except:
    time.sleep(5)

try:
    import pyhook
except:
    raise ImportError('Failed to import pyhook from mcloud')
