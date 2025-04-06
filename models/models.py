from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    input_path = Column(String)
    output_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def create(db: Session, job_id: str,input_path: str="",output_path: str=""):
        job = Job(id=job_id, status="processing",input_path=input_path, output_path=output_path)
        db.add(job)
        db.commit()
        return job
    @staticmethod
    def update_input_path(db: Session, job_id: str,input_path: str=""):
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.input_path = input_path
            db.commit()
        return job

    @staticmethod
    def update_status(db: Session, job_id: str, status: str,output_path: str = ""):
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.output_path = output_path
            db.commit()
        return job

    @staticmethod
    def get_job(db: Session, job_id: str):
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            return {
                "status": job.status,
                "output_path": job.output_path
            }
        return None

    @staticmethod
    def get_all(db: Session, limit: int = 50):
        jobs = db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
        return [
            {
                "id": job.id,
                "status": job.status,
                "output_path": job.output_path,
                "timestamp": job.created_at.isoformat()
            }
            for job in jobs
        ]

    from sqlalchemy import and_

    @staticmethod
    def get_filtered(db: Session, from_date: str = None, to_date: str = None, limit: int = 100):
        query = db.query(Job)

        if from_date:
            try:
                from_dt = datetime.fromisoformat(from_date)
                query = query.filter(Job.created_at >= from_dt)
            except ValueError:
                pass  # optional: log or raise error

        if to_date:
            try:
                to_dt = datetime.fromisoformat(to_date)
                query = query.filter(Job.created_at <= to_dt)
            except ValueError:
                pass  # optional: log or raise error

        query = query.order_by(Job.created_at.desc()).limit(limit)
        jobs = query.all()

        return [
            {
                "id": job.id,
                "status": job.status,
                "output_path": job.output_path,
                "timestamp": job.created_at.isoformat()
            }
            for job in jobs
        ]