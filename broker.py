import asyncio
import os
import aiokafka

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class KafkaWorker:
    def __init__(self):
        self._producer = aiokafka.AIOKafkaProducer(bootstrap_servers=os.environ.get("KAFKA_URL"))

    async def producing(self, topic: str, data: list[str]):
        """
        Produce messages to a Kafka topic.

        Args:
            topic (str): The Kafka topic to produce messages to.
            data (List[str]): The list of messages to be produced.

        Raises:
            aiokafka.errors.ProducerStoppedError: If there is an error while producing messages.
        """
        producer = self._producer
        await producer.start()
        try:
            for obj in data:
                await producer.send_and_wait(topic=topic, value=bytes(obj, "utf-8"))
                print("message sent")
        finally:
            await producer.stop()

    @staticmethod
    async def _consuming():
        """
        Consume messages from a Kafka topic and parse streamer data using TwitchParser.
        """
        topic = "topic_for_users"
        consumer = aiokafka.AIOKafkaConsumer(topic, bootstrap_servers=os.environ.get("KAFKA_URL"),
                                             loop=asyncio.get_event_loop())
        await consumer.start()
        try:
            from twitch.parser import TwitchParser
            while True:
                async for message in consumer:
                    await TwitchParser().parse_streamer(message.value.decode("utf-8"))
        except Exception:
            await consumer.stop()

    async def start_consuming(self):
        """
        Start consuming messages from Kafka and parsing streamer data.
        """
        await self._consuming()
