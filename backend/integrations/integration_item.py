from datetime import datetime
from typing import Optional, List, Any, Dict

class NotionItem:
    def __init__(
        self,
        id: Optional[str] = None,
        type: Optional[str] = None,
        parent_id: Optional[str] = None,
        name: Optional[str] = None,
        creation_time: Optional[datetime] = None,
        last_modified_time: Optional[datetime] = None,
    ):
        self.id = id
        self.type = type
        self.parent_id = parent_id
        self.name = name
        self.creation_time = creation_time
        self.last_modified_time = last_modified_time

class AirtableItem:
    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
        parent_id: Optional[str] = None,
        parent_path_or_name: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.parent_id = parent_id
        self.parent_path_or_name = parent_path_or_name

class HubspotItem:
    def __init__(
        self,
        id: str,
        type: str,
        created_at: datetime,
        updated_at: datetime,
        archived: bool = False,
        archived_at: Optional[datetime] = None,
        
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,

        company_name: Optional[str] = None,
        domain: Optional[str] = None,

        dealname: Optional[str] = None,
        amount: Optional[float] = None,
        stage: Optional[str] = None,

        subject: Optional[str] = None,
        status: Optional[str] = None,

        associations: Optional[Dict[str, Any]] = None,
        raw_properties: Optional[Dict[str, Any]] = None,
    ):
        # common
        self.id = id
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.archived = archived
        self.archived_at = archived_at

        # contact
        self.firstname = firstname
        self.lastname = lastname
        self.email = email

        # company
        self.company_name = company_name
        self.domain = domain

        # deal
        self.dealname = dealname
        self.amount = amount
        self.stage = stage

        # ticket
        self.subject = subject
        self.status = status

        # others
        self.associations = associations or {}
        self.raw_properties = raw_properties or {}