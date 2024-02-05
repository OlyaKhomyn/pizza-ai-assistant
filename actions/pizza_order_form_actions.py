from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.forms import ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from utils import utils


INTERJECTION_INTENTS = ["item_change", "add_more_toppings", "explain", "remove_item",
						"cancel_order", "general_inquiry", "menu_question", "ask_recommendation"]


class ValidatePizzaOrderForm(FormValidationAction):
	def name(self):
		return "validate_pizza_order_form"

	@staticmethod
	def toppings_db() -> List[Text]:
		return ['funghi', 'artichoke', 'ham', 'olives', 'onions', 'potatoes', 'bacon', 'mortadella',
				'salami', 'mozzarella', 'burrata', 'bufala', 'tomatoes', 'corn', 'salmon', 'tuna']

	@staticmethod
	def pizza_db() -> List[Text]:
		return ['hawaii','margherita','pepperoni','vegetarian','americana','marinara','napoli',
				'romana','4 cheeses','capricciosa','calzone','seafood']

	def validate_pizza(self, dispatcher):
		pizza_type = self.composite_slots.get('pizza_type')
		validated_pizzas = []
		delete_group = []
		for pizza in pizza_type:
			if pizza['value'].lower() in self.pizza_db():
				validated_pizzas.append(pizza)
			else:
				dispatcher.utter_message(text="Unfortunately, {} is not currently available."
											  "\nWe ask you to choose from our available options.".format(pizza['value']))
				delete_group.append(pizza['group'])
		return validated_pizzas, set(delete_group)

	def validate_toppings(self, dispatcher):
		pizza_toppings = self.composite_slots.get('pizza_toppings')
		validated_toppings = []
		delete_group = []
		for topping in pizza_toppings:
			val_top = []
			for val in topping['value']:
				if val.lower() in self.toppings_db():
					val_top.append(val)
				else:
					dispatcher.utter_message(text="Unfortunately, {} topping is not currently available."
												  "\nPlease choose from our available options.".format(val))
			if val_top:
				validated_toppings.append({'value': val_top, 'group': topping['group']})
			else:
				delete_group.append(topping['group'])

		return validated_toppings, set(delete_group)

	async def extract_pizza_type(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS or tracker.latest_action_name == 'action_reset_pizza_change_form':
			return {}

		requested_slot = tracker.get_slot('requested_slot')
		if requested_slot == 'pizza_type' or tracker.latest_message['intent']['name'] == 'item_start_generic':
			if list(tracker.get_latest_entity_values("pizza_type", None)):
				pizza_type = tracker.get_slot('pizza_type') if tracker.get_slot('pizza_type') else []
				if self.composite_slots.get('pizza_type'):
					pizza_type.extend(self.composite_slots.get('pizza_type'))

				return {'pizza_type': pizza_type}

		return {}

	async def extract_pizza_toppings(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS:
			return {}

		requested_slot = tracker.get_slot('requested_slot')
		if requested_slot == 'pizza_type' or tracker.latest_message['intent']['name'] == 'item_start_generic':
			if list(tracker.get_latest_entity_values("pizza_toppings", None)):
				pizza_toppings = tracker.get_slot('pizza_toppings') if tracker.get_slot('pizza_toppings') else []
				if self.composite_slots.get('pizza_toppings'):
					pizza_toppings.extend(self.composite_slots.get('pizza_toppings'))

				return {'pizza_toppings': pizza_toppings}

		return {}

	def check_hanging(self, tracker, entity_name):
		type_groups = [type['group'] for type in tracker.get_slot('pizza_type')] if tracker.get_slot('pizza_type') else []
		toppings_groups = [type['group'] for type in tracker.get_slot('pizza_toppings')] if tracker.get_slot('pizza_toppings') else []
		entity = tracker.get_slot(entity_name) if tracker.get_slot(entity_name) else []
		new_entities = []
		hanging = False
		for ent in entity:
			group = ent['group']
			if group not in type_groups and group not in toppings_groups:
				hanging = True
				continue
			new_entities.append(ent)

		return new_entities, hanging


	async def extract_pizza_size(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS:
			return {}

		val_pizza_size, hanging = self.check_hanging(tracker, 'pizza_size')

		requested_slot = tracker.get_slot('requested_slot')
		if list(tracker.get_latest_entity_values("pizza_size", None)):
			if tracker.latest_message['intent']['name'] == 'item_start_generic':
				if self.composite_slots.get('pizza_size'):
					val_pizza_size.extend(self.composite_slots.get('pizza_size'))

				return {'pizza_size': val_pizza_size}

			if requested_slot == 'pizza_size':
				pizza_sizes = utils.extract_missing_group_entity(tracker, dispatcher, 'pizza_size')
				return pizza_sizes

		return {'pizza_size': val_pizza_size} if hanging else {}

	async def extract_pizza_amount(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS:
			return {}

		val_pizza_amount, hanging = self.check_hanging(tracker, 'pizza_amount')

		requested_slot = tracker.get_slot('requested_slot')
		if list(tracker.get_latest_entity_values("pizza_amount", None)):
			if tracker.latest_message['intent']['name'] == 'item_start_generic':
				if self.composite_slots.get('pizza_amount'):
					val_pizza_amount.extend(self.composite_slots.get('pizza_amount'))

				return {'pizza_amount': val_pizza_amount}

			if requested_slot == 'pizza_amount':
				pizza_amount = utils.extract_missing_group_entity(tracker, dispatcher, 'pizza_amount')
				return pizza_amount

		return {'pizza_amount': val_pizza_amount} if hanging else {}

	async def extract_pizza_crust(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS:
			return {}

		val_pizza_crust, hanging = self.check_hanging(tracker, 'pizza_crust')

		requested_slot = tracker.get_slot('requested_slot')
		if list(tracker.get_latest_entity_values("pizza_crust", None)):
			if tracker.latest_message['intent']['name'] == 'item_start_generic':
				if self.composite_slots.get('pizza_crust'):
					val_pizza_crust.extend(self.composite_slots.get('pizza_crust'))

				return {'pizza_crust': val_pizza_crust}

			if requested_slot == 'pizza_crust':
				pizza_crust = utils.extract_missing_group_entity(tracker, dispatcher, 'pizza_crust')
				return pizza_crust

		return {'pizza_crust': val_pizza_crust} if hanging else {}

	async def extract_add_more_pizza(self, dispatcher, tracker, domain):
		if tracker.latest_message['intent'].get('name') in INTERJECTION_INTENTS:
			return {}

		groups = [type['group'] for type in tracker.get_slot('pizza_type')] if tracker.get_slot('pizza_type') else []
		pizza_toppings_groups = [topping['group'] for topping in tracker.get_slot("pizza_toppings")] if tracker.get_slot('pizza_toppings') else []
		groups.extend(pizza_toppings_groups)

		pizza_crust = tracker.get_slot('pizza_crust') if tracker.get_slot('pizza_crust') else []

		if len(set(groups)) > len(pizza_crust):
			return {'add_more_pizza': "false"}

		return {}

	async def next_requested_slot(self, dispatcher, tracker, domain):
		if tracker.get_slot('pizza_change') == 'true':
			return SlotSet("requested_slot", None)

		pizza_type = tracker.get_slot("pizza_type") if tracker.get_slot("pizza_type") else []
		pizza_toppings = tracker.get_slot("pizza_toppings") if tracker.get_slot("pizza_toppings") else []

		pizza_size = tracker.get_slot("pizza_size")
		pizza_amount = tracker.get_slot("pizza_amount")
		pizza_crust = tracker.get_slot("pizza_crust")
		sliced = tracker.get_slot("sliced")

		if (not pizza_toppings and not pizza_type) or tracker.get_slot("add_more_pizza") == "true":
			return SlotSet("requested_slot", "pizza_type")

		groups = [type['group'] for type in pizza_type]
		groups.extend([topping['group'] for topping in pizza_toppings])

		number_of_groups = len(set(groups))

		if not pizza_size or len(pizza_size) != number_of_groups:
			return SlotSet("requested_slot", "pizza_size")
		if not pizza_amount or len(pizza_amount) != number_of_groups:
			return SlotSet("requested_slot", "pizza_amount")
		if not pizza_crust or len(pizza_crust) != number_of_groups:
			return SlotSet("requested_slot", "pizza_crust")
		if not sliced:
			return SlotSet("requested_slot", "sliced")

		return SlotSet("requested_slot", None)

	def del_empty_group(self, del_group):
		pizza_amount = self.composite_slots.get('pizza_amount')
		pizza_size = self.composite_slots.get('pizza_size')
		pizza_amount = [amount for amount in pizza_amount if amount['group'] not in del_group] if pizza_amount else None
		pizza_size = [size for size in pizza_size if size['group'] not in del_group] if pizza_size else None
		self.composite_slots['pizza_amount'] = pizza_amount
		self.composite_slots['pizza_size'] = pizza_size

	async def run(self, dispatcher, tracker, domain):
		extractor = utils.CompositeEntitiesExtractor(tracker)
		self.composite_slots = extractor.extract()

		if self.composite_slots.get('pizza_type'):
			val_type, del_group = self.validate_pizza(dispatcher)
			self.del_empty_group(del_group)
			self.composite_slots['pizza_type'] = val_type

		if self.composite_slots.get('pizza_toppings'):
			val_top, del_group = self.validate_toppings(dispatcher)
			self.del_empty_group(del_group)
			self.composite_slots['pizza_toppings'] = val_top

		extraction_events = await self.get_extraction_events(
			dispatcher, tracker, domain
		)
		tracker.add_slots(extraction_events)

		validation_events = await self._extract_validation_events(
			dispatcher, tracker, domain
		)

		return validation_events


class AskForPizzaSize(Action):
	def name(self) -> Text:
		return "action_ask_pizza_size"

	def run(self, dispatcher, tracker, domain):
		text = "What size of {} would you like? \nAvailable sizes are: Small, Medium and Large."
		if utils.ask_missing_group(dispatcher, tracker, 'pizza_size', text):
			return []

		dispatcher.utter_message(text="What pizza size would you like?")
		return []


class AskForPizzaAmount(Action):
	def name(self) -> Text:
		return "action_ask_pizza_amount"

	def run(self, dispatcher, tracker, domain):
		if utils.ask_missing_group(dispatcher, tracker, 'pizza_amount', "And how many {} would you like?"):
			return []

		dispatcher.utter_message(text="How many pizzas would you like?")
		return []


class AskForPizzaCrust(Action):
	def name(self):
		return "action_ask_pizza_crust"

	def run(self, dispatcher, tracker, domain):
		text = "What crust do you want for {}? \nYou can choose from: " \
			   "Stuffed crust, Cracker crust, Flat bread crust, Thin crust."
		if utils.ask_missing_group(dispatcher, tracker, 'pizza_crust', text):
			return []

		dispatcher.utter_message(text="What pizza crust would you like?")
		return []


class SetAddMorePizza(Action):
	def name(self):
		return "action_set_add_more_pizza"

	def run(self, dispatcher, tracker, domain):
		return [SlotSet('add_more_pizza', "true")]


