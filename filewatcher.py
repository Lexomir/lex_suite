import os
import sys 
import time

class FileWatcher(object):

    # Constructor
    def __init__(self, file, callback=None, refresh_delay_secs=1, *args, **kwargs):
        self._cached_stamp = 0
        self.filename = file
        self.refresh_delay_secs = refresh_delay_secs
        self.file_exists = False

    # Look for changes
    def look(self):
        did_exist = self.file_exists
        self.file_exists = os.path.exists(self.filename)

        if self.file_exists:
            stamp = os.stat(self.filename).st_mtime
            if stamp != self._cached_stamp:
                self._cached_stamp = stamp
                # File has changed, so do something...
                print('File changed:', self.filename)
                return True
        return did_exist != self.file_exists

    # Keep watching in a loop        
    def watch(self):
        while self.running: 
            try: 
                # Look for changes
                self.look() 
            except KeyboardInterrupt: 
                print('\nDone') 
                break 
            except FileNotFoundError:
                # Action on file not found
                pass
            except: 
                print('Unhandled error: %s' % sys.exc_info()[0])
            yield

    def stop(self):
        self.running = False
