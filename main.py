
from email import message
import time
from unicodedata import name
import anyio

import aiohttp
from urllib.request import urlopen
from typing import List
from asynco import asyncify, create_task_group, syncify


async def fetch(session: aiohttp.ClientSession, url: str):
    # make a HTTP GET request for the URL.
    # note that get_request is a coroutine object
    try:
        async with session.get(url) as response:
            print("Url: {}, status: {}".format(url, response.status))
            txt = await response.text()
            return txt
    except Exception as error:
        print(str(error))


# running multiple async functions during the same period of time
async def crawl_urls_run() -> List[str]:
    res = []
    async with aiohttp.ClientSession() as session:
        async with create_task_group() as task_group:
            for url in get_urls_to_crawl():
                # run multiple async functions concurrently
                try:
                    promise = task_group.run(fetch)(session, url)
                    res.append(promise)
                except Exception as ex:
                    print("Failed to get data for url {} error: {}".format(url, ex))
    return [p.value for p in res]


async def async_func(name: str):
    await anyio.sleep(1)
    return f"I am non-blocking func, {name}"

def sync_func(name: str):
    time.sleep(1)
    return f"I am blocking func, {name}"


def sync_func_II(name: str):
    time.sleep(1)
    # started from a worker thread i.e assuming that the main program was ASYNC -> anyio.run(main)
    # send that async function to be run in the main thread running all the async code
    res = syncify(async_func, raise_sync_error=False)(name=name)
    return res


def get_urls_to_crawl() -> List[str]:
    urls_list = [
        'https://www.cnn.com/', 'https://www.foxnews.com/', 'https://www.bbc.com/', 'https://www.dawn.com',
        'https://www.cnbc.com', 'https://www.twitter.com'
    ]
    return urls_list


async def async_main():
    result = await crawl_urls_run()
    
    print('======================================\n')

    # asyncify🚀
    # safely executed in a "worker thread" without blocking the event loop. 🎉
    # run it on a worker thread this way allow to mix async code with blocking code more easily
    message = await asyncify(sync_func)(name="run_blocking_inside_async")
    
    print("Use the main async execution. {}".format(message))
    print('\n======================================\n')

    # syncify()🤓
    # in sync code and need to call an async function from within the sync code in a way that is sync-compatible
    message = await asyncify(sync_func_II)(name="run_async_inside_blocking")
    print("Use the main async execution. {}".format(message))

def sync_main():
    print('\n======================================\n')

    """
    If your program is mainly sync and you use syncify(raise_sync_error=False) that will run anyio.run().

    Running many times anyio.run() from a mainly sync program could be expensive.
    Because every time it has to start a new event loop, etc.

    If you need to call syncify(raise_sync_error=False) many times, for example in a for loop.
    Consider wrapping that for loop in a single async function, and calling that one instead.

    """
    message = sync_func_II(name="run_async_inside_blocking_and_create_event_loop")
    print("Start a full new async execution with anyio.run(). {}".format(message))
    print('\n======================================\n')


if __name__ == "__main__":
    # start the async func main
    anyio.run(async_main)
    sync_main()
