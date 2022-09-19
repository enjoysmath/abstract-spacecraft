from PyQt5.QtGui import QFont
from core.app import App
import sys

last_session = 'last_session_pickle.pickle'

if __name__ == '__main__':
    app = App([])
    app.setFont(QFont(app.font().family(), 12))
    app.setStyle('macintosh')  # TODO remove or put as option / what are other styles?
    
    app.load_last_session_or_blank()
    
    sys.exit(app.exec_())