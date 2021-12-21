# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.slu.entityresolution import StatusCode

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        set_session_attribute(handler_input, "last_status", StatusCode.ER_SUCCESS_NO_MATCH.value)
        set_session_attribute(handler_input, "skill_state", "onStart")
        speak_output =  ('Vamos lá! <break time="0.3s"/> Peça para seu amigo te falar a palavra no ouvido. '
        '<amazon:effect name="whispered">Ah, fala pra ele falar bem baixinho pra eu não ouvir, '
        'enquanto isso eu tou aqui esperando alguns segundinhos...</amazon:effect>'
        '<break time="3s"/> Nós já podemos começar?')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class YesOrNoIntentHandler(AbstractRequestHandler):
    """Single handler for Yes and No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        skill_state = get_session_attribute(handler_input, "skill_state")
        
        if (skill_state == "onStart"):
            if ask_utils.get_intent_name(handler_input) == "AMAZON.YesIntent":
                speak_output = ('Certo! Vamos dar início aos procedimentos. '
                'Preciso de um momento pois irei conectar ao seu cérebro para fazer o download de suas redes neurais! '
                '<audio src="soundbank://soundlibrary/computers/typing/typing_05"/> Concentre-se... '
                '<audio src="soundbank://soundlibrary/computers/typing/typing_05"/> '
                '<audio src="soundbank://soundlibrary/computers/beeps_tones/beeps_tones_02"/> '
                '<audio src="soundbank://soundlibrary/computers/beeps_tones/beeps_tones_02"/> '
                '<audio src="soundbank://soundlibrary/computers/beeps_tones/beeps_tones_03"/> '
                'Pareamento cerebral concluído com sucesso. Estou devidamente pronta. Diga as palavras aleatoriamente e te direi qual é a palavra do seu amigo!')
                
                set_session_attribute(handler_input, "skill_state", "onAsk")
            else:
                speak_output = 'Vou aguardar só mais um pouquinho. <break time="3s"/> Ele já te sussurrou?'
        
        elif (skill_state == "onCheck"):
            if ask_utils.get_intent_name(handler_input) == "AMAZON.YesIntent":
                speak_output = 'Eu sou muito boa nisso! Quer jogar novamente?'
                set_session_attribute(handler_input, "skill_state", "onPlayAgain")
            else:
                speak_output = 'Poxa! Não costumo errar assim, quer me dar outra chance?'
                set_session_attribute(handler_input, "skill_state", "onRetry")
                set_session_attribute(handler_input, "last_status", StatusCode.ER_SUCCESS_NO_MATCH.value)
                
        elif (skill_state == "onPlayAgain"):
            if ask_utils.get_intent_name(handler_input) == "AMAZON.YesIntent":
                speak_output = 'Então vamos! Diga as palavras aleatoriamente e te direi qual é a palavra do seu amigo!'
                set_session_attribute(handler_input, "skill_state", "onAsk")
                set_session_attribute(handler_input, "last_status", StatusCode.ER_SUCCESS_NO_MATCH.value)
            else:
                speak_output = 'Tudo bem. Até o próximo pareamento de cérebros. Tchauzinho!'
                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .response
                )
        
        elif (skill_state == "onRetry"):
            if ask_utils.get_intent_name(handler_input) == "AMAZON.YesIntent":
                speak_output = 'Êba! Me diga outra palavra!'
                set_session_attribute(handler_input, "skill_state", "onAsk")
            else:
                speak_output = ('Tudo bem. Mas em minha defesa, tudo indica que houve uma perda de pacotes ao realizar o download das suas redes neurais! '
                'Tchau tchau!' )
                
                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .response
                )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class AskWordIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        skill_state = get_session_attribute(handler_input, "skill_state")
        return ask_utils.is_intent_name("AskWordIntent")(handler_input) and skill_state == "onAsk"

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slot = ask_utils.request_util.get_slot(handler_input, "keyWord")
        current_status = slot.resolutions.resolutions_per_authority[0].status.code.value
        last_status = get_session_attribute(handler_input, "last_status")
        
        if (last_status == StatusCode.ER_SUCCESS_MATCH.value):
            speak_output = "A palavra do seu amigo é " + slot.value + ". Eu acertei?"
            set_session_attribute(handler_input, "skill_state", "onCheck")
        else:
            speak_output = slot.value + " não é a palavra. Me diga outra palavra."
            set_session_attribute(handler_input, "last_status", current_status)

        return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
    
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ('Essa skill tem o objetivo de impressionar um amigo seu adivinhando a palavra que ele falar pra você através de um truque estabelecido. '
        'Você pode procurar mais informações através da descrição dessa skill no aplicativo da Alexa.')

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Tchauzinho!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hum, eu não entendi. Você pode falar a palavra e eu direi se é a que seu amigo falou ou não."
        reprompt = "Eu não ouvi, pode dizer a palavra?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Eu não entendi, sim ou não?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Desculpa, eu não entendi. Tente novamente."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


def set_session_attribute(handler_input, key, value):
    handler_input.attributes_manager.session_attributes[key] = value;

def get_session_attribute(handler_input, key):
    return handler_input.attributes_manager.session_attributes[key];


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(YesOrNoIntentHandler())
sb.add_request_handler(AskWordIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()