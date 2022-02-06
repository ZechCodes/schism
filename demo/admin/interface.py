class AdminAPI:
    def __init__(self):
        print("ADMIN CREATED")

    def say_hi(self) -> str:
        return "Hi from the admin service"

    async def start(self):
        print("Admin API has started!")
