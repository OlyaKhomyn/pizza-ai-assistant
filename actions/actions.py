from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.forms import ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from utils import utils


class ActionUtterConfirm(Action):
	def name(self):
		return "action_utter_confirm"

	def run(self, dispatcher, tracker, domain):
		current_order = utils.CurrentOrder(tracker)
		text = current_order.get_current_order()

		text += " Do you want to add any more pizza?"

		dispatcher.utter_message(text=text)
		return []

class ActionUtterAnythingElse(Action):
	def name(self):
		return "action_utter_anything_else"

	def run(self, dispatcher, tracker, domain):
		current_order = utils.CurrentOrder(tracker)
		text = current_order.get_current_order()

		text += " Do you want to add anything else?"

		dispatcher.utter_message(text=text)
		return []


class CancelOrder(Action):
	def name(self):
		return "action_cancel_order"

	def run(self, dispatcher, tracker, domain):
		return [AllSlotsReset()]
