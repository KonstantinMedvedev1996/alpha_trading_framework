import asyncio
from app.interfaces.cli.console import console_loop
from app.core.commands.securities import get_or_create_security_id

from app.db.domain import create_tables, drop_tables

from app.sandbox.storage import ensure_file_exists
from app.sandbox.state import AppState
from app.sandbox.controller import run_app

from app.infrastructure.services.futures import get_active_futures
from app.domain.assets.futures import get_security, get_securities_df

async def main():
    print("Ready for a wonderful journey")
    ensure_file_exists()
    state = AppState()
    await run_app(state)
    # print(Base.metadata.tables)
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)

# def create_tables():
#     engine.echo = True
#     # Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     engine.echo = True


if __name__ == "__main__":
    
    asyncio.run(main())
    
    # df = asyncio.run(get_active_futures())
    # print(df)
    
    # sec = asyncio.run(get_security(name="AAA"))
    # print(sec)
    
    # sec = asyncio.run(get_securities_df(platform='moex', security_type='future', status='active'))
    # print(sec)
    
    
    
    
    
    # asyncio.run(console_loop())
    # create_tables()
    # drop_tables()
    # number = asyncio.run(get_or_create_security_id(name="RTS"))
    # print(f"security id is {number}")
