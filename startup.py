import logging
import asyncio
from uvicorn import Server, Config
from database import create_db_and_tables

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量，用于存储 Server 实例和任务
main_app_server = None
fallback_app_server = None
main_app_task = None
fallback_app_task = None

async def stop_server(server):
    """
    停止指定的服务器实例。

    :param server: 要停止的服务器实例
    """
    if server:
        logging.info("正在停止服务器...")
        await server.shutdown()
        logging.info("服务器已停止。")

async def start_fallback_app():
    """
    启动回退应用服务器。
    """
    global fallback_app_server
    logging.info("启动回退应用...")
    config = Config("fallback_app:app", host="0.0.0.0", port=8080, reload=True)
    fallback_app_server = Server(config)
    await fallback_app_server.serve()

async def start_main_app():
    """
    启动主应用服务器。
    """
    global main_app_server
    logging.info("启动主应用...")
    config = Config("main_app:app", host="0.0.0.0", port=8080, reload=True)
    main_app_server = Server(config)
    await main_app_server.serve()

def check_database_connection():
    """
    检查数据库连接是否正常。

    :return: 如果数据库连接成功返回 True，否则返回 False
    """
    try:
        create_db_and_tables()
        return True
    except Exception as e:
        logging.error(f"数据库连接错误: {e}")
        return False

async def main():
    """
    主函数，循环检查数据库连接并启动相应的应用。
    """
    global main_app_server, fallback_app_server, main_app_task, fallback_app_task
    while True:
        if check_database_connection():
            if main_app_task is None or main_app_task.done():
                logging.info("数据库已连接，启动主应用...")
                if fallback_app_task and not fallback_app_task.done():
                    await stop_server(fallback_app_server)
                    fallback_app_task = None
                try:
                    main_app_task = asyncio.create_task(start_main_app())
                except Exception as e:
                    logging.error(f"启动主应用失败: {e}")
            else:
                logging.info("主应用已在运行。")
        else:
            if fallback_app_task is None or fallback_app_task.done():
                logging.info("数据库未连接，启动回退应用...")
                if main_app_task and not main_app_task.done():
                    await stop_server(main_app_server)
                    main_app_task = None
                try:
                    fallback_app_task = asyncio.create_task(start_fallback_app())
                except Exception as e:
                    logging.error(f"启动回退应用失败: {e}")
            else:
                logging.info("回退应用已在运行。")
        await asyncio.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    asyncio.run(main())