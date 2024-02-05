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

class ActionChangeOrder(Action):
	def name(self):
		return 'action_change_order'

	def run(self, dispatcher, tracker, domain):
		pizza_size = tracker.get_slot("pizza_size")
		pizza_type = tracker.get_slot("pizza_type")
		pizza_amount = tracker.get_slot("pizza_amount")
		SlotSet("pizza_type", pizza_type)
		SlotSet("pizza_size", pizza_size)
		SlotSet("pizza_amount", pizza_amount)
		return[]


class ActionOrderNumber(Action):
	def name(self):
		return 'action_order_number'

	def run(self, dispatcher, tracker, domain):
		name_person = tracker.get_slot("client_name")
		number_person = tracker.get_slot("phone_number")
		order_number =  str(name_person + "_"+number_person)

		return[SlotSet("order_number", order_number)]

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
