from motor.motor_asyncio import AsyncIOMotorClient
from settings import get_config
setup = get_config()


class Mongo:
    """
    Singleton class for managing the MongoDB connection.

    This class provides a single connection instance to the MongoDB database using the AsyncIOMotorClient.
    The connection is established on the first instantiation of the class and reused for subsequent instantiations.
    """
    _connection = False

    def __new__(cls) -> AsyncIOMotorClient:
        """
        Create a new instance of the class or return the existing connection instance.
        """
        if not cls._connection:
            cls._connection = AsyncIOMotorClient(setup.mongodb_url)
        return cls._connection
