from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from os import getenv
load_dotenv()


MQTT_HOST=getenv("MQTT_HOST", "localhost")
MQTT_PORT=getenv("MQTT_PORT", "1883")
MQTT_USERNAME = getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = getenv("MQTT_PASSWORD", "")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


def get_list_of_devices() -> list[str]:
    """Returns a list of devices and their corresponding topics."""
    return [
      {"name": "Living room light", "topic": "moreillon/light-d084cb/command"}, 
      {"name": "Kitchen light", "topic": "/moreillon/light-a4c2f0/command"}
    ]

def send_mqtt_message(topic: str, message: str) -> str:
    """Sends a message to an MQTT topic."""
    client.publish(topic, message)
    return "Message sent!"



tool = FunctionTool.from_defaults(
    send_mqtt_message,
)


# initialize llm
llm = OpenAI(model="gpt-4o-mini")

system_prompt="You can send MQTT messages to control the light. For example, you can send the message { 'state': 'OFF' } to the MQTT topic 'moreillon/light-d084cb/command' to turn off the light."

# initialize openai agent
agent = OpenAIAgent.from_tools(tools=[tool], llm=llm, verbose=True, system_prompt=system_prompt)


client.connect(MQTT_HOST, int(MQTT_PORT))
client.loop_start()
agent.chat("Please turn the lights on in the living room.")
client.loop_stop()
