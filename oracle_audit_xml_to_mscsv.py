import argparse
import csv
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass

# Set true to skip 'rdsadmin' user activity
SKIP_RDSADMIN = True
# Set no. of steps for progress display
EVENT_COUNT_STEP = 100000

@dataclass
class AuditItem:
    db_id: str = ''
    db_user: str = ''
    session_id: str = ''
    timestamp: str = ''
    timestamp_msec: str = ''
    sql_bind: str = ''
    sql_text: str = ''
    remote_host: str = ''

def ParseOracleAuditXmlFile(filename):
    event_count = 0
    context = ET.iterparse(filename, events=('start', 'end'))
    _, root = next(context)  # 一つ進めて root を得る
    root.clear()  # 使わないのでrootを空

    audit_item = None
    for event, elem in context:
        #print(event, elem, elem.text)
        if event == 'start' and elem.tag == 'AuditRecord':
            audit_item = AuditItem()
            elem.clear()
        elif event == 'end':
            if elem.tag == 'DBID':
                audit_item.db_id = elem.text
            elif elem.tag == 'DB_User':
                audit_item.db_user = elem.text
            elif elem.tag == 'Session_Id':
                audit_item.session_id = elem.text
            elif elem.tag == 'Sql_Bind':
                audit_item.sql_bind = elem.text
            elif elem.tag == 'Sql_Text':
                audit_item.sql_text = elem.text
            elif elem.tag == 'Userhost':
                audit_item.remote_host = elem.text
            elif elem.tag == 'Extended_Timestamp':
                audit_item.timestamp = elem.text
            elif elem.tag == 'AuditRecord':
                event_count = event_count + 1
                if (event_count % EVENT_COUNT_STEP == 0):
                    print('  processed:' + str(event_count))

                if audit_item.db_user != '/' and audit_item.db_user != '' and not (SKIP_RDSADMIN and audit_item.db_user == 'RDSADMIN'):
                    log_time = audit_item.timestamp
                    audit_item.timestamp = log_time[0:4] + log_time[5:7] + log_time[8:10] + log_time[11:13] + log_time[14:16] + log_time[17:19]
                    audit_item.timestamp_msec = log_time[20:26]
                    yield audit_item
            elem.clear()
        
    print('  processed:' + str(event_count))

def write_ms_csv_row(csv_writer, audit_item, session_start_time, session_end_time):
    # skip if no session start info
    if audit_item.session_id not in session_start_time:
        return
    
    row_to_be_written = []
    row_to_be_written.append(audit_item.db_id) # Host
    row_to_be_written.append(audit_item.db_id) # Database
    row_to_be_written.append(audit_item.session_id) # SID
    row_to_be_written.append('')     # Serial
    row_to_be_written.append(session_start_time[audit_item.session_id])     # Logged In
    row_to_be_written.append(session_end_time[audit_item.session_id] if audit_item.session_id in session_end_time else '')     # Logged Out
    row_to_be_written.append(audit_item.db_user) # DB User
    row_to_be_written.append(audit_item.timestamp) # SQL Start Time
    row_to_be_written.append(audit_item.timestamp_msec) # SQL Start Time(Micro Sec)
    row_to_be_written.append(audit_item.sql_text) # SQL Text
    row_to_be_written.append(audit_item.sql_bind) # Bind Variables
    row_to_be_written.append('')     # Object
    row_to_be_written.append('')     # Elapsed Time
    row_to_be_written.append('')     # Program
    row_to_be_written.append(audit_item.remote_host) # Client Information - Host

    csv_writer.writerow(row_to_be_written)

# Check session information for the specified file
def create_session_list(filename):
    # Check by QUERY (if no CONNECT info, use first query as login and last query as logout)
    print('Create session list by QUERY')
    session_start_time = {}
    session_end_time = {}
    for audit_item in ParseOracleAuditXmlFile(filename):
        if audit_item.session_id not in session_start_time:
            # use this sql start time
            session_start_time[audit_item.session_id] = audit_item.timestamp
        if audit_item.session_id not in session_end_time:
            # use this sql start time
            session_end_time[audit_item.session_id] = audit_item.timestamp
        
        if audit_item.timestamp < session_start_time[audit_item.session_id]:
            session_start_time[audit_item.session_id] = audit_item.timestamp
        if session_end_time[audit_item.session_id] < audit_item.timestamp:
            session_end_time[audit_item.session_id] = audit_item.timestamp

    return session_start_time, session_end_time

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'oracle_audit_xml',
        metavar='ORACLE_AUDIT_XML',
        help='RDS for Oracleから出力された監査ログ内容(xml形式)'
    )
    arg_parser.add_argument(
        'output_csv_file_name',
        metavar='OUTPUT_CSV_FILE_NAME',
        help='マイニングサーチ形式CSV出力ファイル名'
    )

    # 引数取得
    args = arg_parser.parse_args()
    oracle_audit_xml = args.oracle_audit_xml
    output_csv_file_name = args.output_csv_file_name

    # Session Login/Logout information
    session_start_time, session_end_time = create_session_list(oracle_audit_xml)
    print('no. of sessions:' + str(len(session_start_time)))

    # Create csv file
    with open(output_csv_file_name, 'w') as fo:
        csv_writer = csv.writer(fo, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        CSV_HEADER = ['Host','Database','SID','Serial','Logged In','Logged Out','DB User','SQL Start Time','SQL Start Time(Micro Sec)','SQL Text','Bind Variables','Object','Elapsed Time','Program','Client Information - Host']

        csv_writer.writerow(CSV_HEADER)
        for audit_item in ParseOracleAuditXmlFile(oracle_audit_xml):
            if audit_item.sql_text == '':
                continue

            write_ms_csv_row(csv_writer, audit_item, session_start_time, session_end_time)

if __name__ == '__main__':
    main()