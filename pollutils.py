from typing import List, Optional
from vkwave.bots.utils.keyboards.keyboard import Keyboard


def get_keybord(answers: List[str], payload_name: str) -> Keyboard:
    keyboard: Keyboard = Keyboard(inline=True)
    for index, answer in enumerate(answers, 1):
        keyboard.add_text_button(answer, payload={f"{payload_name}": f"{answer}"})
        if index != len(answers):
            keyboard.add_row()
    return keyboard.get_keyboard()


def read_lines_from_file(path: str) -> List[str]:
    content: Optional[List[str]] = None
    with open(path, "r") as file:
        content = file.readlines()
    content = [line.strip() for line in content]
    return content


def get_user_lastname_firstname(user_data: str) -> str:
    full_vk_profile_name: str = (
        user_data["response"][0]["last_name"]
        + " "
        + user_data["response"][0]["first_name"]
    )
    return full_vk_profile_name