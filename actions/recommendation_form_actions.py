import random

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


class ValidateRecommendationForm(FormValidationAction):
    def name(self):
        return "validate_recommendation_form"

    def get_mapping(self, val):
        map = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
        }
        amount = map.get(val.lower())
        return amount if amount else 1

    async def extract_recommendation_amount(self, dispatcher, tracker, domain):
        pizza_amount = next(tracker.get_latest_entity_values("pizza_amount"), None)
        if pizza_amount:
            try:
                pizza_amount = int(pizza_amount)
            except ValueError:
                pizza_amount = self.get_mapping(pizza_amount)

        return {"recommendation_amount": pizza_amount} if pizza_amount else {}


class SetIngredientPos(Action):
    def name(self):
        return 'set_ingredient_pos'

    def run(self, dispatcher, tracker, domain):
        ingredient_pos = next(tracker.get_latest_entity_values("pizza_toppings"), None)
        return [SlotSet("ingredient_pos", ingredient_pos.lower())] if ingredient_pos else []


class SetIngredientNeg(Action):
    def name(self):
        return 'set_ingredient_neg'

    def run(self, dispatcher, tracker, domain):
        ingredient_neg = next(tracker.get_latest_entity_values("pizza_toppings"), None)
        return [SlotSet("ingredient_neg", ingredient_neg.lower())] if ingredient_neg else []


class SetAllergiesList(Action):
    def name(self):
        return 'set_allergies_list'

    def utter_response(self, dispatcher, allergies_list):
        resp = "We'll make sure to omit any {} products."
        gluten = "Okay! We'll make your pizza with the special gluten-free dough."

        for allergy in allergies_list:
            if allergy.lower() == 'gluten':
                dispatcher.utter_message(text=gluten)
            else:
                dispatcher.utter_message(text=resp.format(allergy.lower()))

    def run(self, dispatcher, tracker, domain):
        allergies_list = list(tracker.get_latest_entity_values("allergy_list", None))
        self.utter_response(dispatcher, allergies_list)

        return [SlotSet("allergy_list", allergies_list)] if allergies_list else []


class MakeRecommendation(Action):
    def name(self):
        return 'make_recommendation_action'

    @staticmethod
    def toppings_db() -> List[Text]:
        return ['funghi', 'artichoke', 'ham', 'olives', 'onions', 'potatoes', 'bacon', 'mortadella',
                'salami', 'mozzarella', 'burrata', 'bufala', 'tomatoes', 'corn', 'salmon', 'tuna']

    def run(self, dispatcher, tracker, domain):
        rec_amount = tracker.get_slot("recommendation_amount")
        ingredient_pos = tracker.get_slot("ingredient_pos")
        ingredient_neg = tracker.get_slot("ingredient_neg")
        allergies_list = tracker.get_slot("allergy_list")

        toppings = set(self.toppings_db())

        allergy_toppings = {
            'lactose': set(['mozzarella', 'bufala', 'burrata']),
            'fish': set(['tuna', 'salmon'])
        }

        no_ingredient = {
            'cheese': set(['mozzarella', 'bufala', 'burrata']),
            'meat': set(['ham', 'bacon', 'mortadella', 'salami'])
        }

        add_ingredient = None

        if ingredient_neg:
            if no_ingredient.get(ingredient_neg):
                toppings = toppings.difference(no_ingredient.get(ingredient_neg))
            else:
                toppings = toppings.difference(set([ingredient_neg]))
        if ingredient_pos:
            if ingredient_pos in toppings:
                add_ingredient = ingredient_pos
            else:
                dispatcher.utter_message(text="Unfortunately, {} topping is not available.".format(ingredient_pos))
        if allergies_list:
            for allergy in allergies_list:
                al = allergy_toppings.get(allergy.lower())
                if al:
                    toppings = toppings.difference(al)

        pizzas = []
        resp = "How about "
        for _ in range(0, rec_amount):
            suggestion = [random.choice(list(toppings))]
            toppings = toppings.difference(set(suggestion))
            if add_ingredient:
                suggestion.append(add_ingredient)
            resp += 'one '
            resp += ' and '.join(suggestion)
            resp += ' pizza, '
            pizzas.append(suggestion)
        resp = resp[:-2]
        resp += '?'
        dispatcher.utter_message(text=resp)
        return [SlotSet('suggestion', pizzas)]


class AddRecommendationToOrder(Action):
    def name(self):
        return 'add_recommendation_to_order'

    def run(self, dispatcher, tracker, domain):
        suggestions = tracker.get_slot('suggestion')
        groups = utils.get_group_list(tracker)

        if groups:
            group = max(groups) + 1
        else:
            group = 1

        toppings = tracker.get_slot('pizza_toppings') if tracker.get_slot('pizza_toppings') else []
        for suggestion in suggestions:
            toppings.append({'value': suggestion, 'group': group})
            group += 1

        return [SlotSet('pizza_toppings', toppings)]
