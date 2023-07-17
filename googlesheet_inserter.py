import pygsheets
from typing import Dict, List, Union, Any

class GoogleSheetInserter:
    """Класс для добавления записей в Google Sheet."""
    
    def __init__(
        self, credence_service_file:str = "", googlesheet_file_url:str = ""
    ) -> None:
        """Инициализирует класс.
        Args:
            credence_service_file (str): Путь до сервисного файла credence.json (Google Sheet API).
            googlesheet_file_url (str): Ссылка на Google Sheet.
        Returns:
        """
        self.credence_service_file = credence_service_file
        self.googlesheet_file_url = googlesheet_file_url

    def _get_googlesheet_by_url(
        self, googlesheet_client: pygsheets.client.Client
    ) -> pygsheets.Spreadsheet:
        """Получает Google.Docs таблицу по ссылке на документ."""
        sheets: pygsheets.Spreadsheet = googlesheet_client.open_by_url(
            self.googlesheet_file_url
        )
        return sheets.sheet1

    def _insert_data_back_googlesheet(
        self,
        sheet: pygsheets.Spreadsheet,
        data: List[List[Union[str, bool]]],
        start_col: str,
        end_col: str,
    ) -> bool:
        """Находит номер последней заполненной строки и вставляет данные после нее.
        Args:
            sheet (pygsheets.Spreadsheet): - Объект электронной таблицы Google.Docs.
            data (List[List[Union[str, bool]]]): - Cловарь с данными, предназначенными для вставки.
            start_col (str): - столбец таблицы, с которого начинается вставка.
            end_col (str): - столбец таблицы, на котором заканчивается вставка.
        Returns: - True в случае успешной вставки и False в противном случае.
        """
        last_filled_row: List[str] = len(
            list(filter(lambda cell: cell != "", sheet.get_col(1)))
        )  # column 1 in googlesheet excel = A-column
        try:
            sheet.update_values(
                f"{start_col}{last_filled_row + 1}:{end_col}{last_filled_row + 1}", data
            )
        except:
            return False
        else:
            return True

    def _get_googlesheet_client(self) ->  pygsheets.client.Client:
        """Он авторизуется с помощью служебного ключа и возвращает объект клиента Google Docs."""
        return pygsheets.authorize(
            service_file=self.credence_service_file
        )

    def _insert_info_in_googlesheet(
        self,
        data: List[List[Union[str, bool]]],
        start_col: str = "A",
        end_col: str = "E",
    ) -> bool:
        """Вставляет строку данных в таблицу Google.
        Args:
            data (List[List[Union[str, bool]]]):  Cловарь с данными, предназначенными для вставки.
            start_col (str): Cтолбец таблицы, с которого начинается вставка.
            end_col (str): Cтолбец таблицы, с которого заканчивается вставка.
        Returns: True в случае успешной вставки и False в противном случае.
        """
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client)
        is_inserted: bool = self._insert_data_back_googlesheet(
            wks, data, start_col, end_col
        )
        return is_inserted

    def write_information_in_googlesheet(
        self,
        primary_col: str,
        user_poll_data: Dict[str, Union[str, bool, Any]],
        current_date: str,
    ) -> bool:
        """Записывает данные в электронную таблицу Google.
        Args:
            primary_col (str): Значение, идентифицирующее строку данных.
            user_poll_data (Dict[str, Union[str, bool, Any]]): Данные для записи.
            current_date (str): Дата записи. 
        Returns:
        """
        print("Результаты опроса в обработчике date_handler: ", user_poll_data)
        print("ФИО пользователя, прошедшего опрос:", primary_col)
        return self._insert_info_in_googlesheet(
            [
                [
                    primary_col,
                    user_poll_data["diagnosis"],
                    user_poll_data["medical_certificate_data"],
                    user_poll_data["date_of_last_class_attendance"],
                    user_poll_data["medical_certificate"],
                    current_date,
                ]
            ],
            start_col="A",
            end_col="F",
        )
        
