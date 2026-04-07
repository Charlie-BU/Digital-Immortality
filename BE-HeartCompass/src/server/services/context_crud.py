import logging
from sqlalchemy.orm import Session

from src.database.enums import UserGender, RelationStage, MBTI, parseEnum
from src.database.models import RelationChain, Event, ChatTopic, Crush, User

logger = logging.getLogger(__name__)


async def ccDeleteEvent(db: Session, user_id: int, event_id: int) -> dict:
    try:
        event = db.get(Event, event_id)
        if not event:
            return {
                "status": -1,
                "message": "Event not found",
            }
        if event.relation_chain.user_id != user_id:
            return {
                "status": -2,
                "message": "You are not authorized to delete this event",
            }
        if not event.is_active:
            return {
                "status": -3,
                "message": "Event is not active",
            }
        event.is_active = False
        db.commit()
        return {
            "status": 200,
            "message": "Event deleted",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting event {event_id}: {e}")
        return {
            "status": -4,
            "message": "Error deleting event",
        }


async def ccHardDeleteEvent(db: Session, user_id: int, event_id: int) -> dict:
    try:
        event = db.get(Event, event_id)
        if not event:
            return {
                "status": -1,
                "message": "Event not found",
            }
        if event.relation_chain.user_id != user_id:
            return {
                "status": -2,
                "message": "You are not authorized to delete this event",
            }
        if event.is_active:
            return {
                "status": -3,
                "message": "Event has not been deleted yet",
            }

        db.delete(event)
        db.commit()
        return {
            "status": 200,
            "message": "Event hard deleted",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error hard deleting event {event_id}: {e}")
        return {
            "status": -4,
            "message": "Error hard deleting event",
        }


async def ccGetEventById(db: Session, user_id: int, event_id: int) -> dict:
    event = db.get(Event, event_id)
    if not event:
        return {
            "status": -1,
            "message": "Event not found",
        }
    if event.relation_chain.user_id != user_id:
        return {
            "status": -2,
            "message": "You are not authorized to get this event",
        }
    if not event.is_active:
        return {
            "status": -3,
            "message": "Event has been deleted",
        }
    return {
        "status": 200,
        "message": "Get event success",
        "event": event.toJson(),
    }


async def ccGetEventsByRelationChainId(
    db: Session, user_id: int, relation_chain_id: int, page_size: int, current_page: int
) -> dict:
    relation_chain = db.get(RelationChain, relation_chain_id)
    if not relation_chain:
        return {
            "status": -1,
            "message": "Relation chain not found",
        }
    if relation_chain.user_id != user_id:
        return {
            "status": -2,
            "message": "You are not authorized to get events in this relation chain",
        }
    query = (
        db.query(Event)
        .filter(Event.relation_chain_id == relation_chain_id, Event.is_active == True)
        .order_by(Event.created_at.desc())
    )
    events = query.limit(page_size).offset((current_page - 1) * page_size).all()
    return {
        "status": 200,
        "message": "Get events success",
        "total": query.count(),
        "events": [event.toJson() for event in events],
    }


async def ccDeleteChatTopic(db: Session, user_id: int, chat_topic_id: int) -> dict:
    try:
        chat_topic = db.get(ChatTopic, chat_topic_id)
        if not chat_topic:
            return {
                "status": -1,
                "message": "Chat topic not found",
            }
        if chat_topic.relation_chain.user_id != user_id:
            return {
                "status": -2,
                "message": "You are not authorized to delete this chat topic",
            }
        if not chat_topic.is_active:
            return {
                "status": -3,
                "message": "Chat topic is not active",
            }
        chat_topic.is_active = False
        db.commit()
        return {
            "status": 200,
            "message": "Chat topic deleted",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting chat topic {chat_topic_id}: {e}")
        return {
            "status": -4,
            "message": "Error deleting chat topic",
        }


async def ccHardDeleteChatTopic(db: Session, user_id: int, chat_topic_id: int) -> dict:
    try:
        chat_topic = db.get(ChatTopic, chat_topic_id)
        if not chat_topic:
            return {
                "status": -1,
                "message": "Chat topic not found",
            }
        if chat_topic.relation_chain.user_id != user_id:
            return {
                "status": -2,
                "message": "You are not authorized to delete this chat topic",
            }
        if chat_topic.is_active:
            return {
                "status": -3,
                "message": "Chat topic has not been deleted yet",
            }

        db.delete(chat_topic)
        db.commit()
        return {
            "status": 200,
            "message": "Chat topic hard deleted",
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error hard deleting chat topic {chat_topic_id}: {e}")
        return {
            "status": -4,
            "message": "Error hard deleting chat topic",
        }


async def ccGetChatTopicById(db: Session, user_id: int, chat_topic_id: int) -> dict:
    chat_topic = db.get(ChatTopic, chat_topic_id)
    if not chat_topic:
        return {
            "status": -1,
            "message": "Chat topic not found",
        }
    if chat_topic.relation_chain.user_id != user_id:
        return {
            "status": -2,
            "message": "You are not authorized to get this chat topic",
        }
    if not chat_topic.is_active:
        return {
            "status": -3,
            "message": "Chat topic has been deleted",
        }
    return {
        "status": 200,
        "message": "Get chat topic success",
        "chat_topic": chat_topic.toJson(),
    }


async def ccGetChatTopicsByRelationChainId(
    db: Session, user_id: int, relation_chain_id: int, page_size: int, current_page: int
) -> dict:
    relation_chain = db.get(RelationChain, relation_chain_id)
    if not relation_chain:
        return {
            "status": -1,
            "message": "Relation chain not found",
        }
    if relation_chain.user_id != user_id:
        return {
            "status": -2,
            "message": "You are not authorized to get chat topics in this relation chain",
        }
    query = (
        db.query(ChatTopic)
        .filter(
            ChatTopic.relation_chain_id == relation_chain_id,
            ChatTopic.is_active == True,
        )
        .order_by(ChatTopic.created_at.desc())
    )
    chat_topics = query.limit(page_size).offset((current_page - 1) * page_size).all()
    return {
        "status": 200,
        "message": "Get chat topics success",
        "total": query.count(),
        "chat_topics": [chat_topic.toJson() for chat_topic in chat_topics],
    }


async def ccCreateCrush(
    db: Session,
    user_id: int,
    crush_name: str,
    gender: UserGender,
    mbti: MBTI,
) -> dict:
    try:
        new_crush = Crush(
            creator_id=user_id,
            name=crush_name,
            gender=gender,
            mbti=mbti,
        )
        db.add(new_crush)
        db.commit()
        return {
            "status": 200,
            "message": "Crush successfully created",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create crush for user {user_id}: {e}")
        return {"status": -1, "message": "Internal Server Error"}


async def ccCreateRelationChain(
    db: Session, user_id: int, crush_id: int, stage: RelationStage
) -> dict:
    try:
        crush = db.get(Crush, crush_id)
        if not crush:
            return {"status": -1, "message": "Crush not found"}

        if crush.creator_id != user_id:
            return {
                "status": -2,
                "message": "Permission denied: This is not your crush",
            }

        existing_chain_length = (
            db.query(RelationChain)
            .filter(RelationChain.crush_id == crush_id, RelationChain.is_active == True)
            .count()
        )
        if existing_chain_length > 0:
            return {"status": -3, "message": "Crush ID conflict: already bound"}
        new_relation_chain = RelationChain(
            user_id=user_id,
            crush_id=crush_id,
            current_stage=stage,
            is_active=True,
        )
        db.add(new_relation_chain)
        db.commit()
        return {
            "status": 200,
            "message": "Relation chain created",
        }

    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to create relation for user {user_id} and crush {crush_id}: {e}"
        )
        return {"status": -4, "message": "Internal Server Error"}


async def ccDeleteCrush(db: Session, user_id: int, crush_id: int) -> dict:
    try:
        crush = db.get(Crush, crush_id)
        if not crush:
            return {"status": -1, "message": "Crush not found"}
        if crush.creator_id != user_id:
            return {
                "status": -2,
                "message": "Permission denied: This is not your crush",
            }
        if not crush.is_active:
            return {"status": -3, "message": "Crush has been deleted"}
        crush.is_active = False
        db.commit()
        return {"status": 200, "message": "Crush successfully deleted"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete crush {crush_id}:{e}")
        return {"status": -4, "message": "Internal Server Error"}


async def ccDeleteRelationChain(
    db: Session, user_id: int, relation_chain_id: int
) -> dict:
    try:
        relation_chain = db.get(RelationChain, relation_chain_id)
        if not relation_chain:
            return {"status": -1, "message": "RelationChain not found"}
        if relation_chain.user_id != user_id:
            return {
                "status": -2,
                "message": "Permission denied: This is not your relationChain",
            }
        if not relation_chain.is_active:
            return {"status": -3, "message": "RelationChain has been deleted"}
        relation_chain.is_active = False
        db.commit()
        return {"status": 200, "message": "RelationChain successfully deleted"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete relationChain {relation_chain_id}:{e}")
        return {"status": -4, "message": "Internal Server Error"}


async def ccGetCrushById(db: Session, user_id: int, crush_id: int) -> dict:
    crush = db.get(Crush, crush_id)
    if not crush:
        return {"status": -1, "message": "Crush not found"}
    if crush.creator_id != user_id:
        return {"status": -2, "message": "Permission denied: This is not your crush"}
    if not crush.is_active:
        return {"status": -3, "message": "Crush has been deleted"}
    return {
        "status": 200,
        "message": "Get crush success",
        "crush": crush.toJson(include_relations=True),
    }


async def ccGetCrushesByUser(
    db: Session, user_id: int, page_size: int, current_page: int
) -> dict:
    query = (
        db.query(Crush)
        .filter(Crush.creator_id == user_id, Crush.is_active == True)
        .order_by(Crush.created_at.desc())
    )
    crushes = query.limit(page_size).offset((current_page - 1) * page_size).all()
    return {
        "status": 200,
        "message": "Get crushes success",
        "total": query.count(),
        "crushes": [crush.toJson() for crush in crushes],
    }


async def ccGetRelationChainById(
    db: Session, user_id: int, relation_chain_id: int
) -> dict:
    relation_chain = db.get(RelationChain, relation_chain_id)
    if not relation_chain:
        return {"status": -1, "message": "RelationChain not found"}
    if relation_chain.user_id != user_id:
        return {
            "status": -2,
            "message": "Permission denied: This is not your relationChain",
        }
    if not relation_chain.is_active:
        return {"status": -3, "message": "RelationChain has been deleted"}
    return {
        "status": 200,
        "message": "Get relation chain success",
        "relation_chain": relation_chain.toJson(include_relations=True),
    }


async def ccGetRelationChainsByUser(
    db: Session, user_id: int, page_size: int, current_page: int
) -> dict:
    query = (
        db.query(RelationChain)
        .filter(RelationChain.user_id == user_id, RelationChain.is_active == True)
        .order_by(RelationChain.created_at.desc())
    )
    relation_chain = query.limit(page_size).offset((current_page - 1) * page_size).all()
    return {
        "status": 200,
        "message": "Get relation chains success",
        "total": query.count(),
        "relation_chains": [
            relation_chain.toJson(include_relations=True)
            for relation_chain in relation_chain
        ],
    }


async def ccUpdateCrush(db: Session, user_id: int, crush_id: int, body: dict) -> dict:
    try:
        crush = db.get(Crush, crush_id)
        if not crush:
            return {"status": -1, "message": "Crush not found"}
        if crush.creator_id != user_id:
            return {
                "status": -2,
                "message": "Permission denied: This is not your crush",
            }
        if not crush.is_active:
            return {"status": -3, "message": "Crush has been deleted"}
        editable_columns = ["name", "mbti", "gender"]
        update_count = 0
        for key in body:
            if key in editable_columns:
                new_value = body[key]
                if key == "gender":
                    try:
                        new_value = parseEnum(UserGender, new_value)
                    except ValueError:
                        return {"status": -5, "message": "Invalid gender"}
                if key == "mbti":
                    try:
                        new_value = parseEnum(MBTI, new_value)
                    except ValueError:
                        return {"status": -6, "message": "Invalid mbti"}
                setattr(crush, key, new_value)
                update_count += 1
        if update_count > 0:
            db.commit()
        return {"status": 200, "message": "Crush updated"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update crush {crush_id}:{e}")
        return {"status": -4, "message": "Internal Server Error"}
