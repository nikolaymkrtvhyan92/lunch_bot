"""
Singleton lock для предотвращения множественного запуска бота
"""
import os
import sys
import fcntl

class SingletonLock:
    """Гарантирует что только один инстанс приложения запущен"""
    
    def __init__(self, lockfile='/tmp/lunch_bot.lock'):
        self.lockfile = lockfile
        self.fp = None
    
    def acquire(self):
        """Получить блокировку"""
        try:
            self.fp = open(self.lockfile, 'w')
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.fp.write(str(os.getpid()))
            self.fp.flush()
            return True
        except IOError:
            print("⚠️ Другой инстанс бота уже запущен! Выходим...")
            return False
    
    def release(self):
        """Освободить блокировку"""
        if self.fp:
            fcntl.lockf(self.fp, fcntl.LOCK_UN)
            self.fp.close()
            try:
                os.remove(self.lockfile)
            except:
                pass

