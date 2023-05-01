from typing import List, Optional

from core.database import Base, engine, generate_uuid, generate_uuid_str
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OhioenergyProvider(Base):
    __tablename__ = "providers"

    # id: Mapped[int] = mapped_column(primary_key=True)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid_str
    )
    utility_type: Mapped[str] = mapped_column(index=True)
    scrape_timestamp: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(index=True)
    address: Mapped[str]
    phone: Mapped[str]
    url: Mapped[str] = mapped_column(index=True)
    # price: Mapped[float]
    price: Mapped[str]
    rate_type: Mapped[str]
    percent_renewable: Mapped[str]
    intro_price: Mapped[str]
    term_length: Mapped[str]
    early_term_fee: Mapped[str]
    monthly_fee: Mapped[str]
    promo_offer: Mapped[str]

    def __repr__(self) -> str:
        return f"Provider(id={self.id!r}, utility_type={self.utility_type!r}, scrape_timestamp={self.scrape_timestamp!r}, name={self.name!r}, address={self.address!r}, phone={self.phone!r}, url={self.url!r}, price={self.price!r}, rate_type={self.rate_type!r}, percent_renewable={self.percent_renewable!r}, intro_price={self.intro_price!r}, term_length={self.term_length!r}, early_term_fee={self.early_term_fee!r}, monthly_fee={self.monthly_fee!r}, promo_offer={self.promo_offer!r})"


## Create table metadata
Base.metadata.create_all(engine)
