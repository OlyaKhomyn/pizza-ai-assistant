from rasa_sdk import Tracker, FormValidationAction


class ValidateDrinksForm(FormValidationAction):
    def name(self):
        return "validate_drinks_form"

    async def extract_drinks(self, dispatcher, tracker, domain):
        drink = next(tracker.get_latest_entity_values("drink"), None)
        drink_amount = next(tracker.get_latest_entity_values("drink_amount"), None)

        if drink:
            val = {'drink': drink, 'amount': drink_amount if drink_amount else 1}
            drinks = tracker.get_slot('drinks') if tracker.get_slot('drinks') else []
            drinks.append(val)
            return {'drinks': drinks}

        return {}