
from pathlib import Path

from py_rcg_booking_automation import SupporterCRMExporter



if __name__ == '__main__':


    supporter_crm_export = SupporterCRMExporter()
    supporter_crm_export.export(Path('Supporters.csv'))
