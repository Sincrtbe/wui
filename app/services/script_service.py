"""Servicio de guiones."""
from sqlalchemy.orm import Session
from app.models import Script, Tag
from app.schemas.script import ScriptCreate, ScriptUpdate


class ScriptService:
    """Servicio de gestión de guiones."""

    @staticmethod
    def create(db: Session, script: ScriptCreate) -> Script:
        """Crea un nuevo guión."""
        db_script = Script(
            channel_id=script.channel_id,
            title=script.title,
            description=script.description,
            voice_script=script.voice_script,
            graphic_script=script.graphic_script,
            status="draft",
        )
        db.add(db_script)
        db.flush()

        if script.tags:
            for tag_name in script.tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                db_script.tags.append(tag)

        db.commit()
        db.refresh(db_script)
        return db_script

    @staticmethod
    def get_all(db: Session, channel_id: int | None = None, status: str | None = None, search: str | None = None) -> list[Script]:
        """Obtiene guiones con filtros opcionales."""
        query = db.query(Script)

        if channel_id is not None:
            query = query.filter(Script.channel_id == channel_id)

        if status is not None:
            query = query.filter(Script.status == status)

        if search is not None:
            query = query.filter(
                (Script.title.contains(search)) | (Script.description.contains(search))
            )

        return query.all()

    @staticmethod
    def get_by_id(db: Session, script_id: int) -> Script | None:
        """Obtiene un guión por ID."""
        return db.query(Script).filter(Script.id == script_id).first()

    @staticmethod
    def update(db: Session, script_id: int, script_update: ScriptUpdate) -> Script | None:
        """Actualiza un guión."""
        db_script = db.query(Script).filter(Script.id == script_id).first()
        if not db_script:
            return None

        update_data = script_update.model_dump(exclude_unset=True)
        tags = update_data.pop("tags", None)

        for key, value in update_data.items():
            setattr(db_script, key, value)

        if tags is not None:
            db_script.tags.clear()
            for tag_name in tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                db_script.tags.append(tag)

        db.commit()
        db.refresh(db_script)
        return db_script

    @staticmethod
    def delete(db: Session, script_id: int) -> bool:
        """Elimina un guión."""
        db_script = db.query(Script).filter(Script.id == script_id).first()
        if not db_script:
            return False

        db.delete(db_script)
        db.commit()
        return True
