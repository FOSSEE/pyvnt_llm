"""
LoadingSpinner: Provides a beautiful loading spinner for terminal output.
"""

import threading
import time

class LoadingSpinner:
    """A beautiful loading spinner for terminal"""

    def __init__(self, message="Loading"):
        self.message = message
        self.spinning = False
        self.thread = None
        # Different spinner styles
        self.spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'bars': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
            'arrows': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'clock': ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛'],
            'brain': ['🧠', '💭', '💡', '⚡', '🔥', '✨'],
            'gears': ['⚙️ ', '🔧', '⚡', '💻', '🤖', '🎯']
        }
        self.current_spinner = self.spinners['gears']

    def _spin(self):
        """Internal spinning method"""
        idx = 0
        while self.spinning:
            spinner_char = self.current_spinner[idx % len(self.current_spinner)]
            print(f'\r{spinner_char} {self.message}...', end='', flush=True)
            time.sleep(0.2)
            idx += 1

    def start(self, message=None):
        """Start the spinner"""
        if message:
            self.message = message
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self, final_message=None):
        """Stop the spinner"""
        self.spinning = False
        if self.thread:
            self.thread.join()
        print('\r' + ' ' * 80, end='')
        print('\r', end='')
        if final_message:
            print(f'✅ {final_message}')

# Example usage:
# spinner = LoadingSpinner('Processing')
# spinner.start()
# time.sleep(5)  # Simulate long-running process
# spinner.stop()