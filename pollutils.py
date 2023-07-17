from typing import List, Optional
from vkwave.bots.utils.keyboards.keyboard import Keyboard


def get_keybord(answers:List[str], payload_name:str) -> Keyboard:
    """Возвращает виртуальную клавиатуру со списком ответов.
    Args:
        answers (List[str]): Список ответов на вопрос.
        payload_name (str): Имя payload для определения вопроса.
    Returns:
        Keyboard: клавиатура где каждая кнопка - вариант ответа на вопрос.
    """
    keyboard: Keyboard = Keyboard(inline=True)
    for index, answer in enumerate(answers, 1):
        keyboard.add_text_button(answer, payload={f"{payload_name}": f"{answer}"})
        if index != len(answers):
            keyboard.add_row() # переносим кнопки на новый ряд
    return keyboard.get_keyboard()


def read_lines_from_file(path:str) -> List[str]:
    """Возвращает список строк из файла.
    Args:
        path (str): Путь до файла.
    Returns:
        List[str]: список строк из файла.
    """
    content: Optional[List[str]] = None
    with open(path, "r", encoding='UTF-8') as file:
        content = file.readlines()
    content = [line.strip() for line in content]
    return content


def get_user_lastname_firstname(user_data:dict) -> str:
    """Возвращает фамилию и имя пользователя.
    Args:
        user_data (dict): Словарь с данными о пользователе.
    Returns:
        List[str]: список строк из файла.
    """
    full_vk_profile_name: str = (
        user_data["response"][0]["last_name"]
        + " "
        + user_data["response"][0]["first_name"]
    )
    return full_vk_profile_name
