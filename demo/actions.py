# -*- coding: utf-8 -*-

import logging

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet, UserUtteranceReverted, \
                                 ConversationPaused

# logger = logging.getLogger(__name__)


class Action_trakhees_locations(Action):
    """Returns the trakhees_locations utterance"""

    def name(self):
        return "action_trakhees_locations"

    def run(self, dispatcher, tracker, domain):

        freezone_license_location = next(tracker.get_latest_entity_values('freezone_license_location'), None)

        # retrieve the correct chitchat utterance dependent on the intent
        if freezone_license_location in []:
            dispatcher.utter_template('utter_approve_trakhees_location', tracker)
        else:
            dispatcher.utter_template('utter_deny_trakhees_location', tracker)
        dispatcher.utter_template('utter_list_all_trakhees_locations', tracker)
        return []


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
