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


class ActionPizzaQuestionPositive(Action):
	def name(self):
		return 'action_pizza_question_positive'

	def run(self, dispatcher, tracker, domain):
		mapping = {
			"cheese": ["burrata", "bufala", "mozzarella"],
			"meat": ["salami", "mortadella", "bacon", "ham"]
		}
		available_toppings = ['funghi','artichoke','ham','olives','onions','potatoes','bacon','mortadella',
							  'salami','mozzarella','burrata','bufala','tomatoes','corn','salmon','tuna']
		available_types = ['hawaii','margherita','pepperoni','vegetarian','americana','marinara','napoli',
						   'romana','4 cheeses','capricciosa','calzone','seafood']

		extractor = utils.CompositeEntitiesExtractor(tracker)
		slots = extractor.extract()

		pizza_type = slots.get('pizza_type')
		pizza_toppings = slots.get('pizza_toppings')

		av = []
		na = []
		text = ""

		if pizza_type:
			for type in pizza_type:
				if type['value'].lower() in available_types:
					av.append(type['value'].lower())
				else:
					na.append(type['value'].lower())
			if av:
				text += "Yes, we have {} pizza on a menu. ".format(' and '.join(av))
			if na:
				text += "Unfortunately, we don't have {}.".format(' and '.join(na))
			dispatcher.utter_message(text=text)

		av = []
		na = []
		mapped = []
		text = ""
		if pizza_toppings:
			for topping in pizza_toppings[0]['value']:
				if topping.lower() in available_toppings:
					av.append(topping.lower())
				elif mapping.get(topping):
					mapped.append("Yes, we have {} topping. You can choose from: {}.".
								  format(topping, ', '.join(mapping.get(topping))))
				else:
					na.append(topping.lower())
			if av:
				text += "Yes, we have {} topping. ".format(' and '.join(av))
			if mapped:
				text += ' '.join(mapped)
			if na:
				text += "Unfortunately, we don't have {} topping.".format(' and '.join(na))
			dispatcher.utter_message(text=text)

		if not pizza_type and not pizza_toppings:
			dispatcher.utter_message(text="Sorry I didn't understand it. Can you rephrase it please?")
		return []


class ActionPizzaQuestionNegative(Action):
	def name(self):
		return 'action_pizza_question_negative'

	def run(self, dispatcher, tracker, domain):
		mapping = {
			"cheese": ["pepperoni", "americana", 'romana', 'seafood', 'napoli', 'hawaii'],
			"meat": ["margherita", "hawaii", "vegetarian", 'romana', '4 cheeses']
		}

		extractor = utils.CompositeEntitiesExtractor(tracker)
		slots = extractor.extract()

		pizza_toppings = slots.get('pizza_toppings')
		text = ""

		av = []
		if pizza_toppings:
			for topping in pizza_toppings[0]['value']:
				if mapping.get(topping):
					text += "Yes, we have pizza with no {}. You can choose from: {}.".\
						format(topping, ', '.join(mapping.get(topping)))
				else:
					av.append(topping)
			if av:
				text += "Yes, we have pizza without {}. " \
						"You can choose from our custom toppings anything you like.".format(' and '.join(av))

		if text:
			dispatcher.utter_message(text=text)
		else:
			dispatcher.utter_message(text="Sorry I didn't understand it. Can you rephrase it please?")
		return []


class GetToppingsListAction(Action):
	def name(self):
		return "action_get_toppings_list"

	def run(self, dispatcher, tracker, domain):
		available_toppings = ['funghi', 'artichoke', 'ham', 'olives', 'onions', 'potatoes', 'bacon', 'mortadella',
							  'salami', 'mozzarella', 'burrata', 'bufala', 'tomatoes', 'corn', 'salmon', 'tuna']

		response = "Here are the toppings that we offer: {}.".format(', '.join(available_toppings))

		dispatcher.utter_message(text=response)
		return []


class GetMenuAction(Action):
	def name(self):
		return "action_get_menu"

	def run(self, dispatcher, tracker, domain):
		available_toppings = ['funghi', 'artichoke', 'ham', 'olives', 'onions', 'potatoes', 'bacon', 'mortadella',
							  'salami', 'mozzarella', 'burrata', 'bufala', 'tomatoes', 'corn', 'salmon', 'tuna']
		available_pizza = ['hawaii','margherita','pepperoni','vegetarian','americana','marinara','napoli',
						   'romana','4 cheeses','capricciosa','calzone','seafood']

		response = "We are offering the following pizza: {}. " \
				   "\nYou can also choose from our custom toppings: {}.".\
			format(', '.join(available_pizza), ', '.join(available_toppings))

		dispatcher.utter_message(text=response)
		return []
