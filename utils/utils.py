import re
import itertools


class CompositeEntitiesExtractor:
    """
    Derived from https://github.com/BeWe11/rasa_composite_entities/tree/master
    """

    def __init__(self, tracker):
        self.tracker = tracker

    def get_patterns(self):
        patterns = [
            "pizza_amount pizza_size pizza_type",
            "pizza_size pizza_type",
            "pizza_amount pizza_type",
            "pizza_amount pizza_type pizza_size",
            "pizza_type",
        ]
        return patterns

    def replace_entity_values(self, text, entities):
        s = 0
        new_text = ""
        index_map = []
        for i in range(0, len(entities)):
            new_text += text[s: entities[i]['start']]
            entity_start = len(new_text)
            new_text += entities[i]['entity']
            index_map.append((i, entity_start, len(new_text)))
            s = entities[i]['end']

        return new_text, index_map

    def get_contained_entity_indices(self, patterns, new_text, index_map):
        contained_entity_indices = []
        for pattern in sorted(patterns, key=len, reverse=True):
            for match in re.finditer(pattern, new_text):
                contained_in_match = [index for (index, start, end) in index_map
                                      if start >= match.start() and end <= match.end()]
                all_indices = set(
                    itertools.chain.from_iterable(contained_entity_indices)
                )
                if all_indices & set(contained_in_match):
                    continue
                contained_entity_indices.append(contained_in_match)

        return contained_entity_indices

    def set_new_slots_values(self, contained_entity_indices, entities):
        pizza_types = self.tracker.get_slot("pizza_type") if self.tracker.get_slot("pizza_type") else []
        pizza_toppings = self.tracker.get_slot("pizza_toppings") if self.tracker.get_slot("pizza_toppings") else []

        if pizza_types or pizza_toppings:
            groups = [type['group'] for type in pizza_types]
            groups.extend([topping['group'] for topping in pizza_toppings])

            group = max(groups) + 1
        else:
            group = 1

        slots_val = {}
        for contained_in_match in contained_entity_indices:
            contained_entities = list(
                sorted([entities[i] for i in contained_in_match], key=lambda x: x["start"])
            )

            for entity in contained_entities:
                val = slots_val.get(entity['entity'], [])
                val.append({'value': entity['value'], 'group': group})
                slots_val[entity['entity']] = val
            group += 1

        return slots_val, group

    def extract_toppings(self, entities, group):
        toppings = []

        for entity in entities:
            if entity['entity'] == 'pizza_toppings':
                toppings.append(entity['value'])

        toppings = [{'value': toppings, 'group': group}] if toppings else None

        return toppings

    def extract(self):
        latest_message = self.tracker.latest_message
        entities = latest_message['entities']

        new_text, index_map = self.replace_entity_values(latest_message['text'], entities)

        patterns = self.get_patterns()

        contained_entity_indices = self.get_contained_entity_indices(patterns, new_text, index_map)

        slots, group = self.set_new_slots_values(contained_entity_indices, entities)
        toppings = self.extract_toppings(entities, group)
        slots['pizza_toppings'] = toppings

        return slots


def extract_missing_group_entity(tracker, dispatcher, entity_name):
    current_entity_val = tracker.get_slot(entity_name)
    pizza_types = tracker.get_slot('pizza_type')
    pizza_toppings = tracker.get_slot("pizza_toppings")

    if not pizza_types and not pizza_toppings:
        return {}

    pizza_types = pizza_types if pizza_types else []
    pizza_toppings = pizza_toppings if pizza_toppings else []

    groups = [type['group'] for type in pizza_types]
    groups.extend([topping['group'] for topping in pizza_toppings])

    num_groups = max(groups)

    if current_entity_val and len(current_entity_val) == int(num_groups):
        return {}

    if not current_entity_val:
        missing_groups = groups
    else:
        missing_groups = sorted(set(groups) - set([size['group'] for size in current_entity_val]))

    entities = tracker.latest_message['entities']
    new_entity_val = []

    extracted_entities = [entity for entity in entities if entity['entity'] == entity_name]

    for entity in extracted_entities:
        slot_val = {'value': entity['value'], 'group': missing_groups[0]}
        new_entity_val.append(slot_val)

    if not new_entity_val:
        new_entity_val = current_entity_val
    else:
        if current_entity_val:
            for ent in current_entity_val:
                if not ent in new_entity_val:
                    new_entity_val.append(ent)

    return {entity_name: new_entity_val}


def ask_missing_group(dispatcher, tracker, entity_name, message):
    entity_val = tracker.get_slot(entity_name)
    pizza_types = tracker.get_slot("pizza_type")
    pizza_toppings = tracker.get_slot("pizza_toppings")

    if pizza_types or pizza_toppings:
        pizza_types = pizza_types if pizza_types else []
        pizza_toppings = pizza_toppings if pizza_toppings else []

        groups = [type['group'] for type in pizza_types]
        groups.extend([topping['group'] for topping in pizza_toppings])

        num_groups = max(groups)
    else:
        num_groups = 0

    for i in range(1, int(num_groups) + 1):
        if entity_val:
            val = [type for type in entity_val if type['group'] == i]
        else:
            val = None

        if not val:
            if pizza_types:
                type = [type for type in pizza_types if type['group'] == i]
                if type:
                    dispatcher.utter_message(text=message.format(type[0]['value']))
                    return True

            if pizza_toppings:
                topping = [topping for topping in pizza_toppings if topping['group'] == i]
                if topping:
                    dispatcher.utter_message(text=message.format(' and '.join(topping[0]['value']) +' pizza'))
                    return True

    return False


def get_group(tracker):
    toppings = tracker.get_slot("pizza_toppings") if tracker.get_slot("pizza_toppings") else []
    types = tracker.get_slot("pizza_type") if tracker.get_slot("pizza_type") else []

    type_groups = [t['group'] for t in types]
    topping_groups = [t['group'] for t in toppings]
    type_groups.extend(topping_groups)

    if len(set(type_groups)) == 1:
        if types:
            group = types[0]['group']
        else:
            group = toppings[0]['group']
        return group

    type_to_add = next(tracker.get_latest_entity_values("pizza_type"), None)
    if type_to_add:
        exist = [t for t in types if t['value'].lower() == type_to_add.lower()]
        if exist:
            return exist[0]['group']

    topping_to_add = list(tracker.get_latest_entity_values("pizza_toppings")) \
        if list(tracker.get_latest_entity_values("pizza_toppings")) else []
    if topping_to_add:
        exist = [t for t in toppings if set(topping_to_add).issubset(set(t['value']))]
        if exist:
            return exist[0]['group']

    return None

class CurrentOrder:
    def __init__(self, tracker):
        self.tracker = tracker

    def get_group_val(self, slot, group):
        if slot:
            for val in slot:
                if val['group'] == group:
                    return val['value']
        return ''

    def form_pizza_group_msg(self, type, pizza_amount, pizza_size, pizza_crust, pizza_toppings):
        amount = self.get_group_val(pizza_amount, type['group'])
        size = self.get_group_val(pizza_size, type['group'])
        crust = self.get_group_val(pizza_crust, type['group'])
        toppings = self.get_group_val(pizza_toppings, type['group'])

        msg = "{} {} {} {}".format(amount, size, crust, type['value'])
        if toppings:
            msg += " with extra {}".format(' and '.join(toppings))

        return msg

    def form_pizza_custom_group_msg(self, topping, pizza_amount, pizza_size, pizza_crust):
        amount = self.get_group_val(pizza_amount, topping['group'])
        size = self.get_group_val(pizza_size, topping['group'])
        crust = self.get_group_val(pizza_crust, topping['group'])

        msg = "{} {} {} pizza with {}".format(amount, size, ' and '.join(topping['value']), crust)

        return msg

    def get_drinks(self, text):
        drinks = self.tracker.get_slot('drinks')

        if drinks:
            text += ' and'
            for drink in drinks:
                text += " {} {}".format(drink['amount'], drink['drink'])
                text += ','
            text = text[:-1]
        text += '.'

        return text

    def get_current_order(self):
        pizza_size = self.tracker.get_slot("pizza_size")
        pizza_toppings = self.tracker.get_slot("pizza_toppings")
        pizza_type = self.tracker.get_slot("pizza_type")
        pizza_amount = self.tracker.get_slot("pizza_amount")
        pizza_crust = self.tracker.get_slot("pizza_crust")
        sliced = self.tracker.get_slot("sliced")

        msgs = []

        if pizza_type:
            for type in pizza_type:
                msg = self.form_pizza_group_msg(type, pizza_amount, pizza_size, pizza_crust, pizza_toppings)
                msgs.append(msg)

        if pizza_toppings:
            for topping in pizza_toppings:
                group = topping['group']

                if pizza_type:
                    type_group = [type['group'] for type in pizza_type if type['group'] == group]
                    if type_group and type_group[0] == group:
                        continue

                msg = self.form_pizza_custom_group_msg(topping, pizza_amount, pizza_size, pizza_crust)
                msgs.append(msg)

        text = "Great. So your order is {} {}".format(', '.join(msgs), "sliced" if sliced == "yes" else "not sliced")
        text = self.get_drinks(text)

        return text


def get_group_list(tracker):
    toppings = tracker.get_slot("pizza_toppings") if tracker.get_slot("pizza_toppings") else []
    types = tracker.get_slot("pizza_type") if tracker.get_slot("pizza_type") else []

    type_groups = [t['group'] for t in types]
    topping_groups = [t['group'] for t in toppings]
    type_groups.extend(topping_groups)

    return set(type_groups)


def get_current_pizza_groups_choices(tracker):
    toppings = tracker.get_slot("pizza_toppings") if tracker.get_slot("pizza_toppings") else []
    types = tracker.get_slot("pizza_type") if tracker.get_slot("pizza_type") else []
    type_values = [type['value'] for type in types]
    topping_values = [(topping['value'],topping['group'])  for topping in toppings]

    msg = ' or '.join(type_values)

    type_groups = [type['group'] for type in types]

    if toppings:
        msg = msg + ' or ' if msg else msg
        for val, group in topping_values:
            if group in type_groups:
                continue
            msg += ' and '.join(val)
            msg += ' pizza'
            msg += ' or '

        msg = msg[:-4]
    msg += '.'

    return msg
