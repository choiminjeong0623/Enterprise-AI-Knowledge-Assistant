class HistoryBuilder:

    def __init__(self, repository):
        self.repository = repository

    def build(self, limit=5):
        """
        TODO:
        Conversation + Message 구조로 전환 후
        MessageRepository를 이용하도록 리팩터링 예정.
        """

        return []