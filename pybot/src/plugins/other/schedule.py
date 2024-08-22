from nonebot import on_command, get_driver, logger, require
import asyncio
import multiprocessing
from multiprocessing import Process, Queue, Value
import traceback
import os
import signal
import time
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from io import BytesIO
from ...utils import fetch_problem, get_problem_body, create_image_from_text, fetch_problems_total_number
from ...utils import db_manager
from datetime import datetime
from nonebot.adapters.qq import MessageEvent

# Global variables
current_load_process = None
process_status_queue = Queue()
terminate_flag = Value('b', False)

def run_async_load(start_id, end_id, languages, terminate_flag):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(load_all_images(start_id, end_id, languages, terminate_flag))
    finally:
        loop.close()


def load_images_process(start_id, end_id, languages, terminate_flag):
    try:
        run_async_load(start_id, end_id, languages, terminate_flag)
        process_status_queue.put(("completed", None))
    except Exception as e:
        process_status_queue.put(("error", str(e)))

async def fetch_and_store_image(question_id: int, language: str):
    try:
        data = fetch_problem(question_id)
        if data is not None:
            is_paid_only = data['isPaidOnly']
            if is_paid_only:
                return
            title, content = get_problem_body(data, language)
            title_slug = data['titleSlug']
            img_buffer = BytesIO()
            img = create_image_from_text(title, content, language)
            img.save(img_buffer, format="PNG")
            db_manager.store_image(question_id, language, img_buffer, title_slug, is_paid_only)
            img_buffer.close()  # Ensure the buffer is closed
            logger.info(f"Image for question {question_id} in {language} stored successfully")
    except Exception as e:
        logger.error(f"Failed to fetch and store image for question {question_id} in {language}: {e}")
        logger.error(traceback.format_exc())

async def load_all_images(start_id: int, end_id: int, languages: list, terminate_flag):
    tasks = []
    try:
        has_processed_all = False
        for question_id in range(start_id, end_id + 1):
            if terminate_flag.value:
                logger.info("Termination flag detected, stopping image loading")
                break
            for language in languages:
                is_exist, is_paid_only = db_manager.image_exists_and_is_paid_only(question_id, language)
                if not is_exist and not is_paid_only:
                    tasks.append(fetch_and_store_image(question_id, language))
            
            # Run tasks concurrently in smaller batches
            if len(tasks) >= 10:  # Adjust this number based on your needs
                await asyncio.gather(*tasks)
                tasks.clear()
            
            if question_id == end_id:
                has_processed_all = True
        # Run any remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
        
        logger.info("Stopped image loading.")
        if has_processed_all and not terminate_flag.value:
            db_manager.update_last_updated('images')
    except Exception as e:
        logger.error(f"Error in load_all_images: {e}")
        logger.error(traceback.format_exc())
    finally:
        # Ensure all tasks are properly cleaned up
        for task in tasks:
            if not task.done():
                task.cancel()

def safe_terminate_process(process: Process | None):
    global terminate_flag
    if process and process.is_alive():
        logger.info(f"Signaling process with pid {process.pid} to terminate")
        terminate_flag.value = True
        
        # Wait for the process to terminate gracefully
        start_time = time.time()
        while time.time() - start_time < 30:  # Wait for up to 30 seconds
            if not process.is_alive():
                break
            time.sleep(0.1)
        
        if process.is_alive():
            logger.warning("Process did not terminate gracefully, attempting to terminate forcefully")
            process.terminate()
            process.join(timeout=5)
            
            if process.is_alive():
                logger.warning("Process still alive after termination, attempting to kill")
                if process.pid:
                    try:
                        os.kill(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process has already terminated
        
        if not process.is_alive():
            process.close()
            logger.info("Process terminated successfully")
        else:
            logger.error("Failed to terminate the process")
    else:
        logger.info("No active process to terminate")

@scheduler.scheduled_job("cron", hour="3", minute="0")  # Run every day at 3:00 AM
async def scheduled_load_images():
    global current_load_process, terminate_flag
    logger.info("Starting daily image loading task")
    if db_manager.should_update_table('images'):
        if current_load_process is None or not current_load_process.is_alive():
            terminate_flag.value = False
            current_load_process = Process(target=load_images_process, 
                                           args=(1, fetch_problems_total_number(), ['en', 'cn'], terminate_flag))
            current_load_process.start()
            logger.info("Image loading process started")
        else:
            logger.info("Image loading process is already running")
    else:
        logger.debug("Skipping image loading task as it was updated recently")

manual_load = on_command("load_images", priority=1, block=True)

@manual_load.handle()
async def trigger_load_images(event: MessageEvent):
    global current_load_process, terminate_flag
    if current_load_process is None or not current_load_process.is_alive():
        try:
            terminate_flag.value = False
            current_load_process = Process(target=load_images_process, 
                                        args=(1, fetch_problems_total_number(), ['en', 'cn'], terminate_flag))
            current_load_process.start()
            logger.info(f"Image loading process started, pid: {current_load_process.pid}")
        except Exception as e:
            logger.error(f"Failed to start image loading process: {e}")
            logger.error(traceback.format_exc())
            safe_terminate_process(current_load_process)
            await manual_load.finish("图片加载任务启动失败，请查看日志以获取更多信息。")
        await manual_load.finish("图片加载任务已在后台启动，请使用 check_load_images 命令查看状态。")
    else:
        await manual_load.finish("图片加载任务已经在运行中，请等待其完成。")

cancel_load = on_command("cancel_load_images", priority=1, block=True)

@cancel_load.handle()
async def cancel_load_images(event: MessageEvent):
    global current_load_process
    if current_load_process and current_load_process.is_alive():
        safe_terminate_process(current_load_process)
        current_load_process = None
        await cancel_load.finish("图片加载任务已被取消。")
    else:
        await cancel_load.finish("当前没有正在运行的图片加载任务。")

check_load = on_command("check_load_images", priority=1, block=True)

@check_load.handle()
async def check_load_images(event: MessageEvent):
    global current_load_process
    if current_load_process and current_load_process.is_alive():
        await check_load.finish("图片加载任务正在进行中。")
    elif not process_status_queue.empty():
        status, error = process_status_queue.get()
        if status == "completed":
            await check_load.finish("图片加载任务已完成。")
        elif status == "error":
            await check_load.finish(f"图片加载任务发生错误: {error}")
    else:
        await check_load.finish("当前没有正在运行的图片加载任务。")

# Cleanup function to be called when the bot is shutting down
async def cleanup():
    global current_load_process
    if current_load_process:
        safe_terminate_process(current_load_process)
        current_load_process = None
    
    # Clear the status queue
    while not process_status_queue.empty():
        process_status_queue.get()

# Register the cleanup function to be called on bot shutdown
get_driver().on_shutdown(cleanup)