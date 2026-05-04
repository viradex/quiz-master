from PyQt6.QtWidgets import QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class BackgroundMusicPlayer(QWidget):
    def __init__(self, url):
        super().__init__()
        self.url = url

        self._setup_player()

    def _setup_player(self):
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()

        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(self.url)
        self.audio_output.setVolume(0.5)
        self.player.mediaStatusChanged.connect(self._handle_loop)

    def _handle_loop(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def start(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop_and_reset(self):
        self.player.stop()
