import asyncio
from app.interfaces.cli.console import console_loop
from app.core.commands.securities import get_or_create_security_id

from app.db.domain import create_tables, drop_tables

   


def main():
    print("Ready for a wonderful journey")
    # print(Base.metadata.tables)
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)

# def create_tables():
#     engine.echo = True
#     # Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     engine.echo = True


if __name__ == "__main__":
    main()
    asyncio.run(console_loop())
    # create_tables()
    # drop_tables()
    # number = asyncio.run(get_or_create_security_id(name="RTS"))
    # print(f"security id is {number}")
