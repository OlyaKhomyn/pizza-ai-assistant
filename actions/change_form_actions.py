from rasa_sdk import Action
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.events import SlotSet

from utils import utils


class ValidateChangeForm(FormValidationAction):
    def name(self):
        return "validate_change_form"

    async def extract_group_to_change(self, dispatcher, tracker, domain):
        if tracker.latest_message['intent'].get('name') == 'remove_item':
            pizza_toppings = list(tracker.get_latest_entity_values("pizza_toppings", None))
            pizza_type = next(tracker.get_latest_entity_values("pizza_type"), None)
            if pizza_toppings and pizza_type:
                return {}

            if not pizza_type and not pizza_toppings:
                return {}

            group = utils.get_group(tracker)
            return {"group_to_change": group} if group else {}


        requested_slot = tracker.get_slot("requested_slot")
        group = tracker.get_slot("group_to_change")

        if group:
            return {}

        if tracker.get_slot('requested_slot') == 'group_to_change' or len(utils.get_group_list(tracker))==1:
            group = utils.get_group(tracker)
        if not group and requested_slot == 'group_to_change':
            dispatcher.utter_message(text="Couldn't find the pizza that you specified.")
            return {}

        return {"group_to_change": group} if group else {}

    async def extract_entity_to_change(self, dispatcher, tracker, domain):
        change_dict = {}

        if tracker.latest_message['intent'].get('name') == 'remove_item':
            pizza_toppings = list(tracker.get_latest_entity_values("pizza_toppings", None))
            pizza_type = next(tracker.get_latest_entity_values("pizza_type"), None)
            if pizza_toppings and pizza_type:
                dispatcher.utter_message(text='Please specify either pizza topping or pizza type at once.')
                return {}

            if pizza_toppings:
                change_dict['pizza_toppings'] = pizza_toppings
            if pizza_type:
                change_dict['pizza_type'] = pizza_type
                change_dict['remove'] = True

            return {'entity_to_change': change_dict}

        if (tracker.get_slot('group_to_change') and tracker.get_slot('requested_slot') == 'entity_to_change') \
                or len(utils.get_group_list(tracker))==1:

            pizza_size = next(tracker.get_latest_entity_values("pizza_size"), None)
            pizza_type = next(tracker.get_latest_entity_values("pizza_type"), None)
            pizza_amount = next(tracker.get_latest_entity_values("pizza_amount"), None)
            pizza_crust = next(tracker.get_latest_entity_values("pizza_crust"), None)

            if pizza_size:
                change_dict['pizza_size'] = pizza_size
            if pizza_type:
                change_dict['pizza_type'] = pizza_type
            if pizza_amount:
                change_dict['pizza_amount'] = pizza_amount
            if pizza_crust:
                change_dict['pizza_crust'] = pizza_crust

        return {'entity_to_change': change_dict} if change_dict else {}

    def change_entity(self, tracker, dispatcher, entity_name):
        entity_to_change = tracker.get_slot('entity_to_change')

        if entity_to_change and entity_to_change.get(entity_name):
            group_to_change = tracker.get_slot('group_to_change')
            entity = tracker.get_slot(entity_name) if tracker.get_slot(entity_name) else []

            for type in entity:
                if type['group'] == group_to_change:
                    dispatcher.utter_message(text="Very well. {} has been successfully changed to {}.".
                                             format(type['value'].capitalize(), entity_to_change.get(entity_name)))
                    type['value'] = entity_to_change.get(entity_name)

            return {entity_name: entity}

        return {}

    def remove_group(self, tracker, entity):
        group_to_change = tracker.get_slot('group_to_change')

        elements = tracker.get_slot(entity) if tracker.get_slot(entity) else []
        elements = [element for element in elements if element['group'] != group_to_change]

        return {entity: elements}

    async def extract_pizza_type(self, dispatcher, tracker, domain):
        entity_to_change = tracker.get_slot('entity_to_change')
        remove_pizza = entity_to_change.get('pizza_type') if entity_to_change else None

        if entity_to_change and remove_pizza:
            if entity_to_change.get('remove'):
                remove_pizza = entity_to_change.get('pizza_type')
                dispatcher.utter_message(text="{} has been successfully removed.".format(remove_pizza.capitalize()))
                return self.remove_group(tracker, 'pizza_type')

        return self.change_entity(tracker, dispatcher, 'pizza_type')

    async def extract_pizza_size(self, dispatcher, tracker, domain):
        entity_to_change = tracker.get_slot('entity_to_change')
        remove_pizza = entity_to_change.get('pizza_type') if entity_to_change else None

        if entity_to_change and remove_pizza:
            if entity_to_change.get('remove'):
                return self.remove_group(tracker, 'pizza_size')

        return self.change_entity(tracker, dispatcher, 'pizza_size')

    async def extract_pizza_amount(self, dispatcher, tracker, domain):
        entity_to_change = tracker.get_slot('entity_to_change')
        remove_pizza = entity_to_change.get('pizza_type') if entity_to_change else None

        if entity_to_change and remove_pizza:
            if entity_to_change.get('remove'):
                return self.remove_group(tracker, 'pizza_amount')

        return self.change_entity(tracker, dispatcher, 'pizza_amount')

    async def extract_pizza_crust(self, dispatcher, tracker, domain):
        entity_to_change = tracker.get_slot('entity_to_change')
        remove_pizza = entity_to_change.get('pizza_type') if entity_to_change else None

        if entity_to_change and remove_pizza:
            if entity_to_change.get('remove'):
                return self.remove_group(tracker, 'pizza_crust')

        return self.change_entity(tracker, dispatcher, 'pizza_crust')

    async def extract_pizza_toppings(self, dispatcher, tracker, domain):
        entity_to_change = tracker.get_slot('entity_to_change')

        if entity_to_change and entity_to_change.get('pizza_toppings'):
            group_to_change = tracker.get_slot('group_to_change')
            pizza_toppings = tracker.get_slot('pizza_toppings') if tracker.get_slot('pizza_toppings') else []

            remove_toppings = entity_to_change.get('pizza_toppings')

            for topping in pizza_toppings:
                if topping['group'] == group_to_change:
                    for remove_top in remove_toppings:
                        if remove_top in topping['value']:
                            topping['value'].remove(remove_top)
                            dispatcher.utter_message(text="{} has been successfully removed.".
                                                     format(remove_top.capitalize()))

            # remove empty
            pizza_toppings = [pizza_topping for pizza_topping in pizza_toppings if pizza_topping['value']]

            return {'pizza_toppings': pizza_toppings}

        return {}

    async def next_requested_slot(self, dispatcher, tracker, domain):
        group_to_change = tracker.get_slot("group_to_change")
        entity_to_change = tracker.get_slot("entity_to_change")

        if not group_to_change:
            return SlotSet("requested_slot", "group_to_change")
        if not entity_to_change:
            return SlotSet("requested_slot", "entity_to_change")

        return SlotSet("requested_slot", None)


class AskForPizzaChangeType(Action):
    def name(self):
        return "action_ask_group_to_change"

    def run(self, dispatcher, tracker, domain):
        response = "Please choose a pizza which you want to change: "

        pizza_choices = utils.get_current_pizza_groups_choices(tracker)
        response += pizza_choices

        dispatcher.utter_message(text=response)
        return []


class ResetPizzaChangeForm(Action):
    def name(self):
        return "action_reset_pizza_change_form"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet('group_to_change', None), SlotSet('entity_to_change', None), SlotSet('pizza_change', "false")]


class SetPizzaChangeFlag(Action):
    def name(self):
        return "action_set_pizza_change_flag"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet('pizza_change', "true")]
