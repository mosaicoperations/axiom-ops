import os
import sys

def get_log_file_location() -> str:
    main_file = getattr(sys.modules['__main__'], '__file__', None)
    if main_file:
        root_path = os.path.dirname(os.path.abspath(main_file))
    else:
        root_path = os.getcwd()
    
    log_directory = os.path.join(root_path, 'logs')
    
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    return os.path.join(log_directory, 'application.log')