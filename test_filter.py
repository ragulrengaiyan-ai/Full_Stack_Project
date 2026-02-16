from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Provider(Base):
    __tablename__ = 'test_providers'
    id = Column(Integer, primary_key=True)
    service_type = Column(String)
    location = Column(String)
    address = Column(String, nullable=True)
    background_verified = Column(String, default="verified")

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Mock data
session.add_all([
    Provider(id=1, service_type='babysitter', location='Chennai', address=None),
    Provider(id=2, service_type='babysitter', location='Dindugul', address=None),
    Provider(id=3, service_type='babysitter', location='Nagapattinam', address='Some address in Nagapattinam'),
])
session.commit()

def test_filter(service_type, location):
    print(f"\nTesting: service_type={service_type}, location={location}")
    query = session.query(Provider).filter(Provider.background_verified == "verified")
    
    if service_type:
        query = query.filter(Provider.service_type.ilike(f"{service_type}"))
    
    if location:
        query = query.filter(or_(
            Provider.location.ilike(f"%{location}%"),
            Provider.address.ilike(f"%{location}%")
        ))
    
    results = query.all()
    print(f"Results Count: {len(results)}")
    for r in results:
        print(f"ID:{r.id} | Loc:{r.location} | Addr:{r.address}")

test_filter('babysitter', 'chennai')
test_filter('babysitter', None)
