# api_services.py
import requests
import json
import datetime

# --- Utility Functions ---

def build_api_payload(event_id, child_id, ac_id, parent_id, value):
    inner_json_string = (
        f'{{"Event":"{event_id}","Child": [{{"Control_Id":"{child_id}", "AC_ID": "{ac_id}",'\
        f'\"Parent\": [{{"Control_Id":"{parent_id}","Value": \"{value}\",\"Data_Form_Id\": \"\"}}]}}]}}'
    )
    return json.dumps({"input": inner_json_string})

def build_push_payload(sid, params_dict):
    params_str = ",".join([f'\"{key}\": {{"VALUE\":\"{val}\"}}' for key, val in params_dict.items()])
    inner_json_string = f'{{"PARAMETERS":{{"SID": {{"VALUE\":\"{sid}\"}},{params_str}}}}}'
    return json.dumps({"input": inner_json_string})

def build_get_client_payload(event_id, child_id, ac_id, parent_id, value):
    payload_dict = {
      "Event": event_id,
      "Child": [
        {
          "Control_Id": child_id,
          "AC_ID": ac_id,
          "Parent": [
            {
              "Control_Id": parent_id,
              "Value": str(value),
              "Data_Form_Id": ""
            }
          ]
        }
      ]
    }
    return json.dumps(payload_dict)

def build_get_client_payload_no_parent(event_id, child_id, ac_id):
    payload_dict = {
      "Event": event_id,
      "Child": [
        {
          "Control_Id": child_id,
          "AC_ID": ac_id
        }
      ]
    }
    return json.dumps(payload_dict)

def build_flat_push_payload(params_dict):
    return json.dumps(params_dict)

def make_api_request(url, headers, data_payload_string):
    try:
        response = requests.post(url, headers=headers, data=data_payload_string, timeout=15)

        if response.status_code == 200:
            try:
                # Handle standard JSON response
                return response.json()
            except json.JSONDecodeError:
                # Handle non-JSON success messages
                if "Data Saved Succesfully" in response.text or "Record saved successfully" in response.text:
                    return {"result": "1", "resultmessage": response.text}
                else:
                    return {"result": "0", "resultmessage": "Unknown success response", "details": response.text}
        else:
            return {"error": f"API returned status {response.status_code}", "details": response.text}

    except requests.exceptions.Timeout:
         return {"error": "API call failed: Request timed out"}
    except Exception as e:
        return {"error": f"API call failed: {e}"}

# --- Service-Specific Functions (Your Tools) ---

def get_accounts_by_mobile(mobile_number):
    """Gets the list of accounts linked with a 10-digit mobile number."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '298', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '2ff9d827-d81f-495f-9216-35c24c8a897d', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109182", "109184", "117125", "109183", mobile_number)
    print("Calling Api that Gets the list of accounts linked with a 10-digit mobile number")
    return make_api_request(url, headers, payload)

def get_account_details(account_id):
    """Gets account details for a specific account ID."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '302', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '50b5da06-63a7-4b4f-a38d-e97d1a686aa5', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109256", "109254", "117264", "109255", account_id)
    return make_api_request(url, headers, payload)

def get_bill_and_payment_details(account_id):
    """Gets bill and payment details for a specific account ID."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '303', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '31ccc9f9-fede-48fe-8145-5c90ae741b8c', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109186", "109188", "117126", "109185", account_id)
    return make_api_request(url, headers, payload)

def get_last_5_complaints(mobile_number):
    """Gets the last 5 complaint details against a 10-digit mobile number."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '304', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'b1c359d5-1ce2-4c45-9490-d09f8804a714', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109193", "109194", "117128", "109187", mobile_number)
    return make_api_request(url, headers, payload)

def get_complaint_detail_by_number(complaint_number):
    """Gets specific complaint details for a given complaint number."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '305', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '6ba4d6d3-c364-4648-8db3-680cb2ab98a6', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109258", "109259", "117265", "109257", complaint_number)
    return make_api_request(url, headers, payload)

def get_complaints_for_feedback(mobile_number):
    """Gets a list of closed complaints pending feedback for a mobile number."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSON"
    headers = {
        'sid': '308', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '656f9820-a281-453d-9f4b-13e2c654091f', 'Content-Type': 'application/json'
    }
    payload = build_api_payload("109415", "109416", "117497", "109189", mobile_number)
    return make_api_request(url, headers, payload)

def submit_complaint_feedback(complaint_id, feedback_confirmation, q_ans1, q_ans2, q_ans3, remarks):
    """Submits feedback for a specific complaint. feedback_confirmation is 1 for Satisfied, 2 for Unsatisfied."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSON"
    headers = {
        'sid': '309', 'pid': '304', 'fid': '10223', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '87ef1d97-703c-4f65-9b18-61ff2dab46df', 'Content-Type': 'application/json'
    }
    params = {
        "DATA_ID1": complaint_id,
        "FEEDBACK_CONFIRMATION": feedback_confirmation,
        "QUES_ANS1": q_ans1,
        "QUES_ANS2": q_ans2,
        "QUES_ANS3": q_ans3,
        "REMARKS": remarks
    }
    payload = build_push_payload("309", params)
    return make_api_request(url, headers, payload)

def register_technical_complaint_no_account(mobile_no, name, address, area_id, complaint_type_id, remarks, issue_type="", type_val="11KV", soc="9"):
    """Registers a new technical complaint (No Account). 'soc' is 9 (chatbot). Service ID 310."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSONClient"
    headers = {
        'sid': '310', 'pid': '304', 'fid': '10548', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '2348b719-ea89-4e9f-a9fc-122f3824e2dc', 'Content-Type': 'application/json'
    }
    payload_dict = {
        "SID": "310",
        "ADDRESS": address,
        "AREA_ID": str(area_id),
        "COMPLAINT_TYPE": str(complaint_type_id),
        "ISSUE_TYPE": issue_type,
        "TYPE": type_val,
        "MOBILE_NO": mobile_no,
        "NAME": name,
        "REMARKS": remarks,
        "SOC": soc
    }
    payload = build_flat_push_payload(payload_dict)
    return make_api_request(url, headers, payload)

def register_technical_complaint_with_account(account_id, complaint_type_id, mobile_no, remarks, area_id, issue_type="", soc="9"):
    """Registers a new technical complaint (With Account). 'soc' is 9 (chatbot). Service ID 311."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSONClient"
    headers = {
        'sid': '311', 'pid': '304', 'fid': '10548', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '851c902f-130f-4f8e-8eb0-26aa2fb6af31', 'Content-Type': 'application/json'
    }
    payload_dict = {
        "SID": "311",
        "ACCOUNT_ID": str(account_id),
        "AREA_ID": str(area_id),
        "ISSUE_TYPE": issue_type,
        "COMPLAINT_TYPE": str(complaint_type_id),
        "MOBILE_NO": mobile_no,
        "REMARKS": remarks,
        "SOC": soc
    }
    payload = build_flat_push_payload(payload_dict)
    return make_api_request(url, headers, payload)

def send_bill_sms_unregistered_mobile(account_no, mobile_no, soc="9"):
    """Sends bill information via SMS to a mobile number not registered to the account. 'soc' is 9 for chatbot."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSON"
    headers = {
        'sid': '317', 'pid': '304', 'fid': '10567', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'caca3b85-986c-4ff6-970b-3158475d130a', 'Content-Type': 'application/json'
    }
    params = {
        "ACCOUNT_NO": account_no,
        "MOBILE_NO": mobile_no,
        "SOC": soc
    }
    payload = build_push_payload("317", params)
    return make_api_request(url, headers, payload)

def generate_callback_request(mobile_no, missed_call_time="", soc="9"):
    """Generates a callback request for a 10-digit mobile number. 'soc' is 9 for chatbot."""
    if not missed_call_time:
        missed_call_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSON"
    headers = {
        'sid': '322', 'pid': '304', 'fid': '10336', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'f7882d34-6d42-4f2e-bdfa-70469a13777f', 'Content-Type': 'application/json'
    }
    params = {
        "MISSED_CALL_TIME": missed_call_time,
        "MOBILE_NO": mobile_no,
        "SOC": soc
    }
    payload = build_push_payload("322", params)
    return make_api_request(url, headers, payload)

def register_commercial_complaint(account_id, area_id, complaint_type_id, issue_type, mobile_no, remarks, type_val, soc="11"):
    """Registers a new commercial complaint. 'soc' is 11, 'type_val' is for Meter/Shifting complaint type."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/PushdataJSON"
    headers = {
        'sid': '367', 'pid': '304', 'fid': '10548', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'ba2026d6-2a3a-4555-81cf-9b22b5d30de2', 'Content-Type': 'application/json'
    }
    params = {
        "ACCOUNT_ID": account_id,
        "AREA_ID": area_id,
        "COMPLAINT_TYPE": complaint_type_id,
        "ISSUE_TYPE": issue_type,
        "MOBILE_NO": mobile_no,
        "REMARKS": remarks,
        "SOC": soc,
        "TYPE": type_val
    }
    payload = build_push_payload("367", params)
    return make_api_request(url, headers, payload)

def check_registration_status(mobile_number):
    """Checks if a mobile number is 'registered' (has a previous No Supply complaint) and returns area details. Service ID 406."""
    url = "http://13.235.20.106/DDSUH/api/AppsavyRestService/GetDataJSONClient"
    headers = {
        'sid': '406', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '41711d50-fc8f-41fa-8334-3269b1fcccc2', 'Content-Type': 'application/json'
    }
    payload = build_get_client_payload("129822", "129821", "160646", "129820", mobile_number)
    return make_api_request(url, headers, payload)

def check_outage_details(area_id):
    """Checks for current power outages for a specific Area ID. Service ID 410."""
    url = "http://13.235.20.106/DDSUH/api/AppsavyRestService/GetDataJSONClient"
    headers = {
        'sid': '410', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '2fe2fca8-e2e0-4a45-93f6-e1a178caf9ec', 'Content-Type': 'application/json'
    }
    payload = build_get_client_payload("130105", "130107", "161414", "130106", area_id)
    return make_api_request(url, headers, payload)

def get_district_details():
    """Gets the list of all available districts. Service ID 412."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSONClient"
    headers = {
        'sid': '412', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': '81a3d6b4-4b0c-4197-bb39-5d98cea51242', 'Content-Type': 'application/json'
    }
    payload = build_get_client_payload_no_parent("130174", "130179", "161640")
    return make_api_request(url, headers, payload)

def get_subdivision_details(district_data_id):
    """Gets the list of subdivisions for a specific District DATA_ID. Service ID 413."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSONClient"
    headers = {
        'sid': '413', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'f6c20e0d-a9d8-4c68-9fd5-856e55f780d0', 'Content-Type': 'application/json'
    }
    payload = build_get_client_payload("130176", "130181", "161642", "130177", district_data_id)
    return make_api_request(url, headers, payload)

def get_area_details(subdivision_data_id):
    """Gets the list of areas for a specific Subdivision DATA_ID. Service ID 414."""
    url = "http://13.235.20.106/ddsuh/api/AppsavyRestService/GetDataJSONClient"
    headers = {
        'sid': '414', 'pid': '304', 'fid': '10540', 'cid': '93', 'uid': 'CHATBOT_API',
        'roleid': '1643', 'TokenKey': 'ffefdc08-4d71-40c9-ad96-06a58d09ae66', 'Content-Type': 'application/json'
    }
    payload = build_get_client_payload("130180", "130175", "161641", "130178", subdivision_data_id)
    return make_api_request(url, headers, payload)