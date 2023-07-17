import uuid
import config
import pollutils
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any
from vkwave.bots import SimpleLongPollBot, SimpleBotEvent
from vkwave.bots.core.dispatching.router.router import BaseRouter
from vkwave.api.methods._error import APIError
from loguru import logger
from googlesheet_inserter import GoogleSheetInserter

logger.add(
    config.settings["LOG_FILE"],
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="1 week",
    compression="zip",
)


class HealthPollBot(SimpleLongPollBot):
    """Класс для опроса состояния здоровья студентов ВК.
    Attr: 
        current_date (str): Дата опроса.
    """
    
    class PollStage(Enum):
        """Стадии опроса."""
        
        WILL_CERTIFICATE = auto()
        CERTIFICATE_DATA = auto()
        SYMPTOMS = auto()
        LAST_DAY_IN_UNIVERSATY = auto()
        DONE = auto()
        IN_PROGRESS = auto()
        IS_ILL = auto()
        
    # Словарь с вопросами, где стадии соответствует вопрос
    question: Dict[PollStage, Union[str, List[Any]]] = {
        PollStage.WILL_CERTIFICATE: [
            "Будет ли справка",
            ["Будет", "Нет, буду лечиться дома"],
        ],
        PollStage.CERTIFICATE_DATA: "От какого числа будет справка? Например, 10.11.2021 (только в таком формате)",
        PollStage.SYMPTOMS: "Опишите ваши симптомы, через символ. Например, температура, кашель, болит горло",
        PollStage.LAST_DAY_IN_UNIVERSATY: "Какого числа были последний день на занятиях? Например, 10.11.2021 (только в таком формате)",
        PollStage.DONE: "Спасибо, что прошли опрос. В случае ошибки или возникновения вопросов, пишите https://vk.com/me_lnikov",
        PollStage.IS_ILL: "Вы болеете?"
    }

    def __init__(
        self,
        tokens:str,
        group_id:str|int,
        router: Optional[BaseRouter] = None,
        uvloop: bool = False,
        respondents: Dict[str, Dict] = None,
        inserter:GoogleSheetInserter = None,
    ) -> None:
        """Инициализирует класс.
        Args:
            tokens (str): Токен бота для доступа к Telegram API.
            group_id (str|int): id публичной страницы ВКонтакте от имени которой опрос.
            router (Optional[BaseRouter]): Роутер для маршрутизации бота.
            uvloop (bool): Внешний эвентлуп.
            respondents (Dict[str, Dict]): Список id участников опроса.
            inserter (GoogleSheetInserter): Агрегат для вставки данных в Google Sheet.
        Returns:
        """
        super().__init__(tokens, group_id=group_id, router=router, uvloop=uvloop)
        self.current_date: str = ""
        self.respondents = respondents if respondents else dict()
        self._inserter: GoogleSheetInserter = inserter

    @property
    def poll_googlesheet_credence_service_file(self) -> str:
        """Возвращает сервисный файл Google API."""
        return self._inserter.credence_service_file
    
    @poll_googlesheet_credence_service_file.setter
    def poll_googlesheet_credence_service_file(self, credence_service_file: str) -> None:
        """Устанавливает сервисный файл Google API."""
        self._inserter.credence_service_file = credence_service_file

    @property
    def pollresult_googlesheet_file_url(self) -> str:
        """Возвращает ссылку на Google документ."""
        return self._inserter.googlesheet_file_url
    
    @pollresult_googlesheet_file_url.setter
    def pollresult_googlesheet_file_url(self, googlesheet_file_url: str) -> None:
        """Устанавливает ссылку на Google документ."""
        self._inserter.googlesheet_file_url = googlesheet_file_url


bot: HealthPollBot = HealthPollBot(
    tokens=config.settings["TOKEN"],
    group_id=config.settings["VK_GROUP_ID"],
    inserter=GoogleSheetInserter(),
)
bot.poll_googlesheet_credence_service_file = config.settings["CREDS_FILE"]


@bot.message_handler(bot.regex_filter(r"(\d{1,2}(\.|\\|\/)\d{1,2}(\.|\\|\/)\d{2,4})"))
async def date_handler(event: SimpleBotEvent) -> None:
    """Обрабатывает вопрос про дату последнего посещения занятий."""
    
    user_id: str = str(event.object.object.message.from_id)
    text_msg: str = event.object.object.message.text.strip()
    print("Сообщение пользователя из обработчика date_handler: ", text_msg)
    if user_id in bot.respondents:
        if (
            bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.LAST_DAY_IN_UNIVERSATY
        ):
            bot.respondents[user_id][bot.current_date][
                "date_of_last_class_attendance"
            ] = text_msg
            if bot.respondents[user_id][bot.current_date]["diagnosis"]:
                bot.respondents[user_id][bot.current_date][
                    "poll_stage"
                ] = HealthPollBot.PollStage.DONE

                user_vk_profile_data: Dict[
                    str, Optional[Union[str, int, list]]
                ] = await bot.api_context.users.get(
                    user_ids=[user_id], return_raw_response=True
                )
                full_name: str = pollutils.get_user_lastname_firstname(user_vk_profile_data)
                bot._inserter.write_information_in_googlesheet(
                        full_name,
                        bot.respondents[user_id][bot.current_date],
                        bot.current_date,
                    )
                try:
                    await event.answer(
                        message=HealthPollBot.question[HealthPollBot.PollStage.DONE]
                    )
                except APIError as send_error:
                    logger.debug(f"{send_error.message}: Trouble id: {user_id}")
                    return
                except Exception as error:
                    pass
        elif (
            bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.CERTIFICATE_DATA
        ):
            bot.respondents[user_id][bot.current_date][
                "medical_certificate_data"
            ] = text_msg

        if (
            bot.respondents[user_id][bot.current_date]["poll_stage"]
            != HealthPollBot.PollStage.DONE
        ):
            bot.respondents[user_id][bot.current_date][
                "poll_stage"
            ] = HealthPollBot.PollStage.SYMPTOMS
            try:
                await event.answer(
                    message=HealthPollBot.question[HealthPollBot.PollStage.SYMPTOMS]
                )
            except APIError as send_error:
                logger.debug(f"{send_error.message}: Trouble id: {user_id}")
                return


@bot.message_handler(bot.payload_contains_filter("will_certificate"))
async def is_certificate_handler(event: SimpleBotEvent):
    """Обрабатывает вопрос про справку о болезне."""
    
    user_id: str = str(event.object.object.message.from_id)
    text_msg: str = event.object.object.message.text.strip()
    bot_msg: str = ""
    print("Сообщение пользователя из обработчика is_certificate_handler: ", text_msg)
    if user_id in bot.respondents:
        if (
            text_msg == "Будет"
            and bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.WILL_CERTIFICATE
        ):
            bot.respondents[user_id][bot.current_date]["medical_certificate"] = True
            bot.respondents[user_id][bot.current_date][
                "poll_stage"
            ] = HealthPollBot.PollStage.CERTIFICATE_DATA
            bot_msg = HealthPollBot.question[HealthPollBot.PollStage.CERTIFICATE_DATA]
        elif (
            text_msg == "Нет, буду лечиться дома"
            and bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.WILL_CERTIFICATE
        ):
            bot.respondents[user_id][bot.current_date]["medical_certificate"] = False
            bot.respondents[user_id][bot.current_date][
                "poll_stage"
            ] = HealthPollBot.PollStage.SYMPTOMS
            bot_msg = HealthPollBot.question[HealthPollBot.PollStage.SYMPTOMS]
        try:
            await event.answer(message=bot_msg)
        except APIError as send_error:
            logger.debug(f"{send_error.message}: Trouble id: {user_id}")
            return
    else:
        pass


@bot.message_handler(bot.payload_contains_filter("yes_no"))
async def is_ill_handler(event: SimpleBotEvent):
    """Обрабатывает вопрос болен ли пользователь."""
    
    user_id: str = str(event.object.object.message.from_id)
    print('Payload', event.object.object.message.payload)
    text_msg: str = event.object.object.message.text.strip()
    bot_msg: str = ""
    bot_keyboard = None
    print("Сообщение пользователя из обработчика is_ill_handler: ", text_msg)
    if user_id in bot.respondents:
        if (
            text_msg == "Да"
            and bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.IN_PROGRESS
        ):
            bot.respondents[user_id][bot.current_date]["ill"] = True
            bot.respondents[user_id][bot.current_date][
                "poll_stage"
            ] = HealthPollBot.PollStage.WILL_CERTIFICATE

            question, answers = HealthPollBot.question[HealthPollBot.PollStage.WILL_CERTIFICATE]
            bot_msg = question
            bot_keyboard = pollutils.get_keybord(answers, payload_name="will_certificate")
        elif (
            text_msg == "Нет"
            and bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.IN_PROGRESS
        ):
            bot.respondents[user_id][bot.current_date]["ill"] = False
            bot_msg = (
                f"Ну и хорошо. Не болей! \n{HealthPollBot.question[HealthPollBot.PollStage.DONE]}"
            )
        try:
            await event.answer(message=bot_msg, keyboard=bot_keyboard)
        except APIError as send_error:
            logger.debug(f"{send_error.message}: Trouble id: {user_id}")
            return
    else:
        pass


@bot.message_handler(bot.regex_filter(r"((!|\/)start (.*?) (https://docs.google.com/(.*?)))"))
async def start_handler(event: SimpleBotEvent) -> None:
    """Организует начало опроса."""
    
    text_msg: str = event.object.object.message.text.strip()
    path_to_file_with_respondents_ids, bot.pollresult_googlesheet_file_url = text_msg.split(' ')[1:]
    bot.current_date = datetime.today().strftime("%Y-%m-%d")
    try:
        file_with_poll_user_ids: Optional[List[str]] = pollutils.read_lines_from_file(
            path_to_file_with_respondents_ids
        )
    except EnvironmentError as file_error:
        logger.debug(file_error)
        await event.answer(f"{file_error}")
        return

    for poll_user_id in file_with_poll_user_ids:
        if poll_user_id not in bot.respondents:
            bot.respondents[str(poll_user_id)] = {
                bot.current_date: {
                    "poll_stage": HealthPollBot.PollStage.IN_PROGRESS,
                    "ill": False,
                    "diagnosis": "",
                    "medical_certificate": False,
                    "medical_certificate_data": "",
                    "date_of_last_class_attendance": "",
                }
            }
        else:
            bot.respondents[str(poll_user_id)][bot.current_date] = {
                "poll_stage": HealthPollBot.PollStage.IN_PROGRESS,
                "ill": False,
                "diagnosis": "",
                "medical_certificate": False,
                "medical_certificate_data": "",
                "date_of_last_class_attendance": "",
            }
        try:
            await bot.api_context.messages.send(
                peer_id=poll_user_id,
                random_id=uuid.uuid4().int,
                message=HealthPollBot.question[HealthPollBot.PollStage.IS_ILL],
                keyboard=pollutils.get_keybord(["Да", "Нет"], payload_name="yes_no")
            )
        except APIError as send_error:
            logger.debug(f"{send_error.message}: Trouble id: {poll_user_id}")
            continue

@bot.message_handler(bot.regex_filter(r"(^[^!\/](@|#)?[\d\w\s\W]+)|(^(?!\d{1,2}(\.|\\|\/)\d{1,2}(\.|\\|\/)\d{2,4})*$)"))
async def symptoms_handler(event: SimpleBotEvent) -> None:
    """Обрабатывает вопрос про симптомы заболевания."""
    
    user_id: str = str(event.object.object.message.from_id)
    text_msg: str = event.object.object.message.text.strip(" @#")
    print("Сообщение пользователя из обработчика symptoms_handler: ", text_msg)
    if user_id in bot.respondents:
        if (
            bot.respondents[user_id][bot.current_date]["poll_stage"]
            == HealthPollBot.PollStage.SYMPTOMS
        ):
            bot.respondents[user_id][bot.current_date][
                "poll_stage"
            ] = HealthPollBot.PollStage.LAST_DAY_IN_UNIVERSATY
            bot.respondents[user_id][bot.current_date]["diagnosis"] = text_msg
            try:
                await event.answer(
                    message=HealthPollBot.question[HealthPollBot.PollStage.LAST_DAY_IN_UNIVERSATY]
                )
            except APIError as send_error:
                logger.debug(f"{send_error.message}: Trouble id: {user_id}")
                return
        else:
            pass       
bot.run_forever()
