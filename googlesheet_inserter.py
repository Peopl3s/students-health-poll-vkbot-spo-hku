import pygsheets
from typing import Dict, List, Union, Any

class GoogleSheetInserter:
    def __init__(
        self, credence_service_file: str = "", googlesheet_file_url: str = ""
    ) -> None:
        self.credence_service_file = credence_service_file
        self.googlesheet_file_url = googlesheet_file_url

    def _get_googlesheet_by_url(
        self, googlesheet_client: pygsheets.client.Client
    ) -> pygsheets.Spreadsheet:
        """Get Google.Docs Table sheet by document url"""
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
        """Finds the number of the last filled line and inserts the data after it
        :param sheet: - Google.Docs Spreadsheet object.
        :param data: - dictionary with data intended for insertion.
        :param start_col: - the column of the table from which the insertion begins.
        :param end_col: - the column of the table with which the insert ends.
        :return: - True in case of successful insertion and False otherwise
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

    def _get_googlesheet_client(self):
        """It is authorized using the service key and returns the Google Docs client object"""
        return pygsheets.authorize(
            service_file=self.credence_service_file
        )

    def _insert_info_in_googlesheet(
        self,
        data: List[List[Union[str, bool]]],
        start_col: str = "A",
        end_col: str = "E",
    ) -> bool:
        """Inserts a row of data into a Google table
        :param data: - dictionary with data intended for insertion.
        :param start_col: - the column of the table from which the insertion begins.
        :param end_col: - the column of the table with which the insert ends.
        :return: - True in case of successful insertion and False otherwise
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
        """Writes data to a Google Spreadsheet
        :param primary_col: - the value identifying the data string.
        :param user_poll_dataЖ: - data for recording.
        :param current_date: - recording date. 
        :return:
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