import requests
import datetime
from config import BITRIX_WEBHOOK


def get_old_leads():
    """
    Возвращает лиды со статусом NEW, которые старше 2 часов.
    """
    url = f"{BITRIX_WEBHOOK}crm.lead.list"
    payload = {
        "filter": {"STATUS_ID": "NEW"},  
        "select": ["ID", "TITLE", "NAME", "LAST_NAME", "STATUS_ID", "DATE_CREATE", "PHONE"],
    }
    response = requests.post(url, json=payload).json()

    leads = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for lead in response.get("result", []):
        created = datetime.datetime.fromisoformat(lead["DATE_CREATE"])
        age_minutes = (now - created).total_seconds() / 60
        if age_minutes >= 1:  # старше 2 часов
            phone = lead.get("PHONE", [])
            leads.append({
                "ID": lead["ID"],
                "TITLE": lead.get("TITLE", "—"),
                "NAME": lead.get("NAME", "—"),
                "PHONE": phone[0]["VALUE"] if phone else "—",
                "STATUS_ID": lead.get("STATUS_ID", "NEW")
            })
    return leads


def add_comment_to_lead(lead_id: str, text: str):
    url = f"{BITRIX_WEBHOOK}crm.timeline.comment.add"
    payload = {
        "fields": {
            "ENTITY_ID": lead_id,
            "ENTITY_TYPE": "lead",
            "COMMENT": text
        }
    }
    response = requests.post(url, json=payload).json()
    print("Comment response:", response)
    return response


def postpone_lead_task(lead_id: str, minutes: int = 120):
    url = f"{BITRIX_WEBHOOK}tasks.task.add"
    deadline = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
    payload = {
        "fields": {
            "TITLE": f"Follow up Lead #{lead_id}",
            "DESCRIPTION": f"Нужно связаться с лидом {lead_id}",
            "DEADLINE": deadline,
            "RESPONSIBLE_ID": 1,             
            "UF_CRM_TASK": [f"L_{lead_id}"]   # привязка к лиду
        }
    }
    response = requests.post(url, json=payload).json()
    print("Task response:", response)
    return response


def update_lead_status(lead_id: str, status: str = "IN_PROCESS"):
    url = f"{BITRIX_WEBHOOK}crm.lead.update"
    payload = {
        "id": lead_id,
        "fields": {"STATUS_ID": status}
    }
    response = requests.post(url, json=payload).json()
    print("Update response:", response)
    return response
def get_leads_by_status(status: str):
    url = f"{BITRIX_WEBHOOK}crm.lead.list"
    payload = {
        "filter": {"STATUS_ID": status},
        "select": ["ID", "TITLE", "NAME", "LAST_NAME", "PHONE", "STATUS_ID", "DATE_CREATE"]
    }
    response = requests.post(url, json=payload).json()

    leads = []
    for lead in response.get("result", []):
        phone = lead.get("PHONE", [])
        leads.append({
            "ID": lead["ID"],
            "TITLE": lead.get("TITLE", "—"),
            "NAME": lead.get("NAME", "—"),
            "PHONE": phone[0]["VALUE"] if phone else "—",
            "STATUS_ID": lead.get("STATUS_ID", "—"),
            "DATE_CREATE": lead.get("DATE_CREATE", "—")
        })
    return leads
