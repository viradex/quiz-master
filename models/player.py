class Player:
    def __init__(self, player_id, nickname, connection):
        self.player_id = player_id
        self.nickname = nickname
        self.connection = connection

        self.score = 0
        self.connected = True
        self.last_active_time = 0.0

        self.current_answer = None
        self.has_answered = False

    def update_score(self, points):
        self.score += points

    def submit_answer(self, answer_index):
        self.current_answer = answer_index
        self.has_answered = True

    def reset_for_question(self):
        self.current_answer = None
        self.has_answered = False

    def disconnect(self):
        self.connected = False

    def update_activity(self, timestamp):
        self.last_active_time = timestamp
