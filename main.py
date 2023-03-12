import logging
import subprocess

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)


class SystemManagementDirect(Extension):
    def __init__(self):
        logger.info('Loading extension')
        super(SystemManagementDirect, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_keyword()

        # Find the keyword id using the keyword (since the keyword can be changed by users)
        for keyword_id, keyword in extension.preferences.items():
            if query == keyword:
                self.on_match(keyword_id)
                return HideWindowAction()

    # noinspection PyMethodMayBeStatic
    def on_match(self, keyword_id):
        if keyword_id == 'lock-screen':
            logger.debug("Locking the screen...")
            subprocess.Popen(['loginctl', 'lock-session'])
        if keyword_id == 'suspend':
            logger.debug("Suspending system...")
            subprocess.Popen(['systemctl', 'suspend', '-i'])
        if keyword_id == 'shutdown':
            logger.debug("Shutting down system...")
            subprocess.Popen(['systemctl', 'poweroff', '-i'])
        if keyword_id == 'restart':
            logger.debug("Rebooting system...")
            subprocess.Popen(['systemctl', 'reboot', '-i'])
        if keyword_id == "logout":
            logger.debug("Logging out user...")
            session_id = \
                subprocess.getoutput("loginctl --no-legend --no-pager session-status | head -n 1 | awk '{print $1}'")
            window_ids = subprocess.getoutput("wmctrl -l | awk '{print $1}'").splitlines()

            # Gracefully close all windows before logout
            for window_id in window_ids:
                logger.debug("Gracefully closing window with id=%s", window_id)
                subprocess.Popen(["wmctrl", "-i", "-c", window_id])

            # Kill login session
            logger.debug("Terminating session id=%s", session_id)
            subprocess.Popen(["loginctl", "terminate-session", session_id])


SystemManagementDirect().run()
