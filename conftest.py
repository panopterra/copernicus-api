import os

import pytest


@pytest.fixture(scope='module')
def test_resources_dir():
    """
    Yields the corresponding test resources directory for the module currently
    being tested.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    str
        Path to test resources directory.
    """

    current_file_path = os.path.abspath(os.getenv('PYTEST_CURRENT_TEST')).replace('\\', '/').replace('//', '/')
    root_dir = current_file_path.split('test/')[0]

    test_file_path = current_file_path.split('test/')[1]
    test_file_path = '::'.join(test_file_path.split('::')[:-1])
    test_file_path = test_file_path.replace('_test.py', '')
    test_resources_dir = os.path.join(root_dir, 'test_resources', test_file_path).replace('\\', '/').replace('//', '/')
    yield test_resources_dir

