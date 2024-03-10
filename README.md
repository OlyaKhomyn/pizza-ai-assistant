# Pizza Assistant

### About
Artificial Intelligence text/vocal user assistant that is able to automate a task of ordering a pizza. It has been designed to handle the monotonous tasks that otherwise would require speaking to the human operator such as: asking what is on a menu, place an order for a delivery or takeaway, order a drink, ask for a recommendation and others. 

The assistant was developed using Rasa v3.6, which is an open-source Conversational AI framework. The model was then connected to Amazon Alexa Skill for vocal integration.

### Demo

https://github.com/OlyaKhomyn/pizza-ai-assistant/assets/41692593/44e9ac00-41a0-4758-b517-e7fa9e34aae3


### Properties
Users are able to ask various informative question in the middle of conversation, change their orders, ask for a recommendation, remove items and/or cancel the whole order. The assistant, therefore, can handle all types of users, such as under-informative, over-informative, low coherence or high coherence. Depending on the user input, the assistant can take different conversational paths. 

Here are the possible input sentences that it understands: 
<ul>
  <li>”What do you have on a menu?” - the system informs about available options</li>
  <li>”I want to order a small Margherita pizza” - starts asking about all required slots and placing an order</li>
  <li>”Can you recommend me anything?” - asks about user preferences and provides a recommendation</li>
  <li>”Add extra onions topping” - add requested topping to the order.</li>
</ul>

### Evaluation
To test different NLU pipelines, a separate test file was created that consists of the sentences that were not used for the training (78 sentences, 3 sentences per intent on the average). Build-in Rasa rasa test nlu command was used to run the tests.

<img width="200" alt="image" src="https://github.com/OlyaKhomyn/pizza-ai-assistant/assets/41692593/011094c6-7143-4c69-80b9-11ff5f110f50">
<img width="200" alt="image" src="https://github.com/OlyaKhomyn/pizza-ai-assistant/assets/41692593/3e474b92-ba38-4ffd-bcc3-59b303e45e41">

### Train the chatbot
```
rasa train
```

### Test chatbot
```
rasa test
```

### Talk to chatbot
```
rasa shell
```
