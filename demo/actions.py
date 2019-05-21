# -*- coding: utf-8 -*-

import logging
from typing import Dict, Text, Any, List, Union, Optional

from rasa_core_sdk import ActionExecutionRejection
from rasa_core_sdk import Tracker
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.executor import CollectingDispatcher
from rasa_core_sdk.forms import FormAction, REQUESTED_SLOT

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet, UserUtteranceReverted, \
                                 ConversationPaused
from lemma_farasa  import lemmatize

# logger = logging.getLogger(__name__)


class Action_trakhees_locations(Action):
    """Returns the trakhees_locations utterance"""

    TRAKHEES_LOCATION = ["المدينة العالمية", "سوق التنين 1 و2", "مول ابن بطوطة", "جزر جميرا",
    " ديسكفري جاردن", "الحدائق", "نخلة جميرا", "نخلة ديره", "جميرا بارك", "قرية جميرا", "دبي ووتر فرونت",
    "جزر لعالم", "ليمتليس", "داون تاون جبل علي", "الفرجان", "قرية جبل علي", " الخيل بلازا", "جميع مشروعات جمارك دبي",
    "مواني دبي العالمية"]

    def name(self):
        return "action_trakhees_locations"

    def run(self, dispatcher, tracker, domain):

        freezone_license_location = next(tracker.get_latest_entity_values('freezone_license_location'), None)
        lemmatized_locations = [lemmatize(lemmatize(i)) for i in self.TRAKHEES_LOCATION]
        # retrieve the correct chitchat utterance dependent on the intent
        print(lemmatized_locations)
        print("Value is {}".format(freezone_license_location))
        print([True if freezone_license_location in i else False for i in lemmatized_locations])
        if any([True if freezone_license_location in i else False for i in lemmatized_locations]):
            dispatcher.utter_template('utter_approve_trakhees_location', tracker)
        else:
            dispatcher.utter_template('utter_deny_trakhees_location', tracker)
        dispatcher.utter_template('utter_trakhees_locations', tracker)
        return []

class CancelLicenceForm(FormAction):

    def name(self):
       # type: () -> Text
       """Unique identifier of the form"""

       return "cancel_licence_form"

    @staticmethod
    def required_slots(tracker):
       # type: () -> List[Text]
       """A list of required slots that the form has to fill"""

       can_cancel_licence = tracker.get_slot("can_cancel_licence")
       if can_cancel_licence is None:
           return ["can_cancel_licence", "cancelled_licence_type",
            "cancelled_licence_company_type"]
       elif not can_cancel_licence:
           return ["can_cancel_licence"]
       else:
           cancelled_licence_type = tracker.get_slot("cancelled_licence_type")
           if cancelled_licence_type is None or cancelled_licence_type == "company":
               return ["can_cancel_licence", "cancelled_licence_type",
                "cancelled_licence_company_type"]
           else:
               return ["can_cancel_licence", "cancelled_licence_type"]

    def slot_mappings(self):
            # type: () -> Dict[Text: Union[Dict, List[Dict]]]
            """A dictionary to map required slots to
                - an extracted entity
                - intent: value pairs
                - a whole message
                or a list of them, where a first match will be picked"""

            return {"cancelled_licence_type": [self.from_entity(entity="cancelled_licence_type",
                                                intent="ask_to_cancel_visa"),
                                                self.from_entity(entity="licenses_list",
                                                                intent="enter_data"),
                                                self.from_entity(entity="cancelled_licence_type",
                                                                intent="choose")],
                    "can_cancel_licence": [self.from_intent(intent='affirm',
                                                     value=True),
                                           self.from_intent(intent='deny',
                                                     value=False),
                                           self.from_entity(entity="can_cancel_licence",
                                                     intent="choose")],
                    "cancelled_licence_company_type": [self.from_entity(entity="cancelled_licence_company_type",
                                                        intent="ask_to_cancel_visa"),
                                                       self.from_entity(entity="cancelled_licence_company_type",
                                                                        intent="choose")]}

    def validate_can_cancel_licence(self,
                             value: Text,
                             dispatcher: CollectingDispatcher,
                             tracker: Tracker,
                             domain: Dict[Text, Any]) -> Optional[Text]:
            """Validate can_cancel_licence value."""

            if isinstance(value, str):
                if 'true' in value:
                    # convert "out..." to True
                    return True
                elif 'false' in value:
                    # convert "in..." to False
                    return False
                else:
                    dispatcher.utter_template('utter_wrong_can_cancel_licence',
                                              tracker)
                    # validation failed, set slot to None
                    return None

            else:
                # affirm/deny was picked up as T/F
                return value

    def validate_cancelled_licence_type(self,
                             value: Text,
                             dispatcher: CollectingDispatcher,
                             tracker: Tracker,
                             domain: Dict[Text, Any]) -> Optional[Text]:
            """Validate cancelled_licence_type."""

            if "تجاري" in value or "commerical" in value:
                return "commerical"
            elif "شركة" in value or "company" in value:
                return "company"
            elif "حر" in value or "freezone" in value:
                return "freezone"
            else:
                dispatcher.utter_template('utter_cancelled_licence_not_supported', tracker)

                # affirm/deny was picked up as T/F
                return None

    def validate_cancelled_licence_company_type(self,
                             value: Text,
                             dispatcher: CollectingDispatcher,
                             tracker: Tracker,
                             domain: Dict[Text, Any]) -> Optional[Text]:
            """Validate cancelled_licence_company_type"""

            print("In cancelled_licence_company_type, val: {}".format(value))
            if "محلي" in value or "law" in value:
                return "law"
            elif "فرع" in value or "branch" in value:
                return "branch"
            else:
                dispatcher.utter_template('utter_cancelled_licence_company_not_supported', tracker)

                # affirm/deny was picked up as T/F
                return None


    def submit(self, dispatcher, tracker, domain):
       # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
       """Define what the form has to do
           after all required slots are filled"""

       # utter submit template
       can_cancel_licence = tracker.get_slot("can_cancel_licence")
       if not can_cancel_licence:
           dispatcher.utter_template('utter_can_not_cancel_licence', tracker)
       else:
           cancelled_licence_type = tracker.get_slot("cancelled_licence_type")
           if cancelled_licence_type == "company":
               cancelled_licence_company_type = tracker.get_slot("cancelled_licence_company_type")
               if cancelled_licence_company_type in ["law", "branch"]:
                   dispatcher.utter_template('utter_cancelled_licence_company_' +
                    cancelled_licence_company_type, tracker)
               else:
                    dispatcher.utter_template('utter_cancelled_licence_company_not_supported', tracker)
           elif cancelled_licence_type in ["freezone", "commerical"]:
               dispatcher.utter_template('utter_cancelled_licence_' + cancelled_licence_type, tracker)
           else:
               dispatcher.utter_template('utter_cancelled_licence_not_supported', tracker)

       return [SlotSet("can_cancel_licence", None), SlotSet("cancelled_licence_type", None),
        SlotSet("cancelled_licence_company_type", None)]

# class ActionStoreName(Action):
#     """Stores the users name in a slot"""
#
#     def name(self):
#         return "action_store_name"
#
#     def run(self, dispatcher, tracker, domain):
#
#         person_name = next(tracker.get_latest_entity_values('name'), None)
#
#         # if no name was extracted, use the whole user utterance
#         # in future this will be stored in a `name_unconfirmed` slot and the
#         # user will be asked to confirm their name
#         if not person_name:
#             person_name = tracker.latest_message.get('text')
#
#         return [SlotSet('person_name', person_name)]
#
#
# class ActionStoreCompany(Action):
#     """Stores the company name in a slot"""
#
#     def name(self):
#         return "action_store_company"
#
#     def run(self, dispatcher, tracker, domain):
#         company = next(tracker.get_latest_entity_values('company'), None)
#
#         # if no company entity was extracted, use the whole user utterance
#         # in future this will be stored in a `company_unconfirmed` slot and
#         # the user will be asked to confirm their company name
#         if not company:
#             company = tracker.latest_message.get('text')
#
#         return [SlotSet('company_name', company)]
#
#
# class ActionStoreJob(Action):
#     """Stores the job in a slot"""
#
#     def name(self):
#         return "action_store_job"
#
#     def run(self, dispatcher, tracker, domain):
#         jobfunction = next(tracker.get_latest_entity_values('jobfunction'),
#                            None)
#
#         # if no jobfunction entity was extracted, use the whole user utterance
#         # in future this will be stored in a `job_unconfirmed` slot and
#         # the user will be asked to confirm their job title
#         if not jobfunction:
#             jobfunction = tracker.latest_message.get('text')
#
#         return [SlotSet('job_function', jobfunction)]
#
#
# class ActionStoreEmail(Action):
#     """Stores the email in a slot"""
#
#     def name(self):
#         return "action_store_email"
#
#     def run(self, dispatcher, tracker, domain):
#         email = next(tracker.get_latest_entity_values('email'), None)
#
#         # if no email entity was recognised, prompt the user to enter a valid
#         # email and go back a turn in the conversation to ensure future
#         # predictions aren't affected
#         if not email:
#             dispatcher.utter_message("We need your email, "
#                                      "please enter a valid one.")
#             return [UserUtteranceReverted()]
#
#         return [SlotSet('email', email)]
#
#
# class ActionPause(Action):
#     """Pause the conversation"""
#
#     def name(self):
#         return "action_pause"
#
#     def run(self, dispatcher, tracker, domain):
#
#         return [ConversationPaused()]
