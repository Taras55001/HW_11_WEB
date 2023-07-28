from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_


from src.database.models import Contact
from src.schemas import ContactResponse



async def get_contacts(limit: int, offset: int, db: AsyncSession):
    sq = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(sq)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    sq = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(sq)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactResponse, db: AsyncSession):
    contact = Contact(name=body.name, surname=body.surname, birthday=body.birthday, phone=body.phone, email=body.email,
                      user_id=body.user_id)
    if body.description:
        contact.description = body.description
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactResponse, db: AsyncSession):
    sq = select(Contact).filter_by(id=contact_id)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone = body.phone
        contact.email = body.email
        contact.user_id = body.user_id
        contact.description = body.description
        await db.commit()
        await db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: AsyncSession):
    sq = select(Contact).filter_by(id=contact_id)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact(user_id: int,
    contact_name: str,
    surname: str,
    email: str,
    db: AsyncSession):
    sq = select(Contact).filter_by(user_id=user_id)
    result = await db.execute(sq)
    query = result.scalars().all()
    if contact_name:
        query = [contact for contact in query if contact.name == contact_name]
    if surname:
        query = [contact for contact in query if contact.surname == surname]
    if email:
        query = [contact for contact in query if contact.email == email]

    return query[0] if query else None


async def upcoming_birthdays(user_id, db):
    current_date = datetime.now().date()
    future_birthday = current_date + timedelta(days=7)
    sq = select(Contact).filter(
        and_(Contact.user_id == user_id, Contact.birthday >= current_date, Contact.birthday <= future_birthday)
    )
    result = await db.execute(sq)
    return result.scalars().all()
