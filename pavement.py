from paver.easy import task, sh


@task
def run_tests():
    sh('export PYTHONPATH=$PYTHONPATH:$(pwd)')
    sh('flake8')
    sh('python tests/test_esri_harvest.py ')
    sh('python tests/test_filecache.py ')
