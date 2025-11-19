
from openpyxl.styles import Alignment, Font
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter

from django.core.files.base import File
from selc_core.models import ReportFile




def create_workbook():
    work_book = Workbook()
    #get the default active sheet.
    active_sheet = work_book.active
    work_book.remove(active_sheet)

    return work_book



#for creating title text normally at the first row of every work sheet.
def init_sheet_title(sheet: Worksheet, title='', row=1, column=1, span_column=None):
    header_cell = sheet.cell(row=row, column=column, value=title)
    header_cell.alignment = Alignment(vertical='center', horizontal='center')
    header_cell.font = Font(bold=True, size=14)

    if span_column is not None:
        sheet.merge_cells(start_row=row, start_column=column, end_row=row, end_column=span_column)

    return header_cell




#function that populates table headers in a given worksheet.
def init_header_cells(sheet: Worksheet, headers: list, row=2):

    if not headers:
        return

    for col, header in enumerate(headers, start=1):
        header_cell = sheet.cell(row=row, column=col, value=header)
        header_cell.alignment = Alignment(vertical='center', horizontal='center')
        header_cell.font = Font(bold=True, size=12)
        pass

    pass




def set_column_widths(sheet: Worksheet, widths: dict):
    """
    widths = {column_index: width_value}
    """
    for col_idx, width in widths.items():
        col_letter = get_column_letter(col_idx)
        sheet.column_dimensions[col_letter].width = width
        pass
    pass






def saveWorkbook(work_book: Workbook, file_name: str, file_type: str):

    temp_path = f'/temp/report{file_type}'
    work_book.save(temp_path)

    with open(temp_path, 'rb') as excel_file:
        report_file = ReportFile.objects.create(file_name=file_name, file_type=file_type)
        report_file.file = File(excel_file)
        report_file.save()

    pass