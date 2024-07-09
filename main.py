import multiprocessing
from multiprocessing import Barrier, Lock, Process
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from time import time, sleep
from datetime import datetime

app = FastAPI()


def test_with_barrier(synchronizer, serializer):
    name = multiprocessing.current_process().name
    synchronizer.wait()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sleep(2)
    with serializer:
        print("process %s ----> %s" % (name, now))


def test_without_barrier():
    name = multiprocessing.current_process().name
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sleep(2)
    print("process %s ----> %s" % (name, now))


@app.get("/start_processes/{num_processes}", response_class=JSONResponse)
def start_processes(num_processes: int = Path(..., description="Number of processes to start")):
    if num_processes < 2:
        raise HTTPException(status_code=400, detail="Number of processes must be at least 2")

    synchronizer = Barrier(2)
    serializer = Lock()

    processes = [
        Process(name=f'p{i + 1} - test_with_barrier', target=test_with_barrier,
                args=(synchronizer, serializer)) if i < num_processes // 2
        else Process(name=f'p{i + 1} - test_without_barrier', target=test_without_barrier)
        for i in range(num_processes)
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    return {"status": f"Started and completed {num_processes} processes"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
