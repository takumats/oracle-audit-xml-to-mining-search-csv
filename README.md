# oracle-audit-xml-to-mining-search-csv
A Python script to convert a Oracle Audit log file (XML style) to "MiningSearch" style CSV file.

## usage
```
python3 oracle_audit_xml_to_mscsv.py <AUDIT_LOG> <OUTPUT_CSV_FILE_NAME> 
```

## 入力となるファイル
入力となるファイルは以下のファイルです。
* Oracleの監査ログをXML形式で出力したものを結合
* ファイル全体はルートのXMLの要素

サンプル：
```xml
<data>
<AuditRecord><Audit_Type>1</Audit_Type><Session_Id>250064</Session_Id><StatementId>3</StatementId><EntryId>1</EntryId><Extended_Timestamp>2024-03-29T14:54:00.782747Z</Extended_Timestamp><DB_User>SCOTT</DB_User><OS_User>tmatsuo</OS_User><Userhost>WORKGROUP\XXXXX</Userhost><OS_Process>14032</OS_Process><Terminal>XXXXX</Terminal><Instance_Number>0</Instance_Number><Object_Schema>SYS</Object_Schema><Object_Name>DUAL</Object_Name><Action>3</Action><Returncode>0</Returncode><Scn>643676</Scn><DBID>955988972</DBID><Current_User>SCOTT</Current_User>
<Sql_Text>SELECT DECODE(USER, &apos;XS$NULL&apos;,  XS_SYS_CONTEXT(&apos;XS$SESSION&apos;,&apos;USERNAME&apos;), USER) FROM SYS.DUAL</Sql_Text>
</AuditRecord>
<AuditRecord><Audit_Type>1</Audit_Type><Session_Id>250064</Session_Id><StatementId>4</StatementId><EntryId>3</EntryId><Extended_Timestamp>2024-03-29T14:54:00.863435Z</Extended_Timestamp><DB_User>SCOTT</DB_User><OS_User>tmatsuo</OS_User><Userhost>WORKGROUP\XXXXX</Userhost><OS_Process>14032</OS_Process><Terminal>XXXXX</Terminal><Instance_Number>0</Instance_Number><Action>47</Action><Returncode>0</Returncode><Scn>643679</Scn><DBID>955988972</DBID><Current_User>SCOTT</Current_User>
<Sql_Bind> #1(8):SQL*Plus</Sql_Bind>
<Sql_Text>BEGIN DBMS_APPLICATION_INFO.SET_MODULE(:1,NULL); END;</Sql_Text>
</AuditRecord>
<AuditRecord><Audit_Type>1</Audit_Type><Session_Id>250064</Session_Id><StatementId>5</StatementId><EntryId>4</EntryId><Extended_Timestamp>2024-03-29T14:54:00.891473Z</Extended_Timestamp><DB_User>SCOTT</DB_User><OS_User>tmatsuo</OS_User><Userhost>WORKGROUP\XXXXX</Userhost><OS_Process>14032</OS_Process><Terminal>XXXXX</Terminal><Instance_Number>0</Instance_Number><Action>44</Action><Returncode>0</Returncode><DBID>955988972</DBID><Current_User>SCOTT</Current_User>
</AuditRecord>
...
</data>
```

## 制限事項
* 同一セッションの最初のSQL実行日時をセッションの開始日時、最後のSQL実行日時をセッションの終了日時としています
* 再起動などをしてセッションIDが重複している場合異なるセッションと紐づけらることがあります
