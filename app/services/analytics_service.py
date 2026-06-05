"""Servicio de análisis de datos."""
import json
import os
from sqlalchemy.orm import Session
from app.models.daily_stat import DailyStat
from app.models.channel import Channel
from tools.script_runner import run_script
from datetime import date

def run_daily_stats_import(db: Session, channel_id: int):
    """Ejecuta DatosDiarios.py para un canal e importa los resultados a la BD."""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return {"error": "Canal no encontrado"}
    
    # Obtener el ID de YouTube desde los social_links o el custom_url
    # En creacionDcanal.py se guarda en social_links["youtube"]
    youtube_url = channel.social_links.get("youtube", "") if channel.social_links else ""
    yt_id = youtube_url.split("/")[-1] if youtube_url else ""
    
    if not yt_id:
        return {"error": "No se pudo determinar el ID de YouTube del canal"}
    
    # Ejecutar el script
    # El script DatosDiarios.py guarda en la carpeta 'vistas_diarias' por defecto
    output_dir = "vistas_diarias"
    result = run_script("DatosDiarios.py", args=[yt_id, output_dir])
    
    if not result.success:
        return {"error": f"Error al ejecutar script: {result.error or result.stderr}"}
    
    # Leer el JSON generado
    json_path = os.path.join("tools", output_dir, f"{yt_id}_stats.json")
    if not os.path.exists(json_path):
        return {"error": "Archivo de resultados no encontrado"}
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Guardar en la base de datos
    new_stat = DailyStat(
        channel_id=channel_id,
        view_count=data.get("viewCount", 0),
        subscriber_count=data.get("subscriberCount", 0),
        video_count=data.get("videoCount", 0),
        stat_date=date.today()
    )
    
    # Evitar duplicados para el mismo día
    existing = db.query(DailyStat).filter(
        DailyStat.channel_id == channel_id,
        DailyStat.stat_date == date.today()
    ).first()
    
    if existing:
        existing.view_count = new_stat.view_count
        existing.subscriber_count = new_stat.subscriber_count
        existing.video_count = new_stat.video_count
    else:
        db.add(new_stat)
    
    db.commit()
    return {"success": True, "data": data}
