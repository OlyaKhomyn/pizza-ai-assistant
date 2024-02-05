from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.forms import ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from utils import utils


class ValidateExtraToppingsForm(FormValidationAction):
	def name(self):
		return 'validate_extra_toppings_form'

	@staticmethod
	def toppings_db() -> List[Text]:
		return ['funghi', 'artichoke', 'ham', 'olives', 'onions', 'potatoes', 'bacon', 'mortadella',
				'salami', 'mozzarella', 'burrata', 'bufala', 'tomatoes', 'corn', 'salmon', 'tuna']

	def validate_toppings(self, dispatcher, pizza_toppings):
		validated_toppings = []
		for topping in pizza_toppings:
			if topping.lower() in self.toppings_db():
				validated_toppings.append(topping)
			else:
				dispatcher.utter_message(text="Unfortunately, {} topping is not currently available."
											  "\nPlease choose from our available options.".format(topping))
		return validated_toppings

	async def extract_more_toppings(self, dispatcher, tracker, domain):
		requested_slot = tracker.get_slot("requested_slot")

		if requested_slot != 'group_to_add':
			more_toppings = list(tracker.get_latest_entity_values("pizza_toppings"))
			more_toppings = self.validate_toppings(dispatcher, more_toppings)

			if more_toppings:
				return {"more_toppings": more_toppings}

		return {}

	async def extract_group_to_add(self, dispatcher, tracker, domain):
		requested_slot = tracker.get_slot("requested_slot")
		group = tracker.get_slot("group_to_add")

		if group:
			return {}

		group = utils.get_group(tracker)
		if not group and requested_slot=='group_to_add':
			dispatcher.utter_message(text="Couldn't find the pizza that you specified.")
			return {}

		return {"group_to_add": group} if group else {}

	async def extract_pizza_toppings(self, dispatcher, tracker, domain):
		more_toppings = tracker.get_slot("more_toppings")
		group = tracker.get_slot("group_to_add")

		if not more_toppings or not group:
			return {}

		pizza_toppings = tracker.get_slot("pizza_toppings") if tracker.get_slot("pizza_toppings") else []
		exist = [t for t in pizza_toppings if t['group'] == group]

		if exist:
			exist[0]['value'].extend(more_toppings)
		else:
			new_val = {'value': more_toppings, 'group': group}
			pizza_toppings.append(new_val)

		dispatcher.utter_message(text="Extra {} have been added your order.".format(' and '.join(more_toppings)))

		return {'pizza_toppings': pizza_toppings}

	async def next_requested_slot(self, dispatcher, tracker, domain):
		more_toppings = tracker.get_slot("more_toppings")
		group_to_add = tracker.get_slot("group_to_add")

		if not more_toppings:
			return SlotSet("requested_slot", "more_toppings")
		if not group_to_add:
			return SlotSet("requested_slot", "group_to_add")

		return SlotSet("requested_slot", None)


class AskForPizzaType(Action):
	def name(self):
		return "action_ask_group_to_add"

	def run(self, dispatcher, tracker, domain):
		response = "Please choose a pizza for which you want to add the toppings: "

		pizza_choices = utils.get_current_pizza_groups_choices(tracker)
		response += pizza_choices

		dispatcher.utter_message(text=response)
		return []


class ActionResetExtraToppingsForm(Action):
	def name(self):
		return 'action_reset_extra_toppings'

	def run(self, dispatcher, tracker, domain):
		return [SlotSet("more_toppings", None), SlotSet("group_to_add", None), SlotSet('pizza_change', "false")]
