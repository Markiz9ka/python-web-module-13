import fastapi
from fastapi import Request
from fastapi import HTTPException
import database
import contacts.schema as schema
import contacts.model as model
from datetime import datetime, timedelta
import auth.service
from slowapi import Limiter
from slowapi.util import get_remote_address


router = fastapi.APIRouter(prefix="/contacts", tags=["Contacts"])
auth_service = auth.service.Auth()
limiter = Limiter(key_func=get_remote_address)

@router.get("/")
@limiter.limit("10/minute")
async def root(
    request: Request,
    db=fastapi.Depends(database.get_database),
    user = fastapi.Depends(auth_service.get_user)
)-> list[model.ContactResponse]:
    
    return [contact for contact in db.query(schema.Contacts).filter(schema.Contacts.user_id == user.id).all()]

@router.get("/find/{contact_id}")
@limiter.limit("10/minute")
async def get_by_id(
    contact_id: int,
    request: Request,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> model.ContactResponse:
    contact = db.query(schema.Contacts).filter(
        schema.Contacts.id == contact_id,
        schema.Contacts.user_id == user.id
    ).first()
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact

@router.post("/")
@limiter.limit("10/minute")
async def post_root(
    request: Request,
    contact: model.ContactModel,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
)-> model.ContactModel:
    new_contact = schema.Contacts(user_id=user.id,**contact.__dict__)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact

@router.delete("/{contact_id}")
@limiter.limit("10/minute")
async def del_by_id(contact_id : int,
                    request: Request,   
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
):
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id,schema.Contacts.user_id == user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()

    return {"message": "Contact deleted"}

@router.patch("/{contact_id}")
@limiter.limit("10/minute")
async def patch_contact(contact_id:int,
                        request: Request,
    contact_data: model.ContactUpdate,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> model.ContactResponse:
    contact = db.query(schema.Contacts).filter(schema.Contacts.id == contact_id, schema.Contacts.user_id == user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in contact_data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact

@router.get("/search")
@limiter.limit("10/minute")
async def search_contacts(
    request: Request,
    name: str = None,
    surename: str = None,
    email: str = None,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
) -> list[model.ContactResponse]:
    query = db.query(schema.Contacts).filter(schema.Contacts.id == user.id)
    
    if name:
        query = query.filter(schema.Contacts.name == name)
    if surename:
        query = query.filter(schema.Contacts.surename == surename)
    if email:
        query = query.filter(schema.Contacts.email == email)
    
    results = query.all()
    return results

@router.get("/upcoming-birthdays")
@limiter.limit("10/minute")
async def get_upcoming_birthdays(
    request: Request,
    db=fastapi.Depends(database.get_database),
    user=fastapi.Depends(auth_service.get_user)
)-> list[model.ContactResponse]:
    today = datetime.today().date()
    upcoming_date = datetime.today().date() + timedelta(days=7)

    contacts_with_upcoming_birthdays = db.query(schema.Contacts).filter(
        schema.Contacts.user_id == user.id,
        schema.Contacts.date_of_birth.between(today, upcoming_date)
    ).all()

    return contacts_with_upcoming_birthdays