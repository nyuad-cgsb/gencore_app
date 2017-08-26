import os
import unittest
import subprocess


environment_1 = '''
name: env_1
version: 1
build: 0
dependencies:
  - perl
channels:
  - bioconda
  - r
  - defaults
  - condaforge
'''

environment_2 = '''
name: env_2
version: 2
build: 0
dependencies:
  - perl
channels:
  - bioconda
  - r
  - defaults
  - condaforge
'''


def run(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    status = process.returncode
    return (stdout, stderr, status)


def create_env(content, filename='environment.yml'):
    with open(filename, 'w') as fenv:
        fenv.write(content)


def remove_env_file(filename='environment.yml'):
    os.remove(filename)


class IntegrationTest(unittest.TestCase):
    def assertStatusOk(self, status):
        self.assertEqual(status, 0)

    def assertStatusNotOk(self, status):
        self.assertNotEqual(0, status)

    def test_env(self):
        create_env(environment_1)
        from gencore_app.utils import main_env
        e = main_env.from_file('environment.yml')
        self.assertEqual(e.version, '1-0')
        self.assertEqual(e.name, 'env_1')

    def test_labels(self):
        create_env(environment_1)
        from gencore_app.utils import main_env
        from gencore_app.utils.main_upload import gen_labels
        e = main_env.from_file('environment.yml')
        labels = gen_labels(e)
        self.assertEqual(labels, ['main', 'perl', 'perl=latest'])

    def tearDown(self):
        run('rm -f environment.yml')


if __name__ == '__main__':
    unittest.main()
